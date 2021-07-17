# Burp Suite使用介绍（四）

0x00 Intruder Scan
------------------

* * *

发送一个你想csrf_token的请求到intruder。

### 1)Positions设置如下：

![enter image description here](http://drops.javaweb.org/uploads/images/3d4dda9da208fa1e8161c3c1fcf830004a29372e.jpg)

### 2)Options设置如下：

```
Request Engine

```

![enter image description here](http://drops.javaweb.org/uploads/images/c5f4284a5f6214179525ed077545b7a703f73115.jpg)

```
options>Grep-Extract>add

```

![enter image description here](http://drops.javaweb.org/uploads/images/68d52ec878ddc07cbd8b1475b7d023e19cb639f1.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b79ef610c20992fe44719dbad019ea553945bd8e.jpg)

### 3)payloads设置如下

![enter image description here](http://drops.javaweb.org/uploads/images/cd26b88235744f47249c745de919c217726aaede.jpg)

这里payload type设置递归(Recursive grep)，在Initial payload for first request设置一个有效的csrf_token值作为第一项

![enter image description here](http://drops.javaweb.org/uploads/images/da3ad63151f959bde0e60b7153ba98eb5430cea2.jpg)

0x01 Active Scan with sqlmap
----------------------------

* * *

其实这个结合sqlmap有两种方法，然后跟@c4bbage讨论了下,我采用的也是他那个代码，但是在注入的时候我发现在burpsuite里查看HTTP history(历史记录)里的token是没有变化的，但是还是可以注入，刚开始挺纳闷的，我以为他写的那个代码有问题，后来他说不是，在burpsuite里是看不到的，然后我也同意他说的，就是替换这个过程直接经过宏功能替换了，不会显示在历史记录里。我这里就说下第二种方法吧。第一种点这里。

### 1)首先是登录csrf_token页面，不需要拦截。然后选择Options>Sessions>Add

![enter image description here](http://drops.javaweb.org/uploads/images/f830fc13ef11602946b679af47ad31d3ff718de1.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/3b5acbe48de4f597d03dadf68e07f93c865ec608.jpg)

### 2)接着会弹出一个窗口选择Select macro>add

![enter image description here](http://drops.javaweb.org/uploads/images/459c8cabd48c6d042e03148e72a72f7809786fde.jpg)

### 3)点击add後会弹出两个页面如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/cd7d0e96b9ed6f69c596a51446925a03189bcd72.jpg)

### 4)选择2-3个页面，第一个页面是请求页面，第二个页面是post数据的时候的页面，为了便于查看我这里添加了3个页面。

![enter image description here](http://drops.javaweb.org/uploads/images/f2fad08beb9cb55e992c232505dd7cbe208a9915.jpg)

### 5)选择第二个页面点击Configure item，指定root，添加一个自定义token参数

![enter image description here](http://drops.javaweb.org/uploads/images/734ee47daa0143839c7e0d89487c626461c4e9e5.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f75a2fbd3aa30c7e7767b275da3c9e0c5c31ad79.jpg)

### 6)最后配置完可以点击Test macro看看我们配置成功了没

![enter image description here](http://drops.javaweb.org/uploads/images/99f1c761d96cae65aae4c5e856406bacdd814a8d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/77fec226b3dc494fad70f83163f7346d1eda77ed.jpg)

### 7)如果以上配置成功，再选择Scope选择应用范围

![enter image description here](http://drops.javaweb.org/uploads/images/746f7a63378392d1af5ae289b65b939327d6a0fb.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8bea8e2441ec05608287a9157d97e52c107e810c.jpg)

### 8)接着就是放到sqlmap里去跑数据咯

如果是post页面，这里是把post的数据保存到request.txt文件里，然后运行命令如下：

```
./sqlmap.py -r request.txt –proxy=http://127.0.0.1:8080

```

如果是get页面命令如下：

```
./sqlmap.py –u “www.target.com/vuln.php?id=1” –proxy=http://127.0.0.1:8080

```

![enter image description here](http://drops.javaweb.org/uploads/images/54f9e35f9c368195b35bad47a21b4954ada08bec.jpg)

0x02 Session Randomness Analysis Sequencer
------------------------------------------

* * *

请求拦截一个地址，在响应内容中如果有cookie，或者我们可以在sequencer中自定义配置token参数

![enter image description here](http://drops.javaweb.org/uploads/images/cc583ae705419f84d4aa1e6ae56960c5373b772d.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f66e6ee0122c98ebee5b48976e95df0c0f29c5d5.jpg)

然后点击Start live capture进行分析

![enter image description here](http://drops.javaweb.org/uploads/images/a04e50359b4d19f38f59c47e4b2348b9f111706d.jpg)

等分析完即可生成报告，通过报告我们可以看出token是否可以伪造。

参考资料：http://resources.infosecinstitute.com/session-randomness-analysis-burp-suite-sequencer/