# 戳戳HackShield Ring0反調試

_Author: 蔡耀德_

0x00 前言
=======

* * *

之前玩遊戲，玩累了想說用Cheat Engine來搞搞遊戲，果然被檢測了，上網找了一下他anti debugger的方式是從Ring0來的，但是大多數都只剩下解法沒有實作，只好自己做做看了

0x01 前置準備
=========

* * *

1.  可以跑TMD殼的VM
    
    [http://forum.gamer.com.tw/Co.php?bsn=07650&sn=4416070](http://forum.gamer.com.tw/Co.php?bsn=07650&sn=4416070)
    
2.  雙機調試
    
    HS本身有對內核調試器檢測所以這邊直接用HideKd解決
    
    [http://blog.dbgtech.net/blog/?p=93](http://blog.dbgtech.net/blog/?p=93)
    

1.  開發平台
    
    直接用WDK解決,內含會用到的windbg
    
    [https://msdn.microsoft.com/zh-tw/windows/hardware/gg454513.aspx](https://msdn.microsoft.com/zh-tw/windows/hardware/gg454513.aspx)
    

0x02 測試遊戲保護
===========

* * *

HS啟動後的效果:

![](http://drops.javaweb.org/uploads/images/2b0b832855c7dd8eca1f7348023fbbeee930a82c.jpg)

開著SOD的OD找不到遊戲

再來是寫外掛常用的CE

開内核模式會直接被偵測到

如果不開 直接鎖定的話的話會跳錯誤

![](http://drops.javaweb.org/uploads/images/03be038c6470ce374504140798f1d6480a83a8da.jpg)

![](http://drops.javaweb.org/uploads/images/c5371267dfae0180c9ceff3cd16d772155ae06ee.jpg)

到以上基本上可以確定常用的工具都不能用了

只好來處理HS了!

0x03 分析遊戲保護
===========

* * *

![](http://drops.javaweb.org/uploads/images/0feb9635972e17dc4d7972e57ceb642ef70439ea.jpg)

遊戲丟進OD，入口點看是TMD殼，放棄

直接啟動遊戲後等HackShield加載

拿PcHunter看看

SSDT表

![](http://drops.javaweb.org/uploads/images/9827d258515312cf997807631f300e95dfb3ea0c.jpg)

ShadowSSDT表

![](http://drops.javaweb.org/uploads/images/72983b63265c865941bfd785cef65277f59b5361.jpg)

![](http://drops.javaweb.org/uploads/images/263c5c19a3e10c62d1f09478574eb61784e6116f.jpg)

上面三張圖可以看到，HackShield在Ring0的地方加載了他的驅動hook了很多debugger會用到的函數，以及一些未導出的函數

先補提一下windows大概的函數調用過程

![](http://drops.javaweb.org/uploads/images/45955b2642ee51ce5a596fd45e012e87536d8901.jpg)

在SSDT表裡面的函數最後都會透過SSDT表轉發到該函數地址執行

所以HackShield就在該函數的R0部分裝上了鉤子

執行過程就變成這樣

![](http://drops.javaweb.org/uploads/images/a8c808af60568c2fd9a8d609492acfc60bd9a389.jpg)

在調用該函數的時候順便調用了反外掛的檢測

//這邊就當大家都已經會雙機調試而且已經處理好了

HS加載以前的

![](http://drops.javaweb.org/uploads/images/77ae787d323d654ccc1608694b73d587a4ea4c47.jpg)

讓HS啟動以後…..

![](http://drops.javaweb.org/uploads/images/d2fd15c919264f45890108a155ad5ebaa3089dcd.jpg)

跟進去剛剛的地址看看

![](http://drops.javaweb.org/uploads/images/4fa6147c6c1171748f96a14b46b3ceb4afe41c8f.jpg)

可以看到他先被jmp到HS的處理函數裡面了

其他函數也都大同小異

到這邊分析完成

0x04 處理遊戲保護
===========

* * *

//這邊就當大家都已經會寫跟編譯driver了

PCHunter工具有直接恢復的功能,但直接恢復過不久他就會把鉤子寫回去!

所以這裡用其他的處理方式

以下用nt!ntWriteVirtualMemory示範

![](http://drops.javaweb.org/uploads/images/34ba0cf4f940e8748ee8054b7c49c3197af6a6f4.jpg)

由於不能直接恢復鉤子,而且HS本身會定期調用自身檢測鉤子在不在

所以在他前幾個byte寫入自己的鉤子

![](http://drops.javaweb.org/uploads/images/3f51c8637577b7b48922566cdec1376825359fb5.jpg)

至於怎麼判斷….(win7_32位元作業系統)

![](http://drops.javaweb.org/uploads/images/b16cbbb69e1d7798bc51196c20e02ab93db0cf57.jpg)

把所有函數處理掉以後就差不多了!

0x05 成果
=======

* * *

可以使用OD跟CE了! Enjoy it!

![](http://drops.javaweb.org/uploads/images/4ea86afa7d31f4722b1fd080b052f07ca8b3bd11.jpg)

![](http://drops.javaweb.org/uploads/images/26c2b6b90790450614070bc25b62dece17965d05.jpg)

0x06 番外篇
========

* * *

後來發現他檢測鉤子是否被修改的方法其實只是定期調用自己個函數,如果有定期調用的話他並不會去把它的鉤子寫回去

所以只要定期去執行HS hook的內容,就可以直接bypass掉hs對鉤子是否被改寫的檢測了!這應該算是HS小小的一個0day吧!