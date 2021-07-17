### gopher 协议介绍

> Gopher 协议是 HTTP 协议出现之前，在 Internet 上常见且常用的一个协议。当然现在 Gopher 协议已经慢慢淡出历史。
> Gopher 协议可以做很多事情，特别是在 SSRF 中可以发挥很多重要的作用。利用此协议可以攻击内网的 FTP、Telnet、Redis、Memcache，也可以进行 GET、POST 请求。这无疑极大拓宽了 SSRF 的攻击面。
> 
> Gopher 可以模仿 POST 请求，故探测内网的时候不仅可以利用 GET 形式的 PoC（经典的 Struts2），还可以使用 POST 形式的 PoC。

#### gopher局限

* 大部分 PHP 并不会开启 fopen 的 gopher wrapper
* file_get_contents 的 gopher 协议不能 URLencode
* file_get_contents 关于 Gopher 的 302 跳转有 bug，导致利用失败
* PHP 的 curl 默认不 follow 302 跳转
* curl/libcurl 7.43 上 gopher 协议存在 bug（%00 截断）， 7.49 可用

