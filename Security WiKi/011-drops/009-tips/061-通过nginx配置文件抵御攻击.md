# 通过nginx配置文件抵御攻击

0x00 前言
-------

* * *

大家好，我们是OpenCDN团队的Twwy。这次我们来讲讲如何通过简单的配置文件来实现nginx防御攻击的效果。

其实很多时候，各种防攻击的思路我们都明白，比如限制IP啊，过滤攻击字符串啊，识别攻击指纹啦。可是要如何去实现它呢？用守护脚本吗？用PHP在外面包一层过滤？还是直接加防火墙吗？这些都是防御手段。不过本文将要介绍的是直接通过nginx的普通模块和配置文件的组合来达到一定的防御效果。

0x01 验证浏览器行为
------------

* * *

### 简易版

我们先来做个比喻。

> 社区在搞福利，在广场上给大家派发红包。而坏人派了一批人形的机器人(没有语言模块)来冒领红包，聪明工作人员需要想出办法来防止红包被冒领。
> 
> 于是工作人员在发红包之前，会给领取者一张纸，上面写着“红包拿来”，如果那人能念出纸上的字，那么就是人，给红包，如果你不能念出来，那么请自觉。于是机器人便被识破，灰溜溜地回来了。

是的，在这个比喻中，人就是浏览器，机器人就是攻击器，我们可以通过鉴别cookie功能(念纸上的字)的方式来鉴别他们。下面就是nginx的配置文件写法。

```
if ($cookie_say != "hbnl"){
    add_header Set-Cookie "say=hbnl";
    rewrite .* "$scheme://$host$uri" redirect;
}

```

让我们看下这几行的意思，当cookie中say为空时，给一个设置cookie say为hbnl的302重定向包，如果访问者能够在第二个包中携带上cookie值，那么就能正常访问网站了，如果不能的话，那他永远活在了302中。你也可以测试一下，用CC攻击器或者webbench或者直接curl发包做测试，他们都活在了302世界中。

当然，这么简单就能防住了？当然没有那么简单。

### 增强版

仔细的你一定会发现配置文件这样写还是有缺陷。如果攻击者设置cookie为say=hbnl（CC攻击器上就可以这么设置），那么这个防御就形同虚设了。我们继续拿刚刚那个比喻来说明问题。

> 坏人发现这个规律后，给每个机器人安上了扬声器，一直重复着“红包拿来，红包拿来”，浩浩荡荡地又来领红包了。
> 
> 这时，工作人员的对策是这样做的，要求领取者出示有自己名字的户口本，并且念出自己的名字，“我是xxx，红包拿来”。于是一群只会嗡嗡叫着“红包拿来”的机器人又被撵回去了。
> 
> 当然，为了配合说明问题，每个机器人是有户口本的，被赶回去的原因是不会念自己的名字，虽然这个有点荒诞，唉。

然后，我们来看下这种方式的配置文件写法

```
if ($cookie_say != "hbnl$remote_addr"){
    add_header Set-Cookie "say=hbnl$remote_addr";
    rewrite .* "$scheme://$host$uri" redirect;
}

```

这样的写法和前面的区别是，不同IP的请求cookie值是不一样的，比如IP是1.2.3.4，那么需要设置的cookie是say=hbnl1.2.3.4。于是攻击者便无法通过设置一样的cookie(比如CC攻击器)来绕过这种限制。你可以继续用CC攻击器来测试下，你会发现CC攻击器打出的流量已经全部进入302世界中。

不过大家也能感觉到，这似乎也不是一个万全之计，因为攻击者如果研究了网站的机制之后，总有办法测出并预先伪造cookie值的设置方法。因为我们做差异化的数据源正是他们本身的一些信息（IP、user agent等）。攻击者花点时间也是可以做出专门针对网站的攻击脚本的。

### 完美版

那么要如何根据他们自身的信息得出他们又得出他们算不出的数值？

我想，聪明的你一定已经猜到了，用salt加散列。比如md5("opencdn$remote_addr")，虽然攻击者知道可以自己IP，但是他无法得知如何用他的IP来计算出这个散列，因为他是逆不出这个散列的。当然，如果你不放心的话，怕cmd5.com万一能查出来的话，可以加一些特殊字符，然后多散几次。

