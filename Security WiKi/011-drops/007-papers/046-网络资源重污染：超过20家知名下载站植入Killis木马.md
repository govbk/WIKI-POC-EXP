# 网络资源重污染：超过20家知名下载站植入Killis木马

Xcode编译器引发的苹果病毒大爆发事件还未平息，又一起严重的网络资源带毒事故出现在PC互联网上。

这是一个名为Killis（杀是）的驱动级木马，该木马覆盖国内二十余家知名下载站，通过各大下载站的下载器或各种热门资源传播，具有云控下发木马、带有数字签名、全功能流氓推广、破坏杀毒软件等特点。根据360安全卫士监测，最近10小时内，Killis木马已经攻击了50多万台电脑。

0x01 Killis木马传播：下载站隐蔽推广
=======================

* * *

下载站遍布暗雷的广告位诱导早已不是什么新鲜事了。但试问：即便是如同枪林弹雨中左躲右闪的士兵一样躲过了所有的“陷阱”，你就安全了么？

答案是否定的，因为Killis木马的源头就隐藏在一些知名下载站的真实下载地址中。

以国内某大型下载站为例，当用户点击一些资源的真实下载地址后，下载回来的首先是一个下载器（[http://down10.zol.com.cn/zoldownload/W.P.S.4885.20.2394@81_114617.exe](http://down10.zol.com.cn/zoldownload/W.P.S.4885.20.2394@81_114617.exe)）：

![](http://drops.javaweb.org/uploads/images/e96850dc690739ce63f98a0e935ee6c536a9b540.jpg)

这个程序运行后，除了为用户下载原本需要的资源以外，它同时会向服务器请求一个推广列表：

![](http://drops.javaweb.org/uploads/images/e9e7522f54a55bc0a9825c3f1f3d9e167b79b8c5.jpg)

Killis木马就在这时进入电脑。再看带有Killis木马推广行为的下载站列表，只要你在国内下载站下载文件，几乎无可避免会遇到Killis木马的侵袭，此木马背后产业链的流量控制能力由此可见一斑：

![](http://drops.javaweb.org/uploads/images/fa67531e386e96a3d294a833bd87ca79799e18d5.jpg)

![](http://drops.javaweb.org/uploads/images/eb9cce0ce8b4a45e595d1be23ea74907e07e12de.jpg)

![](http://drops.javaweb.org/uploads/images/6e41252207e3b8d7fe0cc107cdc7c4a9f62c1a73.jpg)

0x02 KILLIS木马分析：AV终结者+全功能流氓推广器
==============================

* * *

Killis木马伪装成“传奇霸业”的端游客户端，并利用一些公司泄露的过期签名，为自己签发木马。而这个游戏客户端只是个幌子，木马真正的功能是将用户计算机做为一个刷量终端，不断的进行推广。此木马可以云控安装软件，安装插件，放桌面放快捷方式，改桌面快捷方式，改桌面图标，杀指定进程。Killis作为一个全功能的推广器隐藏在受害用户计算机中，并且还有一个杀进程驱动，用来结束多家杀软的进程，防止木马推广被拦截。

木马原始包：629c04c150ef632b098fe65cf3ff3b60

![](http://drops.javaweb.org/uploads/images/7f3111823d0df0082a82ea7e4c93f6327b14acc7.jpg)

木马驱动，带有一个过期的签名：4f504c748025aa34d9c96d0e7f735004

Xuanyi Electronic (Shanghai) Co., Ltd.

![](http://drops.javaweb.org/uploads/images/ad441d526e5b2e5187ef8b69f59eee541af309e0.jpg)

被这个木马利用的签名列表：

```
Open Source Developer, 东莞市迈强电子科技有限公司
Luca Marcone
Baoji zhihengtaiye co.,ltd
Jiangsu innovation safety assessment Co., Ltd.
Wemade Entertainment co.,Ltd
Beijing Chunbai Technology Development Co., Ltd
Fuqing Yuntan Network Tech Co.,Ltd.
Guangzhou Kingteller Technology Co.,Ltd.
Shenzhen Liantian Technology Co., Ltd
Xuanyi Electronic (Shanghai) Co., Ltd.

```

用来做伪装的游戏安装包：

![](http://drops.javaweb.org/uploads/images/554751a1800761a08e7b6972766da8531c5aed24.jpg)

木马功能分析：驱动部分，是一个名为KILLIS的设备，用来负责查杀进程操作：

![](http://drops.javaweb.org/uploads/images/cf74bcd57c3492e86924317d141e3ae089535b4e.jpg)

驱动打开进程与结束进程：

![](http://drops.javaweb.org/uploads/images/e861b80f3ca32567e626ba7e9413c2b5c98de7d4.jpg)

驱动pid查找结束进程：

![](http://drops.javaweb.org/uploads/images/f2a276728ce313d6fbddd1e7ef983285c079e881.jpg)

![](http://drops.javaweb.org/uploads/images/4702823b9623619e2928e59839be9fbe980cfa2e.jpg)

Ring3部分，是一个下载推广器，内置了一批推广列表，通过Base64编码：

![](http://drops.javaweb.org/uploads/images/bf30cd0a30982f41b5cc5e308bf06585646c2f78.jpg)

解码后发现的木马推广列表：

*   [http://cd001.www.duba.net/duba/install/2011/ever/kinst_18_807.exe](http://cd001.www.duba.net/duba/install/2011/ever/kinst_18_807.exe)
*   [http://cd001.www.duba.net/duba/install/2011/ever/kinst_18_807.exe](http://cd001.www.duba.net/duba/install/2011/ever/kinst_18_807.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117109.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117109.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117110.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117110.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117111.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117111.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117112.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117112.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117113.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117113.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117114.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117114.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117257.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117257.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117258.exe](http://dlsw.br.baidu.com/ditui/zujian/Baidu_Setup_1.6.200.359_ftn_1050117258.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050103270.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050103270.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104230.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104230.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104231.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104231.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104232.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104232.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104237.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050104237.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050106262.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050106262.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117109.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117109.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117110.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117110.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117111.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117111.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117112.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117112.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117113.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117113.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117114.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduAn.Setup.0528.4.0.0.8029_1050117114.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_2.14.2.46_sw-0050103270.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_2.14.2.46_sw-0050103270.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_2.14.2.46_sw-0050104237.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_2.14.2.46_sw-0050104237.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_2.14.2.46_sw-0050106262.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_2.14.2.46_sw-0050106262.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050104230.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050104230.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050104231.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050104231.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050104232.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050104232.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117109.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117109.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117110.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117110.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117111.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117111.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117112.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117112.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117113.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117113.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117114.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117114.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117257.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117257.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117258.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduPinyinSetup_3.0.2.675_sw-0050117258.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050103270.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050103270.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104230.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104230.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104231.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104231.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104232.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104232.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104237.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050104237.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050106262.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050106262.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117109.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117109.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117110.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117110.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117112.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117112.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117113.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117113.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117114.exe](http://dlsw.br.baidu.com/ditui/zujian/BaiduSd.Setup.3.0.0.4611.youqian_1050117114.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050104231.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050104231.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117109.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117109.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117110.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117110.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117111.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117111.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117112.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117112.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117113.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117113.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117114.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117114.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117257.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117257.exe)
*   [http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117258.exe](http://dlsw.br.baidu.com/ditui/zujian/bdbrowserSetup-7.5.502.1781-ftn_1050117258.exe)
*   [http://down.7654.com/downloads/special/qqpcmgr/PCMgr_Setup_10_8_16208_227(123003700).exe](http://down.7654.com/downloads/special/qqpcmgr/PCMgr_Setup_10_8_16208_227(123003700).exe)
*   [http://down.tqshopping.com/n3/mmt_90_3.exe](http://down.tqshopping.com/n3/mmt_90_3.exe)
*   [http://download.2345.cn/silence/2345Explorer_239153_silence.exe](http://download.2345.cn/silence/2345Explorer_239153_silence.exe)
*   [http://download.2345.com/union_common/kwmusic_103398_240798_Silence.exe](http://download.2345.com/union_common/kwmusic_103398_240798_Silence.exe)
*   [http://download.suxiazai.com/for_down/2013/install1088203.exe](http://download.suxiazai.com/for_down/2013/install1088203.exe)

木马的云控打点信息，收集客户端的mac地址，系统信息等提交云端，云端下发推广列表给木马推广执行：

![](http://drops.javaweb.org/uploads/images/0b21e203aa78f2e67dd900d17e0601356d5ab60b.jpg)

木马检查杀软进程，包括360、腾讯和金山的软件进程：

![](http://drops.javaweb.org/uploads/images/fe4a4e94d7b2f204e65080b93f6cad6764fabbc7.jpg)

![](http://drops.javaweb.org/uploads/images/4555de384bd70e2d2be4f97fb9f63e61273b0023.jpg)

![](http://drops.javaweb.org/uploads/images/ff43cca5b71423f6638680caa77906749e2f0005.jpg)

木马注册插件：

![](http://drops.javaweb.org/uploads/images/b72846fbb5075e970ebd472915867b250c443beb.jpg)

木马创建服务，并向设备发送消息：

![](http://drops.javaweb.org/uploads/images/cff8972f98abbc65310ec04521db754678d84811.jpg)

0x03 安全建议
=========

* * *

针对国内众多下载站遭Killis木马污染的情况，360安全中心已将此情况进行通报，提醒各网站加强对推广资源的审核和管控，以免对用户造成损失。同时360安全产品也会对下载网站推广木马的行为进行风险提示。

针对广大网友，建议尽量选择安全可靠的渠道进行下载。如果发现电脑自动安装了不请自来的软件，应及时全盘扫描杀毒，以防系统残留木马，对账号和数据安全造成更严重的风险。