# 第五季极客大挑战writeup

0x01 misc
---------

* * *

**too young too simple**

一个叫flag.bmp的文件，但是无法打开。文件头42 4D确实是bmp文件的头，但是文件尾`49 45 4E 44 AE 42 60 82`却是png文件的尾。

![enter image description here](http://drops.javaweb.org/uploads/images/856535a2cc33a9ccdabbb69272c5368ded6b67df.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/8ef5cf9262a3c928d40e6d3fbb6edb214abe4e86.jpg)

另外文件头中的IHDR也能确信这是一个png图片。将文件头的`42 4D E3 BF 22 00 00 00`修改为png头`89 50 4E 47 0D 0A 1A 0A`，顺利打开得到一张图片。

![enter image description here](http://drops.javaweb.org/uploads/images/448a78fe5588df47e7526b2c56edff374dc2fdbf.jpg)

图上是appleu0大神的blog地址，后面的提示意味不明。搜了下`weichuncai`并访问blog才知道这是blog上的动漫人物。与之聊天输入flag得到Flag。Flag貌似是海贼王里的。大神果然是十足的动漫控啊！

![enter image description here](http://drops.javaweb.org/uploads/images/6e5b851e09354b623ecce8902986aca94e5b96dd.jpg)

**你喜不喜欢萌萌哒的姐姐**

一张loli的图，在jpg尾FF D9后还有很多可显字符。

![enter image description here](http://drops.javaweb.org/uploads/images/10b8610767f8de81fe8f5a855500bc9eb76a2986.jpg)

全部复制出来，看编码应该是base64，放到hackbar里base64decode一下，却得到很多不可显字符，但是发现了JFIF标识，应该是base64encode了一张图片得到的。

![enter image description here](http://drops.javaweb.org/uploads/images/560f0aaca5c938abebb1f6f0acf28711d61c4008.jpg)

下面是解码脚本。

```
import base64

f = open('1.jpg', 'rb')
pic = f.read()
index = pic.find('\xff\xd9')
flag = pic[index + 5:]
f.close()

f1 = open('flag.jpg', 'w')
f1.write(base64.decodestring(flag))
f1.close()

```

运行得到flag.jpg。

![enter image description here](http://drops.javaweb.org/uploads/images/2d352231c3f79d299df5766bc008535cb8d95e04.jpg)

**开胃小菜**

题目要求修改参赛口号为Hacked by white god!。

在个人信息页面`http://hack.myclover.org/team_info`的HTML注释中发现提示：

![enter image description here](http://drops.javaweb.org/uploads/images/2770b95e09848e49e60437ee0b62e661ee73bc35.jpg)

更新口号翻译为upvoice，简直不忍直视，不能再low。 访问`http://hack.myclover.org/team_info/upvoice?voice=Hacked+by+white+god!`得到Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/2472c2b856759a0fe69bbb0285b27bc0824066c9.jpg)

**白神的假期**

一张jpg图片，在文件尾FF D9后还有不少内容，而且是rar文件头`52 61 72 21`。

![enter image description here](http://drops.javaweb.org/uploads/images/fc70a5417e7dafc5e5ebeba76393a8f07a3940df.jpg)

复制出剩下的部分成rar文件解压得到flag.txt。

![enter image description here](http://drops.javaweb.org/uploads/images/989a5c96fd4a7127629da41bc68c838173bcd20e.jpg)

在base64decode一下就得到Flag：`KEY:SYC{Y34h!Thi5_15_th3_jp9_r4r_K3Y}`

**reg**

![enter image description here](http://drops.javaweb.org/uploads/images/9d3a804dcf43c7637838bbc844596ba0eadde9d8.jpg)

看到com啥的基本上就知道这肯定是个url了，再加上开始部分twi以及com之前的部分是从syclover中取，就能猜出是twitter.com，追加上后面的asdlalalalala得到url：`twitter.com/asdlalalalala`，访问url得到Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/7aeb7d092d3709af00ed1713ed7f1b0f0a317916.jpg)

**bilibili**

最坑的题没有之一。出题者丧心病狂居然要求通过bilibili的会员晋级考试，还得至少80分。好不容易通过修改HTML代码弄出了一张通过图，竟然还要关注出题者。无奈只好仔细百度做题，还好这时候只需要60就晋级成功，出题者也无法分辨我到底是60还是80。  

0x02 pentest
------------

* * *

**HTTP Base1**

Flag在HTTP response header中。

![enter image description here](http://drops.javaweb.org/uploads/images/226e9af315dc093cc77099fd36661e3107d23e90.jpg)

**HTTP Base2**

![enter image description here](http://drops.javaweb.org/uploads/images/7cab713befb6409b07371e16b5d2adace714a274.jpg)

题目要求必须本机访问，开始以为加上X-Forwarder-For: 127.0.0.1到request header中就能解决，后来才知道也有从Client-IP来判断访问者来路的，于是填上Client-IP: 127.0.0.1到request header中得到Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/31746e082f069b025c740ff778bcc6b8e7f34e03.jpg)

**HTTP Base3**

![enter image description here](http://drops.javaweb.org/uploads/images/6e15d6c82db2da9680fddd1e3f41d78264cb322c.jpg)

题目显示访问者是普通用户，所以思路是变成管理员，再加上cookie中发现有：userid=33; userlevel=2;于是将userid和userlevel都置为1，再次访问得到Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/8d5f85e90942369d545aeedb55dd3ec16a470c79.jpg)

**CrackPWD1**

![enter image description here](http://drops.javaweb.org/uploads/images/007cd151b896490bd9cb336c5af5843a92224e83.jpg)

直接上ophcrack。Ophcrack基于彩虹表来破解hash口令，特别是针对XP的LM-NT hash，成功率很高。 下载地址：

```
http://sourceforge.jp/projects/ophcrack/releases/

http://sourceforge.net/projects/ophcrack/files/

```

![enter image description here](http://drops.javaweb.org/uploads/images/d6f16266cf43f137fb259d38979e483ed92ea51a.jpg)

**CrackPWD2**

![enter image description here](http://drops.javaweb.org/uploads/images/9a8019ae6dab98be026340a7273dba59860b5c54.jpg)

提示口令起始为`SYC#`且长度为8，只需要生成一份包含所有可能性的字典交给工具跑。后4位每位上可见字符一共94个，字典大小为94的4次方行，约7800w。

![enter image description here](http://drops.javaweb.org/uploads/images/4b5cf678cfd710a8a5ea941302df26e172672ef8.jpg)

再加上毛子强大的工具oclhashcat（http://hashcat.net/oclhashcat/），几乎是秒破口令。oclhashcat是一款使用GPU显卡来破密码的工具，分为N卡版和A卡版，号称世界上最快的密码破解器。 运行命令：

```
cudaHashcat64.exe -t 32 -m 1000 NT.hash pass.dic

```

![enter image description here](http://drops.javaweb.org/uploads/images/99096f03f783bce3754cd3e7ca3cea1139aecacf.jpg)

**美男子**

![enter image description here](http://drops.javaweb.org/uploads/images/29d1a4574d331f38167fc85a4cfbcf2f4147375b.jpg)

按提示需要认证为美男子。查看cookie发现是：`user=diaosi; isboy=0; pass=d93fa3b25f83f202cc51257eee2c9207;`访问者被设为diaosi了，不能忍，果断修改us`er=meinanzi; isboy=1;`刷新得到Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/7a6e6994b673982870c8fbf280300b33ce56f74d.jpg)

Cookie中的md5解开是ds0，没用上。

**Login**

![enter image description here](http://drops.javaweb.org/uploads/images/73be6c3351272cde1f0a1049536edfa8420ebd0d.jpg)

以`username=appleU0&password=syclover`登录，发现一行提示 Tips: coverage login。 各种搜索不知道啥叫覆盖登录。各种乱想终于想到是覆盖login，变量覆盖漏洞。经历ISCC2014的变量覆盖题，猜变量名是一件头大的事。我设想了几个可能的变量名：

```
admin\flag\key\KEY\user\login\submit

```

以及可能的值：`1\true\flag\key\admin\flag\login`，爆破了下没有结果，甚至连中文的值都试过，登录\提交，无果。最终觉得既然是覆盖login，变量名应该就是login，于是在GET的url后面添加上?login=1，尝试了下得到Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/fdd4504f9dc472f3f94fc1da6427aedc93eff667.jpg)

**白神的shell**

![enter image description here](http://drops.javaweb.org/uploads/images/db9acd8502d217cd836eee831e0d965de3b8b860.jpg)

直接上代码吧，多线程也不会，跑的慢点，不过也能出结果。

```
import httplib

s = 'zxcvbnmasdfghjklqwertyuiop'
length = len(s)
uri = '/pentest/findshell/white_god_s_webshell_'
conn = httplib.HTTPConnection("syc.myclover.org")

for i in range(length):
    for j in range(length):
        for k in range(length):
            conn.request("GET", uri + s[i] + s[j] + s[k] + ".php")
            response = conn.getresponse()
            response.read()
            if response.status == 200:
                print "white_god_s_webshell_%s%s%s" % (s[i], s[j], s[k]) + ".php"
                exit()

```

![enter image description here](http://drops.javaweb.org/uploads/images/981472836a7a8a9130be5a497ef4a69f09dc6ccd.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/ae62568966b7d7b0e4e655ace25fbf3d55fdb5bb.jpg)

**德玛西亚**

![enter image description here](http://drops.javaweb.org/uploads/images/7dcbbd66a12a87bbc4ba62a386b4cbd903b4e99c.jpg)

下载的dhs文件可以用7z解压缩，打开解压的文件发现内容是某用户访问baidu的cookie，于是可以用劫持到的cookie冒充该用户登录百度。

![enter image description here](http://drops.javaweb.org/uploads/images/4bb73ff45453124b271c383e7a5fc4cb2155d56d.jpg)

利用hackbar修改cookie，刷新登录百度，该用户的baidu id是dsploit_test。开始以为flag会在网盘、文库等地方，找了下没找到，回到个人中心，发现用户有贴吧操作痕迹，果断查看发帖和回帖发现Flag。

![enter image description here](http://drops.javaweb.org/uploads/images/0e63edc12941f6481a9e1544790316556fd0f904.jpg)

**Web Base1**

简单的Get型注入。

```
python sqlmap.py –u http://syc.myclover.org/pentest/web1/read.php?id=1 --dbms mysql -D webbase1 -T flag --dump

```

![enter image description here](http://drops.javaweb.org/uploads/images/11e8448cb2e6096d16edb96f63ef3ef487f6d9fb.jpg)

**Web Base2**

Post搜索型注入。

```
python sqlmap.py –u http://syc.myclover.org/pentest/web2/search.php --data “key=my” --dbms mysql -D webbase2 -T #flag --dump

```

![enter image description here](http://drops.javaweb.org/uploads/images/eb3cf9aa9b5c01d8ccea508b4bde97816143b744.jpg)

**SQL注入**

链接是sqlmap.org的山寨页面，在http response header里发现提示，index.php?id=。分别取id=1/2/3/4，页面与默认页面均不同。id=4-1与id=3一样，id=2%2B1与id=3也一样，id应该就是所需要的注入点了。 如果直接上sqlmap的话，会发现有mysql的payload，但是sqlmap无法识别database类型。

![enter image description here](http://drops.javaweb.org/uploads/images/9a5e5b424339f38985f2a7ac249e481435d47dfa.jpg)

在尝试多个tamper之后，发现对关键字进行保护(对关键字添加/_!_/，如/!_select_/)的versionedmorekeywords.py能有斩获，payload发生了变化，也可以跑出一个数据库。

![enter image description here](http://drops.javaweb.org/uploads/images/875076c8830e6545abe0353ee39460e59f14a7e3.jpg)

MySQL的表结构都存放在information_schema中，不能访问这个库，就无法知道sqli库的结构，使用common-tables爆破表名也未果。下图中无法获取数据库的个数，当时觉得可能是过滤了information_schema，也没有想到好的绕过方法，至此暂时陷入了僵局。

![enter image description here](http://drops.javaweb.org/uploads/images/37716aee69b604836f74fe73f041d677a1ab04d1.jpg)

两天后，主办方在页面注释中给出了新提示，

> ，

原来是吞掉了payload中的union，select和blank。可以用selselect和uniunionon来bypass。tamper中的nonrecursivereplacement.py刚好提供了此功能，但是需要对其稍作修改，keywords = ("UNION", "SELECT", "INSERT", "UPDATE", "WHERE", "FROM")中的后4项应去掉，只保留UNION和SELECT。这也是我之前使用versionedmorekeywords.py和nonrecursivereplacement.py的组合没跑出来表的原因。 但是到这一步，能跑出information_schema，也能得出sqli库的表名i_find_key，却得不出列名，经比对count(tables)和count(column)的payload，发现count(column)多使用了一个关键字AND，于是把AND也加入到nonrecursivereplacement.py的keywords中，最终得到Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308003131159.png)

PS：最后一步不知列名，也可以靠手注获得Flag，前提是i_find_key表仅1列。

![enter image description here](http://static.wooyun.org/20141103/2014110308003124971.png)

**lfi**

既然叫lfi，那就是Local File Inclusion了。

![enter image description here](http://static.wooyun.org/20141103/2014110308003123624.png)

第一步要求从博客访问lfi页面，那就加上

```
referer: http://syclover.sinaapp.com/

```

![enter image description here](http://static.wooyun.org/20141103/2014110308003158782.png)

根据提示file变量有lfi漏洞，读下readme.php

![enter image description here](http://static.wooyun.org/20141103/2014110308003219686.png)

既然Flag is in your_heart，那就读下your_heart.php，得到Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308003258881.png)

**Wireless**

![enter image description here](http://static.wooyun.org/20141103/2014110308003277843.png)

生成一个syc19800101-syc20001231的字典，用aircrack-ng跑下就有了。

![enter image description here](http://static.wooyun.org/20141103/2014110308003241964.png)

**F4ck**

Jsfu*k编码，复制所有编码到浏览器console处运行，得到Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308003222206.png)

**CodeAudit1**

下载附件，对其中index.php进行代码审查。

```
<?php
    $id = isset($_GET['syc&id']) ? $_GET['syc&id'] : "";
    $sql = "SELECT id, title FROM news";
    if (!empty($id)) {
        $id = mysql_escape_string($id);
        $sql .= " WHERE id=$id";
    }
    //echo $sql; exit;
    $result = mysql_query($sql);
    $i = 0;
    while ($row = mysql_fetch_array($result, MYSQL_ASSOC)) :
?>

```

参数syc&id仅仅使用mysql_escape_string进行了转义而且还没有引号保护，这就产生了注入点。我们可以使用union查询把flag从数据库中搜出来。从codeaudit1.sql中能获取数据库的结构。注意&和#需要编码为%26和%23。

![enter image description here](http://%21[enter%20image%20description%20here][47]/)

**CodeAudit2**

扫描codeaudit2的网页发现存在首页备份文件index.php.bak，下载下来看看源码。

```
<?php
        $username = isset($_POST['username']) ? $_POST['username'] : "";
        $password = isset($_POST['password']) ? $_POST['password'] : "";
        $type = isset($_COOKIE['type']) ? $_COOKIE['type'] : "1";

        if (empty($username) || empty($password) || empty($type)) {
            echo "Credits Can not be empty!";
            exit;
        }

        $username = mysql_escape_string($username);
        $password = mysql_escape_string($password);
        $type = mysql_escape_string($type);

        $sql = "SELECT password FROM user WHERE username='${username}' and type=${type}";
        $result = mysql_query($sql);
        if (mysql_num_rows($result) !== 1) {
            echo "System error!";
            exit;
        }

        $row = mysql_fetch_row($result);
        if ($row[0] == md5(base64_encode($password))) {
            echo "FLAG: *****************";
        }
    ?>

```

页面需要正常提供3个参数，username和password是POST型，type是cookie型。我们只需要保证查询出来的result仅有1行，且输入的password满足md5(base64_encode($password))=数据库中的password，页面就会自动输出Flag。

三个参数中username和password有单引号和转义函数的保护，type参数没有单引号，因此type是一个cookie型注入点。由于页面访问及其不稳定，请求频率稍微快点服务器就返回502错误，而且是基于时间的盲注，即使加上—delay参数，sqlmap也没能远程跑出注入点（在本地倒是跑出来基于时间的盲注）。只能寻求手工注入，结合burpsuite，盲注出了username=admin和passoword=fdc4110d6d6612ced3faacd93ee01749。但是password破解不了…，只能另辟蹊径。

再次审查代码，发现可以输入不存在的username，然后利用type的注入点union select任意的密码，这里可以用concat(16进制的密码)来bypass对引号的转义。输入$password=1，hex(md5(base64_encode($password))) = 0x 6364643936643363633733643164626461666661303363633663643733333962，只需要设置type = 1 union select concat(0x 6364643936643363633733643164626461666661303363633663643733333962)既可得到Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308003717157.png)

**来搞站了**

![enter image description here](http://static.wooyun.org/20141103/2014110308003766593.png)

打开链接，是myclover.org的一个分站，主办方还特意提醒不要上“重型扫描器”…

![enter image description here](http://static.wooyun.org/20141103/2014110308003881738.png)

没啥东西，既然是博客就加上/blog，进了一个wordpress站点。

![enter image description here](http://static.wooyun.org/20141103/2014110308003832927.png)

wordpress通常思路是先找出使用了哪些plugin，然后针对爆出过漏洞的plugin进行渗透。这个站点用wordpress专用扫描器wpscan扫了下，仅有一个插件akismet，是一个过滤垃圾留言的。上www.exploit-db.com搜了下该插件，上次出漏洞已经是7年前，心里顿时哇凉哇凉的。

![enter image description here](http://static.wooyun.org/20141103/2014110308003899078.png)

接着用wpscan枚举了下用户名，仅有一个是admin，也顺便使用了wpscan和wpbf（http://www.freebuf.com/tools/36904.html）爆破了下admin口令，感觉太慢，没有结果。虽然后来得知确实是弱口令，而且在弱口令字典中，不知为毛没有爆出来…

还有个想法就是社工了，本来自己社工就弱，blog的博主名LateRain基本上也是常见词，毛都没射出来。

思路陷入停滞状态，持续了两天。两天后，依然没人得分，我感觉在做的人不多，抱着死马当活马医的想法，于是挑了个时间上了“重型扫描器”——AWVS。果然不负众望，扫出了弱口令，我心里那个激动啊。

![enter image description here](http://static.wooyun.org/20141103/2014110308003822047.png)

速度使用admin/abc123登进后台管理。首先上传插件拿webshell，对shell打了个包，上传插件，系统提示需要输入ftp密码才能上传，试了下abc123，不对，遂放弃此路，还有其他路子。第二条编辑插件，写入一句话到页面中，没找到保存或更新按钮，只能换最后一条路了。最后是编辑主题，我在/wp-content/themes/twentytwelve/header.php内插入了一句话，虽然浏览器访问说是500错误，但用菜刀还是成功连接。

![enter image description here](http://static.wooyun.org/20141103/2014110308003883258.png)

在站点根目录下有个`fd9c8263b299ee07656aa9e18ac0417a.php`，Flag就在其中。

![enter image description here](http://static.wooyun.org/20141103/2014110308003940772.png)

![enter image description here](http://static.wooyun.org/20141103/2014110308004061294.png)

不知道什么情况主办方回滚了一次，还把弱口令改了，幸好有前人留下的一句话在`http://pt1.myclover.org/blog/wp-content/themes/twentytwelve/content.php`，密码是wood。所以能复现成功。  

0x03 reverse
------------

* * *

**VeryEasy_ELF**

既然VeryEasy，直接strings一下，发现疑似flag字符串，拼起来输入到程序中就是Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308004073944.png)

**如花姐姐**

![enter image description here](http://static.wooyun.org/20141103/2014110308004039814.png)

IDA Pro加载一下ruhua.exe，在sub_401410函数中可以看到注册成功与否的判断过程。

![enter image description here](http://static.wooyun.org/20141103/2014110308004055090.png)

首先读取用户名到v3中，读取密码到v5中，用户名和密码的长度不能超过10，然后v3和v5分别经函数sub_401500和sub_401530处理后，进行比较，不等就注册失败，相等则注册成功。 再看一下sub_401500和sub_401530。

![enter image description here](http://static.wooyun.org/20141103/2014110308004029322.png)

![enter image description here](http://static.wooyun.org/20141103/2014110308004068011.png)

伪代码很简单，用户名的每一位是(a[i]^3)-20，密码的每一位则是(a[i]+2)^0x10，据此可以写出注册机。

```
username = raw_input('Username:')
password = ''
for i in range(len(username)):
    password += chr((((ord(username[i]) ^ 3) - 20) ^ 0x10) - 2)
print "Password:" + password

```

syclover对应的密码就是：JtZIFo@K

**BMW**

反编译bmw.apk后，有个TheFlagIsNotHere.java的文件中存在一个getKey()函数，直觉告诉我运行完该函数就能获得Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308004174432.png)

新建一个java class，将代码copy过来，运行得到Flag。Java代码如下：

```
public class bmw 
{
    public static final int LEN = "!0123456789abcdefghijklmnopqrstuvwxyz{}".length();
    public static final String SOURCE = "!0123456789abcdefghijklmnopqrstuvwxyz{}";
    public static String key = "v}f0frqjudwx4dwl3qv2}3xilqgp71";

    public static void main(String[] args) 
    {
        getKey();
    }

    public static void getKey()
    {
        StringBuilder stringbuilder = new StringBuilder();
        key.length();
        int i = 0;
        do
        {
            if(i >= key.length())
                return;
            int j = "!0123456789abcdefghijklmnopqrstuvwxyz{}".indexOf(key.charAt(i));
            if(j == 2)
                j = 2 + LEN;
            if(j == 1)
                j = 1 + LEN;
            if(j == 0)
                j = LEN;
            stringbuilder.append("!0123456789abcdefghijklmnopqrstuvwxyz{}".charAt(j + -3));
            i++;
            System.out.println(stringbuilder);
        } while(true);
    }
}

```

运行结果如图：

![enter image description here](http://static.wooyun.org/20141103/2014110308004182823.png)

**女神**

![enter image description here](http://static.wooyun.org/20141103/2014110308004122752.png)

题目给了一个PE程序，首先PEid查了下源程序，带了UPX的壳，恰好PEid自带的插件能脱。

![enter image description here](http://static.wooyun.org/20141103/2014110308004159868.png)

脱完之后，OD加载程序，逐步分析，在GetDlgItemTextA处下断点，从获取到用户输入的Key后开始分析。

```
004011D4    8D7C24 10       lea     edi, dword ptr [esp+0x10]       ; esp+0x10=key的起始地址
004011D8    83C9 FF         or      ecx, 0xFFFFFFFF 
004011DB    33C0            xor     eax, eax    
004011DD    F2:AE           repne   scas byte ptr es:[edi]  
004011DF    F7D1            not     ecx 
004011E1    49              dec     ecx 
004011E2    83F9 0D         cmp     ecx, 0xD                        ; length(key)=13
004011E5    0F85 F0000000   jnz     004012DB    

004011ED    8A440C 10       mov     al, byte ptr [esp+ecx+0x10] 
004011F1    3C 30           cmp     al, 0x30                        ; key[i]>=0x30
004011F3    0F8C E2000000   jl      004012DB    
004011F9    3C 39           cmp     al, 0x39                        ; key[i]<=0x39
004011FB    0F8F DA000000   jg      004012DB    

00401207    0FBE7C24 16     movsx   edi, byte ptr [esp+0x16]        ; edi=key[6]
0040120C    0FBE4C24 10     movsx   ecx, byte ptr [esp+0x10]        ; ecx=key[0]
00401211    0FBE5424 19     movsx   edx, byte ptr [esp+0x19]        ; edx=key[9]
00401216    8D4439 A0       lea     eax, dword ptr [ecx+edi-0x60]   ; eax=key[6]+key[0]-0x60
0040121A    83EA 26         sub     edx, 0x26                       ; edx=key[9]-0x26
0040121D    3BC2            cmp     eax, edx                        ; key[6]+key[0]-0x60=key[9]-0x26
0040121F    0F85 B6000000   jnz     004012DB    

00401225    8A5C24 17       mov     bl, byte ptr [esp+0x17]         ; bl=key[7]
00401229    8D41 D0         lea     eax, dword ptr [ecx-0x30]   
0040122C    99              cdq     
0040122D    0FBEF3          movsx   esi, bl                         ; esi=key[7]
00401230    83E2 03         and     edx, 0x3    
00401233    03C2            add     eax, edx    
00401235    8D56 D0         lea     edx, dword ptr [esi-0x30]       ; edx=key[7]-0x30
00401238    C1F8 02         sar     eax, 0x2                        ; eax=(key[0]-0x30)>>2
0040123B    3BC2            cmp     eax, edx                        ; (key[0]-0x30)>>2=key[7]-0x30
0040123D    0F85 98000000   jnz     004012DB    

00401243    385C24 14       cmp     byte ptr [esp+0x14], bl         ; key[4]=key[7]
00401247    0F85 8E000000   jnz     004012DB    

0040124D    0FBE4424 11     movsx   eax, byte ptr [esp+0x11]    
00401252    8D1430          lea     edx, dword ptr [eax+esi]    
00401255    03D1            add     edx, ecx    
00401257    03D7            add     edx, edi                        ; edx=key[0]+key[1]+key[6]+key[7]
00401259    81FA D4000000   cmp     edx, 0xD4                       ; key[0]+key[1]+key[6]+key[7]=0xD4
0040125F    75 7A           jnz     short 004012DB  

00401261    0FBE5424 12     movsx   edx, byte ptr [esp+0x12]    
00401266    0FBE7424 15     movsx   esi, byte ptr [esp+0x15]    
0040126B    03F2            add     esi, edx                        ; esi=key[2]+key[5]
0040126D    03C1            add     eax, ecx                        ; eax=key[0]+key[1]
0040126F    3BC6            cmp     eax, esi                        ; key[2]+key[5]=key[0]+key[1]
00401271    75 68           jnz     short 004012DB  

00401273    0FBE4424 13     movsx   eax, byte ptr [esp+0x13]        ; eax=key[3]
00401278    42              inc     edx                             ; edx=key[2]+1
00401279    3BD0            cmp     edx, eax                        ; key[2]+1=key[3]
0040127B    75 5E           jnz     short 004012DB  

0040127D    807C24 16 38    cmp     byte ptr [esp+0x16], 0x38       ; key[6]=0x38
00401282    75 57           jnz     short 004012DB  
00401284    807C24 10 39    cmp     byte ptr [esp+0x10], 0x39       ; key[0]=0x39
00401289    75 50           jnz     short 004012DB  
0040128B    807C24 18 30    cmp     byte ptr [esp+0x18], 0x30       ; key[8]=0x30
00401290    75 49           jnz     short 004012DB  

00401294    B1 32           mov     cl, 0x32    
00401296    384C04 10       cmp     byte ptr [esp+eax+0x10], cl     ; key[i]=0x32?
0040129A    75 01           jnz     short 0040129D  
0040129C    45              inc     ebp                             ; ebp=count(key[i]==0x32)
0040129D    40              inc     eax 
0040129E    83F8 0D         cmp     eax, 0xD    
004012A1    7C F3           jl      short 00401296  
004012A3    83FD 03         cmp     ebp, 0x3                        ; count(key[i]==0x32)=3
004012A6    75 33           jnz     short 004012DB  

004012A8    0FBE4424 1B     movsx   eax, byte ptr [esp+0x1B]    
004012AD    0FBE4C24 1A     movsx   ecx, byte ptr [esp+0x1A]        ; ecx=key[10]
004012B2    8D50 FF         lea     edx, dword ptr [eax-0x1]        ; edx=key[11]-1
004012B5    3BCA            cmp     ecx, edx                        ; key[10]=key[11]-1
004012B7    75 22           jnz     short 004012DB  

004012B9    83C1 D0         add     ecx, -0x30  
004012BC    83C0 D0         add     eax, -0x30  
004012BF    0FAFC8          imul    ecx, eax                        ; ecx=key[10]*key[11]
004012C2    0FBE4424 1C     movsx   eax, byte ptr [esp+0x1C]    
004012C7    83E8 30         sub     eax, 0x30                       ; eax=key[12]
004012CA    33D2            xor     edx, edx    
004012CC    3BC8            cmp     ecx, eax                        ; key[10]*key[11]=key[12]

```

有了上述各个条件，加上key[2](http://drops.wooyun.org/wp-content/uploads/2014/10/215.png)=0x35的提示，容易分析出9156258207236就是Key。

![enter image description here](http://static.wooyun.org/20141103/2014110308004155686.png)

**toosimple**附件又是一个apk，反编译后几个java文件翻了翻，没有结果，但是发现了一个libgetKey.so，是个ELF文件，果断祭出IDA，果不其然发现了关键函数calculateKey()。

![enter image description here](http://static.wooyun.org/20141103/2014110308004127313.png)

顺着伪代码写了个脚本，运行下得到Flag。

```
str = 'RW@w,!fWj&Bpa=zlemIu6}'
dest = list(str)
v0 = 11
v1 = 1 
v2 = 0
while v2 != 21:
    v3 = ord(dest[v2])
    if v2 > 10:
        dest[v2] = chr(v3 - v0)
        v0 -= 1
    else:
        dest[v2] = chr(v3 + v1)
        v1 += 1
    v2 += 1
print "Flag:"+''.join(dest)

```

![enter image description here](http://static.wooyun.org/20141103/2014110308004299232.png)

**ATM**

![enter image description here](http://static.wooyun.org/20141103/2014110308004276845.png)

先本地运行程序，同时用IDA加载。

![enter image description here](http://static.wooyun.org/20141103/2014110308004242285.png)

sub_804859E即输出上面的部分。要求覆盖到存放money的内存地址为0x63795324，即$Syc，下图中对应的是a1的内存地址，同时a1也是sub_804859E函数的参数。

![enter image description here](http://static.wooyun.org/20141103/2014110308004222857.png)

![enter image description here](http://static.wooyun.org/20141103/2014110308004235628.png)

再看下接收输入的函数sub_804872A。

![enter image description here](http://static.wooyun.org/20141103/2014110308004251972.png)

v22是我们的输入部分，v24作为存放money的参数带入sub_804859E中运行。由于没有对输入v22的长度做校验，我们就可以输入较长字符串来覆盖掉v24的内存地址，达到目的。下面看下v22和v24之间地址差，以便确定需要多长的shellcode。

![enter image description here](http://static.wooyun.org/20141103/2014110308004271738.png)

因此只需要0x3C-0x1A=34个字符及就能覆盖掉v22到v24之间的内存地址，再加上$Syc就能使money=0x63795324。因此shellcode可以取为a*34+$Syc。本地溢出的结果如图。

![enter image description here](http://static.wooyun.org/20141103/2014110308004313471.png)

**EasyElf**

出了一个VeryEasy_ELF，又来一个EasyELF，IDA加载下，下面的else分支，有疑似flag。输入的password存在v14处，v14与疑似flag字样进行比较，比对正确提交却不正确。真正的True flag在上面的if分支中，与用户输入无关。

![enter image description here](http://static.wooyun.org/20141103/2014110308004383936.png)

![enter image description here](http://static.wooyun.org/20141103/2014110308004383944.png)

根据伪代码的脚本如下，运行得到Flag。

```
v3 = '\x69\x75\x6f\x63\x67\x71\x70\x67'
v13 = [''] * 8
i = 7
while i >= 0:
    v13[i] = chr((ord(v3[7 - i])) - i)
    i -= 1
print 'Flag:SYC{'+''.join(v13)+'}'

```

![enter image description here](http://static.wooyun.org/20141103/2014110308004339549.png)

**00xx**

![enter image description here](http://static.wooyun.org/20141103/2014110308004391093.png)

开始不知道啥叫SEH，百度百科上是这么说的：SEH("Structured Exception Handling")，即结构化异常处理，是(windows)操作系统提供给程序设计者的强有力的处理程序错误或异常的武器。OD加载00xx时，在获取到用户输入后，单步运行很容易产生异常，然后程序就结束了。但是可以通过一些内存地址来跳过这些异常。 首先在GetDlgItemTextW处下断，输入后，程序返回到0040111F，运行完0040111F后，应修改EIP（CPU区域右键有个New origin here选项就是EIP跳转功能）直接跳转到00401136。然后F7进入到目标函数00401190。

![enter image description here](http://static.wooyun.org/20141103/2014110308004450537.png)

运行完00401193，应直接跳转到004011A3处，从这里开始程序将00403018处的unicode字符串sYC.与00403378处输入字符串的前4位分别作异或，结果存放在00403388处

![enter image description here](http://static.wooyun.org/20141103/2014110308004421287.png)

![enter image description here](http://static.wooyun.org/20141103/2014110308004424021.png)

![enter image description here](http://static.wooyun.org/20141103/2014110308004449616.png)

运行完004011ED后，应直接跳转到00401206处，从这里开始程序开始处理输入字符串第4位之后的部分，0040123A处要求上面异或后的4位相加=wtoi(key[4:])+0x3E，满足此条件后，再判断异或后的前3位是不是”C6;”。因此可以退出key的前3位分别是0x43^0x73，0x36^0x59，0x3B^0x43，对应的是”0ox”。

![enter image description here](http://static.wooyun.org/20141103/2014110308004433335.png)

但是这里没有对key[3](http://drops.wooyun.org/wp-content/uploads/2014/10/38.png)做限制，事实上只要满足key[4](http://drops.wooyun.org/wp-content/uploads/2014/10/47.png)^0x2E+0x76=wtoi(key[4:])，均能注册成功。

![enter image description here](http://static.wooyun.org/20141103/2014110308004497280.png)

唯一能解释最终flag(0oxX236)的只有题目叫00xx了。 溢出和SEH这块确实不怎么会，有不对的地方，请大牛们批评指正。  

0x04 program
------------

* * *

**XOR**

![enter image description here](http://static.wooyun.org/20141103/2014110308004480389.png)

题目提示XOR以及与正常程序的比对，那就将out.exe前4字节7D 6B A0 31和正常程序00xx.exe前4字节4D 5A 90 00异或下得到30 31 30 31，猜测所谓的加密就是源程序每两字节分别与30 31异或，下面是解密代码。

```
f1 = open('out.exe', 'r')
out = list(f1.read())
xor = [0x30, 0x31]
for i in range(len(out)):
    out[i] = chr(ord(out[i]) ^ xor[i % 2])
f1.close()

f2 = open('xor.exe', 'w')
f2.write(''.join(out))
f2.close()

```

运行输出的xor.exe拿到Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308004584629.png)

**LIGHT**

![enter image description here](http://static.wooyun.org/20141103/2014110308004571224.png)

开窗游戏的算法，我参考了一篇论文《华容道、开窗等经典智力问题的求解算法研究》。下面是原文中对算法的解释。 经过分析得知，操作顺序不影响操作结果，对一个窗户操作偶数次等价于操作0次(即不操作)；操作奇数次等价于操作1次，故最后的解答的形式可以表示为一个数组a(i, j)。窗子(i, j)不需要操作时，a(i, j)=0；窗子(i, j)需要操作一次时，a(i, j)=1。 因为每个窗户(i, j)有两种状态，一共有m_n个，所以一共有2n_m 种可能，时间复杂度很大。进一步分析可知，窗子(i, j)的状态只与以下因素有关：窗子(i, j)的初始状态，以及a(i, j)，a(i-1, j)，a(i+1, j)，a(i, j-1)，a(i, j+1)。假设已经确定第一行的每个窗子是否操作，则对于窗子(1, j)，由于窗子(1,j)的初始颜色以及a(1, j)，a(i, j-1)，a(i, j+1)都已确定，则该窗子的颜色只能由a(i+1, j)来调整。模拟第一行的操作过程后，若a(1, j)仍为开,则必须a(2, j)=1才能使窗子(1, j)满足条件；同理当a(1, j)为关时，可知a(2, j)=0，这样a(2, j)(1≤j≤n)也已经确定，依此类推可推出所有a(i, j)的值(1≤i≤m, 1≤j≤n )，最后验证最后一行窗子是否都已关闭即可。 从而可以枚举第一行每个窗子是否操作，共需枚举2n种可能。对于每种可能按以上方法进行递推，找出其中可使最后一行均为关闭的方案即可。具体算法如下(C#)：

```
/************************************************************
请将1.txt置于Light.exe同路径下程序自动读取1.txt的状态进行求解
************************************************************/
using System;
using System.Collections.Generic;
using System.IO;

namespace LIGHT
{
    class Program
    {
        private static int m = 0, n = 0;                            // 窗户的行数m和列数n
        private static int[,] window;                               // 窗户的状态数组
        private static List<String> solution = new List<string>();  // 最终的解法

        static void Main(string[] args)
        {
            init();  //读取1.txt并初始化window[m,n]

            if (solve())
            {
                Console.WriteLine("Solved!");
                foreach (string s in solution)
                {
                    Console.Write(s + " ");
                }
            }
            else
                Console.WriteLine("Can't solve!");
            Console.ReadKey();
        }

        public static void init()
        {
            List<String> state = new List<string>();  //以行为单位存放1.txt中的内容
            try
            {
                FileStream fs = new FileStream("./1.txt", FileMode.Open);
                StreamReader sr = new StreamReader(fs);
                string strLine = null;
                while ((strLine = sr.ReadLine()) != null)
                {
                    state.Add(strLine);
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e.Message);
                Environment.Exit(0);
            }

            m = state.Count;
            n = state[0].Length;
            window = new int[m, n];
            for (int i = 0; i < m; i++)
            {
                for (int j = 0; j < n; j++)
                {
                    window[i, j] = Int32.Parse(state[i][j].ToString());
                }
            }
        }

        public static bool solve()  // 全变成0，return true; 不能全变成0，return false
        {
            int max = (int)Math.Pow(2, n);
            for (int k = 0; k < max; k++)  // 对第一行的所有可能进行枚举
            {
                int r = k;
                int[,] tmp = new int[m, n];

                for (int i = 0; i < m; i++)  // 将原始情况复制到临时数组中操作
                {
                    for (int j = 0; j < n; j++)
                    {
                        tmp[i, j] = window[i, j];
                    }
                }

                for (int j = 0; j < n; j++)  // 第一行
                {
                    if (r % 2 == 1)
                    {
                        change(0, j, tmp);
                        solution.Add("(" + 1 + "," + (j + 1) + ")");
                    }
                    r = r / 2;
                }

                for (int i = 1; i < m; i++)  // 递推后面的行
                {
                    for (int j = 0; j < n; j++)
                    {
                        if (tmp[i - 1, j] == 1)
                        {
                            change(i, j, tmp);
                            solution.Add("(" + (i + 1) + "," + (j + 1) + ")");
                        }
                    }
                }

                bool check = true;
                for (int j = 0; j < n; j++)  // 验证最后一行是否全是0
                {
                    if (tmp[m - 1, j] == 1)
                    {
                        check = false;
                        solution.Clear();
                        break;
                    }
                }
                if (check)
                    return true; // 全0有解！
            }
            return false;  // 无解
        }

        private static void change(int i, int j, int[,] tmp)  // 开关窗操作，分9种情形
        {
            tmp[i, j] = swap(tmp[i, j]);
            if (0 < i && i < m - 1 && 0 < j && j < n - 1)
            {
                tmp[i, j - 1] = swap(tmp[i, j - 1]);
                tmp[i - 1, j] = swap(tmp[i - 1, j]);
                tmp[i, j + 1] = swap(tmp[i, j + 1]);
                tmp[i + 1, j] = swap(tmp[i + 1, j]);
                return;
            }
            if (0 < i && i < m - 1 && j == 0)
            {
                tmp[i - 1, 0] = swap(tmp[i - 1, 0]);
                tmp[i, 1] = swap(tmp[i, 1]);
                tmp[i + 1, 0] = swap(tmp[i + 1, 0]);
                return;
            }
            if (i == 0 && 0 < j && j < n - 1)
            {
                tmp[0, j - 1] = swap(tmp[0, j - 1]);
                tmp[0, j + 1] = swap(tmp[0, j + 1]);
                tmp[1, j] = swap(tmp[1, j]);
                return;
            }
            if (0 < i && i < m - 1 && j == n - 1)
            {
                tmp[i, n - 2] = swap(tmp[i, n - 2]);
                tmp[i - 1, n - 1] = swap(tmp[i - 1, n - 1]);
                tmp[i + 1, n - 1] = swap(tmp[i + 1, n - 1]);
                return;
            }
            if (i == m - 1 && 0 < j && j < n - 1)
            {
                tmp[m - 1, j - 1] = swap(tmp[m - 1, j - 1]);
                tmp[m - 2, j] = swap(tmp[m - 2, j]);
                tmp[m - 1, j + 1] = swap(tmp[m - 1, j + 1]);
                return;
            }
            if (i == 0 && j == 0)
            {
                tmp[0, 1] = swap(tmp[0, 1]);
                tmp[1, 0] = swap(tmp[1, 0]);
                return;
            }
            if (i == 0 && j == n - 1)
            {
                tmp[0, n - 2] = swap(tmp[0, n - 2]);
                tmp[1, n - 1] = swap(tmp[1, n - 1]);
                return;
            }
            if (i == m - 1 && j == n - 1)
            {
                tmp[m - 1, n - 2] = swap(tmp[m - 1, n - 2]);
                tmp[m - 2, n - 1] = swap(tmp[m - 2, n - 1]);
                return;
            }
            if (i == m - 1 && j == 0)
            {
                tmp[m - 2, 0] = swap(tmp[m - 2, 0]);
                tmp[m - 1, 1] = swap(tmp[m - 1, 1]);
                return;
            }
        }

        private static int swap(int i)
        {
            return (i == 1) ? 0 : 1;
        }
    }
}

```

题中提供初始情况的运行结果如下：

![enter image description here](http://static.wooyun.org/20141103/2014110308004520203.png)

**小菜一碟**

![enter image description here](http://static.wooyun.org/20141103/2014110308004539719.png)

e有多种取值，但是最终的明文能被识别的很少。鉴于e不大，可以枚举出所有可能的e，看了下结果，发现有一种情形明文每个位置的值都在130以下，能按ascii解码。

```
def foo(num1, num2, cmd):
    q = r = s = t = 0
    r1 = num1
    r2 = num2
    s1 = t2 = 1
    s2 = t1 = 0

    while r2 > 0:
        q = int(r1 / r2)
        r = r1 % r2
        s = s1 - q * s2
        t = t1 - q * t2

        r1 = r2
        r2 = r
        s1 = s2
        s2 = s
        t1 = t2
        t2 = t

    if cmd == 1:  # cmd = 1, return gcd(num1,num2)
        return r1
    if cmd == 2:  # cmd = 2, reyurn num^(-1)(mod num2) 
        if s1 < 0:
            return s1 + num2
        return s1

cipher = [1286,7792,11086,13837,4162,11482,3562,383,15995,21350,15374,3562,8713,15995,3267,16051,18518,16194,3562,15995,15374]
n = 23651
f = 23232

length = len(cipher)
e = []
for i in range(3, 10000, 2):
    if foo(i, f, 1) == 1:
        e.append(i)

for j in range(len(e)):
    d = foo(e[j], f, 2)
    plain = []
    for k in range(length):
        plain.append(pow(cipher[k], d, n))

    flag = True
    for l in range(length):
        if plain[l] > 128:
            flag = False
    if flag:
        for m in range(length):
            plain[m] = chr(plain[m])
        print 'e = %4d d = %5d plain = %s' % (e[j], d, "".join(plain))

```

运行结果：

![enter image description here](http://static.wooyun.org/20141103/2014110308004590547.png) 

0x05 #linux
-----------

* * *

**奇怪的txt**

解压附件得到一个key.txt，中间部分是实际文件的二进制码，能看出是一个BZ2文件，右侧是对应的ASCII值。

![enter image description here](http://static.wooyun.org/20141103/2014110308004578215.png)

写一个脚本将中间部分复制出来到一个新文件中。

```
import binascii

f = open('key.txt','r')
content = ''
for line in f.readlines():
    content += line[9:49]
f.close()
content = content.replace(' ','')

he = binascii.a2b_hex(content)
f1 = open('newkey.bz2','w')
f1.write(he)
f1.close()

```

运行后得到newkey.bz2，解压三次后得到一个key文件。base64decode一下得到FLAG:SYC{L1nux_taR_gZ1p_SYC}。

![enter image description here](http://static.wooyun.org/20141103/2014110308004514152.png)

**史上第二难的题目**

![enter image description here](http://static.wooyun.org/20141103/2014110308004673371.png)

运行下程序，结果是10000行9位数，多次运行发现每次的结果都一致。将运行结果复制到文件中，读取文件进行排序。

```
f = open('lin2.txt','r')
num = list()
for line in f.readlines():
    num.append(line[0:9])
f.close()
num.sort()
print num[6249]

```

运行结果如图。

![enter image description here](http://static.wooyun.org/20141103/2014110308004690967.png)

**lalala**

![enter image description here](http://static.wooyun.org/20141103/2014110308004664021.png)

源程序在我的kali上无法运行，一直没找到libcrypto.so.1.0.0，求大神指教。

![enter image description here](http://static.wooyun.org/20141103/2014110308004629057.png)

不能运行那就上IDA吧，据题意及f5得到的伪代码来看，这里应该用的是RC4加密算法。输入的4个ASCII码数字做密钥，下图红框中应该是密文，用密钥解密密文，若解出来的明文前三字符以SYC(83 89 67)开头，则明文就是Flag。

![enter image description here](http://static.wooyun.org/20141103/2014110308004618280.png)

我们就可以针对密文进行爆破，下面是爆破脚本。

```
def rc4(data, key):
    #if the data is a string, convert to hex format.
    if(type(data) is type("string")):
        tmpData = data
        data = []
        for tmp in tmpData:
            data.append(ord(tmp))

    #if the key is a string, convert to hex format.
    if(type(key) is type("string")):
        tmpKey = key
        key = []
        for tmp in tmpKey:
            key.append(ord(tmp))

    #the Key-Scheduling Algorithm
    x = 0
    box = list(range(256))
    for i in range(256):
        x = (x + box[i] + key[i % len(key)]) % 256
        box[i], box[x] = box[x], box[i]

    #the Pseudo-Random Generation Algorithm
    x = 0
    y = 0
    out = []
    for c in data:
        x = (x + 1) % 256
        y = (y + box[x]) % 256
        box[x], box[y] = box[y], box[x]
        out.append(c ^ box[(box[x] + box[y]) % 256])

    result = ""
    printable = True
    for tmp in out:
        if(tmp < 0x21 or tmp > 0x7e):
            # there is non-printable character
            printable=False
            break
        result += chr(tmp)

    if(printable == False):
        result = ""
        #convert to hex string   
        for tmp in out:
            result += "{0:02X}".format(tmp)

    return result

if __name__ == '__main__':
    a = '!"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~'
    b = ')}'
    length = len(a)
    ciphertext = '\x5F\x20\x6B\x24\x1C\x48\xCA\xFC\xF5\x41\x2D\xD4\xDA'

    for i in range(length):
        for j in range(length):
            for k in range(length):
                for l in range(len(b)):
                    key = a[i] + a[j] + a[k] + b[l]
                    plaintext = rc4(ciphertext, key)
                    if plaintext[0:3]=='SYC':
                        print '%s %s' % (key,plaintext)
                        exit(0)

```

其中RC4算法来自`http://blog.csdn.net/white_eyes/article/details/6560355`。运行得到

![enter image description here](http://static.wooyun.org/20141103/2014110308004663253.png)

密钥是@#()。我想了下主办方干嘛要限制第4个字符呢，于是把第4个字符范围扩大到所有可见字符，原来还有一解：'g=C，对应的十六进制明文是5359432B17FA53419C25E9979E，恰好也是SYC开头。

![enter image description here](http://static.wooyun.org/20141103/2014110308004695903.jpg)

最后附上题目附件及我用到的代码和参考的论文。部分py如运行不顺，请在linux中运行。 链接: http://pan.baidu.com/s/1eQs0u6A 密码: hv8e