# 給初學者的DLL Side Loading的UAC繞過

0x00 UAC是什麼？
============

* * *

在Windows從Vista版本之後加⼊了多個安全性防護如隨機化模組地址(ALSR)、資料防⽌執行(DEP)、使⽤者帳⼾控制(UAC) … 等，ALSR與DEP為exploit上的shellcode插⼊利⽤帶來的相當程度的困難度(當然站在現在技術⽽言繞過並⾮難事)不過今天要談的並非這兩者防護，⽽是要談使用者帳⼾控制(UAC)。（後續再次提及使用者帳⼾控制此防護都以縮寫UAC代稱）

為什麼微軟要⼤費周章再設計⼀個UAC防護？在WinNT時代來臨的第⼀個版本也是由史以來活最久的系統— Windows XP，在⼀開始設計上只要當下程式運⾏的權限是在使⽤者為管理員的時候，那麼想為所欲為都是可被接受的，例如常見攻擊行為註冊表寫⼊、刪除檔案、增加帳號、下載檔案、安裝驅動 … 等。經歷了各式⽊馬後⾨手法的洗禮後，微軟深知⽊馬與後門攻擊對象不再聰明的使⽤用者上，多半聰明的電腦使⽤者不會輕易開啟來路不明的程式，⽽通常受到攻擊的人都為一般電腦使用者，多半對使用者權限沒有什麼觀念，故導致Windows XP時代很容易中個木馬就整台電腦被駭客Own走了！

於是在下⼀個版本Windows — Vista，微軟增加了⼀個策略性的UAC防護，這種防護根據維基百科上可以查詢得到管轄的範疇如下：

UAC需要授權的動作包括：

*   配置Windows Update
*   增加或刪除⽤戶帳戶
*   改變⽤戶的帳戶類型
*   改變UAC設定
*   安裝ActiveX
*   安裝或移除程式
*   安裝置驅動程式
*   設定家⾧監護
*   將檔案移動或複製到Program Files或Windows目錄
*   檢視其他⽤戶資料夾

基本上，只要有涉及到存取系統磁碟的根目錄（例如C:\），存取Windows目錄，Windows系統目錄，Program Files目錄，存取Windows安全資訊以及讀寫系統登錄資料庫（Registry）的程式存取動作，都會需要通過UAC的認證。

結果新增了UAC後的Vista做什麼事情都會彈出視窗導致使⽤者體驗觀感很差罵聲連連，於是在WIndows7時候新增了四種UAC模式：

*   第⼀級（最⾼等級）：相當於Windows Vista中的UAC，即對所有改變系統設定的⾏為進行提醒
*   第⼆級（預設）：只有當程式試圖改變系統設定時才會彈出UAC提示，使⽤者改變系統設定時不會彈出提示
*   第三級：與第二級基本相同，但不使⽤安全桌面
*   第四級：從不提⽰（相當於關閉UAC）

不過因為⼤部分使⽤者其實並不知道UAC存在的重要性（知道是什麼的大多數也就覺得它很煩所以決定直接關閉）所以本文章接下來的討論都是基於使用者設定為「預設」情況下來分析、探討，並給出⼀個繞過的思路。

那麼這邊簡單的說明⼀下如果我們在寫⼀支程序在遇到Windows Vista以後的版本大致上什麼時候會遇到UAC、以及令人覺得棘⼿手的部分：

*   當程序需要寫⼊檔案到C槽、Windows或是System32底下可以嗎？答案是否定的，因為資料權限有區分的關係,假如寫⼊之目標資料夾權限沒有給予寫入、修改權限（可在終端機下icacls命令查詢），例如C槽、Windows、System、System32、Program Files …等目錄，會有影響到系統或者其他程式的運作的可能性，就會彈出UAC視窗提醒是否要執⾏此行為。
*   運⾏外部程式可以嗎？這倒是不一定，要看你準備要運行的程式是否有簽章，如果今天你執⾏的程式具有簽章並且為微軟或者微軟授權認可之簽章，那麼將可直接通過UAC檢查，不必跳出視窗提醒（這很重要，後續會利⽤到）；若沒有簽章或者私⼈簽章不受微軟授權呢？那麼UAC會提醒你這支程式可能會造成危害，彈出視窗提醒使⽤用者。

