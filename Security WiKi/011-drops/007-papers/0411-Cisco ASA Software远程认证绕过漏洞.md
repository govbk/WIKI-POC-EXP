# Cisco ASA Software远程认证绕过漏洞

0x01 漏洞简介
---------

* * *

Cisco ASA Software的部分管理接口在身份认证时存在验证逻辑问题，导致攻击者可以绕过身份认证，实现未授权操作。

0x02 漏洞原理
---------

* * *

默认情况下，ASA的管理接口通过basic auth+cookie的方式进行认证，如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/0f4a57e11c7e1e3bcbaaadc8946499d0067b9bc4.jpg)

漏洞存在于Configuration选项卡的Customization页面的preview功能。此页面用于修改webvpn的用户登录页面。但Preview的管理请求处理逻辑缺乏Basic Auth认证，仅仅通过验证cookie的有效性来进行判定。但Cookie验证逻辑上存在问题， Lua代码如下：

```
Function CheckAsdmSession(cookie,no_redirect)

省略部分代码..
Local f = io.open(‘asdm/’..cookie, “r”)
If f ~= nil then
    f:close()
    return true;
end

```

可以看出，在CheckAsdmSession 函数中，仅仅校验该函数cookie传入的文件存在与否。通过修改Cookie中ced的值，设置为设备上存在的文件，如`Ced=../../locale/ru/LC_MESSAGES/webvpn.mo`，即可达到绕过验证的效果。

![enter image description here](http://drops.javaweb.org/uploads/images/2628b81a75b1b8aa89654b0ccd1c00ede231cd22.jpg)

我们可以通过对`/+CSCOE+/cedf.html`页面的请求查看preview页面的修改结果。

![enter image description here](http://drops.javaweb.org/uploads/images/d6b5d949efa7b9f6e14a657ca84a4016fffbcc97.jpg)

现有系统对于preview页面的生效需要进行basic auth校验的，但固件版本保留了老的生效接口/+CSCOE+/cedsave.html（老接口不需要进行basic auth认证），通过调用此接口，即可完成对login page的html代码的修改。如下：

![enter image description here](http://drops.javaweb.org/uploads/images/5f53d057fe70b8a2dace10d28acd0a1572be4356.jpg)

通过修改登录页的代码，攻击者截获用于登录VPN的账号密码，也可以进行诸如劫持、挂马等操作。

0x03 漏洞修复
---------

* * *

目前cisco已经针对固件提供了修复方案，受影响的ASA版本可以通过官方通告进行查看。VPN类设备多属于企业的入口，提醒各公司运维人员以最高优先级修复。 官方链接：[http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20141008-asa](http://tools.cisco.com/security/center/content/CiscoSecurityAdvisory/cisco-sa-20141008-asa)