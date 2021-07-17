# 比葫芦娃还可怕的百度全系APP SDK漏洞 - WormHole虫洞漏洞分析报告

作者：瘦蛟舞，蒸米

”You can’t have a back door in the software because you can’t have a back door that’s only for the good guys.“ - Apple CEO Tim Cook

”你不应该给软件装后门因为你不能保证这个后门只有好人能够使用。” – 苹果CEO 库克

0x00 序
======

* * *

最早接触网络安全的人一定还记得当年RPC冲击波，WebDav等远程攻击漏洞和由此产生的蠕虫病毒。黑客只要编写程序扫描网络中开放了特定端口的机器，随后发送对应的远程攻击代码就可以控制对方主机，在控制对方主机后，程序可以继续扫描其他机器再次进行攻击。因为漏洞出在主机本身，想要修复漏洞必须安装补丁才行，但因为很多人并不会及时升级系统或者安装补丁，所以漏洞或者蠕虫会影响大量的机器非常长的时间，甚至有的蠕虫病毒可以感染全世界上亿的服务器，对企业和用户造成非常严重的损失。

Android发布后，我们就一直幻想着能发现一个像PC上的远程攻击一样厉害的漏洞，但是Android系统默认并没有开放任何端口，开放socket端口的APP也非常稀少，似乎出现像PC那样严重的漏洞是不太可能的。但可惜的是，世界上并没有绝对的安全，就在这么几个稀少的端口中，我们真的找了一个非常严重的socket远程攻击漏洞，并且影响多个用户量过亿的APP，我们把这个漏洞称之为WormHole虫洞漏洞。

0x01 影响和危害
==========

* * *

WormHole虫洞漏洞到底有多严重呢？请看一下我们统计的受影响的APP列表（还没有统计全）：

百度地图 检测版本8.7  
百度手机助手 检测版本6.6.0  
百度浏览器 检测版本6.1.13.0  
手机百度 检测版本6.9  
hao123 检测版本6.1  
百度音乐 检测版本5.6.5.0  
百度贴吧 检测版本6.9.2  
百度云 检测版本7.8  
百度视频 检测版本7.18.1  
安卓市场 检测版本6.0.86  
百度新闻 检测版本5.4.0.0  
爱奇艺 检测版本6.0  
乐视视频 检测版本5.9  
...完整列表见附录

这个列表是2015年10月14号统计的百度系APP的最新版，理论上所有小于等于检测版本的这些百度系的APP都有被远程攻击的危险。根据易观智库的统计排行：

