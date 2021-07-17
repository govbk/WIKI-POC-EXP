# 在补丁上戳个洞——利用已经被修复的漏洞实现IE沙箱逃逸

**作者:FlowerCode@腾讯玄武实验室**

english version:https://xuanwulab.github.io/2015/08/27/Poking-a-Hole-in-the-Patch/

0x00 The Problem
================

* * *

James Forshaw在2014年11月曾向微软报告过一个Windows Audio Service的本地权限提升漏洞。

Windows Audio Service负责管理系统中所有进程的音频会话。这个服务会把会话参数存储到`HKCU\Software\Microsoft\Internet Explorer\LowRegistry\Audio\PolicyConfig`。

为了使低权限进程也可修改音频会话的参数，服务在存储时会递归设置所有子键的ACL为Low IL可控。

若在这个注册表键下设置一个符号链接指向高权限注册表键，就可能导致高权限注册表键变为Low IL可控。

0x01 The Patch
==============

* * *

微软发布了安全公告MS14-071，并发布了KB3005607补丁修复这个漏洞。 这个补丁增加了两个函数，SafeRegCreateKeyEx和DetectRegistryLink。

DetectRegistryLink大致的代码逻辑如下：

```
int DetectRegistryLink(const HKEY key_handle, const wchar_t sub_key_path[], HKEY * out_handle)
{
    int detect_result = 0;
    HKEY sub_key_handle;
    LSTATUS status = RegOpenKeyExW(key_handle,
                                   sub_key_path,
                                   REG_OPTION_OPEN_LINK,
                                   KEY_ALL_ACCESS,
                                   &sub_key_handle);

    if (status != ERROR_SUCCESS) {
        if (status == ERROR_FILE_NOT_FOUND) {
            detect_result = 3;
        } else if (status == ERROR_ACCESS_DENIED) {
            detect_result = 4;
        } else {
            detect_result = 5;
        }
    } else {
        DWORD key_type;
        BYTE data[MAX_PATH * 2];
        DWORD data_size = sizeof(data);

        status = RegQueryValueExW(sub_key_handle, 
                                  kSymbolicLinkValueName, 
                                  nullptr,
                                  &key_type, 
                                  data, 
                                  &data_size);

        if (((status == ERROR_SUCCESS) || (status == ERROR_MORE_DATA)) && (key_type == REG_LINK)) {
            detect_result = 1;
        } 
        if ((status == ERROR_FILE_NOT_FOUND) && (detect_result != 1)) {
            HKEY temp_key_handle;
            status = RegOpenKeyExW(key_handle,
                                   sub_key_path,
                                   0,
                                   KEY_READ,
                                   &temp_key_handle);

            RegCloseKey(temp_key_handle);
            detect_result = (status == ERROR_SUCCESS) + 1;
        }

        *out_handle = sub_key_handle;
    }

    return detect_result;
}

```

DetectRegistryLink对于注册表符号链接做了比较严格的判断。这个函数使用REG_OPTION_OPEN_LINK打开注册表键之后处理了多种情况，包括重定向到不存在的键值等。最终打开的注册表键句柄被传出函数复用。

外层的SafeRegCreateKeyEx在创建注册表键之前调用了这个函数进行检查，发现有注册表符号链接则使用NtDeleteKey进行删除，最后统一使用RegCreateKeyEx创建一个新的注册表键。

```
HKEY sub_key_handle;
int detect_result = DetectRegistryLink(key_handle, kSubKeyPath, &sub_key_handle);

if (detect_result == 1) {
    status = NtDeleteKey(sub_key_handle);
    RegCloseKey(sub_key_handle);
    sub_key_handle = nullptr;

    if (!NT_SUCCESS(status)) {
        return ERROR_ACCESS_DENIED;
    }
}

if (detect_result > 3) {
    if (sub_key_handle) {
        RegCloseKey(sub_key_handle);
    }

    return ERROR_ACCESS_DENIED;
}

DWORD create_disposition = 0;

if (sub_key_handle) {
    create_disposition = REG_OPENED_EXISTING_KEY;
} else {
    status = RegCreateKeyExW(key_handle,
                             kSubKeyPath,
                             0,
                             nullptr,
                             0,
                             KEY_ALL_ACCESS,
                             nullptr,
                             &sub_key_handle,
                             &create_disposition);

    if (status != ERROR_SUCCESS) {
        return status;
    }

    if (create_disposition != REG_CREATED_NEW_KEY) {
        RegCloseKey(sub_key_handle);
        return ERROR_ACCESS_DENIED;
    }
}

```

