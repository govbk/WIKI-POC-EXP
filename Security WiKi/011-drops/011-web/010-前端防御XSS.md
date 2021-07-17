# 前端防御XSS

0x00 前言
=======

* * *

我不否认前端在处理XSS的时候没有后端那样方便快捷，但是很多人都在说过滤XSS的事就交给后端来做吧。前端做没什么用。我个人是非常反感这句话的。虽然说前端防御XSS比较麻烦，但是，不是一定不行。他只是写的代码比后端多了而已。而且前端防御XSS比后端防御XSS功能多，虽说后端也可以完成这些功能，但是代码量会比前端代码多很多很多。其实说了那么多，交给nginx||apache||nodeJs||Python会更好处理。但是我不会C，也就没办法写nginx模块了。而且也不在本文章的范围内，等我什么时候学会C再说把。

0x01 后端数据反馈过滤
=============

* * *

现在大部分的网站都是在后端过滤一下后，就交给数据库，然后前端输出，整个流程只有后端做了防护，一般这个防护被绕过或者某个参数的防护没有做，那么网站就会被沦陷了（请别以为XSS只能获取cookie，熟练的程度取决于你的思想和编程） 现在我们来假设一下网站的一个URL参数没有做好过滤，直接导入数据库了，然后在前端反馈结果。代码如下：

把用户输入的内容导入到数据库里defenderXssTest_GetData.php：

```
<?php
if(empty($_GET['xss'])){        //判断当前URL是否存在XSS参数
    exit(); 
}
$xssString = $_GET['xss'];
/*数据库基础配置*/
$mysql_name ='localhost';
$mysql_username ='root';
$mysql_password ='123456';
$mysql_database ='xsstest'; 
$conn = mysql_connect($mysql_name,$mysql_username,$mysql_password);
mysql_query("set names 'utf8'");
mysql_select_db($mysql_database);

$sql = "insert into XSSTest (xss) values ('$xssString')";
mysql_query($sql);
mysql_close();

```

返回数据库中最后一条数据内容（即最新的内容）defenderXssTest_QueryData.php：

```
<?php
/*数据库基础配置*/
$mysql_name ='localhost';
$mysql_username ='root';
$mysql_password ='123456';
$mysql_database ='xsstest'; 
$conn = mysql_connect($mysql_name,$mysql_username,$mysql_password);
mysql_query("set names 'utf8'");
mysql_select_db($mysql_database);

$sql ="select * from XSSTest where id = (select max(id) from XSSTest)"; //返回数据库中最后一条数据
$xssText = mysql_query($sql);
while($row = mysql_fetch_array($xssText)){  //显示从数据库中返回的数据
    echo $row['xss'];
}
mysql_close();

```

前端输入及反馈defenderXssTest.html：

```
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>前端防御XSS#Demo1</title>
</head>
<body>
    <input type="text" name="xss">
    <input type="submit" value="提交" id="xssGet">
</body>
<!--测试请记得更换jQuery路径！-->
<script type="text/javascript" src="/Public/js/library/jquery.js"></script>
<script>
    $("#xssGet").click(function(){
        $.ajax({
            url: '/defenderXssTest_GetData.php',
            type: 'get',
            dataType: 'text',
            data: "xss="+$('input:first').val(),
            cache:false, 
            async:false,
        })
        .done(function() {
            $.ajax({
                url: '/defenderXssTest_QueryData.php',
                type: 'post',
                dataType: 'text',
                cache:false, 
                async:false,
            })
            .done(function(data) {
                $("body").append(data);
            })
        })
    });
</script>
</html>

```

一共三个文件，因为测试用，我就没把数据库基础配置分离出来放在其他文件里了。

现在我们在浏览器里打开defenderXssTest.html文件:

