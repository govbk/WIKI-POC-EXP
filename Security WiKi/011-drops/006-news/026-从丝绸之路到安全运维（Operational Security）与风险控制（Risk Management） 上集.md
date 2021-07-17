# 从丝绸之路到安全运维（Operational Security）与风险控制（Risk Management） 上集

0x00 背景
-------

* * *

2013年10月2日，在大家都沉浸在十一长假喜悦中的时候，遥远的美国爆发出了一个震惊Tor社区和比特币社区的消息，运营在Tor上使用hidden service和用比特比交易的Silkroad丝绸之路被FBI查封，并且创始人Ross William Ulbricht，也就化名为Dread Pirate Roberts的网站管理员和主要运营者在美国被抓。在大家都认为这种运营方式无懈可击绝无被查水表可能的时候，勤劳的FBI却早在今年7月就已经获得了丝绸之路服务器的硬盘镜像，并且潜伏在服务器中长达3个月，从而获得了网站管理员的真实身份。

和美国政府作对，面对的将是全世界最强大的社工手段和全世界最全的0day库，一旦被定位，很可能会被物理消灭。这样的人需要的是智慧，胆识和技术，不幸的是，似乎丝绸之路的创始人哪样都差了那么一些。

根据FBI提交给法官的文件，里面详细的描述了他们是如何找到并且如何证明Ross就是DPR这个人的。不过该文件却对如何进入silkroad的服务器一笔带过，这让Tor社区感到非常不安，大家都在怀疑FBI是通过和NSA的合作关系，利用了传说中的国家级大数据和隐藏在Tor中的后门找到了服务器的真实IP，通过IP又通过一纸搜查令让服务器提供商复制了一份服务器硬盘内容。

不过即使FBI没能进入丝绸之路的服务器，要找到创始人看来也没有想象中的那么困难。FBI的文件显示，在丝绸之路创立的初期，创始人犯了很多2B错误。

0x01 过程
-------

* * *

2011年1月27日，用 altoid 用户名在 shoomery.注册并发帖宣传丝绸之路(链接：[http://www.shroomery.org/forums/showflat.php/Number/13860995](http://www.shroomery.org/forums/showflat.php/Number/13860995))

2011年1月29日，用altoid用户名在bitcointalk.org注册并发帖宣传，原帖已被删，但是被人引用了(链接：[https://bitcointalk.org/index.php?topic=175.msg42670#msg42670](https://bitcointalk.org/index.php?topic=175.msg42670#msg42670))

2011年10月11日，在bitcointalk.org 用altoid用户名发帖招程序员,并且帖子里附上了用自己真实姓名注册的gmail地址rossulbricht@gmail.com (连接：[https://bitcointalk.org/index.php?topic=47811.0](https://bitcointalk.org/index.php?topic=47811.0))

![enter image description here](http://drops.javaweb.org/uploads/images/f2d14f9679da07c260a5b6e00bf38d826eac0207.jpg)

2012年3月5日，在stackoverlow以真实姓名和邮箱注册了帐号"Ross Ulbricht” ->rossulbricht@gmail.com

2013年3月13日，被丝绸之路用户FriendlyChemist勒索，他后来通过丝路的私信(非加密，服务器被端之后被FBI看光光)找杀手试图将其做掉，据说杀手和勒索的都是一个人……似乎被摆了一道……

2013年3月16号，在stackoverflow发帖询问如何用PHP的curl连接tor的hidden service(链接[http://stackoverflow.com/questions/15445285/how-can-i-connect-to-a-tor-hidden-service-using-curl-in-php](http://stackoverflow.com/questions/15445285/how-can-i-connect-to-a-tor-hidden-service-using-curl-in-php)) ，发完贴后一分钟，他把用户名改成了frosty

2013年4月某日，他把stackoverflow的注册email改成了frosty@frosty.org

2013年6月某日，他向之前找的杀手买了几个伪造的身份证，用的是他自己驾照上的照片，假名字假地址。收件人是他的真名并且用的真实地址。

2013年7月10号，从加拿大寄到美国的假证件被海关在一次“随机检查”中拦截。

2013年7月23号，丝绸之路的服务器硬盘被FBI镜像。FBI发现服务器的SSHkey里面的用户名是frosty@frosty，根据服务器登录日志显示，最近几次登录来自一家VPN服务商的IP，根据服务商供出的源IP，位置在Ross William Ulbricht住处旁边500米的一个网吧。并且根据Google提[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)户最后几次登录IP也和VPN的IP相同。

2013年7月26号，美国国土安全部工作人员上门查水表，询问假证的事情，他说是被人陷害的，因为 "任何人都能去Tor里那个叫丝绸之路的网站买假证寄给别人来陷害他"

2013年10月2号，Ross在一家社区图书馆，刚刚解锁完笔记本，就被周围20多个便衣FBI按到墙上逮捕。笔记本里他登录的用户名是frosty。

2B行为：

```
1，用真名注册邮箱。用真名注册邮箱可以，一般都用来以真实身份对外公开交流。但是用这个邮箱注册帐号宣传自己的地下邪恶网站就太2B了。  
2，管理一个只能通过tor访问的网站，居然只用了一层VPN。  
3，在丝绸之路服务器中用了自己正在用或者曾经使用过的用户名等信息，比如frosty。  
4, 买假证没关系，假证上用自己的真实照片并且寄到自己家的地址……呵呵……  
5, 第一次被查水表的时候不打自招……  
6, 有价值几千万美元的比特币，居然肉身还待在美国。 

```

如何隐藏呢
-----

* * *

本文但从技术角度讨论下如何不被查水表的方式。

在Tor中用hidden service架设的服务，应该只用Tor管理。SSH登录也应该采用双因素或者三因素认证，比如私钥+密码+动态口令。SSH通过proxychains用Tor的socks5代理登录服务器。

宣传贴和问题应该用随机生成的用户名，通过Tor发帖。

服务器里不要保存任何和自己任何信息有关的内容。

买假证不要用和自己真实证件上一样的照片，不要在收件人上用真名，收件地址是自己家……

赚了差不多的钱之后就应该移民到俄罗斯……  
做到这个程度，假设Tor安全可信的话，即使服务器被拿下，也是无法从服务器里的内容追踪到服务器管理员的。除非从服务器购买信息着手，比如注册用户名和IP，信用卡等等。所以最好找可以用比特币等匿名支付手段购买的服务器，或者用黑卡，购买的时候也要通过Tor。

本章总结
----

* * *

安全最重要的因素是人，凡事都要考虑到人会犯的错误，大意，懒惰等等。可以说，在目前的信息安全体系中，人类才是最大的弱点，机器是冷酷可靠的。