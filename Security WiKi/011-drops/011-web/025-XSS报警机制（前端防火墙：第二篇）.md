# XSS报警机制（前端防火墙：第二篇）

0x00 前言
=======

* * *

在第一章结尾的时候我就已经说了，这一章将会更详细的介绍前端防火墙的报警机制及代码。在一章出来后，有人会问为什么不直接防御，而是不防御报警呢。很简单，因为防御的话，攻击者会定位到那一段的JavaScript代码，从而下次攻击的时候绕过代码。如果不防御而报警的话，攻击者会降低警觉，不会在看JavaScript代码（至少我是这样）。回到正题，下面说的代码，是基于thinkphp框架和bootstrap3.3.5框架。如果你的网站没有使用thinkphp3.2.3框架的话，可以参照我的思路重新写一个。这里我强调一下“前端防御XSS是建立在**后端忘记做过滤，没有做过滤，疏忽做过滤的基础上的...**

0x01 前端要做的事
===========

* * *

其实标题应该改成“XSS报警机制”的，因为在这一章里使用了大量的后端代码。但是第一章的标题都出来了，也没法改了。

前端要做的事情在第一章的时候就已经说了，代码如下：

![p1](http://drops.javaweb.org/uploads/images/76175ce108f74ffdec6ad94826ed832a83659fd9.jpg)

现在我们就是针对第38行进行修改，改成我们后台接受的API URL。就像这样：

![p2](http://drops.javaweb.org/uploads/images/a1560fb9f0b9bfbc8fe8d31825e141a7569f4b63.jpg)

对，就这一行。没有其他代码。在实际的线上环境中，也只需要上面5行。可以直接copy到您的线上环境中，记得把倒数第二行的url改成自己的地址就行了。难道就那么简单？不，0x05节还有一部分前端代码。0x01~0x04主要是针对于平台。

0x02 数据库要做的事
============

* * *

一共两个表。fecm_user和fecm_bugdata。

fecm_user的字段信息如下：

![p3](http://drops.javaweb.org/uploads/images/834d3fda123a4ce92fd9b1551859564c74449ed8.jpg)

*   name：管理员账户名
*   md5name：3次name值的md5
*   password：3次密码的md5
*   email：管理员邮箱
*   create_date：管理员创建时间

为了安全起见（其实就是懒）没有写添加管理员的，自行在数据库里添加

fecm_bugdata的字段信息如下：

![p4](http://drops.javaweb.org/uploads/images/8379fc11c0314ed6a916bd656b861934130ee1ef.jpg)

*   url：漏洞的url地址
*   category：漏洞类型
*   cookies：攻击者的cookies
*   ua：攻击者的User-Agent
*   hxff_ip：攻击者的HTTP_X_FORWARDED_FOR
*   hci_ip：攻击者的HTTP_CLIENT_IP
*   ra_ip：攻击者的REMOTE_ADDR
*   time：攻击者攻击的时间
*   fixes：漏洞是否修复（0为未修复，1为已修复）

0x03 后端要做的事
===========

* * *

因为后端代码太多，所以我就说一些核心的后端处理代码。

在0x01节里，有个核心的代码是`new Image().src = 'http://fecm.cn/Api/addVul/';`

接下来我们来说说这个Api的处理方式（ThinkPHP代码）

```
public function addVul(){
    if(I('get.category','','int') == ""){
        $this->ajaxReturn(array(
            "typeMsg" =>  "error",
            "msgText" =>  "漏洞类型错误",
        ));
    }
    switch (I('get.category','','int')) {
        case '1':
            $vul['category'] = "触发alret函数";
            break;
        case '2':
            $vul['category'] = "发现不在白名单里的第三方JavaScript资源";
            break;
        default:
            $this->ajaxReturn(array(
                "typeMsg" =>  "error",
                "msgText" =>  "漏洞类型错误",
            ));
            break;
    }
    if($_SERVER['HTTP_X_FORWARDED_FOR'] === null){
        $vul['hxff_ip'] = "攻击者没有通过代理服务器访问";
    }else{
        $vul['hxff_ip'] = I('server.HTTP_X_FORWARDED_FOR'); //获取攻击者的HTTP_X_FORWARDED_FOR
    }
    if($_SERVER['HTTP_CLIENT_IP'] === null){
        $vul['hci_ip'] = "攻击者数据包头部没有HTTP_CLIENT_IP";
    }else{
        $vul['hci_ip'] = I('server.HTTP_CLIENT_IP');//获取攻击者的HTTP_CLIENT_IP
    }
    $vul['ra_ip'] = I('server.REMOTE_ADDR');    //获取攻击者的REMOTE_ADDR
    $vulcookie    = I('cookie.');   //获取攻击者的cookies
    for($i = 0;$i<count($vulcookie);$i++){
        $vul['cookies'] .= array_keys($vulcookie)[$i].'='.$vulcookie[array_keys($vulcookie)[$i]].'; ';  //拼接成方便查看的cookies格式
    }
    $vul['url']   = I('server.HTTP_REFERER');   //获取攻击者攻击成功的url
    $vul['ua']    = I('server.HTTP_USER_AGENT');    //获取攻击者的User-Agent
    $vul['time']  = date("Y-m-d");  //获取攻击者攻击的时间
    $vul['fixes'] = 0;  //默认为漏洞未修复
    $bugData = M('bugdata');    //连接fecm_bugdata数据库
    $bugData->data($vul)->add();    //添加到数据库中
}

```

因为这里是接受攻击信息，不能有管理员验证。

后台有一个数据库可视化的表格，这里我使用的Chart.js，下面是后端代码：

```
public function index(){
    $reportForm = M('bugdata'); //连接fecm_bugdata数据库
    $dateTimeLabels = [];
    $dateTimeTotal = [];
    for($i = 0;$i < 7;$i++){    //获取近7天的数据
        $time = date("Y-m-d",strtotime(-$i." day"));
        array_unshift($dateTimeLabels,$time);
        $data['time'] = array('like','%'.$time.'%');
        array_unshift($dateTimeTotal,$reportForm->where($data)->count());
    }
    $reportForm = json_encode(["Labels" => $dateTimeLabels,"Total" => $dateTimeTotal]); //转化成json格式
    $this->assign('reportForm',$reportForm)->assign('total',total());   //交给前端模块
    $this->display();   //前端页面生成
}

```

前端代码：

```
var lineChartData = {
    labels :eval({$reportForm})['Labels'],
    datasets : [
        {
            fillColor : "rgba(151,187,205,0.5)",
            strokeColor : "rgba(151,187,205,1)",
            pointColor : "rgba(151,187,205,1)",
            pointStrokeColor : "#fff",
            data : eval({$reportForm})['Total']
        }
    ]
}
var myLine = new Chart(document.getElementById("Statistics").getContext("2d")).Line(lineChartData);

```

实际的效果图：

![p5](http://drops.javaweb.org/uploads/images/3a0397ae0e50e8f67d6ae992a91e64769b3616fa.jpg)

![p6](http://drops.javaweb.org/uploads/images/45eaf44e12f237202e94071935f821633571b4f3.jpg)

![p7](http://drops.javaweb.org/uploads/images/03874f5bd09739892055e1b5889a129bd020fffa.jpg)

0x04 让我们实际测试一下
==============

* * *

代码就用0x01节的代码。我们输入`<script>alert(1)</script>`。看一下：

![p8](http://drops.javaweb.org/uploads/images/f75cde2743b3d560fd69153d8f9e1f8f3cab3681.jpg)

我们再去平台看一下：

![p9](http://drops.javaweb.org/uploads/images/86ca1986041e988234c13d24601c7f783bfa751b.jpg)

![p10](http://drops.javaweb.org/uploads/images/44764da6e0ff97ccfc2260100e67e065180064f4.jpg)

成功显示了。

0x05 检测第三方js资源是否为xss脚本
======================

* * *

这一节需要用到之前**长短短**分享的代码：

```
for(var i=0,tags=document.querySelectorAll('iframe[src],frame[src],script[src],link[rel=stylesheet],object[data],embed[src]'),tag;tag=tags[i];i++){ 
    var a = document.createElement('a'); 
    a.href = tag.src||tag.href||tag.data; 
    if(a.hostname!=location.hostname){ 
        console.warn(location.hostname+' 发现第三方资源['+tag.localName+']:'+a.href); 
    }
}

```

但是他这里只是在console里显示，没有进一步的操作，而且他这里同时检测了iframe、frame、script、link、object、embed标签，对我们来说只需要script标签就行了，于是我重写了这段代码，首先我们需要一个白名单列表，用于放置网站允许第三方加载的url地址：

```
var scriptList = [
    location.hostname,
]

```

这里只是默认的只允许当前域名加载，打击爱可以根据自己的需要添加。

然后就是获取当前网页的所有script标签：

```
var webScript = document.querySelectorAll('script[src]');

```

在把当前的地址赋值`var webHost = location.hostname;`至于为什么不放在for循环里，因为根据js优化规则，for循环里避免多次一样的赋值。

接下来就是for循环里的代码了：

```
for(var i = 0;i < webScript.length;i++){
    var a = document.createElement('a');    //建立一个新的a标签，方便取值
    a.href = webScript[i].src;  //把script里的src赋值给a标签里的href属性
    if(a.hostname != webHost){  //对比，是否为第三方资源
        for(var j = 0;j < scriptList.length;j++){
            if(a.hostname != scriptList[i]){    //判断当前的第三方资源是否在白名单里
                new Image().src = 'http://fecm.cn/Api/addVul/category/2';   //发送给FECM
            }
        }
    }
}

```

这里我做了一个测试，加载hi.baidu.com的资源：

![p11](http://drops.javaweb.org/uploads/images/7354bb2af9d065c350359effb21cc606fb3b54ae.jpg)

刷新后，打开FECM平台，看一下：

![p12](http://drops.javaweb.org/uploads/images/cc819ead8aedce99a5e8271c79c3b7211ab55a91.jpg)

![p13](http://drops.javaweb.org/uploads/images/72fd7238de6f770506d5ebbc6e30df5a8ad925e5.jpg)

0x06 结语
=======

* * *

因为穷，没有服务器和域名，也没法添加邮件自动提醒功能了。感兴趣的可以自己添加，如果后来我有钱了，我买个服务器，会添加邮件自动提醒的，第一时间会在乌云社区里发布。本来打算采用ED的on事件拦截代码的，但是发现on事件在程序里也会大量使用，索性就没有添加，如果你有思路

下载地址：[http://pan.baidu.com/s/1jGVP7Ps](http://pan.baidu.com/s/1jGVP7Ps)

使用时记得在`Application\Home\Conf\config.php`改下配置（我已经全部加了注释，即使不会thinkphp的也可以搭建）

个人代码写的没有多好，思路可能也比较烂。如果您有什么意见欢迎提出来，我会进一步修改的。