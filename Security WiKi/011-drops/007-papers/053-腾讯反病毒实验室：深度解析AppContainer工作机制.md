# 腾讯反病毒实验室：深度解析AppContainer工作机制

0x00 前言
=======

* * *

Win8开始，Windows引入了新的进程隔离机制AppContainer，MetroAPP以及开启EPM的IE Tab进程都运行在AppContainer隔离环境，在最新的Win10Pre(9926)上，仍然如此。腾讯反病毒实验室对AppContainer的工作机制做一深入解读。

0x01 AppContainer带来的变化
======================

* * *

Vista以前的系统，如XP，用安全描述符（简称SD，下同）里的DACL（discretionary access control list）来控制用户和用户组的访问权限。

Vista以后，增加了Integrity Mechanism，在SD的SACL(system access control list)里增加一个mandatory label的ACE，扩展了Windows安全体系。默认的控制策略是No-Write-Up，允许较低完整性级别的进程读访问较高完整性级别的对象；禁止较低完整性级别的进程写访问较高完整性级别的对象。

Win8引入了AppContainer隔离机制，提供了更细粒度的权限控制，能够阻止对未授权对象的读写访问。

以Win10PreX64(9926)开启EPM的IE Tab进程为例，看看有哪些变化。

从Process Explorer里可以看到，IE Tab进程的完整性级别不再是Low，而是变成了AppContainer：