很可惜，nginx默认是无法进行字符串散列的，于是我们借助nginx_lua模块来进行实现。

```
rewrite_by_lua '
    local say = ngx.md5("opencdn" .. ngx.var.remote_addr)
    if (ngx.var.cookie_say ~= say) then
        ngx.header["Set-Cookie"] = "say=" .. say
        return ngx.redirect(ngx.var.scheme .. "://" .. ngx.var.host .. ngx.var.uri)
    end
';

```

通过这样的配置，攻击者便无法事先计算这个cookie中的say值，于是攻击流量(代理型CC和低级发包型CC)便在302地狱无法自拔了。

大家可以看到，除了借用了md5这个函数外，其他的逻辑和上面的写法是一模一样的。因此如果可以的话，你完全可以安装一个nginx的计算散列的第三方模块来完成，可能效率会更高一些。

这段配置是可以被放在任意的location里面，如果你的网站有对外提供API功能的话，建议API一定不能加入这段，因为API的调用也是没有浏览器行为的，会被当做攻击流量处理。并且，有些弱一点爬虫也会陷在302之中，这个需要注意。

同时，如果你觉得set-cookie这个动作似乎攻击者也有可能通过解析字符串模拟出来的话，你可以把上述的通过header来设置cookie的操作，变成通过高端大气的js完成，发回一个含有doument.cookie=...的文本即可。

那么，攻击是不是完全被挡住了呢？只能说那些低级的攻击已经被挡住而来，如果攻击者必须花很大代价给每个攻击器加上webkit模块来解析js和执行set-cookie才行，那么他也是可以逃脱302地狱的，在nginx看来，确实攻击流量和普通浏览流量是一样的。那么如何防御呢？下节会告诉你答案。

0x02 请求频率限制
-----------

* * *

不得不说，很多防CC的措施是直接在请求频率上做限制来实现的，但是，很多都存在着一定的问题。

那么是哪些问题呢？

首先，如果通过IP来限制请求频率，容易导致一些误杀，比如我一个地方出口IP就那么几个，而访问者一多的话，请求频率很容易到上限，那么那个地方的用户就都访问不了你的网站了。

于是你会说，我用SESSION来限制就有这个问题了。嗯，你的SESSION为攻击者敞开了一道大门。为什么呢？看了上文的你可能已经大致知道了，因为就像那个“红包拿来”的扬声器一样，很多语言或者框架中的SESSION是能够伪造的。以PHP为例，你可以在浏览器中的cookie看到PHPSESSIONID，这个ID不同的话，session也就不同了，然后如果你杜撰一个PHPSESSIONID过去的话，你会发现，服务器也认可了这个ID，为这个ID初始化了一个会话。那么，攻击者只需要每次发完包就构造一个新的SESSIONID就可以很轻松地躲过这种在session上的请求次数限制。

那么我们要如何来做这个请求频率的限制呢？

首先，我们先要一个攻击者无法杜撰的sessionID，一种方式是用个池子记录下每次给出的ID，然后在请求来的时候进行查询，如果没有的话，就拒绝请求。这种方式我们不推荐，首先一个网站已经有了session池，这样再做个无疑有些浪费，而且还需要进行池中的遍历比较查询，太消耗性能。我们希望的是一种可以无状态性的sessionID，可以吗？可以的。

```
rewrite_by_lua '

    local random = ngx.var.cookie_random

    if(random == nil) then
        random = math.random(999999)
    end

    local token = ngx.md5("opencdn" .. ngx.var.remote_addr .. random)
    if (ngx.var.cookie_token ~= token) then
        ngx.header["Set-Cookie"] = {"token=" .. token, "random=" .. random}
        return ngx.redirect(ngx.var.scheme .. "://" .. ngx.var.host .. ngx.var.uri)
    end

';

```

