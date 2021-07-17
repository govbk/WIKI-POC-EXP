# MyBB 后台代码执行漏洞

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

**漏洞分析**

首先全局搜索inclued函数，在\mybb\admin\modules\config\languages.php页面的432行发现include函数：`@include $editfile;`

![](images/15891938340279.png)


该函数包含editfile文件，进行查看该文件来源，可以看到418行该文件由folder文件夹和file文件拼接，其中408行看到file文件由post请求提交，接下来查看folder文件夹来源

![](images/15891938398813.png)


通过该文件84行看到foler文件夹为`MYBB_ROOT."inc/languages/".$editlang."/"`，接下来查看editlang变量，通过89行看到判断该文件名后缀为php的文件是否存在，然后查看该文件下辖的php文件只有english文件，猜测editlang为english，稍后验证，该变量会通过post请求输入

![](images/15891938521341.png)


现在文件的目录结构分析完毕，接下来查看该漏洞页面的接口位置：由于该文件目录为\mybb\admin\modules\config\languages.php，因此，入口为config模板的language方法中，其中控制器为edit，从369行可以看到，同时408行看到post请求中输入file文件

![](images/15891938591053.png)


![](images/15891938619438.png)


因此我们查看该页面uri大概为以下样子：

/mybb/admin/index.php?module=config-languages&action=edit

现在进行分析，该目录为inc/languages/english，因此我们需要向该文件夹下进行上传一个图片，因此我们需要将上传文件目录修改为该文件夹，现在分析如何修改该文件夹：

通过对头像上传文件夹进行跟踪，发现在function_upload.php的222行，该文件夹由全局变量settings控制

![](images/15891938753032.png)


对该变量进行跟踪，`$mybb->settings['avataruploadpath']`，发现对`$mybb->settings['uploadspath']`变量的控制就需要对文件进行修改进行查询，针对关键函数进行搜索：`$db->update_query("settings"`发现在\mybb\admin\modules\config\settings.php文件下1101行：

![](images/15891938987094.png)


通过value和name变量进行更新，其中value变量是从post请求中的upsetting数组中进行获取其name变量的值：

![](images/15891939060804.png)


我们跟踪avataruploadpath变量，进行搜索，有1042行定义数组，而avataruploadpath为数组中的参数，同时也有post请求的upsetting数组进行输入:

![](images/15891939124988.png)


现在寻找数据传入方式，发现action方法为change，请求方式为post：

![](images/15891939185866.png)


通过该页面17行，发现页面在index页面下调用的模板为config下的setting模板：

![](images/15891939272979.png)


因此我们构建的页面就可以为这样，从该页面进行传入数据


```bash
http://url/mybb/admin/index.php?module=config-settings&action=change
```

### 漏洞复现

通过上传头像（上传的头像图片小于1kb，因为网站会进行压缩，将php脚本破坏，因此制作木马要保证大小小于1kb，已做好的图片放在了附件中）

通过修改setting中的avataruploadpath值为./inc/languages/english

修改avataruploadpath值为./inc/languages/English，查看所有的settins变量：

链接：`http://url/mybb/admin/index.php?module=config-settings&action=change`

![](images/15891940378338.png)


找到**Avatar Upload Path**并修改./inc/languages/english

![](images/15891940461340.png)


通过上传头像图片：

`http://url/mybb/admin/index.php?module=user-users&action=edit&uid=1#tab_avatar`

勾选去掉当前头像

![](images/15891940619698.png)


点击save user

发现文件已经上传成功，并且avataruploadpath也修改成功，下面进行包含操作，访问url：`http://url/mybb/admin/index.php?module=config-languages&action=edit&lang=english`

Config模块下的languages下，

![](images/15891940800992.png)


因为该页面包含需要post请求，并且控制器入口为edit，因此我们进行edit，随便点一个php文件进行编辑：

![](images/15891940869557.png)


什么都不用更改，点击save languagefile

![](images/15891940934139.png)


bp抓包：

![](images/15891940993722.png)


将file变量改为我们的头像图片文件名，名字可以从这里看到

![](images/15891941054879.png)


通过邮件查看图片链接：

右键复制链接打开可以看到文件名为avatar_1.jpg

![](images/15891941155584.png)


然后放包发现该代码执行成功，phpinfo()

![](images/15891941222660.png)


测试一句话木马`eval($_GET['a']);`

![](images/15891941318679.png)


测试成功

文件上传后，包含后图像文件会损坏，所以需要执行完命令，创建一个新的shell文件，然后通过poc进行验证shell文件存在

写一句话木马到网站，请使用muma.jpg,然后包含，会在/mybb/admin生成shell.php,一句话木马密码为a

![](images/15891941463976.png)


**附件下载：**

[Mybb_pic](file/Mybb_pic.7z)

**参考链接**

https://xz.aliyun.com/t/7213#toc-2