![enter image description here](http://drops.javaweb.org/uploads/images/ce8b9a806fd90bbdbd29d6d4d9b714f722c8b063.jpg)图1

在进程属性的Security标签可以看到，增加了标志为AppContainer以及Capability的SID：

![enter image description here](http://drops.javaweb.org/uploads/images/930baff608db4632eacde6ea04212e2e66ebc484.jpg)图2

一个AppContainer进程可以访问的对象，在SD的DACL里增加了额外的ACE。以IE Tab进程的进程对象为例：

![enter image description here](http://drops.javaweb.org/uploads/images/64a680c7d69d2051af79f544fd342a5f68730018.jpg)图3

0x02 如何使用AppContainer隔离机制
=========================

* * *

这里我们不讨论MetroAPP，主要看看DesktopAPP如何使用AppContainer隔离机制。

仍然以Win10PreX64(9926)开启EPM的IE Tab进程为例：在IE选项里开启EPM,下断点nt!NtCreateLowBoxToken，然后新建IE Tab，命中断点，截取最上面的几层调用栈：

![enter image description here](http://drops.javaweb.org/uploads/images/06d804a23180cf64b57ea54443fa1c5f619e74dc.jpg)图4

可见，通过CreateProcess这个API就可以创建出AppContainer进程。

看看CreateAppContainerProcessStrW的逻辑片段，把PackageSID String(图2里标记为AppContainer的SID)和CapabilitySID(图2里标记为Capability的SID) string转为SID后，传给了CreateAppContainerProcessW：

![enter image description here](http://drops.javaweb.org/uploads/images/70e710843d7fc05ba34e6a5e7b8319de612b9712.jpg)图5

看看CreateAppContainerProcessW的逻辑片段，把传入的CapabilitySIDs和PackageSID加入到ProcThreadAttributes，然后通过STARTUPINFOEX结构把ProcThreadAttributes传给了CreateProcessW。

![enter image description here](http://drops.javaweb.org/uploads/images/f36b589f8d44f217ab0d7f1fe47d4cec294a804d.jpg)图6

![enter image description here](http://drops.javaweb.org/uploads/images/b385c79ee0e0b292bcec34d3915d6633dfc8a342.jpg)图7

![enter image description here](http://drops.javaweb.org/uploads/images/5fac7e6300f91778646651da5b8e811c575844d7.jpg)图8

搞清楚IE Tab进程的创建逻辑，我们就可以创建自己的AppContainer进程了。

直接复用IE的PackageSID和CapabilitySIDs来创建AppContainer进程。如果需要定义自己的PackageSID，可以参考MSDN上的CreateAppContainerProfile等API，这里就不讨论了。

成功的创建出了具有AppContainer隔离机制的记事本进程。32位和64位进程都可以。可以自由组合Capability，这里我选择了IE Tab 6个Capability里的3个。

![enter image description here](http://drops.javaweb.org/uploads/images/3ee57a800427a7948dc98c4a1c03a3b73518be19.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/82af9ab9734d6232850d93897c408cdf6d0975e5.jpg)

如果程序在设计时没有考虑使用AppContainer隔离机制，依赖没有授权给AppContainer的系统资源，比如系统根目录，用户根目录等，使用AppContainer隔离机制启动程序会失败。

0x03 AppContainer的访问权限控制
========================

* * *

为描述方便，AppContainer进程的AccessToken我们简称为LowBoxToken（下同）。

下面是一个LowBoxToken的部分信息，可以看到TokenFlags的掩码位0x4000是置位的，这表示该Token是一个LowBoxToken。我们还可以看到PackageSid、Capabilities等信息（图2里标志为AppContainer和Capability的SID）。

![enter image description here](http://drops.javaweb.org/uploads/images/abff67fe6e61681430a875958d90021ee77ac292.jpg)图11

0x04 DACL
=========

* * *

DACL的遍历是在SepNormalAccessCheck/SepMaximumAccessCheck里进行的。这里我们以SepNormalAccessCheck为例，来看一看如何处理AppContianer相关的ACE。

一般来说，在遍历DACL时，如果满足以下3个条件中的任意一个，检查停止。

有一个access-denied ACE明确拒绝了请求访问权限中的任意一个；

有一个或者多个access-allowed ACEs明确给予了所有的请求访问权限；

已经检查完了所有的ACE，但是仍然至少有一个请求访问权限没有被明确给予，这种情况下，访问被拒绝。

从Windows Server 2003开始，DACL里ACE的顺序为：

```
Explicit    ACE:Access Denied
Explicit    ACE:Access Allowed
Inherited ACE:Access Denied
Inherited ACE:Access Allowed

```

这个遍历规则和顺序保证了明确拒绝优先于明确允许；明确指定的访问控制优先于继承的访问控制。

以下的内容基于Win10PreX86( 9926)。

0x05 ACCESS_ALLOWED_ACE_TYPE
============================

* * *

在遍历类型为ACCESS_ALLOWED_ACE_TYPE的ACE时，如果ACE的SID前缀为SePackagePrefixSid(S-1-15-2)或者SeCapabilityPrefixSid(S-1-15-3)，则跳转到处理AppContainer访问权限控制的逻辑：

![enter image description here](http://drops.javaweb.org/uploads/images/d68ae48b151cf1cc4d855acc0e54566364b85b33.jpg)图12

如果ACE的SID前缀为SePackagePrefixSid(S-1-15-2)，会先看这个SID是否为ALL APPLICATION PACKAGES，这是一个Well known SID

![enter image description here](http://drops.javaweb.org/uploads/images/9b1c7e10dc9981b61b587ace8def95b0b93a232f.jpg)图13

如果是这个SID，认为匹配成功，不需要再精确比较SID了；否则和Token的PackageSID做精确匹配：

![enter image description here](http://drops.javaweb.org/uploads/images/b524f13e1619594e963a88645c3d78a05ab1eddd.jpg)图14

如果ACE的SID前缀为SeCapabilityPrefixSid(S-1-15-3)，会尝试匹配Token的Capabilities：

![enter image description here](http://drops.javaweb.org/uploads/images/b954426201fc8ce3c7dc1cf34483cbffbf8b4879.jpg)图15

PackageSID或者Capabilities匹配成功后，会通过a13记录获取到的权限以及还剩下未获取到的权限。a13是上层调用传进来的结构指针，上一层函数会根据这个结构的值，判断AppContainer进程是否获取到了请求的访问权限。

看看上一层函数SepAccessCheck的逻辑片段，var_AccessLowbox就是图14/15里的a13。如果PackageSID或者CapabilitieSID给予的权限不能完全覆盖用户请求的权限（var_Remaining != 0），则访问失败：

![enter image description here](http://drops.javaweb.org/uploads/images/6410eb64760813b45261afaa41401860957ca38c.jpg)图16

另外，对于No DACL的情况，也有额外的处理逻辑。AppContainer进程访问No DACL的对象时，是无法获得访问权限的：

![enter image description here](http://drops.javaweb.org/uploads/images/568e5d49bcfabbb1fbf19f142800667dba728bae.jpg)图17

所以在Win8及以上系统中，我们如果想要创建一个所有进程（包括开启EPM的IE Tab ）都能访问的对象，对于该对象的SD，除了在SACL里指定为低完整性级别外，还要考虑在DACL中显示的给予everyone以及ALL APPLICATIONS PACKAGE对应的访问权限控制。

0x06 ACCESS_DENIED_ACE_TYPE
===========================

* * *

在遍历类型为ACCESS_DENIED_ACE_TYPE的ACE时，处理逻辑里并没有区分ACE的SID是否为PackageSID或者CapabilitiesSID。而是简单使用SepSidInTokenSidHash函数在Token的SidHash/RestrictedSidHash里匹配。如果是PackageSID或者CapabilitiesSID，匹配会失败，因此该ACE描述的拒绝访问权限控制不会生效：

![enter image description here](http://drops.javaweb.org/uploads/images/8990dff2c2ad19cf18bef954d55d2bba595e42a6.jpg)图18

做一个实验验证上面的结论，首先我们用AppContainer隔离机制启动一个记事本，复用IE EPM的PackageSID以及部分Capabilities：

![enter image description here](http://drops.javaweb.org/uploads/images/15b307d3fc7bed137e628d120b2bc9612628df54.jpg)图19

把C:\Users{当前用户}\AppData\Local\Packages\windows_ie_ac_001\AC\Temp\test\1.txt设置为下面的权限控制：

![enter image description here](http://drops.javaweb.org/uploads/images/5c0d722431a05cb73b199b7062d2e132189e2f1f.jpg)图20

![enter image description here](http://drops.javaweb.org/uploads/images/94a66571cd0a92363baca68bf8a8adf2a858bc50.jpg)图21

ACE[0]Mask为0x001F01FF，包含要请求的权限0x00100080 虽然ACE[0]明确的拒绝了 S-1-15-2-1430448594-2639229838-973813799-439329657-1197984847-4069167804-1277922394 (图19里标志为AppContainer的SID)，记事本仍然能成功打开1.txt(ACE[1](http://drops.wooyun.org/wp-content/uploads/2015/03/image001.png)明确给予了ALL APPLICATION PACKAGES 0x001F01FF的访问权限)。

0x07 结束语
========

* * *

AppContainer提供了更细粒度的隔离机制，不仅能用于MetroAPP和 IE EPM，当应用程序需要访问未知第三方内容时，也可以考虑使用AppContainer隔离机制，把对系统的潜在影响降到最低。