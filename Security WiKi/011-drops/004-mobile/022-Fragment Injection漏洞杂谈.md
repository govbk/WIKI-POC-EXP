# Fragment Injection漏洞杂谈

0x00 背景
=======

* * *

13年的时候，IBM的安全研究人员发现了1个`Google`框架层的漏洞`Fragment`注入漏洞，该漏洞可以导致`Android`手机的PIN码被重置，大家应该对图1不陌生。这个漏洞之后，业界对该漏洞的影响没有进一步的探讨，本文将对该漏洞进行进一步的探讨，欢迎拍砖。

![enter image description here](http://drops.javaweb.org/uploads/images/65bfa8e1caeb0d01d811e77c5321081e631a5812.jpg)

0x01 Fragment注入漏洞详情
===================

* * *

`Android Framework`提供了`android.preference.PreferenceActivity`这个类来对`preference`进行展示，我们可以继承这个类来展示`preference`，并进行扩展。基类中会接收`Intent`数据，并进行一定检查，其中两个比较重要：

`PreferenceActivity.EXTRA_SHOW_FRAGMENT (’:android:show_fragment’) and PreferenceActivity.EXTRA_SHOW_FRAGMENT_ARGUMENTS (’:android:show_fragment_arguments’)`。第一个`extra`域包含`PreferenceActivity`要动态加载的`Fragment`，第二个`extra`域包含传给该`Fragment`的参数。`Fragment`也可以通过`Fragment.getActivity`这个函数来获取传进来的参数。`PreferenceActivity`会调用`Fragment.instantiate`来动态加载`Fragment`.这个函数通过反射来加载`Fragment`，并把它变成`Fragment`对象。如图2所示。

![enter image description here](http://drops.javaweb.org/uploads/images/b26df4f31e940fbd4e385291976898ff194971db.jpg)

任何继承自`PreferenceActivit`y并对外导出的组件，都会受到攻击。恶意app可以传`:android:show_fragment`这个`extra`值来指定要动态加载的类。在`PreferenceActivity`的`context`里，通过`dalvik.system.PathClassLoader`函数来动态加载类，由于没有对请求的app进行校验，恶意app可以动态加载有漏洞app里面的任何类（包括未导出类），使得恶意app可以访问有漏洞app的隐私信息。

0x02 Fragment注入漏洞利用
===================

* * *

### 1.拒绝服务

由于通过该漏洞可以加载app里面的任何类，包括未导出类，如果未导出类对畸形消息处理不当，将会导致本地拒绝服务漏洞。下面以`IRCCloud软件`为例。

`com.irccloud.android.activity.PreferencesActivity`组件对外导出：

![enter image description here](http://drops.javaweb.org/uploads/images/973118366b624cc035334f189daec5d715320897.jpg)

`com.irccloud.android.activity.PreferencesActivity`组件继承自`PreferenceActivity`：

![enter image description here](http://drops.javaweb.org/uploads/images/1ab9b39571375ec68a60e615b75e19d9e266fa34.jpg)

由于没有对`Fragment`注入漏洞进行防御，可通过该漏洞加载app内任意不导出的组件。选择`com.irccloud.android.fragment.ServerReorderFragment`作为攻击目标：

![enter image description here](http://drops.javaweb.org/uploads/images/f40d63a9bd33e8ac52e8d2d87cf78332f253b876.jpg)

`ServerReorderFragment`没有对畸形消息进行处理，导致拒绝服务，见下图。

![enter image description here](http://drops.javaweb.org/uploads/images/6481db3e320d0c2b39c3d8e202d143fab8743df4.jpg)

### 2.远程命令执行

由于现在很多组件都是基于`Webview`来展示页面，并且`Fragment`组件应用越来越广，以后将会有越来越多的`Webview`组件是基于`Fragment`来展示。由于`Fragment`注入漏洞可以加载app内任意未导出组件，如果基于`Fragment`的`Webview`组件存在`addJavascriptInterface`漏洞，将会导致远程命令执行漏洞。在市面上的app里找了下，发现很多`Webview`组件基于`Fragment`，但是继承自`PreferenceActivity`的组件是不导出的，因此下面将自己写个demo来验证下可行性。

`MainActivity`导出，并继承自`PreferenceActivity`。

![enter image description here](http://drops.javaweb.org/uploads/images/01f865207a29ae0eab01961a96b9014748f1502f.jpg)

WebviewFragment导出js接口，并加载url。

![enter image description here](http://drops.javaweb.org/uploads/images/e81a143b44deddbc9a7eaa2b8e8f0c1f6bcbfab0.jpg)

利用`Fragment Injection`漏洞对`WebviewFragment`攻击。

![enter image description here](http://drops.javaweb.org/uploads/images/c5b8c9676e6f035114c9427713cc3d0e0c501ce7.jpg)

通过`Fragment Injection`漏洞，`WebviewFragment`已加载恶意html，存在远程代码执行漏洞攻击，见图。

![enter image description here](http://drops.javaweb.org/uploads/images/eba870693b7a2ac93f74867f257dcb1fa6a5cb56.jpg)

四、总结
====

* * *

由于可以加载app内的任意未导出组件，因此`Fragment`注入漏洞可攻击点还是挺多的。本文对`Fragment`注入漏洞进行抛砖引玉，希望大牛们能对该漏洞进一步开发。~~~~