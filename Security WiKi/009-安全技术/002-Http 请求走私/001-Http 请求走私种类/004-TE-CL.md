### TE-CL

当收到存在两个请求头的请求包时，前端服务器处理Transfer-Encoding这一请求，而后端服务器只对Content-Length请求头。

**实验地址**：https://portswigger.net/web-security/request-smuggling/lab-basic-te-cl

**实验描述**：

本实验涉及一个前端和后端服务器，两个服务器以不同的方式处理重复的HTTP请求标头。前端服务器拒绝未使用GET或POST方法的请求。

要解决此问题，请向后端服务器走私一个请求，以便后端服务器处理的下一个请求似乎使用GPOST方法。

**实验过程**：

![](images/security_wiki/15905002082932.jpg)


