# Bluetooth Low Energy 嗅探

0x00 前言
=======

* * *

如果你打开这篇文章时期望看到一些新的东西，那么很抱歉这篇文章不是你在找的那篇文章。因为严格的来说这只是一篇整理文。里面没有任何我的发现，也没有我的实际案例。因为我手头上暂时还没有一个有趣的蓝牙低功耗设备。整篇文章的基础都建立在mike ryan这几年公布的演讲内容之上。

0x01 BLE
========

* * *

BLE是什么？BLE全称bluetooth low energy中文又称蓝牙低功耗。最早被人们所知道是在2010年的时候出现在了bluetooth4的spec当中。由于它比传统的蓝牙更能控制功耗和成本，所以在公布之后开始被广泛地应用了起来。

![](http://drops.javaweb.org/uploads/images/8d6e0a8d75e41dee69d57b8c01bdc97ad947b978.jpg)

比如：运动手表，蓝牙智能鼠标，一些超昂贵的智能滑板又或者是一些医疗器材上。bluetooth smart的字样几乎随处可见。由于用户喜欢低功耗，厂家喜欢低成本它便成为了很受欢迎的一样东西。

![](http://drops.javaweb.org/uploads/images/4b5415b759828f9b84788ce46b76ef475e86882e.jpg)

BLE和传统的蓝牙有着许多不同之处。它们使用不同的modulation参数，使用不同的频道（但仍然是2.4GHz），使用不同的频率跳变，使用不同的包格式，即使是数据白化方面也有着诸多不同。当然了，它们也存在一些共同之处。它们还是会使用传统的主控设备-从属设备模式。虽然它的ph层 link layer 层和传统的蓝牙不相同但l2cap层att层还是相同的。

0x02 环境搭建
=========

* * *

因为它是无线通讯，所以这很容易让我们联想到我们可以实施的一些攻击手段。如果可能的话，我们想去嗅探，想去进行包注入，在有必要的时候进行jamming来完成我们余下的攻击。听上去好像没有那么难，也没有那么新鲜。但实际上蓝牙嗅探实现起来却并没有想象的那么简单。对于wifi我们可以购买一张支持监听模式的网卡。但对于蓝牙根本就存在这么欢快的模式。这意味着我们需要一个这样的设备。两个选择，造一个或买一个。幸运的是已经有人做出来了，虽然在功能上还有许多问题（多在于控制成本，我觉得mike应该不会遇到技术上的困难。。），但对于ble嗅探来说还是可以胜任的。so 它就是ubertooth one。

![](http://drops.javaweb.org/uploads/images/0393d2b337d8454ec7fa9be97ef9d19eeb9091fd.jpg)

对于ubertooth one的环境搭建，我认为已经有了一个很友好的文章。所以，如果你在看完这篇文章后想买一个或者买了一个不知道怎么去配置你可以参考的下面这个链接中的文章。

[www.security-sleuth.com/sleuth-blog/2015/9/6/now-i-wanna-sniff-some-bluetooth-sniffing-and-cracking-bluetooth-with-the-ubertoothone](http://www.security-sleuth.com/sleuth-blog/2015/9/6/now-i-wanna-sniff-some-bluetooth-sniffing-and-cracking-bluetooth-with-the-ubertoothone)

如果上面的链接被一股神秘的力量拦截了，你可以直接参照下面的内容。

首先，你需要拥有一个ubertooth one。从某宝入手又或者是从乌云集市购入。为了方便测试还需准备一个buletooth dongle。你的操作系统可以是win，linux或者是mac。本文将以kali linux为例进行安装步骤的讲述。

先安装这些

```
sudo apt-get install cmake libusb-1.0-0-dev make gcc g++ libbluetooth-dev \
pkg-config libpcap-dev python-numpy python-pyside python-qt4

```

完成之安装libbtbb

```
wget https://github.com/greatscottgadgets/libbtbb/archive/2015-09-R2.tar.gz -O libbtbb-2015-09-R2.tar.gz
tar xf libbtbb-2015-09-R2.tar.gz
cd libbtbb-2015-09-R2
mkdir build
cd build
cmake ..
make
sudo make install

```

安装ubertooth工具（kali自带的最好remove掉，因为版本太旧）

```
wget https://github.com/greatscottgadgets/ubertooth/releases/download/2015-09-R2/ubertooth-2015-09-R2.tar.xz -O ubertooth-2015-09-R2.tar.xz
tar xf ubertooth-2015-09-R2.tar.xz
cd ubertooth-2015-09-R2/host
mkdir build
cd build
cmake ..
make
sudo make install
sudo ldconfig

```

安装kismet（安装前同样remove掉系统自带的）

```
sudo apt-get install libpcap0.8-dev libcap-dev pkg-config build-essential libnl-dev libncurses-dev libpcre3-dev libpcap-dev libcap-dev
wget https://kismetwireless.net/code/kismet-2013-03-R1b.tar.xz
tar xf kismet-2013-03-R1b.tar.xz
cd kismet-2013-03-R1b
ln -s ../ubertooth-2015-09-R2/host/kismet/plugin-ubertooth .
./configure
make && make plugins
sudo make suidinstall
sudo make plugins-install

```

将"pcapbtbb"加入到kismet.conf的logtypes= 当中。

安装wireshark

```
sudo apt-get install wireshark wireshark-dev libwireshark-dev cmake
cd libbtbb-2015-09-R2/wireshark/plugins/btbb
mkdir build
cd build
cmake -DCMAKE_INSTALL_LIBDIR=/usr/lib/x86_64-linux-gnu/wireshark/libwireshark3/plugins ..
make
sudo make install

```

安装BR/EDR插件

```
sudo apt-get install wireshark wireshark-dev libwireshark-dev cmake
cd libbtbb-2015-09-R2/wireshark/plugins/btbredr
mkdir build
cd build
cmake -DCMAKE_INSTALL_LIBDIR=/usr/lib/x86_64-linux-gnu/wireshark/libwireshark3/plugins ..
make
sudo make install

```

最后千万不要忘记更新你的firmware

跳到刚才解压过的 ubertooth-2015-09-R2目录。

```
Cd ubertooth-one-firmware-bin
$ ubertooth-dfu -d bluetooth_rxtx.dfu -r
Checking firmware signature
No DFU devices found - attempting to find Ubertooth devices    

1) Found 'Ubertooth One' with address 0x1d50 0x6002    

Select a device to flash (default:1, exit:0):

```

按下回车。完成firmware的更新。如果失败了或出现了莫名其妙的usb错误。不要慌张。试试

```
ubertooth-util -v

```

如果出现

```
Firmware revision: 2014-02-R1
$ ubertooth-util -V
ubertooth 2014-02-R1 (dominicgs@mercury) Wed Jan 29 23:10:46 GMT 2014

```

就意味着应该没有什么太大的问题。折腾到这里你的环境搭建问题就差不多都解决了。

0x03 嗅探的基础理论概念
==============

* * *

让我们继续回到技术之上。我们想要的应该不是坐享其成。所以让我们试着了解一下ble，先看看ble栈长什么模样（如图1 所示）。

![](http://drops.javaweb.org/uploads/images/899024834b96485d89fe4cc6d5dd7fdb651565ed.jpg)

图1 BLE栈

ble栈应该和你看过的ip包很像。最上面绿色的部分是应用层，主要是gatt和att我们可以把它看作是同一层。sm是安全管理层，负责管理安全。最下面link layer层和phy层基本上就是一些rf的处理。因为这次的内容主要是集中在sm，link layer和phy层上，所以对于应用层不会有相关的叙述和解释。让我们试着从下往上看起。

phy layer使用gfsk进行modulation如果你是rf hacking的爱好者，你应该对这个东西不陌生。和传统的蓝牙不同在ble的世界里只有40个频道，也就是传统蓝牙的一半。其中有37个频道用于数据传输，不被用到的频道都会被gap所替代。然后就是hopping 也就是所谓的频率跳变。和wifi或zigbee等不同。蓝牙喜欢打一枪换一个地方。每一个频道上都只会发生一次数据传输。一个request和一个response。在完成之后根据hope increment会跳到下一个频道。

幸运的是ubertooth one内置的 cc2400可以帮助我们完成这些操作。我们不用去编写什么程序，我们不用去造一个轮子，我们只需要去配置一下相关的设定。设置完毕后我们就可以借助ubertooth one来获取我们想要的bits。

让我们继续往上看，来看看 link layer。通过查阅ble的spec我们可以获知link layer的包格式看上去是这样：

![](http://drops.javaweb.org/uploads/images/7d3f029d7f402a94014f7c949e3583364fa85921.jpg)

看上去link layer的格式并不复杂。它包含前导码，访问地址，PDU和CRC校验码。不过似乎有点问题。因为我们前面所提到的都是bits我们需要的是bits，而这里说的都是octets。如何获取我们想要的bits？首先通过ubertooth one我们可以截获海量的数据。所以我们有很多数据。但是我们需要区分开什么是什么。怎么做到呢？我们需要的就是等待我们的已知量access address的出现。根据spec加上小学数学功底，推出前后的数据都是什么。这样一来我们就拥有了整个link later的bits数据。 拥有了这两层之后我们就可以将RF转换成数据包了。

So ubertooth负责这两层我们都搞定了，其它层都可以交给pc去处理，所以问题解决了么？

还没有。因为btle喜欢打一枪换一个地方。所以我们还需要考虑如何去跟踪connection（配对的时候会在37，38，39个三个频道随机跳，起点位置未知。由于ubertooth one 一次只能监听一个频道，所以实战时可能需要多测试几次才能抓到我们需要的6个包来破解tk）。跟踪connection需要知道4样东西。

*   Access address
*   crcinit
*   time slot length
*   hop increment

但如何才能获取这些数据呢？对于aa我们可以坐等数据的流过，重点检查空数据包,因为我们知道空数据包的结构是什么样的，所以我们只需要在截获的数据包中往会跳32bit来获取我们的access address。使用lfsr来还原crcinit.坐等在某个频道等待两个连续包的出现来计算time slot length = Δt / 37，最后再通过我们的高中数学功底来计算出hop increment.（原作者怕观众无聊就一笔带过了太过于数学话的部分）。

anyway，经过这一系列的折腾我们现在具备了跟踪connection的条件。这也就意味着我们可以嗅探ble了。

0x04 BLE通讯的加密
=============

* * *

but wait，难道ble就没有加密么？答案是有，它使用了著名的aes-ccm（不过还是有很多设备的通讯是不加密的 。我不是蓝牙开发者，但这应该和采用的security model有关吧。看了下spec里头说model0和model1没有加密）也许这让你想起了wpa-aes因为它们是一样的加密方式。所以写了这么多，这是在逗我么？答案是，no。因为俏皮的ble使用了自定义的密钥交换协议。它的自定义密钥交换协议又怎么了？让我们先看看它是怎么匹配的，又或者是它有几种匹配模式。

*   Just works
*   6 digit pin
*   OOB

其中的just works 用起来也就是just works。怎么说？因为它永远用0作为tk来进行配对。6 digit pin。名字和内容差不多，使用0-999999之间的数字来当tk来使用。对于爆破来说，实在是太脆弱。实际测试当中爆破6 digit pin都用不到1s。OOB全称out off band，会使用很麻烦的方式进行匹配，暂时没有什么设备在用这种模式。拥有了tk能做什么呢？让我们看看一个例子。

小明新买了个酷炫狂拽的ble设备。开始和自己的其它设备进行配对。黑客配备好自己的ubertooth观察整个配对过程。如果配对使用了just works 或 6 digit pin 黑客通过暴力破解秒获tk。根据tk和配对数据包还原出stk，根据stk和密钥交换获得ltk。

但是需要注意的是为了拥有tk，你起码要在配对进行时抓到下面的6个包：

*   pairing request
*   pairing response
*   pairing confirm
*   pairing confirm
*   pairing random
*   pairing random

由于配对会在37，38，39三个频道进行，外加ubertooth one一次只能监听一个频道，所以最幸运的情况是配对从ubertooth-btle 默认频道37开始进行，随后的部分由ubertooth帮你完成余下的connection跟踪，来完成整个6个包的抓包。如果抓不到你就需要多试几次。。（便宜货嘛，将就点啦 ）

凑够了6个包后将你抓到的包交给神器crackle ，crackle将会为你破解tk和我们的日思夜想的ltk。拥有了ltk我们就可以解密我们嗅探的所有的包！那有了ltk我们是不是就可以直接取代原来的从属设备了呢？还做不到。因为connection还包含一个随机量。。这就没得玩了？也不是，我们需要做的就是jam掉已经有的connection拿着我们的ltk和主控设备去做一些羞羞的事情。

0x05 测试
=======

* * *

测试设备是否可以在当前环境下正常运作，可以先试试wifi

`root@kali:~/Desktop# ubertooth-specan-ui`

![](http://drops.javaweb.org/uploads/images/51464f4582ef16f42c61fccf113af170a9bcd68d.jpg)

手头上没有bluetooth smart设备？那咱就模拟一个。分别在ios设备1和ios设备2上从appstore下载并安装lightblue。设备A模拟主控设备，设备B模拟从属设备

![](http://drops.javaweb.org/uploads/images/3af826bd183f21cae6d93977ab433b127de6c0dc.jpg)

在这里我们装扮成了一个心率计算设备。试图进行匹配。在这个时候攻击者需要提前准备。你可以选择使用pipe来实现实施监听。

`root@kali:~# mkfifo /tmp/pipe`

打开wireshark

`Capture -> Options -> Manage Interfaces -> New`

输入 /tmp/pipe

点击start开始监听。

然后千万别忘了把ubertooth抓到的内容输出到pipe

`root@kali:~# ubertooth-btle -f -c /tmp/pipe`

最最后，不要忘了这一步。不然你抓到的包根本看不成

`Edit → Preferences → Protocols → DLT_USER → Edit → New`

在payload protocol中输入btle

`ok → ok`

如果你想把抓好的包带回家慢慢整，你可以简单的包抓取的内容输出到某个目录下

`ubertooth-util -r ; ubertooth-btle -f -c /output.pcap`

抓到包之后我们最关心的问题是我们有没有抓到的足够的包来破解tk。所以在wireshark中你可以在filter处加上btsmp，确保抓到了我们需要的6个包。

![](http://drops.javaweb.org/uploads/images/3e2485d378946539256518ed74b751c3c523505e.jpg)

确定抓到了包之后我们去下载神器crackle。

```
Git clone https://github.com/mikeryan/crackle.git
cd crackle
make
make install

```

安装完成后，开始借助cracle和我们抓到的包依次破解tk和ltk

![](http://drops.javaweb.org/uploads/images/d9be7aaba5bb4d77989941f2e4aefa88502911bd.jpg)

从上图中我们可以看到我们不但破解了tk，还利用利用tk和其它一些数据成功的还原出了ltk。

接下来我们再来试试利用获取的ltk来破解其他的加密包。假设我们在配对过程中已经拿到了`ltk=7f62c053f104a5bbe68b1d896a2ed49c`

`crackle -l 7f62c053f104a5bbe68b1d896a2ed49c -i test44.pcap -o test66.pcap`

![](http://drops.javaweb.org/uploads/images/89d082f790bed8ebfd1c8cd89cec8e06ef3d0e56.jpg)

可以看到我们成功地破解了7个包。

0x06 解决方案
=========

* * *

使用OOB

```
root@kali:~/Desktop# crackle -i heart.pcap 
Warning: No output file specified. Won't decrypt any packets.
Warning: found multiple connects, only using the latest one
Warning: found multiple LL_ENC_REQ, only using latest one
Warning: found multiple connects, only using the latest one
Warning: found multiple pairing requests, only using the latest one
Warning: found multiple connects, only using the latest one
Warning: found multiple pairing requests, only using the latest one
Warning: already saw two random values, skipping
Warning: found multiple LL_ENC_REQ, only using latest one
TK not found, the connection is probably using OOB pairing
Sorry d00d :(

```

or

等待支持bluetooth4.2的设备的出现（通过ECDH解决）

0x07 总结
=======

* * *

其实第一次发现通过这个设备加上一些软件可以破解btle嗅探到的包时，我是很兴奋的。因为我之前一直都没有见过这样的文章。不过后来和小伙伴们聊了一下，才意识到这一切的前提条件是你得在第一次匹配的时候抓到所有的关键包（如果你只有1个ubertooth意味着你只有1/3的机会）。不过遗憾的是很多设备在完成第一次的匹配之后就会记忆彼此。下次通讯时不会再重新进行匹配。所以为了让这种攻击更现实一些，也许研究如何unpairing会是一个方向。最后感谢索马里的海贼赞助的Ubertooth One。

参考：

*   `https://lacklustre.net/`
*   `www.security-sleuth.com/sleuth-blog/2015/9/6/now-i-wanna-sniff-some-bluetooth-sniffing-and-cracking-bluetooth-with-the-ubertoothone`
*   `https://www.bluetooth.org/en-us/specification/adopted-specifications`