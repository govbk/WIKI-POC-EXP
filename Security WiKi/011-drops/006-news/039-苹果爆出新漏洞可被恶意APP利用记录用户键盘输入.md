# 苹果爆出新漏洞可被恶意APP利用记录用户键盘输入

![enter image description here](http://drops.javaweb.org/uploads/images/7350f5ff2315a2fc2d985611bccbcb26352c4023.jpg)

有安全研究人员发现了苹果的另一个漏洞，可以被用来记录你在iOS设备上的每一个动作。

FireEye声称，此漏洞利用的是iOS在多任务处理时的缺陷。

FireEye发现了一种可以绕过苹果的应用审查过程，并在非越狱的iOS7上成功利用。

恶意app可以在后台运行，允许黑客监视用户的所有活动，包括触摸屏，home按键，音量按钮，并将收集的数据发送到远程服务器上。

![enter image description here](http://drops.javaweb.org/uploads/images/a4921c447fb34dd1555cff6782c731d7d9217a5e.jpg)

根据研究，该漏洞存在于7.0.4，7.0.5，7.0.6和6.1.X的版本中。

在iOS设备上，允许在后台的应用自我刷新，在iOS 7上，可以自己设置是否允许自我刷新，但是这个选项并不能阻止恶意app利用该漏洞进行键盘记录。

![enter image description here](http://drops.javaweb.org/uploads/images/ea3b3ab2796b7d29dbb33020f7c4ff04b2ea5526.jpg)

例如一个播放音乐的APP可以，可以在关闭后台自我刷新的情况下后台播放音乐，那么恶意APP就可以伪装成音乐APP进行监控，目前唯一的办法就是删除该恶意APP。