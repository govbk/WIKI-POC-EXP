# FireEye实验室在一次水坑式攻击中发现IE 0DAY

![enter image description here](http://drops.javaweb.org/uploads/images/b2fe78a60fc02fc40829ca1cfc529c411ba832e1.jpg)

FireEye实验室确认，在美国的一个违法网站上发现了一个新的IE 10的0day，这是一个经典的偷渡式攻击。这个0day攻击成功后，会从远程服务器下载一个XOR编码的payload，然后解码并执行。

发表这个声明是为了警示广大网民，FireEye正在与微软安全团队合作进行防御。

关于这次攻击的详细报告，已经发表在FireEye的博客上：

[operation snowman deputydog actor compromises us veterans of foreign wars website](http://www.fireeye.com/blog/technical/cyber-exploits/2014/02/operation-snowman-deputydog-actor-compromises-us-veterans-of-foreign-wars-website.html)

译者注：水坑攻击是APT攻击的一种常用手段，是指黑客通过分析被攻击者的网络活动规律，寻找被攻击者经常访问的网站的弱点，先攻下该网站并植入攻击代码，等待被攻击者来访时实施攻击。这种攻击行为类似《动物世界》纪录片中的一种情节：捕食者埋伏在水里或者水坑周围，等其他动物前来喝水时发起攻击猎取食物。

原文：[new i.e. zero day found in watering hole attack](http://www.fireeye.com/blog/technical/cyber-exploits/2014/02/new-ie-zero-day-found-in-watering-hole-attack-2.html)