# Fiddler的灵活使用

0x00 前言
=======

* * *

Fiddler是一款强大的web调试工具，其基本用法网上已经有很详细的教程，这里我就不再多说了。下面只是经验之谈，利用Fiddler各种功能达到自动检测漏洞的目的。

0x01 市场需求
=========

* * *

我们在进行漏洞挖掘过程中，由于需要做大量的请求分析、大量的测试规则，且需要不断的重放修改请求进行探测，这导致消耗的精力、时间巨大。如果我们可以将请求保存下来，本地模拟请求的发送，自动修改请求，加载各种漏洞的测试规则，然后对请求的返回结果、状态进行漏洞特点的判断，那么对一些常见的sql注入、xss漏洞、文件包含等漏洞挖掘就非常的方便了。有了这样的需求，我们来看看Fiddler能否给我们提供很好的技术支持

0x02 需求分析
=========

* * *

Fiddler采用代理的方式捕获请求，能够完美的截获请求头，这样就能满足我们的一些登录会话的需求，以及厂商做了rerferer验证、或者其他请求头验证的情况。而且Fiddler很好的支持https，可保存完整的请求以及发送的数据、参数等信息方便快捷的过滤规则，能够保留我们需要的测试session,轻松过滤一些js、css、图片等不必要的请求。

![](http://drops.javaweb.org/uploads/images/823ac729411e383417e974a2952a795e45b86ca4.jpg)

![](http://drops.javaweb.org/uploads/images/9a9e56815416ddf627efae0abf691535f07139f5.jpg)

0x03 干活
=======

* * *

Fiddler虽然支持保存请求头，但是不支持一键保存。每次保存请求头时都需要点一次确认。这使得保存请求非常的不方便。哎！重点来了，看官注意了，后来查询一些资料才知道，Fiddler有一个Fiddler2 Script Editor它支持用户调用其自定义的一些函数，自行编辑脚本，非常简单易懂，位置在rules->Customize rule下。

![](http://drops.javaweb.org/uploads/images/33177d37f4fa739845d0d8161833fc357aed3aaf.jpg)

起初的想法是这样的：在脚本编辑器中有个OnBeforeRequest函数，在该函数下编辑的代码，代表可以在request触发前对request进行处理。

我们先在ClassHandlers下定义一个菜单，用于控制开启插件的开关：

![](http://drops.javaweb.org/uploads/images/5e765f9e99266ac4a2fbdbc73bfcc1a0345342e9.jpg)

在OnBeforeRequest函数下增加如下代码：

```
if(nowsave){
            oSession.SaveRequest(""+oSession.id+"_Request.txt",false);
            
        }

```

意思就是当捕获到session时就将请求request保存到指定目录

![](http://drops.javaweb.org/uploads/images/eceb12acea74504a47535b0bc79b1f0229c46f05.jpg)

来看看效果，在rule下会出现我们添加的菜单，选中它后就开始时时的存储request到本地了：

![](http://drops.javaweb.org/uploads/images/609baa4949e7308f6fc4021c0433ab0040759f9b.jpg)

保存本地的request：

![](http://drops.javaweb.org/uploads/images/8e8d96e45f3e688c318ba7249e1a3ee2afa07dfd.jpg)

post数据，参数、数据也都在其中，

![](http://drops.javaweb.org/uploads/images/ab350ca4a07bea1017947932c64fb33119447dcc.jpg)

能够时时的存储request，再配合自己写的一些对request进行模拟请求探索漏洞的工具，每天随便看看网站，逛逛各大厂商就能挖洞！妈妈再也不用担心我会和漏洞url擦肩而过了！是不是特别给咱妈省心？

然而这还不能满足我们的需求，因为在工作中我们需要对一些特定的请求进行过滤后再进行测试，比如一些请求有插入数据的功能列如评论，如果这种请求进行自动化探测的话，会带来大量的垃圾数据，往往测试时需要过滤掉。另外时时存储会保存大量request,全部都进行测试效率会降低。利用fiddler的过滤规则，我们已经能够保留我们希望测试的request,如果能有一个命令，能一键保存我们过滤留下的session，那效率将会大大提高。然而fiddler并没有这样的功能，就像上边说到的，保存request每次都会弹框点击确认才行。我们再来看看Fiddler 2 Script Edit是否能解决这个问题。果然在OnExecAction函数下可以让我们自定义命令，输入命令后，执行我们想要的代码，直接上代码：

```
case "save":
            var Sessions=UI.GetAllSessions();
                for (var i=0;i<Sessions.Length;i++)
                {
                    Sessions[i].SaveRequest("你的目录"+i.toString()+"_Request.txt",false);
                }
            return true;

```

![](http://drops.javaweb.org/uploads/images/bdc0488bec7cebc073fa08612900bf53b5039875.jpg)

增加一个case，循环保存即可。虽然上面的代码很简单，但是我却分析学习测试了好长时间，包括哪些fiddler的函数可用，用哪个类等等，这段过程就比较曲折了，就不多说了。 来看看效果,打开fiddler,在左下角输入命令save

![](http://drops.javaweb.org/uploads/images/5fb0ff5ab6c8cdd563aaa3f3bd486e8908787bad.jpg)

request被一键保存了：

![](http://drops.javaweb.org/uploads/images/0b30a36b692aaa364be2fc2e74b6e30436341833.jpg)

0x04 总结
=======

* * *

好了request保存以后，对request的分析，就要靠个人如何去写漏洞识别的工具了，不同的人有不同的思路、想法，但是都离不开原始request，这些就不是本文要讲述的了。希望能给大家一点点帮助。