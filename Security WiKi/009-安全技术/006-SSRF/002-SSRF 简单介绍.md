# SSRF 简单介绍

## 关于SSRF

服务端请求伪造，用户通过WEB访问/上传/发出请求，绕过服务器防火墙，获取服务器及其内网信息。SSRF可以说是一个媒介，结合服务器中的服务，常常可以形成一条完整的攻击链。

## 产生条件

由于服务端提供了从其他服务器应用获取数据的功能且没有对用户可控的目标地址做过虑与限制。

在PHP中的curl()，file_get_contents()，fsockopen()等函数。

注：file_get_contents 情况使用 gopher 协议不能 URLencode

## 利用方式

> 演示环境为ssrf-lab，后端用curl实现

### 总述

1. 可以对外网服务器所在内网/本地进行端口扫描，获取一些服务的banner信息。
2. 攻击内网web应用（通过get传参就可以实现的攻击，如：st2,sqli等）。
3. 利用file协议读取本地文件。
4. 攻击fastcgi 反弹shell。
5. 攻击redis、mysql等。
6. 攻击运行在内网或本地的应用程序（比如溢出）

