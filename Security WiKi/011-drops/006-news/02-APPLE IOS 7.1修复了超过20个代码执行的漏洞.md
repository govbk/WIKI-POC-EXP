# APPLE IOS 7.1修复了超过20个代码执行的漏洞

![enter image description here](http://drops.javaweb.org/uploads/images/3d1796a139ccea7b1ae1166564d4446d3bbbb7a2.jpg)

Apple在最新发布的[iOS 7.1](http://support.apple.com/kb/HT6162)系统上，修复了可能导致代码执行以及其他的一些漏洞，这个新版本的发布仅仅是在Apple为了修复SSL证书验证错误而发布[iOS 7.06](https://threatpost.com/apple-fixes-certificate-validation-flaw-in-ios/104427)之后两个周。

上一个版本只是为了修复证书验证的漏洞而专门放出的，此次的版本iOS 7.1修复了大量的漏洞，内核为webkit的Safari的在安全方面做了一次很重要的升级，修复了19个内存泄露的问题，将近一半的漏洞是被谷歌Chrome安全团队发现的。

新版本修复的一个代码执行的漏洞是在读写文件格式处理的ImageIO函数上的问题。Apple同时修复了在ARM中ptmx_get_ioctl函数越界内存访问问题。

除了这些严重的代码执行漏洞，Apple同时修复了一个iTunes Store上的一个漏洞，可以允许攻击者诱骗用户下载恶意程序。

还有几个补丁修复了不太严重的漏洞，完整的修复列表在[这里](http://support.apple.com/kb/HT6162)。