0x01 UAC實際運作狀況
==============

* * *

今天我們寫了一支後門需要執行任何API或者指令時，如果是敏感的API例如寫⼊檔案、開啟註冊表、 創建進程… 等，那麼中途就會呼叫到⼀個稱為RtlQueryElevationFlags的API。（可參考⽼外提供的微軟不公開的API資料[http://undoc.airesoft.co.uk/ntdll.dll/RtlQueryElevationFlags.php](http://undoc.airesoft.co.uk/ntdll.dll/RtlQueryElevationFlags.php)）

這個API檢測完當前權限之後會決定當前程式正在呼叫的命令是否符合當前進程擁有的權限，如果符合就不彈窗 沒有則彈出使用者必須允許的視窗，這個視窗的檢查只用於決定是否可以彈窗對於實際當前進程的權限是沒有相關的，所以Inline Hook這個API其實對於獲得權限沒有任何用途。

不過有趣的是，如果準備CreateProcess⼀個進程具有簽章但⾮微軟授權，那麼就算使⽤者在跳出UAC視窗時選擇否（拒絕CreateProcess該具不知名簽章的進程) 但是因為有簽章關係，所以進程依然會創建！，於是就有⽼外提出了是否可以直接透過修改自身進程內存來防止跳窗（反正依然可以創建進程成功）如果想看那篇防⽌彈UAC窗的技術⽂章可參見：