大家是不是觉得好像有些眼熟？是的，这个就是上节的完美版的配置再加个随机数，为的是让同一个IP的用户也能有不同的token。同样的，只要有nginx的第三方模块提供散列和随机数功能，这个配置也可以不用lua直接用纯配置文件完成。

有了这个token之后，相当于每个访客有一个无法伪造的并且独一无二的token，这种情况下，进行请求限制才有意义。

由于有了token做铺垫，我们可以不做什么白名单、黑名单，直接通过limit模块来完成。

```
http{
    ...
    limit_req_zone $cookie_token zone=session_limit:3m rate=1r/s;
}

```

然后我们只需要在上面的token配置后面中加入

```
limit_req zone=session_limit burst=5;

```

于是，又是两行配置便让nginx在session层解决了请求频率的限制。不过似乎还是有缺陷，因为攻击者可以通过一直获取token来突破请求频率限制，如果能限制一个IP获取token的频率就更完美了。可以做到吗？可以。

```
http{
    ...
    limit_req_zone $cookie_token zone=session_limit:3m rate=1r/s;
    limit_req_zone $binary_remote_addr $uri zone=auth_limit:3m rate=1r/m;
}

```

  

```
location /{

    limit_req zone=session_limit burst=5;

    rewrite_by_lua '
        local random = ngx.var.cookie_random
        if (random == nil) then
            return ngx.redirect("/auth?url=" .. ngx.var.request_uri)
        end
        local token = ngx.md5("opencdn" .. ngx.var.remote_addr .. random)
        if (ngx.var.cookie_token ~= token) then
            return ngx.redirect("/auth?url=".. ngx.var.request_uri)
        end
    ';

}

location /auth {
        limit_req zone=auth_limit burst=1;

        if ($arg_url = "") {
            return 403;
        }

        access_by_lua '
            local random = math.random(9999)
            local token = ngx.md5("opencdn" .. ngx.var.remote_addr .. random)
            if (ngx.var.cookie_token ~= token) then
                ngx.header["Set-Cookie"] = {"token=" .. token, "random=" .. random}
                return ngx.redirect(ngx.var.arg_url)
            end
        ';
}

```

我想大家也应该已经猜到，这段配置文件的原理就是：把本来的发token的功能分离到一个auth页面，然后用limit对这个auth页面进行频率限制即可。这边的频率是1个IP每分钟授权1个token。当然，这个数量可以根据业务需要进行调整。

需要注意的是，这个auth部分我lua采用的是access_by_lua，原因在于limit模块是在rewrite阶段后执行的，如果在rewrite阶段302的话，limit将会失效。因此，这段lua配置我不能保证可以用原生的配置文件实现，因为不知道如何用配置文件在rewrite阶段后进行302跳转，也求大牛能够指点一下啊。

当然，你如果还不满足于这种限制的话，想要做到某个IP如果一天到达上限超过几次之后就直接封IP的话，也是可以的，你可以用类似的思路再做个错误页面，然后到达上限之后不返回503而是跳转到那个错误页面，然后错误页面也做个请求次数限制，比如每天只能访问100次，那么当超过报错超过100次(请求错误页面100次)之后，那天这个IP就不能再访问这个网站了。

于是，通过这些配置我们便实现了一个网站访问频率限制。不过，这样的配置也不是说可以完全防止了攻击，只能说让攻击者的成本变高，让网站的扛攻击能力变强，当然，前提是nginx能够扛得住这些流量，然后带宽不被堵死。如果你家门被堵了，你还想开门营业，那真心没有办法了。

然后，做完流量上的防护，让我们来看看对于扫描器之类的攻击的防御。

0x03 防扫描
--------

* * *

[ngx_lua_waf模块](https://github.com/loveshell/ngx_lua_waf)

这个是一个不错的waf模块，这块我们也就不再重复造轮子了。可以直接用这个模块来做防护，当然也完全可以再配合limit模块，用上文的思路来做到一个封IP或者封session的效果。

0x04 总结
-------

* * *

本文旨在达到抛砖引玉的作用，我们并不希望你直接单纯的复制我们的这些例子中的配置，而是希望根据你的自身业务需要，写出适合自身站点的配置文件。