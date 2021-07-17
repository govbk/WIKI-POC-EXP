# Android安全开发之Provider组件安全

**作者：伊樵、呆狐@阿里聚安全**

0x00 Content Provider组件简介
=========================

* * *

Content Provider组件是Android应用的重要组件之一，管理对数据的访问，主要用于不同的应用程序之间实现数据共享的功能。Content Provider的数据源不止包括SQLite数据库，还可以是文件数据。通过将数据储存层和应用层分离，Content Provider为各种数据源提供了一个通用的接口。

![](http://drops.javaweb.org/uploads/images/e4577592be151720b2085e1fc9ccafb9a846378b.jpg)

创建一个自己的Content Provider需要继承自ContentProvider抽象类，需要重写其中的`onCreate()`、`query()`、`insert()`、`update()`、`delete()`、`getType()`六个抽象方法，这些方法实现对底层数据源的增删改查等操作。还需在AndroidManifest文件注册Content Provider，注册时指定访问权限、exported属性、authority属性值等。

![](http://drops.javaweb.org/uploads/images/1fe54b405b46904d633d4b029263b505d047571a.jpg)

其它APP使用ContentResolver对象来查询和操作Content Provider，此对象具有Content Provider中同名的方法名。这样其他APP接就可以访问Content Provider对应的数据源的底层数据，而无须知道数据的结构或实现。 

如何定位到具体的数据？ 

采用Content Uri，一个Content Uri如下所示：

```
content://com.jaq.providertest.friendsprovider/friends

```

它的组成一般分为三部分：

1.  `content://`:作为 content Uri的特殊标识(必须);
    
2.  权(`authority`):用于唯一标识这个Content Provider，外部访问者可以根据这个标识找到它；在AndroidManifest中也配置的有；
    
3.  路径(`path`): 所需要访问数据的路径，根据业务而定。
    

这些内容就不具体展开详谈了，详见参考【1】【4】。

0x01 风险简介
=========

* * *

如果在AndroidManifest文件中将某个Content Provider的exported属性设置为true，则多了一个攻击该APP的攻击点。如果此Content Provider的实现有问题，则可能产生任意数据访问、SQL注入、目录遍历等风险。

1.1 私有权限定义错误导致数据被任意访问
---------------------

私有权限定义经常发生的风险是：定义了私有权限，但是却根本没有定义私有权限的级别，或者定义的权限级别不够，导致恶意应用只要声明这个权限就能够访问到相应的Content Provider提供的数据，造成数据泄露。

**以公开的乌云漏洞WooYun-2014-57590为例：**

某网盘客户端使用了自己的私有权限，但是在AndroidManifest中却没有定义私有权限，其它APP只要声明这个权限就能访问此网盘客户端提供的Provider，从而访问到用户数据。

在网盘客户端的AndroidManifest中注册Provider时，声明了访问时需要的读写权限，并且权限为客户端自定义的私有权限：

![](http://drops.javaweb.org/uploads/images/69dcfb04f8db396f513ffc14c1db6010ec00f62b.jpg)

但是在AndroidManifest中却没有见到私有权限“`com.huawei.dbank.v7.provider.DBank.READ_DATABASE`”和“`com.huawei.dbank.v7.provider.DBank.WRITE_DATABASE`”的定义：

![](http://drops.javaweb.org/uploads/images/ddd50412137059e5c5783875b50ba2f3c4d9788b.jpg)

反编译客户端后查看到的URI，根据这些可以构造访问到Provider的URI：

![](http://drops.javaweb.org/uploads/images/a98b24213c9fcd2e86107c68fda1da0983827374.jpg)

**编写POC**

以查看网盘下载的文件列表为例， 

在POC的AndroidManifest中声明私有权限，权限的保护级别定义为最低级“`normal`”：

![](http://drops.javaweb.org/uploads/images/a13bcc8d2d91970f71ebb93e114d781612ce31d6.jpg)

主要代码为：

![](http://drops.javaweb.org/uploads/images/0e34bc7baa18eed62dc9166a97461ff41e9c2f23.jpg)

拿到数据库中保存的下载列表数据：

![](http://drops.javaweb.org/uploads/images/188ddc81c4c826220feee9f091941d8c02549708.jpg)

对应的数据库：

![](http://drops.javaweb.org/uploads/images/18687028c0ad2bfe23ce9789f68b255275af4417.jpg)

这样任意的恶意应用程序就可以访问到用户网盘的上传、下载记录，网盘里面存的文件列表等隐私信息。

**再以公开的乌云漏洞wooyun-2013-039697为例：**

定义了私有权限，但是保护等级设置成为了`dangerous`或者`normal`，这样的保护等级对于一些应用的Provide重要性相比保护级低了。 

Provider为：

![](http://drops.javaweb.org/uploads/images/aed75fdaf4d0bb3da031e6e958405cd446bf2729.jpg)

私有权限“`com.renren.mobile.android.permission.PERMISSION_ADD_ACCOUNT`”的定义为：

![](http://drops.javaweb.org/uploads/images/c112ab970273c5c0e5cbec9c5e505583da8f2e10.jpg)

反编译客户端，看到`AcountProvider`对应的实现：

![](http://drops.javaweb.org/uploads/images/aaac12b375e950276028dfaa17678b949096a535.jpg)

编写POC： 

在`AndroidManifest`中定义和声明权限：

![](http://drops.javaweb.org/uploads/images/ee82032458297b9205823b0a073d438a07758e93.jpg)

主要代码为：

![](http://drops.javaweb.org/uploads/images/5a91560c9d484cb6771ae708edf5d810beac20de.jpg)

可看到用户的账户信息，包括uid，手机号，加密后的密码等：

![](http://drops.javaweb.org/uploads/images/34adc27851ad188baa7ebd3789dbea17d781e0cd.jpg)

1.2 本地SQL注入
-----------

当Content Provider的数据源是SQLite数据库时，如果实现不当，而Provider又是暴露的话，则可能会引发本地SQL注入漏洞。

`Content Provider的query( )`的方法定义为：

![](http://drops.javaweb.org/uploads/images/4190b049e5cb1199261417fbe477bfe94d56001a.jpg)

其中参数：

*   `uri`: 为content Uri，要查询的数据库；
    
*   `projection`：为要查询的列名；
    
*   `selection`和`selectionArgs`：要指定查询条件；
    
*   `sortOrder`：查询结果如何排序。
    

`query()`与 SQL 查询对比如下：

![](http://drops.javaweb.org/uploads/images/b8014cd553ddd171f755c8728343644b4c742ab1.jpg)

如果`query( )`中使用的是拼接字符串组成SQL语句的形式去查询底层的SQLite数据库时，容易发生SQL注入。

**以乌云公开漏洞wooyun-2016-0175294为例：**

客户端的`com.sohu.sohuvideo.provider.PlayHistoryProvider`的`exported`属性为“true”：

![](http://drops.javaweb.org/uploads/images/f274fa3e69dde8f9e02819f9e0b8a57f6dd78895.jpg)

反编译客户端，追踪`PlayHistoryProvider`的实现，发现是用拼接字符串形式构造原始的SQL查询语句：

![](http://drops.javaweb.org/uploads/images/a2bc7b998d583f4de357e90735f7e8b87f96356c.jpg)

使用drozer工具，证明漏洞：

![](http://drops.javaweb.org/uploads/images/09cfb1d8244d8a7661cd1398fa53a0f398e7e9dd.jpg)

对外暴露的Content Provider实现了`openFile()`接口，因此其他有相应调用该Content Provider权限的应用即可调用Content Provider的`openFile()`接口进行文件数据访问。但是如果没有进行Content Provider访问权限控制和对访问的目标文件的Uri进行有效判断，攻击者利用文件目录遍历可访问任意可读文件，更有甚者可以往手机设备可写目录中写入任意数据。

**例子1** 

以乌云公开漏洞wooyun-2013-044407为例： 

此APP实现中定义了一个可以访问本地文件的Content Provider组件，为`com.ganji.android.jobs.html5.LocalFileContentProvider`，因为使用了`minSdkServison=“8”`，`targetSdkVersion=”13”`，即此Content Provider采用默认的导出配置，即`android:exported=”true”`：

![](http://drops.javaweb.org/uploads/images/e7e39428bc9e5f913dea56000ac113b673201d13.jpg)

该Provider实现了`openFile()`接口：

![](http://drops.javaweb.org/uploads/images/62dfb4791e1ef5a4b5a52f5ec3ff50482ac8ce84.jpg)

通过此接口可以访问内部存储app_webview目录下的数据，由于后台未能对目标文件地址进行有效判断，可以通过”`../`”实现目录遍历，实现对任意私有数据的访问。

**例子2**

某社交应用客户端，使用了的`minSDKVersion`为8，定义了私有权限，并且`android:protectionLevel`设为了`signature`

![](http://drops.javaweb.org/uploads/images/d7c9eec900c8edbc090ef3dfe955ac094762687c.jpg)

有一个对外暴露的Content Provider，即`com.facebook.lite.photo.MediaContentProvider`，此Provider没有设置访问权限，而另外一个Provider是设置了访问权限的：

![](http://drops.javaweb.org/uploads/images/e1ffb5b15fd65f6633ffbb1dedebb48c33020a9f.jpg)

在`MediaContentProvider`中实现了`openFile()`接口，没有对传入的URI进行限制和过滤：

![](http://drops.javaweb.org/uploads/images/d075d52bd6b6bd43cad677e5c448682810b884f0.jpg)

此接口本来只想让用户访问照片信息的，但是却可以突破限制，读取其他文件： 

POC：

![](http://drops.javaweb.org/uploads/images/ed557dda303c7bf80e7510d22061583a3468d635.jpg)

读取到其他文件的内容为：

![](http://drops.javaweb.org/uploads/images/2944c3d56156b6562ecc7a69402ce6c5f68c43de.jpg)

另外看到`Openfile()`接口的实现中，如果要访问的文件不存在，就会创建此文件，还有可能的风险就是在应用的目录中写入任意文件。

0x02 阿里聚安全开发者建议
===============

* * *

在进行APP设计时，要清楚哪些Provider的数据是用户隐私数据或者其他重要数据，考虑是否要提供给外部应用使用，如果不需要提供，则在AndroidManifes文件中将其exported属性显式的设为“false”，这样就会减少了很大一部分的攻击面。

人工排查肯定比较麻烦，建议开发者使用阿里聚安全提供的安全扫描服务，在APP上线前进行自动化的安全扫描，尽早发现并规避这样的风险。

**注意：**

由于Android组件Content Provider无法在Android 2.2（即API Level 8）系统上设为不导出，因此建议声明最低SDK版本为8以上版本（这已经是好几年前的SDK了，现在一般都会大于此版本）； 

由于API level 在17以下的所有应用的“`android:exported`”属性默认值都为`true`，因此如果应用的Content Provider不必要导出，建议显式设置注册的Content Provider组件的“`android:exported`”属性为`false`； 

如果必须要有数据提供给外部应用使用，则做好设计，做好权限控制，明确什么样的外部应用可以使用，如对于本公司的应用在权限定义时用相同签名即可，合作方的应用检查其签名；不过还是尽量不提供用户隐私敏感信息。

对于必须暴露的Provider，如第二部分遇到的风险解决办法如下：

2.1 正确的定义私有权限
-------------

在AndroidManifest中定义私有权限的语法为：

![](http://drops.javaweb.org/uploads/images/e641e815afaefb93edbf5fb2cbeae6d603fdbfd9.jpg)

其中`android:protectionLevel`的可选值分别表示：

*   `normal`：默认值，低风险权限，在安装的时候，系统会自动授予权限给 application。
    
*   `dangerous`：高风险权限，如发短信，打电话，读写通讯录。使用此protectionLevel来标识用户可能关注的一些权限。Android将会在安装程序时，警示用户关于这些权限的需求，具体的行为可能依据Android版本或者所安装的移动设备而有所变化。
    
*   `signature`： 签名权限，在其他 app 引用声明的权限的时候，需要保证两个 app 的签名一致。这样系统就会自动授予权限给第三方 app，而不提示给用户。
    
*   `signatureOrSystem`：除了具有相同签名的APP可以访问外，Android系统中的程序有权限访问。
    

大部分开放的Provider，是提供给本公司的其他应用使用的，一般的话一个公司打包签名APP的签名证书都应该是一致的，这种情况下，Provider的`android:protectionLevel`应为设为“`signature`”。

2.2 防止本地SQL注入
-------------

注意：一定不要使用拼接来组装SQL语句。 

如果Content Provider的数据源是SQLite数据库，如果使用拼接字符串的形式组成原始SQL语句执行，则会导致SQL注入。 

如下的选择子句：

![](http://drops.javaweb.org/uploads/images/d029d9275f250a792d0aa99f8d444f697df23180.jpg)

如果执行此操作，则会允许用户将恶意 SQL 串连到 SQL 语句上。 

例如，用户可以为`mUserInput`输入“`nothing; DROP TABLE ** ;`”，这会生成选择子句

```
var = nothing; DROP TABLE **;

```

由于选择子句是作为SQL语句处理，因此这可能会导致提供程序擦除基础 SQLite 数据库中的所有表（除非提供程序设置为可捕获 SQL 注入尝试）。

**使用参数化查询：**

要避免此问题，可使用一个“`?`” 作为可替换参数的选择子句以及一个单独的选择参数数组。 

执行此操作时，用户输入直接受查询约束，而不解释为 SQL 语句的一部分。 

由于用户输入未作为 SQL 处理，因此无法注入恶意 SQL。

请使用此选择子句，而不要使用串连来包括用户输入：

```
String mSelectionClause = “var = ?”;

```

按如下所示设置选择参数数组：

```
String[] selectionArgs = {“”};

```

按如下所示将值置于选择参数数组中：

```
selectionArgs[0] = mUserInput;

```

还可调用SQLiteDatabase类中的参数化查询query()方法：

![](http://drops.javaweb.org/uploads/images/c8ae7d7dd8a2968eaf7c68870453b8d303e13b09.jpg)

3.3 防止目录遍历
----------

1、去除Content Provider中没有必要的openFile()接口。 

2、过滤限制跨域访问，对访问的目标文件的路径进行有效判断： 

使用`Uri.decode()`先对`Content Query Uri`进行解码后，再过滤如可通过“`../`”实现任意可读文件的访问的Uri字符串，如：

![](http://drops.javaweb.org/uploads/images/951507df9e684acb0176cb39fbe01c2b938be6c4.jpg)

2.4 通过检测签名来授权合作方应用访问
--------------------

如果必须给合作方的APP提供Provider的访问权限，而合作方的APP签名证书又于自己公司的不同，可将合作方的APP的签名哈希值预埋在提供Provider的APP中，提供Provider的APP要检查请求访问此Provider的APP的签名，签名匹配通过才让访问。

0x03 参考
=======

* * *

【1】《内容提供程序基础知识》[https://developer.android.com/guide/topics/providers/content-provider-basics.html](https://developer.android.com/guide/topics/providers/content-provider-basics.html) 

【2】《Android app端的sql注入》[http://zone.wooyun.org/content/15097](http://zone.wooyun.org/content/15097)

【3】《Android - Content Providers》 [http://www.tutorialspoint.com/android/android_content_providers.htm](http://www.tutorialspoint.com/android/android_content_providers.htm) 

【4】 [http://www.compiletimeerror.com/2013/12/content-provider-in-android.html](http://www.compiletimeerror.com/2013/12/content-provider-in-android.html)

【5】 [https://developer.android.com/guide/topics/manifest/permission-element.html?hl=zh-cn](https://developer.android.com/guide/topics/manifest/permission-element.html?hl=zh-cn)

【6】 [https://developer.android.com/guide/topics/manifest/permission-element.html](https://developer.android.com/guide/topics/manifest/permission-element.html)

【7】 [WooYun: 人人客户端权限问题导致隐私泄露](http://www.wooyun.org/bugs/wooyun-2013-039697) 

【8】 [WooYun: 华为网盘content provider组件可能泄漏用户信息](http://www.wooyun.org/bugs/wooyun-2014-057590) 

【9】 《Android Content Provider Security》[http://drops.wooyun.org/tips/4314](http://drops.wooyun.org/tips/4314)

【10】 [WooYun: 搜狐app注入泄露观看历史](http://www.wooyun.org/bugs/wooyun-2016-0175294) 

【11】《Android Content Provider Security》[http://drops.wooyun.org/tips/4314](http://drops.wooyun.org/tips/4314)

【12】 [WooYun: 赶集网Android客户端Content Provider组件任意文件读取漏洞](http://www.wooyun.org/bugs/wooyun-2013-044407) 

【13】 [WooYun: 58同城Android客户端远程文件写入漏洞](http://www.wooyun.org/bugs/wooyun-2013-044411) 

【14】 《Content Provider文件目录遍历漏洞浅析》，[https://jaq.alibaba.com/blog.htm?id=61](https://jaq.alibaba.com/blog.htm?id=61) 

【15】 [https://github.com/programa-stic/security-advisories/tree/master/FacebookLite](https://github.com/programa-stic/security-advisories/tree/master/FacebookLite)