# 基于ngx_lua模块的waf开发实践

0x00 常见WAF简单分析
==============

* * *

WAF主要分为硬件WAF和软件防火墙，硬件WAF如绿盟的NSFOCUS Web Application Firewall，软件防火墙比较有名的是ModSecurity，再就是代码级别的ngx_lua_waf。下面谈谈个人对几款防火墙的理解：

硬件WAF个人觉得只适合在那种访问量较少的网站，比如政府网站，公司的介绍网站等等。硬件WAF的的优势在于规则有专门的安全公司维护，管理方便，但也存在一个致命的弱点，使用传统的方式来解包到应用层对性能的需求较高，而且当访问量很大的时候延时比较大，这样在高并发访问的情况下要使用硬件WAF就只能使用很多台WAF了，这样成本就非常高了；还有一个在接触过程中发现的问题，就是硬件WAF的规则虽然多而且有人维护，但是一般公司很难敢直接开启阻难，很多都是只记录，并不能阻难，这样WAF的意义就变得小多了。

ModSecurity在网上的评价都是很高的，性能高，规则全。最开始我研究的也是这款WAF，但是在实际使用过程中发现问题，就是在高并发的情况下，运行一段时间，会出现内存飙升，而且不下来的问题。这个问题再ModSecurity的讨论论坛上面也发现了有人提出这样的问题，但一直未解决（https://github.com/SpiderLabs/ModSecurity/issues/785）。针对于规则全的优势，一般使用者也不敢直接开启所有的规则拦截，毕竟每个公司的业务不同，规则也不可能直接套用。

基于高性能，低成本的想法，发现了@loveshell开发的ngx_lua_waf，经过实际使用下来，确实性能极好，由于LUA语言的性能是接近于C的，而且ngx_lua_module本身就是基于为nginx开发的高性能的模块。安全宝的云 WAF，以及cloudflare的新waf也是基于此模块使用LUA开发的。结合ModSecurity的思路，参考@loveshell的ngx_lua_waf来开发适合自己用的WAF，其中使用了很多@loveshell的函数，再此也表示感谢。

0x01 WAF框架设计
============

* * *

WAF开发过程中的主要方向为：

*   主引擎的开发，主要关注主引擎的性能和容错能力
*   规则的开发，主要关注规则的全面可靠，防勿拦截以及防绕过
*   整体方案能够适应多站点，高可用性的环境

WAF的主要功能为：

*   ip黑白名单
*   url黑白名单
*   useragent黑白名单
*   referer黑白名单
*   常见web漏洞防护，如xss，sql注入等
*   cc攻击防护
*   扫描器简单防护
*   其他你想要的功能

WAF的总体检测思路：

*   当用户访问到nginx时，waf首先获取用户的ip，uri，referer，useragent，，cookie，args，post，method，header信息。
*   将获取到的信息依次传给上述功能的函数，如ip规则，在ip规则中，循环到所有的ip规则，如果匹配到ip则根据规则的处理方式来进行处理，匹配到之后不继续匹配后续规则。
*   需要开启的功能依次在主函数中调用即可，顺序也可根据实际场景来确定最合适的顺序。

图示如下：

![enter image description here](http://drops.javaweb.org/uploads/images/bfc479de023d9e04659dccd72a19d45711e73bde.jpg)

0x02 规则格式分析
===========

* * *

规则说明：

比如规则：{"rule00001","rules","args|post|cookie",[[../]],"deny","logon"},

rule00001：规则编号，随意写

rules：规则名称，如xssrules，随意写

args|post|cookie|header：检测位置，|表示或，args，post，cookie，header可多选

../：匹配的正则表达式，标准PCRE正则

deny：处理方式，可选deny ，allow

logon：日志记录与否，可选logon，logoff

0x03 cc攻击防护代码示例
===============

* * *

```
--在nginx.conf的HTTP中加入
--lua_shared_dict limit 50m; 根据主机内存调合适的值
--lua_shared_dict iplimit 20m;
--lua_shared_dict blockiplimit 5m;
-------------------------------------------------------------
CCDeny="on"   --cc攻击开关
CCrate="60/60"--基于url的计数 次/秒
ipCCrate="600/60"--基于ip的计数 次/秒
-------------------------------------------------
ccdenyrules={"ccdeny1","ccdeny","","","","logon"}
function gethost()
    host = ngx.var.host
    if host == nil or type(host) ~= "string" then
        math.randomseed(os.time())
        host = "nohost"..math.random()
    end
    return host
end

function denycc(clientdata)
    if CCDeny=="on" then
        local uri=clientdata[2]
        local host = gethost()
        CCcount=tonumber(string.match(CCrate,'(.*)/'))
        CCseconds=tonumber(string.match(CCrate,'/(.*)'))
        ipCCcount=tonumber(string.match(ipCCrate,'(.*)/'))
        ipCCseconds=tonumber(string.match(ipCCrate,'/(.*)'))
        local token = clientdata[1]..host..uri
        local clientip = clientdata[1]..host
        local limit = ngx.shared.limit
        local iplimit = ngx.shared.iplimit
        local blockiplimit = ngx.shared.blockiplimit
        local req,_=limit:get(token)
        local ipreq,_=iplimit:get(clientip)
        local blockipreq,_=blockiplimit:get(clientip)
        if blockipreq or ipreq then
            if blockipreq or req then
                if blockipreq or req >= CCcount or ipreq >= ipCCcount  then
                    log(ccdenyrules,clientdata)
                    blockiplimit:set(clientip,1,300)
                    ngx.exit(403)
                    return true
                else
                    limit:incr(token,1)
                    iplimit:incr(clientip,1)
                end
            else
                limit:set(token,1,CCseconds)
            end
        else
            iplimit:set(clientip,1,ipCCseconds)
        end
    end
    return false
end

```

0x04 优势举例
=========

* * *

可以很灵活的实现复杂的控制

比如我在我的个人网站上面就使用了这样一个功能，后台页面需要特定useragent才能访问。

代码如下：

```
--特定页面容许特定useragent可访问
function houtai(clientdata)
    if stringmatch(clientdata[2],"wp-admin") then
        if stringmatch(clientdata[4],"hahahaha") then
            return
        else
            ngx.exit(403)
            return
        end
    else
        return
    end
end

```

可以测试http://www.zhangsan.me/wp-admin/

只有在特定的useragent才可以访问此页面，否则报403错误。

0x05 源码下载及使用
============

* * *

源码下载地址为：http://pan.baidu.com/s/18QQya

环境搭建就参考：http://wiki.nginx.org/HttpLuaModule#Installation

waf使用主要就是配置config.lua

SecRuleEngine = "on" attacklog = "on" logpath = "/home/waflog/"

分别为引擎是否开启 是否记录日志 日志的存储路径 日志的存储路径需要给予nginx运行用户的读写权限

0x06 后续研究方向
===========

* * *

*   1.根据ModSecurity规则提取一份较适应自己用的规则
*   2.根据最新出现的漏洞维护规则
*   3.在多个站点的情况下，如果在站点变动，规则变动的时候，不影响其他站点，实现高可用性。

写的很简单，大牛勿喷，希望大家多提建议。

0x07 参考资料
=========

* * *

```
1. https://github.com/loveshell/ngx_lua_waf
2. http://wiki.nginx.org/HttpLuaModule
3. http://www.freebuf.com/tools/54221.html
……
```