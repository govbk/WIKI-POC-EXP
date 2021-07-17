# 一种被命名为Chameleon的病毒可以通过WiFi相互之间传播

![enter image description here](http://drops.javaweb.org/uploads/images/cb398c754ba4796fc5de0f73630451f7df097894.jpg)

你知道计算机病毒可以直接在WiFi之间传播吗，在英国利物浦大学的安全研究人员已经证明了这种WiFi病毒，可以像人类感冒一样在计算机网络之间传播。

这种病毒是找到热点的固件漏洞，然后替换成病毒版本的固件，然后通过无线网络感染其他存在固件漏洞的热点。

Chameleon病毒能够在WiFi当中自我繁殖并且不影响热点的正常运行。

此病毒能够识别无密码的WiFi，然后进行尝试入侵，最有可能在咖啡厅或者机场提供开放式WiFi的地方进行传播。

具体工作流程如下：

```
1. 检测附近的所有WiFi信号。
2. 绕过WiFi加密密码。
3. 绕过密码进入管理员界面。
4. 识别系统设置。
5. 替换固件为价值病毒的固件。
6. 导入原来的系统设置。
7. 开始传播，并回到流程1。

```

在贝尔法斯特与伦敦做了此项实验。

这项实验报告发表在此处：[http://jis.eurasipjournals.com/content/pdf/1687-417X-2013-2.pdf](http://jis.eurasipjournals.com/content/pdf/1687-417X-2013-2.pdf)

![enter image description here](http://drops.javaweb.org/uploads/images/1af315071cc3e005d3472e220b8a6961d49d92f7.jpg)