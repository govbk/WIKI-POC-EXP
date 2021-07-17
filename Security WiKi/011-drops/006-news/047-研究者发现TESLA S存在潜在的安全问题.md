# 研究者发现TESLA S存在潜在的安全问题

![enter image description here](http://drops.javaweb.org/uploads/images/c4d9b7e185a5e001d818ed015c64e5efd0a32bf0.jpg)

Charlie Miller 和 Chris Valasek 曾经花了几个月拆开丰田Prius ，看看内部有什么漏洞，结果他们找到了很多。现在，另一位研究员已经发现并确定了一些TESLA S的安全问题，包括一个很脆弱的因素身份认证系统的依赖，可以远程打开车门。

Tesla S是一个高端的，全电动汽车，其中包括了一些有趣的功能，包括控制汽车多个系统的中控台触摸屏。还有一个iPhone应用程序，允许用户控制一些汽车的功能，包括锁门，悬挂和制动系统和控制天窗。 Nitesh Dhanjani发现，当新用户注册一个特斯拉网站上的帐号时，他们必须建立一个六个字符的密码。这个密码将被用来登陆到iPhone应用程序。

Dhanjani发现，特斯拉的网站并没有来限制针对某一个用户的登录错误次数，因此攻击者可能会尝试暴力破解用户的密码。攻击者还可能诱骗用户得到她的密码，如果他访问用户的iPhone ，登录到特斯拉的应用程序和控制车辆的系统。攻击者在没有iPhone应用程序的情况下还可能利用特斯拉API来检查用户的车辆的位置。

Dhanjani说，攻击者最关心的部分并不是暴力破解。他更担心针对特斯拉业主钓鱼活动的攻击者。

“这里的重点是特斯拉需要实现一个不止一个因子的认证。攻击者不能使用一些常见的手法例如钓鱼，就能够在2014年生产的汽车中实现远程解锁定位。”

“在某些情况下，攻击者可以攻破另一个网站，从中获取用户名和密码，尝试在特斯拉的网站和API中是否能够登陆。 ”

Dhanjani还发现，笔记本电脑通过在仪表盘上的端口连接到车辆，在车辆中可以找出三个独立的IP功能的设备，在仪表板显示屏，中控台和一个身份不明的第三个设备。控制台和仪表板有一个数字，包括SSH和HTTP服务。

该调查员已经把收集到的信息通过一个朋友发送给了Tesla的员工，但是还没有获得官方的回应。

技术细节：[http://www.dhanjani.com/blog/2014/03/curosry-evaluation-of-the-tesla-model-s-we-cant-protect-our-cars-like-we-protect-our-workstations.html](http://www.dhanjani.com/blog/2014/03/curosry-evaluation-of-the-tesla-model-s-we-cant-protect-our-cars-like-we-protect-our-workstations.html)