[http://www.rohitab.com/discuss/topic/38607-disable-uac-elevation-dialog-by-patching-rtlqueryelevationflags-in-windows-explorer/](http://www.rohitab.com/discuss/topic/38607-disable-uac-elevation-dialog-by-patching-rtlqueryelevationflags-in-windows-explorer/)

那麼UAC視窗究竟是什麼？

![p1](http://drops.javaweb.org/uploads/images/5bcc5b4bd06dc5eb2838c37f6e944df32a2fd707.jpg)

如果在Windows7把UAC權限設置為第三種模式（提醒但沒有安全桌面）那麼在彈出UAC視窗的同時可以透過⼯作管理員選擇到該視窗然後觀看它的處理序資訊：

![p2](http://drops.javaweb.org/uploads/images/32587c154703a66d194cbaac64fe32d0a99b5c35.jpg)

你將會發現其實UAC視窗產⽣者並非當前進程而是由system32底下⼀個稱為`consent.exe`（意味著授權）的進程創建的視窗，透過⼯具如PCHunter可以查看到當前`consent.exe`的⽗進程為`svchost.exe`並且創建UAC進程的`svchost.exe`為系統層級。到這邊大致可以推敲一下今天如果我們進程做了一個敏感命令，那麼大致上會是：

```
進程執⾏行敏感命令 
-> 透過未公開API發消息給系統 
-> svchost（系統層級）創建consent.exe彈出提醒 
-> 把結果告知回系統

```

0x02 DLL Side Loading
=====================

* * *

利用IFileOperation COM白名單explorer.exe（⽂件管理器）系統對於explorer.exe做寫⼊Windows、System、System32 … 等隱密資料夾、系統資料夾是完全信任的，我們可以透過這個漏洞,先透過DLL Injection⽅式（用CreateRemoteThread、APC線程狹持注入、輸⼊法注入 … 等都可）將⾃身DLL注⼊進explorer.exe，然後透過IFileOperation COM將⾃身寫入進系統資料夾內，然後透過DLL Side Loading的方式做組合技Combo達成DLL掛起拿下系統權限，本文最後以此⽅案寫了VC專案實測可穿透UAC，⾄於目前各路⼤牛們整理出來系統內可被DLL Side Loading的程式如下表所列：

1.  C:\Windows\System32\sysprep\sysprep.exe 、Cryptbase.dll(Win7),shcore.dll(Win8)、ActionQueue.dll(Win7)
2.  C:\Windows\System32\oobe\setupsqm.exe、wdscore.dll（Win7,Win8,Win10）
3.  C:\Windows\System32\cliconfg.exe、ntwdblib.dll(Win7,Win8,Win10)
4.  C:\Windows\System32\sysprep\winsat.exe、ntwdblib.dll(Win7)、devobj.dll(Win8.Win10)
5.  C:\Windows\System32\mmc.exe參數：eventvwr，ntwdblib.dll（Win7）、elsext.dll（Win8,Win10）

0x03 IFileOperation⽩名單穿透UAC
===========================

* * *

在WIndows XP時代做⽂件移動，explorer.exe是透過CopyFile API實作，但到了Vista後多了UAC會檢測文件移動權限，而explorer.exe本身也改用了IFileOperation COM來實作,⾄於CopyFile API依舊存在，而這個API變成了IFileOperation COM的封裝版本並且公開給使用者層級的應用程式使用。

⾄於UAC檢測就埋在IFileOperation COM內部的實作，有趣的是explorer.exe本身為IFileOperation COM的⽩名單進程，至於這點怎麼發現的呢？

![p3](http://drops.javaweb.org/uploads/images/481abc89f878d4a010e1ecdd45bdd85910102542.jpg)

今天當使⽤者想放置⼀個檔案入 C:\Windows\ 系統資料夾內依舊會發現UAC提醒這個行為會需要系統權限，但是用工作管理員查看會得知：這個UAC提醒視窗居然是explorer.exe本⾝彈出的視窗！意味著explorer.exe本身調用IFileOperation COM來移動檔案入系統權限的資料夾是不受管制的，⽽彈跳提醒視窗是explorer.exe本身提醒的！因此我們可以得知只要想辦法將⾃己的dll注入explorer.exe進程，那麼就可以擁有任意寫入的系統權限了，關鍵代碼撰寫如下：

![p4](http://drops.javaweb.org/uploads/images/68bd5477adfe9c0f943f24bfcbd15aa4104bb93e.jpg)

透過建⽴進程名單快照並且遍歷進程找到Explorer.exe再做 OpenProcess 取得跨進程寫入讀取權限的握柄(Handle)，接著我們需要做的就是把我們的dll（我撰寫此專案時命名為Client.dll）注入進explorer.exe，另外 本次繞過UAC⼿法上是透過系統內置的SQL本地端解析⼯工具 — cliconfg.exe 含有DLL Side Loading來做穿透（相對應的ntwdblib.dll可穩定的Side Loading Win7~Win10）等待DLL注入explorer.exe後，dll須在explorer.exe進程內將⾃己dll複製⼀份到C:\Windows\system32內的ntwdblib.dll（原本應該會呼叫system下的ntwdblib.dll），完成後,此時我們再呼叫⼀次cliconfg.exe,這時候本來應該載入system下的ntwdblib.dll但因我們在同層目錄下放同名的ntwdblib.dll（⾃行撰寫的dll）會被Loadlibrary優先載⼊，我們的dll便可擁有System32下的權限了。

關鍵代碼如下：

![p5](http://drops.javaweb.org/uploads/images/c2bd522d2397d691f7e86afad36756937eb29f97.jpg)

再來就是處理的是DLL內先確認是否被載入在explorer.exe進程內，若是則開始做SideLoading的前置作業，若是成功被cliconfg.exe載⼊則提示過了UAC！

![p6](http://drops.javaweb.org/uploads/images/7a2b8eac38bf17bd67ae83d557b776d6e696b16e.jpg)

注入完成後先檢測當前進程路徑如果是explorer.exe代表我們需要做複製dll到可被DLLSide Loading的位置（本文額外包成了DllHijacking函數）如果檢測到當前進程已經存活在cliconfg.exe內，代表已經成功取得系統權限，就跳出成功的提醒視窗。

至於DllHijacking函數內部的實現如下：

![p7](http://drops.javaweb.org/uploads/images/389fc248111ff6a7b076e70e9df2d5929e4a58b3.jpg)

最後編譯後分別有一個exe執⾏檔與⼀個Client.dll文件，執⾏結果如下：

執行ClientUAC.exe後，彈出了取得UAC權限的視窗提醒，透過⼯作管理員查看該視窗的進程為cliconfg.exe程序，並且執⾏過程沒有任何UAC認證請求彈窗。

![p8](http://drops.javaweb.org/uploads/images/fb9242bde30a5b7146dd804ab7485c96252812a3.jpg)