![p1](http://drops.javaweb.org/uploads/images/0ae4473f8c4b72136f200ef876d6942b162646f3.jpg)

![p2](http://drops.javaweb.org/uploads/images/c622cb5816924adbbf1f82874fabc8edf4da286a.jpg)

现在我们再看下数据库：

![p3](http://drops.javaweb.org/uploads/images/46b3d10deb79d33af2c8230ed2c00185d7f4549b.jpg)

已经导入到数据库里了。

OK，以上就是最普通的储蓄型XSS案例。为什么会出现这个问题呢，是因为PHP没有做好过滤。同时前端也没有做好过滤，这里会有人说前端做没用的，攻击者可以使用burp抓到此数据包，然后改包就可以绕过了。对，确实是这样。但是大伙从一开始就已经被误导了。想知道哪里被误导么，往下看。

这里我画个前端、Nginx、后端都做了过滤的图：

![p4](http://drops.javaweb.org/uploads/images/afd469a238c980da1635d133f584bb6f6cca39d7.jpg)

思维导图URL：[https://www.processon.com/view/link/56c486cde4b0e2317a8b6681](https://www.processon.com/view/link/56c486cde4b0e2317a8b6681)

这里我们可以看到防火墙的第一道门是前端过滤XSS机制。也是目前被大家所熟知的过滤结构。而本章要说的是：为什么不把前端过滤copy或者move到后端过滤机制下呢？

这里是新型的过滤机制的图：

![p5](http://drops.javaweb.org/uploads/images/09b7bc4edc27daec88d9d1e87795d2d86ed4fab1.jpg)

思维导图URL：[https://www.processon.com/view/link/56c4882ce4b0e5041c35ab53](https://www.processon.com/view/link/56c4882ce4b0e5041c35ab53)

这里我们在后端过滤机制的后面加上了前端过滤。为什么要这样做呢？

大家都知道前端过滤XSS是可以被抓包软件给修改的，所以是可以绕过，没有什么用。而Nginx过滤我相信大家都知道，很少有人愿意去用它，因为如果是做安全文章一类的话，是会被Nginx给抛弃当前的数据包的，也就是你发布的文章不会被存到数据库里，而且Nginx防御XSS模块并没有前端、后端那样简单方便，需要配置的东西很多。也导致了很多管理员不在Nginx安全上下功夫，即使管理员配置了Nginx过滤XSS模块，也可以绕过。

利用Nginx的一处逻辑缺陷（详情请移步到：[http://www.freebuf.com/articles/web/61268.html](http://www.freebuf.com/articles/web/61268.html)文章里的0x03小节：利用Nginx&Apache环境bug来实现攻击）,至于后端过滤机制肯定会有不严谨的时候，不然也而不会导致那么多XSS漏洞了。所以当攻击者输入的XSS字符串绕过了前端、Nginx、后端的话，那么就会直接导入到数据库中。那么这个时候后端传来的数据就不可信了。而如果我们在前端显示后端传来的数据时加了过滤会怎么样呢，答案是very good。当然了，这里有个前提，是前端显示后端传来数据的时候使用的是AJAX方法，而不是类似ThinkPHP这样在模板里调用。确切的说：此方法只针对于API接口

现在我们来做一个测试，之前的代码就是使用了AJAX方法，而

defenderXssTest_GetData.php和defenderXssTest_QueryData.php就类似于后端的API接口。我们现在在原有的基础上添加一些代码：

下面是前端过滤XSS的代码，取自于百度FEX前端团队的Ueditor在线编辑器：

```
function xssCheck(str,reg){
    return str ? str.replace(reg || /[&<">'](?:(amp|lt|quot|gt|#39|nbsp|#\d+);)?/g, function (a, b) {
        if(b){
            return a;
        }else{
            return {
                '<':'&lt;',
                '&':'&amp;',
                '"':'&quot;',
                '>':'&gt;',
                "'":'&#39;',
            }[a]
        }
    }) : '';
}

```

然后我们在原有代码的基础上添加xssCheck()函数就行了。如下：

```
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>前端防御XSS#Demo1</title>
</head>
<body>
    <input type="text" name="xss">
    <input type="submit" value="提交" id="xssGet">
</body>
<script type="text/javascript" src="/Public/js/library/jquery.js"></script>
<script>
    $("#xssGet").click(function(){
        $.ajax({
            url: '/defenderXssTest_GetData.php',
            type: 'get',
            dataType: 'text',
            data: "xss="+$('input:first').val(),
            cache:false, 
            async:false,
        })
        .done(function() {
            $.ajax({
                url: '/defenderXssTest_QueryData.php',
                type: 'post',
                dataType: 'text',
                cache:false, 
                async:false,
            })
            .done(function(data) {
                $("body").append(xssCheck(data));
            })
        })
    });
    function xssCheck(str,reg){
        return str ? str.replace(reg || /[&<">'](?:(amp|lt|quot|gt|#39|nbsp|#\d+);)?/g, function (a, b) {
            if(b){
                return a;
            }else{
                return {
                    '<':'&lt;',
                    '&':'&amp;',
                    '"':'&quot;',
                    '>':'&gt;',
                    "'":'&#39;',
                }[a]
            }
        }) : '';
    }
</script>
</html>

```

现在我们来输入XSS字符串看看：

![p6](http://drops.javaweb.org/uploads/images/99644f6e8897279275245a4fbc032f0be6c1f2ec.jpg)

变成了这个样子。我们再去数据库里看下：

![p7](http://drops.javaweb.org/uploads/images/960ada7972faa286732dca31d03f8f0331856f5f.jpg)

的确是完整的XSS字符串，但是前端过滤了，导致此XSS没有用武之地。

所以前端开发人员只需要在网站的base.js代码里把过滤XSS的函数写进去，再把每一个ajax传过来的数据加上函数就可以了。

0x02 前端报警机制
===========

* * *

这里的报警机制不能说特别的完整，是可以绕过的。那这个报警机制到底有何用处呢？就是在攻击者测试的时候发现及报警。

我们都知道测试XSS的时候和装逼的时候，攻击者会输入`alert()`函数，而之前的过滤方式，都是使用正则匹配，从而导致正则过长，匹配不易，运行过慢等问题。而现在我们完全可以重写alert函数来让攻击者在测试的时候，使用的是我们已经重写后的函数，这样做的好处是：当当前的参数不存在XSS的时候，这些函数是不会被触发的。而当当前参数存在XSS的时候，攻击者会依次输入：`woaini`->查看是否在源码里输出->`woaini<>`->查看`<>`有没有被过滤->输入`<script>alret(1)</script>`或者`<img src="test" onerror="alert(1)" />`->使用了我们重写的函数->触发报警机制。这样说可能有些人看不懂，下面是我画的图：

![p8](http://drops.javaweb.org/uploads/images/00e84a130307d55788099b6a1bbea8eb15b8c781.jpg)

思维导图：[https://www.processon.com/view/link/56c55805e4b0e5041c39261f](https://www.processon.com/view/link/56c55805e4b0e5041c39261f)

让我们来看下具体的代码吧：

```
var backAlert = alert;  //把alert赋值给backAlert ，当后面重写alert时，避免照成死循环，照成溢出错误。
window.alert = function(str){       //重写alert函数
    backAlert(str);
    console.log("已触发报警,将数据发送到后台");
}

```

再把console.log换成ajax把数据发送给后台应用。后台接受的时候记得做过滤。前端代码记得加密，防止攻击者看出意图从而导致绕过，不触发报警。因为可能有些公司、个人网站已经有了自己的攻击报警系统、智能日志检索系统，我也就不再写了。把ajax发送的数据过滤后存到数据库里，再显示就行了。可以根据自己现有的框架进行开发，思路上面已经了，不难理解，代码也不难写。如果你不会或者说是不想写，可以等到我下一篇的文章。到时候里面会有全部的源代码。

下一章也是有关XSS防御的，在“前端报警机制”的基础上做的完善，有可能会用到后端，目前思路已经有了，但是没时间写。看三月底之前能不能写出来吧。

0x03 结语
=======

* * *

之前EtherDream已经说了前端防火墙了，只是他做的是防御，而我是不防御直接报警。然后人工修复代码。因为虽然你防御住了，但是后端漏洞还在那，而触发报警机制后就可以进行人工修复。不是说EtherDream写的不好，反之非常好，在他的基础上也可以修改成前端报警机制，不过我还是喜欢让攻击者高兴几十分钟后，就懵逼的样子。在EtherDream的代码中有一个很棒的代码片段，他使用了内联事件监听了onclick等on事件，可以近一步的监听到黑客的操作。因为版权问题，我不方便把代码贴到本文中，毕竟是别人的思想结晶。想了解的话可以去查看：

[http://fex.baidu.com/blog/2014/06/xss-frontend-firewall-1/](http://fex.baidu.com/blog/2014/06/xss-frontend-firewall-1/)	