# 详解XMLHttpRequest的跨域资源共享

### 0x00 背景

* * *

在[Browser Security-同源策略、伪URL的域](http://drops.wooyun.org/papers/151)这篇文章中提到了浏览器的同源策略，其中提到了XMLHttpRequest严格遵守同源策略，非同源不可请求。但是，在实践当中，经常会出现需要跨域请求资源的情况，比较典型的例如某个子域名向负责进行用户验证的子域名请求用户信息等应用。

以往，有一种解决方案是利用JSONP进行跨域的资源请求，但这种方案存在着几点缺陷:

```
1)只能进行GET请求
2)缺乏有效的错误捕获机制。因此在XMLHttpRequest v2标准下，提出了CORS(Cross Origin Resourse-Sharing)的模型，试图保证跨域请求的安全性。

```

现在，各大主流浏览器均支持CORS模型，其中IE 8, IE 9需要使用XDomainRequest进行跨域请求。

### 0x01 基本模型

* * *

虽然说允许了XMLHttpRequest的跨域请求，但是这种许可并不是无条件的。

浏览器在进行请求时也会判断请求的合法性，验证是通过服务器的返回头来进行的，这时就涉及到了具体的请求类型，所以在标准中定义了简单跨域请求。

简单跨域请求就是满足下列条件的请求:

```
请求方法为GET或POST
请求方法中没有设置请求头(Accept, Accept-Language, Content-Language, Content-Type除外)
如果设置了Content-Type头，其值为application/x-www-form-urlencoded, multipart/form-data或 text/plain

```

验证简单跨域请求与非简单跨域请求合法性的区别就在于，验证非简单跨域请求前，浏览器向服务器发送一个OPTIONS方法的预检请求来加以判断，如果预检失败，实际请求将被丢弃。而简单跨域请求浏览器会正常发送请求，再对返回头加以判断以检查请求的合法性。在检查失败时，浏览器将会阻止脚本对返回内容的访问。

在[http://zone.wooyun.org/content/4917](http://zone.wooyun.org/content/4917)中，LZ因为设定了X-Forward-For头，所以浏览器先发送了预检请求，检查失败后丢弃了实际头，所以造成了LZ的误解。

### 0x02 请求时发送的HTTP头

* * *

简单跨域请求并不会包含下面的HTTP头。而预检请求将会发送以下HTTP头

```
Origin: 普通的HTTP请求也会带有，在CORS中专门作为Origin信息供后端比对
Access-Control-Request-Method: 接下来请求的方法，例如PUT, DELETE等等
Access-Control-Request-Headers: 自定义的头部，所有用setRequestHeader方法设置的头部都将会以逗号隔开的形式包含在这个头中

```

其他头，例如实际请求的头部，Cookie头等都将不被包含在预检请求中。

### 0x03 返回的HTTP头

* * *

浏览器主要通过返回的这些HTTP头判断请求是否合法。值得注意的一点是，预检请求通过并不代表请求一定会成功，如果预检请求时服务器返回的HTTP头使浏览器判断请求合法，从而发出了实际请求，但是实际请求的返回头中含有的访问控制头显示请求不合法时，浏览器仍会判定请求不合法，从而向脚本隐藏返回的细节。

```
Access-Control-Allow-Origin: 允许跨域访问的域，可以是一个域的列表，也可以是通配符"*"。这里要注意Origin规则只对域名有效，并不会对子目录有效。即http://foo.example/subdir/是无效的。但是不同子域名需要分开设置，这里的规则可以参照那篇同源策略
Access-Control-Allow-Credentials: 是否允许请求带有验证信息，这部分将会在下面详细解释
Access-Control-Expose-Headers: 允许脚本访问的返回头，请求成功后，脚本可以在XMLHttpRequest中访问这些头的信息(貌似webkit没有实现这个)
Access-Control-Max-Age: 缓存此次请求的秒数。在这个时间范围内，所有同类型的请求都将不再发送预检请求而是直接使用此次返回的头作为判断依据，非常有用，大幅优化请求次数
Access-Control-Allow-Methods: 允许使用的请求方法，以逗号隔开
Access-Control-Allow-Headers: 允许自定义的头部，以逗号隔开，大小写不敏感

```

无论是预检请求或是实际请求，如果在`Access-Control-Allow-Origin, Access-Control-Allow-Credentials, Access-Control-Allow-Methods, Access-Control-Allow-Headers`的检查失败，就会被视为请求失败。

### 0x04 单独谈谈Credentials

* * *

在跨域请求中，默认情况下，HTTP Authentication信息，Cookie头以及用户的SSL证书无论在预检请求中或是在实际请求都是不会被发送的。

但是，通过设置XMLHttpRequest的credentials为true，就会启用认证信息机制。

虽然简单请求还是不需要发送预检请求，但是此时判断请求是否成功需要额外判断Access-Control-Allow-Credentials，如果Access-Control-Allow-Credentials为false，请求失败。

十分需要注意的的一点就是此时Access-Control-Allow-Origin不能为通配符"*"(真是便宜了一帮偷懒的程序员)，如果Access-Control-Allow-Origin是通配符"*"的话，仍将认为请求失败

即便是失败的请求，如果返回头中有Set-Cookie的头，浏览器还是会照常设置Cookie

### 0x05 CORS中的安全隐患

* * *

最大的隐患就在于某些偷懒的程序员会将Access-Control-Allow-Origin设置为"*"从而使得这个CORS模型基本失效，但是由于Credentials模型的保护，很多网上的文章认为的信息泄露问题其实并不存在。在这里的风险其实是可以构造DDoS进行攻击。

另外就是我们会发现，虽然无法得到返回值，简单请求其实是发出的，所以POST请求是可以发出的。这时候，其实就和平常的CSRF一样了，所以并不是说保证了跨域请求限定的域就可以不做CSRF防范了。