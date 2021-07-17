# 关于OpenSSL“心脏出血”漏洞的分析

0x00 背景
-------

* * *

原作者：[Sean Cassidy](http://blog.existentialize.com/pages/about.html)原作者Twitter：@ex509 原作者博客：[http://blog.existentialize.com](http://blog.existentialize.com/)来源：[http://blog.existentialize.com/diagnosis-of-the-openssl-heartbleed-bug.html](http://blog.existentialize.com/diagnosis-of-the-openssl-heartbleed-bug.html)

当我分析[GnuTLS的漏洞](http://blog.existentialize.com/the-story-of-the-gnutls-bug.html)的时候，我曾经说过，那不会是我们看到的最后一个TLS栈上的严重bug。然而我没想到这次OpenSSL的bug会如此严重。

[OpenSSL“心脏出血”漏洞](http://heartbleed.com/)是一个非常严重的问题。这个漏洞使攻击者能够从内存中读取多达64 KB的数据。一些安全研究员表示：

> 无需任何特权信息或身份验证，我们就可以从我们自己的（测试机上）偷来X.509证书的私钥、用户名与密码、聊天工具的消息、电子邮件以及重要的商业文档和通信等数据。

这一切是如何发生的呢？让我们一起从代码中一探究竟吧。

0x01 Bug
--------

* * *

请看ssl/dl_both.c，[漏洞的补丁](http://git.openssl.org/gitweb/?p=openssl.git;a=commitdiff;h=96db9023b881d7cd9f379b0c154650d6c108e9a3)从这行语句开始：

```
int            
dtls1_process_heartbeat(SSL *s)
    {          
    unsigned char *p = &s->s3->rrec.data[0], *pl;
    unsigned short hbtype;
    unsigned int payload;
    unsigned int padding = 16; /* Use minimum padding */

```

一上来我们就拿到了一个指向一条SSLv3记录中数据的指针。结构体SSL3_RECORD的定义如下（译者注：结构体SSL3_RECORD不是SSLv3记录的实际存储格式。一条SSLv3记录所遵循的存储格式请参见下文分析）：

```
typedef struct ssl3_record_st
    {
        int type;               /* type of record */
        unsigned int length;    /* How many bytes available */
        unsigned int off;       /* read/write offset into 'buf' */
        unsigned char *data;    /* pointer to the record data */
        unsigned char *input;   /* where the decode bytes are */
        unsigned char *comp;    /* only used with decompression - malloc()ed */
        unsigned long epoch;    /* epoch number, needed by DTLS1 */
        unsigned char seq_num[8]; /* sequence number, needed by DTLS1 */
    } SSL3_RECORD;

```

每条SSLv3记录中包含一个类型域（type）、一个长度域（length）和一个指向记录数据的指针（data）。我们回头去看dtls1_process_heartbeat：

```
/* Read type and payload length first */
hbtype = *p++;
n2s(p, payload);
pl = p;

```

SSLv3记录的第一个字节标明了心跳包的类型。宏n2s从指针p指向的数组中取出前两个字节，并把它们存入变量payload中——这实际上是心跳包载荷的长度域（length）。注意程序并没有检查这条SSLv3记录的实际长度。变量pl则指向由访问者提供的心跳包数据。

这个函数的后面进行了以下工作：

```
unsigned char *buffer, *bp;
int r;

/* Allocate memory for the response, size is 1 byte
 * message type, plus 2 bytes payload length, plus
 * payload, plus padding
 */
buffer = OPENSSL_malloc(1 + 2 + payload + padding);
bp = buffer;

```

所以程序将分配一段由访问者指定大小的内存区域，这段内存区域最大为 (65535 + 1 + 2 + 16) 个字节。变量bp是用来访问这段内存区域的指针。

```
/* Enter response type, length and copy payload */
*bp++ = TLS1_HB_RESPONSE;
s2n(payload, bp);
memcpy(bp, pl, payload);

```

宏s2n与宏n2s干的事情正好相反：s2n读入一个16 bit长的值，然后将它存成双字节值，所以s2n会将与请求的心跳包载荷长度相同的长度值存入变量payload。然后程序从pl处开始复制payload个字节到新分配的bp数组中——pl指向了用户提供的心跳包数据。最后，程序将所有数据发回给用户。那么Bug在哪里呢？

### 0x01a 用户可以控制变量payload和pl

如果用户并没有在心跳包中提供足够多的数据，会导致什么问题？比如pl指向的数据实际上只有一个字节，那么memcpy会把这条SSLv3记录之后的数据——无论那些数据是什么——都复制出来。

很明显，SSLv3记录附近有不少东西。

说实话，我对发现了OpenSSL“心脏出血”漏洞的那些人的声明感到吃惊。当我听到他们的声明时，我认为64 KB数据根本不足以推算出像私钥一类的数据。至少在x86上，堆是向高地址增长的，所以我认为对指针pl的读取只能读到新分配的内存区域，例如指针bp指向的区域。存储私钥和其它信息的内存区域的分配早于对指针pl指向的内存区域的分配，所以攻击者是无法读到那些敏感数据的。当然，考虑到现代malloc的各种神奇实现，我的推断并不总是成立的。

当然，你也没办法读取其它进程的数据，所以“重要的商业文档”必须位于当前进程的内存区域中、小于64 KB，并且刚好位于指针pl指向的内存块附近。

研究者声称他们成功恢复了密钥，我希望能看到PoC。如果你找到了PoC，[请联系我](http://blog.existentialize.com/pages/about.html)。

### 0x01b 漏洞修补

修复代码中最重要的一部分如下：

```
/* Read type and payload length first */
if (1 + 2 + 16 > s->s3->rrec.length)
    return 0; /* silently discard */
hbtype = *p++;
n2s(p, payload);
if (1 + 2 + payload + 16 > s->s3->rrec.length)
    return 0; /* silently discard per RFC 6520 sec. 4 */
pl = p;

```

这段代码干了两件事情：首先第一行语句抛弃了长度为0的心跳包，然后第二步检查确保了心跳包足够长。就这么简单。

0x02 前车之鉴
---------

* * *

我们能从这个漏洞中学到什么呢？

我是C的粉丝。这是我最早接触的编程语言，也是我在工作中使用的第一门得心应手的语言。但是和之前相比，现在我更清楚地看到了C语言的局限性。

从[GnuTLS漏洞](http://blog.existentialize.com/the-story-of-the-gnutls-bug.html)和这个漏洞出发，我认为我们应当做到下面三条：

```
花钱请人对像OpenSSL这样的关键安全基础设施进行安全审计；
为这些库写大量的单元测试和综合测试；
开始在更安全的语言中编写替代品。

```

考虑到使用C语言进行安全编程的困难性，我不认为还有什么其他的解决方案。我会试着做这些，你呢？

作者简介：Sean是一位关于如何把事儿干好的软件工程师。现在他在[Squadron](http://www.gosquadron.com/)工作。Squadron是一个专为SaaS应用程序准备的配置与发布管理工具。

**测试版本的结果以及检测工具：**

```
OpenSSL 1.0.1 through 1.0.1f (inclusive) are vulnerable
OpenSSL 1.0.1g is NOT vulnerable
OpenSSL 1.0.0 branch is NOT vulnerable
OpenSSL 0.9.8 branch is NOT vulnerable

```

[http://filippo.io/Heartbleed/](http://filippo.io/Heartbleed/)
