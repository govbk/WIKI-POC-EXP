# 关于TRACERT和TTL

最近看了一些文章，比如利用TTL 判断G*F*W，或者一些奇怪设备的位置，特做一个实验，看一下TTL 及TRACERT 。 TRACERT 大概的原理，就是通过发送不断+1 的TTL（TIME TO LIVE）的ICMP REQUEST到达最终设备，最后由最终设备返回ICMP REPLY（中间经过的设备返回的都是ICMP超时---|||||ICMP TIME EX）实现。 先发一个TRACERT 图

![20130128144105_81105.jpg](http://drops.javaweb.org/uploads/images/5dcef595dde94c9d7eabdab508cf5df91526e605.jpg)

首先看第一个包

![20130128143941_96799.jpg](http://drops.javaweb.org/uploads/images/dddecc1b2dd9145e8e930c8abc6bdbc24fd572b1.jpg)

TTL 为1，然后网关102.1 返回了一个超时如下图：

![20130128144209_43363.jpg](http://drops.javaweb.org/uploads/images/5ab539452554fd1698c8cbd0012c4ded3feb8dea.jpg)

TTL+1

![20130128144237_83074.jpg](http://drops.javaweb.org/uploads/images/46c86f6756447760c622973a61950ba949ab4bd8.jpg)

下一个设备返回TTL 超时，这样就能确定了两个设备，如图：

![20130128144326_66137.jpg](http://drops.javaweb.org/uploads/images/812ddd743209c61517e86a21d3ad6748069fe1a3.jpg)

TTL再+1

![20130128144403_98915.jpg](http://drops.javaweb.org/uploads/images/47c355ef4a0cd4b3858fb88fc1a81bee8a87aab4.jpg)

再超时

![20130128144421_98502.jpg](http://drops.javaweb.org/uploads/images/c1f7e6d7cc5e2af7664fcd6ba70916989bf29953.jpg)

最后一个设备（google服务器）TTL 已经是17

![20130128144448_97557.jpg](http://drops.javaweb.org/uploads/images/ef4b69248f4231248ab4a2b254b5ea668075343c.jpg)

谷歌服务器返回ICMP REPLY

![20130128144542_62494.jpg](http://drops.javaweb.org/uploads/images/c6d0f73470e8d9c6fdacf9e6016c9cd45643cccb.jpg)

证明我和GOOGLE 服务器距离17跳。PING GOOGLE  （IP地址变了，但TTL 还是43）

![20130128145247_32010.jpg](http://drops.javaweb.org/uploads/images/fcfc91c06878de4560b91e3b328347bdc3d1a92d.jpg)

基本上确定43+17=61  （google服务器的TTL 好像是61：从另一个国外linux PING 和tracert

![20130128145815_99902.jpg](http://drops.javaweb.org/uploads/images/3cbf5590db0dcd67f9c47f52d8e766710772eb72.jpg)

54+7=61