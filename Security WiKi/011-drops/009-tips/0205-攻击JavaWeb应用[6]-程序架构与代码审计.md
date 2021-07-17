# 攻击JavaWeb应用[6]-程序架构与代码审计

#### 注：

不管多么强大的系统总会有那么些安全问题，影响小的可能仅仅只会影响用户体验，危害性大点的可能会让攻击者获取到服务器权限。这一节重点是怎样去找到并利用问题去获取一些有意思的东西。

#### Before:

有MM的地方就有江湖，有程序的地方就有漏洞。现在已经不是SQL注入漫天的年代了，Java的一些优秀的开源框架让其项目坚固了不少。在一个中大型的Web应用漏洞的似乎永远都存在，只是在于影响的大小、发现的难易等问题。有很多比较隐晦的漏洞需要在了解业务逻辑甚至是查看源代码才能揪出来。JavaWeb跟PHP和ASP很大的不同在于其安全性相对来说更高。但是具体体现在什么地方？JavaWeb开发会有那些问题？这些正是我们今天讨论的话题。

JavaWeb开发概念
-----------

* * *

### Java分层思想

通过前面几章的介绍相信已经有不少的朋友对Jsp、Servlet有一定了解了。上一节讲MVC的有说的JSP+Servlet构成了性能好但开发效率并不高的Model2。在JavaWeb开发当中一般会分出很多的层去做不同的业务。

#### 常见的分层

```
1、展现层(View 视图) 
2、控制层（Controller 控制层） 
3、服务层（Service） 
4、实体层（entity 实体对象、VO(value object) 值对象 、模型层（bean）。
5、业务逻辑层BO(business object) 
6、持久层（dao- Data Access Object 数据访问层、PO(persistant object) 持久对象）

```

### 依赖关系

在了解一个项目之前至少要知道它的主要业务是什么主要的业务逻辑和容易出现问题的环节。其次是了解项目的结构和项目当中的类依赖。再次才是去根据业务模块去读对应的代码。从功能去关联业务代码入手往往比逮着段代码就看效率高无数倍。

前几天在Iteye看到一款不错的生成项目依赖图的工具- Structure101，试用了下Structure101感觉挺不错的，不过是收费的而且价格昂贵。用Structure101生成Jeebbs的项目架构图：

![enter image description here](http://drops.javaweb.org/uploads/images/b58595c080d34fe4ad32daf3f767a4826a8cd5e2.jpg)

Structure101导入jeebss架构图-包调用： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/561aae085b5e25f1658b237e4ad92696f8496fca.jpg)

Structure101包调用详情：

