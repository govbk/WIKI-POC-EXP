# CTF中比较好玩的stego

0x00 引子
=======

* * *

最近国内各种CTF层出不穷，看出来国家对于信息安全终于决定下重本了。因为本人比较喜欢研究怎么藏东西，所以一开始在CTF队组建的时候，就负责了misc（杂项）中的Stego部分，中文翻译过来是“隐写术”。  
乌云上也有好几篇关于隐写术的文章，其中以AppLeU0大大的那篇[隐写术总结](http://drops.wooyun.org/tips/4862)最为经典，还有Gump大大的[数据隐藏技术](http://drops.wooyun.org/tips/12614)。在这儿，本菜鸟也想和大家分享在CTF中见到的比较好玩的stego题目。写的不好，请大大们多多包涵。

0x01 什么叫隐写术？
============

* * *

隐写术，在我们的生活中既熟悉而又陌生。记得童年回忆《猫和老鼠》有关于“隐写术”的这一集：Jerry有一天在玩耍的时候，不小心往自己的身上涂了一种“神奇墨水”，然后把自己藏了起来，还成功的把Tom戏弄一通并赶走了Tom。这种“神奇“的墨水，叫“隐形墨水”，写到纸上之后需要特殊处理才可以看得到对方想要给我们传达的信息。

![Tom_&_Jerry](http://drops.javaweb.org/uploads/images/a0e1e7f7e45a54564d36d15880d92c472998f788.jpg)

同样的，在信息安全中，隐写术也是举足轻重的一块领域，从我们最早接触到的图种（copy /b 1.jpg+1.torrent 1.jpg），到最近有事没事就上个头条的locky，看个图片就中招的[stegosploit](http://stegosploit.info/)，图片木马Stegoloader，还有就是最近三大高危CVE之一CVE-2016-3714（ImageMagick的，linux下用于处理图像的一个应用），然后也有CHM打造后门，等等。总的来说，就和藏东西似的，能藏就藏，而我们就是要去寻找这种蛛丝马迹。

0x02 常用工具
=========

* * *

在CTF中，老司机们可能更偏向于用UE/Winhex一类的16进制的编辑器去打开待分析文件，然后通过拼写文件头（嗯。常用的文件头有几类？）然后blah blah的解决了，也有一言不合就用脚本来解决的。然而，新手们尤其是像我这样的菜鸟们，就比较喜欢用工具先分析一下有什么样的发现，这时候，为什么不考虑使用binwalk呢？早年在freebuf上也有binwalk的身影。寒假刷XCTF的OJ的时候，binwalk用起来很方便，但是也有不方便的时候。  
我要想藏个字符啥的，这个也是binwalk看不出来的。记得最近的某CTF曾经出过这道题：

![misc200](http://drops.javaweb.org/uploads/images/5314985c988e108ecf7431de0b0b97e7c51940f4.jpg)

你用binwalk也没用，人家提示的是stegdetect，和表情包里的链接还有压缩包都没关系。后来大概是因为这张图的缘故，还有了这篇文章：[深入理解JPEG图像格式Jphide隐写](http://drops.wooyun.org/tips/15661)  
关于图片和流量分析的隐写可以参考开头的安利，这儿主要讨论关于mp4等其他格式的。

mp4的情况可以考虑使用ffmpeg，ffmpeg可以把一帧帧的视频分割为一张张的图片。具体怎么使用可以在linux下man ffmpeg。

![mp4](http://drops.javaweb.org/uploads/images/a8fc0f2e15e0108bea10a65545199e9d23846f45.jpg)

0x03 几道可以分辨恶趣味的题目
=================

* * *

今年被吊打过的CTF里，我们可以发现隐写术不那么单调了，体现了隐写术的特点之“物所能及不能藏”。不光是常见的jpg、tiff、png，

![exif](http://drops.javaweb.org/uploads/images/a85acacba35d9f7a96954bf7ef623f69c0a19c30.jpg)

你真的舍得分开它吗？出题点不在这儿，在乎Exif也。

![exif-1](http://drops.javaweb.org/uploads/images/e407d7e3d1535c53249d5c0c517f50d3ab4004c6.jpg)

还有这道：先看左边（用pngcheck来分析的）

![odrrere](http://drops.javaweb.org/uploads/images/acf5c0de80876548bf8a6990471d0bfd9dab0a4b.jpg)

这货处理处理就变了：

![odrrere_1](http://drops.javaweb.org/uploads/images/9d9c089ef6661f40dc61eb7b846267fc01bcbdeb.jpg)

然后就耐心重排IDAT部分的模块即可。

此外新的题目还涉及到了其它格式的诸如mp4，pdf，pcap（涉及到流量分析），midi，exe，TTL等等，此外，我还真没见过往vmdk里藏东西的题目（如果有的话，也是会考察选手的磁盘分析能力吧）

*   word
    
    ![word](http://drops.javaweb.org/uploads/images/472ed8c8fb8d640327ee0d427b14050d9e404c45.jpg)
    
    感觉是会出现在宏或者说是隐藏字符这些小细节上，果然细节决定成败啊……
    
*   pdf
    
    这儿可以给大家推荐[wbStego4open](http://wbstego.wbailer.com/)这个工具，目前出过的PDF的stego中还不算是很难，一般是以字符串为主。
    
*   pcap
    
    这儿会考察选手们的流量分析能力，当然小白们有个特别偏的方法：foremost+strings，运气好的话参考风云杯2016的misc06。
    
*   wav
    
    估计有很多人会记得这张图吧？还给了一首《渡口》
    
    ![misc3-346e2a33](http://drops.javaweb.org/uploads/images/e2b7a953cc655f08f17d6484ac3ad68dd7283f28.jpg)
    
    说到wav，之前看别人的WP囤了这么几张图：
    
    ![wav_code](https://www.asafety.fr/wp-content/uploads/01-2.png)
    
    ![wav_code1](https://www.asafety.fr/wp-content/uploads/03-2.png)
    
    ![code_ed](https://www.asafety.fr/wp-content/uploads/Braille.jpg)
    
    看来脑洞还是蛮大的
    
*   midi
    
    ![mid](http://drops.javaweb.org/uploads/images/bc6b5205a627dbd9b925f4cab2fa0160a9c08b9c.jpg)
    
*   avi
    
    avi的编码标准不同导致的文件体积太大，比赛中应该不会放那么大的视频文件供CTFer下载吧？但谁又能说的准呢？给大家安利一个MSU VideoStego，是用于分析avi文件的小工具。
    
*   exe
    
    exe里藏东西其实还涉及到病毒行为分析，有可能是藏在壳内，也有可能是其他地方，具体情况可以使用IDA或者OD还有C32Asm来进行跟进分析。
    
*   mp4
    
    ![catvideo](http://drops.javaweb.org/uploads/images/a8fc0f2e15e0108bea10a65545199e9d23846f45.jpg)
    

在刚刚结束的风云杯2016上，比较有意思的一道misc04是关于加密与解密，同时还涉及到stego，先是zip伪加密破解，然后得到一张图片。尔等菜鸟们用binwalk分辨出了文件头分出来四张图片，嗯？然后？其实在赛后处理这张图发现了一个诡异的地方：

![xianjian](http://drops.javaweb.org/uploads/images/f49a213324d050aba0298d449b9442be7bb383e2.jpg)

然后就没然后了……

P.s. 老司机们看透了一切，早早在这儿打好了埋伏，这一次是使用了zip伪加密+stego+base32，杀了个misc的回马枪……

0x04 后记
=======

* * *

这一块可以深挖的东西还有很多，都是特别的有意思，如果隐写术和密码学结合起来，也是一道非常有意思的题目，也有见到和算法结合起来的"png number"（png套路蛮多的）。  
个人感觉如果说是顺着CTF这一块往下挖的话，也挺考验选手自身的基础的。