![](http://drops.javaweb.org/uploads/images/62c7fc198221692dcb19faa006a311489a468db6.jpg)

可以看到手机百度、百度手机助手、百度地图等百度系APP有着上亿的下载安装量和加起来超过三亿的活跃用户。

安装了百度的这些APP会有什么后果和危害呢？

1.  无论是 wifi 无线网络或者3G/4G 蜂窝网络，只要是手机在联网状态都有可能受到攻击。攻击者事先无需接触手机，无需使用DNS欺骗。
    
2.  此漏洞只与app有关，不受系统版本影响，在google最新的android 6.0上均测试成功。
    
3.  漏洞可以达到如下攻击效果:
    
    *   远程静默安装应用
    *   远程启动任意应用
    *   远程打开任意网页
    *   远程静默添加联系人
    *   远程获取用用户的GPS地理位置信息/获取imei信息/安装应用信息
    *   远程发送任意intent广播
    *   远程读取写入文件等。

下面是视频DEMO:

俺们做的视频效果太差,下面demo视频是从雷锋网上看到的：

http://www.leiphone.com/news/201510/abTSIxRjPmIibScW.html

0x02 漏洞分析
=========

* * *

安装百度系app后，通过adb shell连接手机，随后使用netstat会发现手机打开了40310/6259端口，并且任何IP都可以进行连接。

![](http://drops.javaweb.org/uploads/images/8d67c8973a853ff11abdf4f5a959e0ae48b2f9e7.jpg)

原来这个端口是由java层的nano http实现的，并且这个http服务，百度给起名叫immortal service（不朽/不死的服务）。为什么叫不朽的呢？因为这个服务会在后台一直运行，并且如果你手机中装了多个有wormhole漏洞的app，这些app会时刻检查40310/6259端口，如果那个监听40310/6259端口的app被卸载了，另一个app会立马启动服务重新监听40310/6259端口。

![](http://drops.javaweb.org/uploads/images/3dc12a0d1a76ba25ac8dd631360a10c8505e0df3.jpg)

我们继续分析，整个immortal service服务其实是一个http服务，但是在接受数据的函数里有一些验证,比如 http 头部remote-addr字段是否是”127.0.0.1”，但是会一点web技巧的人就知道，只要伪造一下头部信息就可把remote-addr字段变成”127.0.0.1”。

![](http://drops.javaweb.org/uploads/images/e75a7ace3bd4a2969b12f97df2fc301e5a1ded10.jpg)

成功的和http server进行通讯后，就可以通过url给APP下达指令了。拿百度地图为例，以下是百度地图APP中存在的远程控制的指令的反汇编代码：

![](http://drops.javaweb.org/uploads/images/af20f8f6f59a60c96221ed113c302fff9302cef2.jpg)

1.  **geolocation 获取用户手机的GPS地理位置（城市，经度，纬度）**
2.  getsearchboxinfo 获取手机百度的版本信息
3.  getapn 获取当前的网络状况（WIFI/3G/4G运营商）
4.  getserviceinfo 获取提供 nano http 的应用信息
5.  getpackageinfo 获取手机应用的版本信息
6.  **sendintent 发送任意intent 可以用来打开网页或者与其他app交互**
7.  **getcuid 获取imei**
8.  getlocstring 获取本地字符串信息
9.  scandownloadfile 扫描下载文件(UCDownloads/QQDownloads/360Download...)
10.  **addcontactinfo 给手机增加联系人**
11.  **getapplist获取全部安装app信息**
12.  **downloadfile 下载任意文件到指定路径如果文件是apk则进行安装**
13.  **uploadfile 上传任意文件到指定路径 如果文件是apk则进行安装**

当我们看到这些远程指令的时候吓了一跳。你说你一个百度地图好好的导航行不行？为什么要去给别人添加联系人呢？添加联系人也就算了，为什么要去别的服务器下载应用并且安装呢？更夸张的是，安装还不是弹出对话框让用户选择是否安装，而是直接申请root权限进行静默安装。下图是代码段：

![](http://drops.javaweb.org/uploads/images/b4cc828c3b3cdbfd88fc3fe3afa89eb1a6031cfb.jpg)

可以看到下载完app后会有三个判断:

1.  手机助手为系统应用直接使用android.permission.INSTALL_PACKAGES权限静默安装应用
2.  手机助手获得 root 权限后使用 su 后执行 pm install 静默安装应用
3.  非以上二种情况则弹出引用安装的确认框

一般用户是非常相信百度系APP，如果百度系APP申请了root权限的话一般都会通过，但殊不知自己已经打开了潘多拉的魔盒。

如果手机没root就没法静默安装应用了吗？不是的，downloadfile和uploadfile可以选择下载文件的位置，并且百度系app会从”/data/data/[app]/”目录下动态加载一些dex或so文件，这时我们只需要利用downloadfile或uploadfile指令覆盖原本的dex或so文件就可以执行我们想要执行的任意代码了。比如说，利用dex或者so获取一个反弹shell，然后把提权的exp传到手机上执行获得root权限，接下来就可以干所有想干的任何事情了。

0x03 POC
========

* * *

因为影响过大，暂不公布，会在WormHole漏洞修复完后更新。

0x04 测试
=======

* * *

简单测试了一下WormHole这个漏洞的影响性，我们知道3G/4G下的手机其实全部处于一个巨大无比的局域网中，只要通过4G手机开个热点，就可以用电脑连接热点然后用扫描器和攻击脚本对全国甚至全世界连接了3G/4G的手机进行攻击。在家远程入侵一亿台手机不再是梦。

我们使用获取包名的脚本，对电信的下一个 C 段进行了扫描，结果如下：

```
Discovered open port 6259/tcp on 10.142.3.25  "com.baidu.searchbox","version":"19"
Discovered open port 6259/tcp on 10.142.3.93  "packagename":"com.baidu.appsearch"
Discovered open port 6259/tcp on 10.142.3.135  "com.hiapk.marketpho","version":"121"
Discovered open port 6259/tcp on 10.142.3.163  "packagename":"com.hiapk.marketpho"
Discovered open port 6259/tcp on 10.142.3.117  "com.baidu.browser.apps","version":"121"
Discovered open port 6259/tcp on 10.142.3.43   "com.qiyi.video","version":"20"
Discovered open port 6259/tcp on 10.142.3.148  "com.baidu.appsearch","version":"121"
Discovered open port 6259/tcp on 10.142.3.196  "com.baidu.input","version":"16"
Discovered open port 6259/tcp on 10.142.3.204  "com.baidu.BaiduMap","version":"20"
Discovered open port 6259/tcp on 10.142.3.145  "com.baidu.appsearch","version":"121"
Discovered open port 6259/tcp on 10.142.3.188  "com.hiapk.marketpho","version":"21"
Discovered open port 40310/tcp on 10.142.3.53  "com.baidu.BaiduMap","version":"122"
Discovered open port 40310/tcp on 10.142.3.162  "com.ting.mp3.android","version":"122" 
Discovered open port 40310/tcp on 10.142.3.139 "com.baidu.searchbox","version":"122"
Discovered open port 40310/tcp on 10.142.3.143 "com.baidu.BaiduMap","version":"122"
Discovered open port 40310/tcp on 10.142.3.176  "packagename":"com.baidu.searchbox"

```

255个IP就有16手机有WormHole漏洞。

除此之外，我们发现华为，三星，联想，金立等公司的某些机型在中国出厂的时候都会预装百度系app，突然间感到整个人都不好了。。。

![](http://drops.javaweb.org/uploads/images/85c95db79e369111cb9088886d3d4be33ba95128.jpg)

0x05 总结
=======

* * *

我们已经在2015年10月14日的时候将WormHole的漏洞报告通过乌云提交给了百度，并且百度已经确认了漏洞并且开始进行修复了。但这次漏洞并不能靠服务器端进行修复，必须采用升级app的方法进行修复，希望用户得到预警后尽快升级自己的应用到最新版，以免被WormHole漏洞攻击。

0x06 受影响的app列表
==============

```
足球直播
足球巨星
足彩网
卓易彩票
助手贴吧
中国足彩网
中国蓝TV
中国蓝HD
珍品网
掌上百度
悦动圈跑步
优米课堂
音悦台
移动91桌面
央视影音
修车易
小红书海外购物神器
侠侣周边游
物色
万达电影
贴吧看片
贴吧饭团
视频直播
生活小工具
上网导航
全民探索
穷游
途牛网 (新版本已经修复)
汽车之家 (新版本已经修复)
拇指医生(医生版)
萌萌聊天
美西时尚
么么哒
蚂蚁短租
旅游攻略
乐视视频
酷音铃声
口袋理财
经理人分享
购车族
歌勇赛
凤凰视频
风云直播Pro
多米音乐
都市激情飙车
懂球帝
蛋蛋理财
穿越古代
彩票到家
彩票365
爆猛料
百姓网
百度桌面Plus
百度云
百度游戏大全
百度音乐2014
百度新闻
百度团购
百度图片
百度贴吧青春版
百度贴吧简版
百度贴吧HD
百度输入法
百度手机助手
百度手机游戏
百度视频HD
百度视频
百度浏览器
百度翻译
百度地图DuWear版
百度地图
百度HD
百度
安卓市场
爱奇艺视频
VidNow
Video Now
T2F话友
Selfie Wonder
PPS影音
PhotoWonder
hao123特价
CCTV手机电视
91桌面
91助手
91爱桌面
91 Launcher
365彩票

```

PS:

1.文章是提前编辑好打算漏洞公开后再发布,趋势已经发文所以跟进.

http://blog.trendmicro.com/trendlabs-security-intelligence/setting-the-record-straight-on-moplus-sdk-and-the-wormhole-vulnerability/

2.网上公布的一些 app 列表大多是根据百度 moplus SDK 的特征指令静态扫描得来这样会有一定误报导致无辜 app 躺枪,比如漫画岛app 虽然集成了此 SDK 但是因为代码混淆策略,指令实现类名被混淆后 findClass 无法找到,所以 exp 都会提示404.

3.关联漏洞

[WooYun: 百度输入法安卓版存在远程获取信息控制用户行为漏洞（可恶意推入内容等4G网络内可找到目标）](http://www.wooyun.org/bugs/wooyun-2015-0145365)

[WooYun: WormHole虫洞漏洞总结报告(附检测结果与测试脚本)](http://www.wooyun.org/bugs/wooyun-2015-0148406)