# UnityGhost的检测和回溯

0x01 问题描述和速查方法
==============

* * *

此次XcodeGhost病毒并不仅仅只篡改Xcode的dmg安装文件，百度安全实验室发现Unity3D也同样被插入了恶意代码。Unity是由Unity Technologies开发的用于创建诸如三维视频游戏、实时三维动画等类型互动内容的多平台的综合型游戏开发工具，Unity可发布游戏至Windows、OS X、Wii、iPhone、Windows phone 8和Android平台。但目前安全实验室搜集到的样本只有感染iOS app，还未发现感染安卓或是Windows平台代码

目前我们观察到Unity OS X平台和Windows平台的安装包版本4.x至5.1.x（范围可能更大）, 64/32位版本均有被修改的现象，被修改后文件均没有数字签名，在文件安装前可以很容易的区分开，对于OS X下dmg文件中包含的pkg文件，可以使用 pkgutil –check-signature Unity.pkg来进行检查。这里附上Windows和OS X下正确版本数字签名校验的截图：

![](http://drops.javaweb.org/uploads/images/ca4fe4084a807d79e04f5fb90665b3695180cfe8.jpg)

![](http://drops.javaweb.org/uploads/images/72ec5b39edcf31644042b7386250dfe75bc41575.jpg)

病毒作者修改了`libiPhone-lib-il2cpp.a`文件, 在其中增加了`libiPhone-lib-il2cpp.a-arch-masterx.x.o`，其中arch为具体的架构名，并修改了project.pbxproj的配置信息。`libiPhone-lib-il2cpp.a`在 mac平台下位于`./Unity/Unity.app/Contents/PlaybackEngines/iossupport/Trampoline/Libraries/ libiPhone-lib-il2cpp.a`，windows平台上的路径为：`Unity/Editor/Data/PlaybackEngines/iossupport/Trampoline/Libraries/libiPhone-lib-il2cpp.a`。

快速自查方法：由于.a是复合的archive文件，解压比较麻烦，可以直接检查`./iossupport/Trampoline/Unity-iPhone.xcodeproj/project.pbxproj`中，是否含有”-ObjC”字符串，如果有则属于被感染版本。下图左侧为受感染文件，右侧为正常文件。

![](http://drops.javaweb.org/uploads/images/a762890a5729e48777936c0a65d86b20222cfd91.jpg)

0x02 代码逻辑
=========

* * *

整体来说，Unity上受感染的恶意代码行为和XcodeGhost行为基本一致，更详细的信息可参看之前[关于XcodeGhost分析](http://drops.wooyun.org/papers/9024)。通过这些分析，可以见到，恶意代码作者有着很强的躲避检测的动机。下图是OS X平台上的一个受感染文件`libiPhone-lib-il2cpp.a-armv7-master.o`。

![](http://drops.javaweb.org/uploads/images/b8a3d91cb046138986fca4ceba3c229099fe442f.jpg)

0x03制作时间
========

* * *

通过对于恶意DMG和官方DMG中的文件信息，我们能够非常清楚的看到恶意代码作者进行打包修改文件的时间，以`unity-4.6.6.dmg`为例：

![](http://drops.javaweb.org/uploads/images/3780b71b106f14a1b5098f4626f5d733c26800cf.jpg)

可以看出，UnityGhost作者在今年6月29日下午进行的修改操作。

下面是我们搜集到的官方发布版本和样本篡改时间的时间轴：

![](http://drops.javaweb.org/uploads/images/9b0288bb244a4afe59e04bfbaa45db418a1cd9f5.jpg)