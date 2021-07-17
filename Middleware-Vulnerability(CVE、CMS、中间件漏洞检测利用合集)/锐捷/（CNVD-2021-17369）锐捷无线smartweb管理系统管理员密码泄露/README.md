## （CNVD-2021-17369）锐捷无线smartweb管理系统管理员密码泄露

影响版本：
- 无线smartweb管理系统

Step1：用guest/guest登陆管理系统，登陆完后，刷新一下后台首页，看一下network中的auth字段
![](./exp.png)

Step2：解密登录管理员账号即可