0x02 The Flaw
=============

* * *

逻辑看似很严密，然而存在一个比较严重的问题。

在使用NtDeleteKey删除目标注册表键之后，系统不再允许对它进行操作。虽然已打开的句柄继续有效，但任何操作都会返回STATUS_KEY_DELETED，只能关闭句柄。

在句柄关闭后，后续操作就只能使用对象名打开一个新的句柄。在这种情况下，系统并不保证和之前同名的对象就是同一个对象。

通过精确的时间差攻击，我们可以抢在RegCreateKeyEx被调用之前创建一个符号链接，从而绕过判断。

0x03 The Exploit
================

* * *

我们仍然以IE 11沙箱为例，说明如何利用此漏洞提升权限。

为了满足利用条件，首先需要让Windows Audio Service做出删除动作。

我们可以故意在`HKCU\Software\Microsoft\Internet Explorer\LowRegistry\Audio\PolicyConfig`注册表键下创建一个符号链接，并触发Windows Audio Service写入，这样就会走入删除逻辑。

如何精确控制写入符号链接的时间很重要。我们当然可以开十万个线程循环写入，总有一天会成功。但其实系统已经提供了这样的触发机制。

NtNotifyChangeKey可以监视一个注册表键，当我们指定的注册表操作发生时，设置一个事件信号。

通过在符号链接上设置通知，我们可以在符号链接被Windows Audio Service删除时立刻触发，并有机会抢在Windows Audio Service创建新的注册表键之前创建一个符号链接。

将符号链接指向`HKCU\Software\Microsoft\Internet Explorer\Low Rights\ElevationPolicy`注册表键下的一个尚不存在的GUID，就可以满足REG_CREATED_NEW_KEY的判断，成功创建目标注册表键。

之后`Windows Audio Service`会使用上层注册表键（PolicyConfig）的安全性设置（Low IL可控）覆盖目标注册表键的安全性设置，导致刚创建的ElevationPolicy键值可被IE沙箱内进程写入。

这时写入任意的AppPath，并将Policy设置为0x3，即可在IE沙箱内以Medium IL启动任意进程。

0x04 The Trick
==============

* * *

Windows Audio Service的注册表操作是在RpcImpersonateClient之后进行的。所以在IE沙箱中直接操作虽然可以竞争成功，但注册表操作会使用源进程的Low IL令牌，权限不足。

James Forshaw在原版的PoC中未能解决这个问题，只能在外部手动启动SndVol.exe触发。

为了解决这个问题，我们需要触发一个Medium IL以上的进程使用音频会话，通常只需要进程发出声音即可。

IE Elevation Policy中默认设置了一些进程可以在沙箱内用Medium IL启动，其中就包括记事本（Notepad.exe）。Medium IL进程启动后我们只有结束进程的权限，但在启动进程时我们可以传递命令行参数。

记事本在打开不存在的文件时会弹出一个系统对话框询问是否需要创建新文件，伴随一声系统默认声音。这就足够触发Windows Audio Service写入注册表键了。

通过反复启动尝试，我们就能多次竞争，保证最终成功。

0x05 The Mitigation
===================

* * *

微软最终在2015年8月的补丁中彻底禁止了Low IL进程创建注册表符号链接。在设置注册表符号链接时，内核通过RtlIsSandboxedToken函数判断当前进程令牌是Low IL或AppContainer则直接返回拒绝访问。这导致任何基于注册表符号链接的攻击在Low IL都无法使用了，因此在IE沙箱内直接利用这个漏洞的可能性被彻底封堵了。

0x06 References
===============

* * *

Issue 99: IE11 AudioSrv RegistryKey EPM Privilege Escalation – James Forshaw https://code.google.com/p/google-security-research/issues/detail?id=99

Windows 音频服务中的漏洞可能允许特权提升 (3005607) https://technet.microsoft.com/library/security/MS14-071

Windows 10 Symbolic Link Mitigations – James Forshaw https://googleprojectzero.blogspot.com/2015/08/windows-10hh-symbolic-link-mitigations.html