![enter image description here](http://drops.javaweb.org/uploads/images/81277ac2697279eb8d02a7a10b2a6c2f7655516e.jpg)

Structure101可以比较方便的去生成类关系图、调用图等。Jeebbs项目比较大，逻辑相对复杂，不过可以看下我的半成品的博客系统。

项目图：

![enter image description here](http://drops.javaweb.org/uploads/images/cfdbc9966a6da9942d842aaaac38a55f121cdfc4.jpg)

架构图：

![enter image description here](http://drops.javaweb.org/uploads/images/765718a41994484583005ccbaa16b0a88c50e0c0.jpg)

控制层：

![enter image description here](http://drops.javaweb.org/uploads/images/5643ff4c5c97249e5b4fbe6220bbbc3757ca3c97.jpg)

调用流程（demo还没处理异常，最好能try catch下用上面的logger记录一下）： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/1d89c2198ad9b3baf045c0ae0769aa8aa00fc13a.jpg)

漏洞发掘基础
------

* * *

Eclipse采用的是SWT编写，俗称万能IDE拥有各种语言的插件可以写。Myeclipse是Eclipse的插件版，功能比eclipse更简单更强大。

导入Web项目到Myeclipse，Myeclipse默认提供了主流的Server可以非常方便的去部署你的Web项目到对应的Server上，JavaWeb容器异常之多，而ASP、 PHP的容器却相对较少。容器可能除了开发者有更多的选择外往往意味着需要调试程序在不同的Server半桶的版本的表现，这是让人一件非常崩溃的事。

调试开源的项目需下载源码到本地然后导入部署，如果没有源代码怎么办？一般情况下JavaWeb程序不会去混淆代码，所以通过之前的反编译工具就能够比较轻松的拿到源代码。但是反编译过来的源代码并不能够直接作用于debug。不过对我们了解程序逻辑和结构有了非常大的帮助，根据逻辑代码目测基本上也能完成debug。 ￼

![enter image description here](http://drops.javaweb.org/uploads/images/7f0082498fadeb5bf9115a824dae56ebba5a0db6.jpg)

在上一节已经讲过了一个客户端的请求到达服务器端后，后端会去找到这个URL所在的类，然后调用业务相关代码完成请求的处理，最后返回处理完成后的内容。跟踪请求的方式一般是先找到对应的控制层，然后深入到具体的逻辑代码当中。另一种方法是事先到dao或业务逻辑层去找漏洞，然后逆向去找对应的控制层。最直接的如model1、model2并不用那么费劲直接代码在jsp、servlet代码里面就能找到一大堆业务逻辑。

### 按业务类型有序测试

普通的测试一般都是按功能和模块去写测试的用例，即按照业务一块一块去测试对应的功能。这一种方式是顺着了Http请求跟踪到业务逻辑代码，相对来说比较简单方便，而且逻辑会更加的清晰。

上面的架构图和包截图不知道有没有同学仔细看，Java里面的包的概念相对来说比较严禁。公认的命名方式是com/org.公司名.项目名.业务名全小写。

如:`org.javaweb.ylog.dao`部署到服务器上对应的文件夹应当是`/WEB-INF/classes/org/javaweb/ylog/dao/`其中的.意味着一级目录。

现在知道了包和分层规范要找到控制层简直就是轻而易举了，一般来说找到Controller或者Action所在的包的路径就行了。左边是jeebbs右边是我的blog，其中的action下和controller下的都是控制层的方法。`@RequestMapping("/top.do")`表示了直接把请求映射到该方法上，Struts2略有不同，需要在xml配置一个action对应的处理类方法和返回的页面。不过这暂时不是我们讨论的话题，我们需要知道隐藏在框架背后的请求入口的类和方法在哪。 ￼

![enter image description here](http://drops.javaweb.org/uploads/images/4ca26b80ee4de9a91be34d4119278a52742406f3.jpg)

用例图：

![enter image description here](http://drops.javaweb.org/uploads/images/5375f658355647e7fd6bbdee3e3282a82b699753.jpg)

### 用户注册问题

用户逻辑图：

![enter image description here](http://drops.javaweb.org/uploads/images/d2827fc9f14501c95fc86ed5b8840f6390da5a6d.jpg)

容易出现的问题:

```
1、没有校验用户唯一性。
2、校验唯一性和存储信息时拼Sql导致Sql注入。
3、用户信息（用户名、邮箱等）未校验格式有效性，可能导致存储性xss。
4、头像上传漏洞。
5、用户类型注册时可控导致注册越权（直接注册管理员帐号）。
6、注册完成后的跳转地址导致xss。

```

### Jeebbs邮箱逻辑验证漏洞：

注册的URL地址是：http://localhost/jeebbs/register.jspx， register.jspx很明显是控制层映射的URL，第一要务是找到它。然后看他的逻辑。

#### Tips：Eclipse全局搜索关键字方法 ￼

![enter image description here](http://drops.javaweb.org/uploads/images/b3125271a3e1d697e48b7c5de9e09ec59a672c11.jpg)

根据搜索结果找到对应文件：

![enter image description here](http://drops.javaweb.org/uploads/images/31631cc2e7e88861ebd59ae85a4b18718923c5ae.jpg)

根据结果找到对应的`public class RegisterAct`类，并查看对应逻辑代码： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/c0d67d48f0ae207e95bc8075f38badfbdbee95f9.jpg)

找到控制层的入口后即可在对应的方法内设上断点，然后发送请求到控制层的URL进入Debug模式。 注册发送数据包时用Tamper data拦截并修改请求当中的email为xss攻击代码。 ￼

￼![enter image description here](http://drops.javaweb.org/uploads/images/f789a446327143a2d6477de1aaa5d1d3df40b0d3.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/98dde57b99b7019ce7ad0fd5ec352f2e0a802d0b.jpg)

选择任意对象右键Watch即可查看对应的值（任意完整的，有效的对象包括方法执行）。 F6单步执行。

￼![enter image description here](http://drops.javaweb.org/uploads/images/19435c23fc7b24d65d0ff0dfa53387055c68aeca.jpg)

F5进入validateSubmit：

![enter image description here](http://drops.javaweb.org/uploads/images/a1586f0ef6f696b65ffa9918a9b6ffeb8aeb28f6.jpg)

F6跟到125行注册调用：

![enter image description here](http://drops.javaweb.org/uploads/images/d063b02c47a9681d1b2451b2dee793244fab82bf.jpg)

F3可以先点开registerMember类看看：

![enter image description here](http://drops.javaweb.org/uploads/images/69e527d4264b055baee52e091623106de660a971.jpg)

找到接口实现类即最终的注册逻辑代码：

![enter image description here](http://drops.javaweb.org/uploads/images/bf1906b3208b5fb8ea76c1837fbf05a3a143e0e1.jpg)

### Jeebbs危险的用户名注册漏洞

Jeebbs的数据库结构当中用户名长度过长：

```
`username` varchar(100) NOT NULL COMMENT '用户名'

```

这会让你想到了什么？

![enter image description here](http://drops.javaweb.org/uploads/images/d42230d6642814e9be19da94ba8ce6fc5c9d03a7.jpg)

当用户名的输入框失去焦点后会发送Ajax请求校验用户名唯一性。请输入一个长度介于 3 和 20 之间的字符串。也就是说满足这个条件并且用户名不重复就行了吧？前端是有用户名长度判断的，那么后端代码呢？因为我已经知道了用户名长度可以存100个字符，所以如果没有判断格式的话直接可以注册100个字符的用户名。首先输入一个合法的用户名完成客户端的唯一性校验请求，然后在点击注册发送数据包的时候拦截请求修改成需要注册的xss用户名，逻辑就不跟了跟上面的邮箱差不多，想像一下用户名可以xss是多么的恐怖。任何地方只要出现粗线下xss用户名就可以轻易拿到别人的cookie。 ￼

![enter image description here](http://drops.javaweb.org/uploads/images/17643ce600add92ffcc36d7d2ad8ef1991cad564.jpg)

### Cookie明文存储安全问题： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/d7922af807efb72739c4e418613266749d045f3b.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/053d3d917be2db9f55691193759e45ee196c773a.jpg)

代码没有任何加密就直接setCookie了，如果说cookie明文储存用户帐号密码不算漏洞的话等会弹出用户明文密码不知道是算不算漏洞。

### 个性签名修改为xss,发帖后显示个性签名处可xss ￼

![enter image description here](http://drops.javaweb.org/uploads/images/975d66370f63c0f650196f2b9e209d5624047acd.jpg)

因为个性签名会在帖子里显示，所以回帖或者发帖就会触发JS脚本了。这里说一下默认不记住密码的情况下（不设置cookie）不能够拿到cookie当中的明文密码，这个漏洞用来打管理员PP挺不错的。不应该啊，起码应该过滤下。

### 不科学的积分漏洞

![enter image description here](http://drops.javaweb.org/uploads/images/bb012456644ca279f109e26ed2652a94f75426e5.jpg)

积分兑换方法如下：

```
@RequestMapping(value = "/member/creditExchange.jspx")
public void creditExchange(Integer creditIn, Integer creditOut, Integer creditOutType, Integer miniBalance, String password, HttpServletRequest request, HttpServletResponse response) {}

```

可以看到这里直接用了SpringMvc注入参数，而这些参数恰恰是控制程序逻辑的关键。比如构建如下URL，通过GET或者POST方式都能恶意修改用户的积分：

```
http://localhost/jeebbs/member/creditExchange.jspx?creditIn=26&creditOut=-27600&creditOutType=1&miniBalance=-10000000&password=wooyun

```

因为他的逻辑是这么写的：

```
if(user.getPoint()-creditOut>miniBalance){
    balance=true;
}else{
    flag=1;
}

```

从User对象里面取出积分的数值，而积分兑换威望具体需要多少是在确定兑换关系后由ajax去后台计算出来的，提交的时候也没有验证计算的结果有没有被客户端改过。其中的creditOut和miniBalance都是我们可控的。所以这个等式不管在什么情况下我们都可以让它成立。

![enter image description here](http://drops.javaweb.org/uploads/images/ba61268758d62673984d6440d13431f3622a1f07.jpg)

### 打招呼XSS 逻辑有做判断：

```
1、用户名为空。
2、不允许发送消息给自己。
3、用户名不存在。

```

在控制层并没有做过滤： ￼

￼![enter image description here](http://drops.javaweb.org/uploads/images/4637975b501ae77493f464ff242832cdcc382b4a.jpg)

在调用com.jeecms.bbs.manager.impl. BbsMessageMngImpl.java的sendMsg方法的时候依旧没有过滤。到最终的BbsMessageDaoImpl 的save方法还是没有过滤就直接储存了; 一般性的做法，关系到用户交互的地方最好做referer和xss过滤检测，控制层负责收集数据的同时最好处理下用户的请求，就算controller不处理起码在service层做下处理吧。

![enter image description here](http://drops.javaweb.org/uploads/images/e442e2b8d64e176850c45c20cd3cda119ff70234.jpg)

#### 发布投票贴xss发布一片投票帖子，标题xss内容。

#### 邮箱的两处没有验证xss

#### 个人资料全部xss

#### 投稿打管理员后台点击查看触发

#### 搜索xss

http://demo.jeecms.com/search.jspx?q=%2F%3E%3Cscript%3Ealert%28document.cookie%29%3B%3C%2Fscript%3Ehello&channelId=

漏洞N………

### 按程序实现逆向测试

#### ”逆向”找SQL注入

SQL注入理论上是最容易找的，因为SQL语句的特殊性只要Ctrl+H 搜索select、from 等关键字就能够快速找到项目下所有的SQL语句，然后根据搜索结果基本上都能够确定是否存在SQL注入。**凡是SQL语句中出现了拼SQL（如select * from admin where id=’”+id+”’）那么基本上80%可以确定是SQL注入。但也有特例，比如拼凑的SQL参数并不受我们控制，无法在前台通过提交SQL注入语句的方式去控制最终的查询SQL。而采用预编译?占位方式的一般不存在注入。**

比如搜索51javacms项目当中的SQL语句： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/6a83dfed3d1c8eb54b0255871e2e2346e5c95de2.jpg)

#### Tips:ORM框架特殊性

### Hibernate HQL：

需要注意的是Hibernate的HQL是对对象进行操作，所以它的SQL可能是：

```
String hql = "from Emp";
Query q = session.createQuery(hql);

```

也可以

```
String hql = "select count(*) from Emp";
Query q = session.createQuery(hql);

```

甚至是

```
String hql = "select new Emp(e.empno,e.ename) from Emp e ";
Query q = session.createQuery(hql);

```

![enter image description here](http://drops.javaweb.org/uploads/images/2b998648a70303eb005d0b66100051c9546a258d.jpg)

### Mybatis(Ibatis3.0后版本叫Mybatis)：

Ibatis、Mybatis的SQL语句可以基于注解的方式写在类方法上面，更多的是以xml的方式写到xml文件。

￼![enter image description here](http://drops.javaweb.org/uploads/images/f258352418b80853691961695a114ec59a269823.jpg)

在当前项目下搜索SQL语句关键字，查找疑似SQL注入的调用：

![enter image description here](http://drops.javaweb.org/uploads/images/a636d552f42dff234719ccc3cea4adbef4091ef1.jpg)

进入搜索结果的具体逻辑代码：

![enter image description here](http://drops.javaweb.org/uploads/images/dc6f488766e2eb8642b9a190c0c15ce30d2b8087.jpg)

最外层的Contrller： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/0314086a3aece3eed3776e97420d758e13270767.jpg)

“逆向”找到控制层URL以后构建的SQL注入请求：

![enter image description here](http://drops.javaweb.org/uploads/images/d835fb5e317b2b4f09057d02f49f8ce5a4ce5e04.jpg)

可能大家关注的代码审计最核心的怎么去发掘SQL注入这样高危的漏洞，其次是XSS等类型的漏洞。

#### 小结：

```
学会怎样Debug。
学会怎样通过从控制层到最终的数据访问层的代码跟踪和从数据访问层倒着找到控制层的入口。
学会怎样去分析功能模块的用例。

```

### 文件上传、下载、编辑漏洞

文件上传漏洞即没有对上传的文件的后缀进行过滤，导致任意文件上传。有的时候就算有后缀判断，但是由于解析漏洞造成GETSHELL这是比较难避免的。

#### 1、没有做任何限制的上传漏洞：

![enter image description here](http://drops.javaweb.org/uploads/images/5640df0c1055e19546700c41ec19c8540839bb12.jpg)

这一种是不需要任何绕过直接就可以上传任意脚本威胁性可想而知。

#### 2、Bypass白名单和黑名单限制

![enter image description here](http://drops.javaweb.org/uploads/images/4296091f926910f9f029300fa02060ebf57f7982.jpg)

某些时候就算做了后缀验证我们一样可以通过查看验证的逻辑代码找到绕过方式。第35、36行分别定义了白名单和黑名单后缀列表。41到46行是第一种通过黑名单方式校验后缀合法性。47到57行代码是第二种通过白名单方式去校验后缀合法性。现在来瞧下上诉代码都有那些方式可以Bypass。

```
1、假设37行代码的upload不是在代码里面写死了而是从客户端传入的参数，那么可以自定义修改path把文件传到当前server下的任意路径。
2、第39行犯下了个致命的错误，因为文件名里面可以包含多个”.”而”xxxxx”.indexOf(“.”)取到的永远是第一个”.”,假设我们的文件名是1.jpg.jsp即可绕过第一个黑名单校验。
3、第42行又是另一个致命错误s.equals(fileSuffix)比较是不区分大小写假设我们提交1.jSP即可突破验证。
4、第50行同样是一个致命的错误，直接用客户端上传的文件名作为最终文件名，可导致多个漏洞包括解析漏洞和上面的1.jpg.jsp上传漏洞。

```

#### 文件上传漏洞修复方案:

```
1、文件上传的目录必须写死
2、把原来的fileName.indexOf(".")改成fileName.lastIndexOf(".")
3、s.equals(fileSuffix)改成s.equalsIgnoreCase(fileSuffix) 即忽略大小写或者把前面的fileSuffix字符转换成小写s.equals(fileSuffix.toLowerCase())

```

### 文件下载漏洞

51JavaCms典型的文件下载漏洞，我们不妨看下其逻辑为什么会存在漏洞。51javacms并没有用流行的SSH框架而是用了Servlert3.0自行做了各种封装，实现了各种漏洞。Ctrl+H搜索DownLoadFilePage找到下载的Servlet：

![enter image description here](http://drops.javaweb.org/uploads/images/f7a7e929412baa87685f20bfe6d605970c14f639.jpg)

改装了下51javacms的垃圾代码： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/53c98d4813a576768f473675ac022d658c2703ba.jpg)

请求不存在的文件：

![enter image description here](http://drops.javaweb.org/uploads/images/42ee04f382cb95b4b3e7f94737503e903e23a2eb.jpg)

跨目录请求一个存在的文件：

![enter image description here](http://drops.javaweb.org/uploads/images/9cb4c63b7004678a5ac86dfc20b6bc300a4151e2.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b5be2686de6d0b2855c37dcfdd4bd7360062244a.jpg)

### 文件编辑漏洞

JeeCms之前的后台就存在任意文件编辑漏洞（JEECMS后台任意文件编辑漏洞and官方漏洞及拿shell ：http://wooyun.org/bugs/wooyun-2010-04030）官方的最新的修复方式是把path加了StartWith验证。

基于Junit高级测试
-----------

* * *

Junit写单元测试这个难度略高需要对代码和业务逻辑有比较深入的了解，只是简单的提下,有兴趣的朋友可以自行了解。

JUnit是由 Erich Gamma 和 Kent Beck 编写的一个回归测试框架（regression testing framework）。Junit测试是程序员测试，即所谓白盒测试，因为程序员知道被测试的软件如何（How）完成功能和完成什么样（What）的功能。Junit是一套框架，继承TestCase类，就可以用Junit进行自动测试了。

![enter image description here](http://drops.javaweb.org/uploads/images/cca473c713d341b4709fae08fb41a3e1dfb1ba37.jpg)

其他
--

* * *

### 1、通过查看Jar包快速定位Struts2漏洞

比如直接打开lerxCms的lib目录：

![enter image description here](http://drops.javaweb.org/uploads/images/6937f536ae7e8af21897320c608ecfa9c2c582cf.jpg)

### 2、报错信息快速确认Server框架

类型转换错误：

![enter image description here](http://drops.javaweb.org/uploads/images/afd58690d03ecb6eed66bb52dffd510bdfe05bd1.jpg)

Struts2：

![enter image description here](http://drops.javaweb.org/uploads/images/1d4faf9721148b4cd105b6086e9e60d23243dce2.jpg)

### 3、二次校验逻辑漏洞

比如修改密保邮箱业务只做了失去焦点唯一性校验，但是在提交的时候听没有校验唯一性

### 4、隐藏在Select框下的邪恶

Select下拉框能有什么漏洞？一般人我不告诉他，最常见的有select框Sql注入、存储性xss漏洞。搜索注入的时候也许最容易出现注入的地方不是搜索的内容，而是搜索的条件！

Discuz select下拉框存储也有类型的问题，但Discuz对Xss过滤较严未造成xss：

![enter image description here](http://drops.javaweb.org/uploads/images/b761ad87bfe0b6162f94a0b83690a221031382fa.jpg)

下拉框的Sql注入： ￼

![enter image description here](http://drops.javaweb.org/uploads/images/ce96f492afa993e4612ad399907ace331d089e6a.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/40880dbeffacdf19dd69f1586b1f7f266d8669ad.jpg)

小结： 本节不过是漏洞发掘审计的冰山一角，很多东西没法一次性写出来跟大家分享。本系列完成后公布ylog博客源码。本节源代码暂不发布，如果需要源码站内。