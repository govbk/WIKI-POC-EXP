# ngx_lua_waf适应多站点情况的研究

0x00 前言
=======

* * *

在前一篇文章《基于ngx_lua模块的waf开发实践》（链接为：http://drops.wooyun.org/tips/5136）中，提出了后续的三个研究方向，其中一个就是在多站点下waf分离的研究，现在将这方面的研究跟大家分享一下。

0x01 问题分析
=========

* * *

最初的思路是直接在nginx中配置多个站点，然后在每个站点中都加载一份waf代码。

流程图如下：

![enter image description here](http://drops.javaweb.org/uploads/images/1cfb417b666447edf255ebf517cd924dce35f101.jpg)

这样做的情况下，如果站点比较多，就会导致nginx配置比较乱，而且当nginx配置多站点的情况下，会出现一些问题。我这里就借用安全宝的一份对比表来说明。

![enter image description here](http://drops.javaweb.org/uploads/images/32b47ba67787b9899891aed307ebeab4541da7f2.jpg)

当然，在实际应用中，一般并不会应用到这么多站点，这里只是做个说明。但是上面说的问题确实是存在的。

0x02 需求分析
=========

* * *

需求1：在nginx中能够只监听1个站点，能够实现所有站点转发

需求2：各个站点可以独立进行控制，包括waf开发，日志开关以及使用的规则

0x03 需求实现
=========

* * *

针对需求1，流程图如下：

![enter image description here](http://drops.javaweb.org/uploads/images/4f059dbc45065895860f49a1e56eadafa97223bc.jpg)

nginx.conf关键代码：

![enter image description here](http://drops.javaweb.org/uploads/images/ffb9b332c7a4727382a06ded7222a87d292b6869.jpg)

waf.lua关键代码：

![enter image description here](http://drops.javaweb.org/uploads/images/9ea626a20494799c3a7f985c2e06a47747f61f0f.jpg)

访问过程分析：

当一个用户访问到waf服务器时，首先获取host参数，根据网址配置里查询到对应的upstream，给预先定义的变量$upstream，从而达到正确转发的目的。

而且后期还可以将网站信息存储在数据库，当第一次访问的时候再加载到内存，达到动态加载的目的。

针对需求2：

网址配置代码如下：

![enter image description here](http://drops.javaweb.org/uploads/images/076ede42eec3e031ef3d77cb97ab09b325a0ceef.jpg)

规则配置代码如下：

![enter image description here](http://drops.javaweb.org/uploads/images/7ef51caa0a8778d3ce158f2846008c104a06bca7.jpg)

这样可以给每一个网站单独配置规则集，并在网址配置里面注明即可。

在网址配置里面可以注明每个网站的waf开关，是否记录日志，以及哪个规则。

在规则配置中可以指定规则的放行或阻拦，日志的开启或关闭。

0x04 后续需解决问题
============

* * *

*   此种方式是一种针对对站点的很好的思路，但此方式还是依赖在nginx中配置各站点的upstream，后续考虑直接在lua代码中配置。
    
*   针对多站点的情况，最好能够结合数据库，将网站信息都存储在数据库中，实现动态加载。
    
*   针对nginx每次变更需要reload，后期考虑写一个控制页面来动态的进行控制，比如规则的的开启或者关闭针对waf各种状态的展示以及日志的处理与展示
    

0x05 总结
=======

* * *

此文只是提供一种思路，当然也不是我想出来的，也是参考各种资料，最主要的是针对现在各种大流量大并发的网络环境下，很多公司包括我们公司有这样一种需求，所以分享出来，希望和更多的人交流，学习。