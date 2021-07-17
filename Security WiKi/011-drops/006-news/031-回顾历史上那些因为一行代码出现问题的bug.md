# 回顾历史上那些因为一行代码出现问题的bug

最近苹果的那一行[没有验证SSL证书的bug代码](https://www.imperialviolet.org/2014/02/22/applebug.html)，闹的纷纷攘攘，其实历史上也有很多出现类似的代码，让我们来回顾一下：

### X

回到2006年，X server检测用户是否为root用户，竟然忘记了[调用检测函数](http://www.x.org/releases/X11R7.0/patches/xorg-server-1.0.1-geteuid.diff)。

```
--- hw/xfree86/common/xf86Init.c
+++ hw/xfree86/common/xf86Init.c
@@ -1677,7 +1677,7 @@
   }
   if (!strcmp(argv[i], "-configure"))
   {
-    if (getuid() != 0 && geteuid == 0) {
+    if (getuid() != 0 && geteuid() == 0) {
        ErrorF("The '-configure' option can only be used by root.\n");
        exit(1);
     }

```

很奇怪吧，编译的时候没有人看到警告信息吗？

### Debian OpenSSL

在2008年，Debian发行了的一个版本[密钥可能被猜测到](http://www.debian.org/security/2008/dsa-1571)

```
--- openssl-a/md_rand.c
+++ openssl-b/md_rand.c
@@ -271,10 +271,7 @@
                else
                        MD_Update(&m,&(state[st_idx]),j);

-/*             
- * Don't add uninitialised data.
                MD_Update(&m,buf,j);
-*/
                MD_Update(&m,(unsigned char *)&(md_c[0]),sizeof(md_c));
                MD_Final(&m,local_md);
                md_c[1]++;

```

嗯，这个是三行修复代码，搞不明白代码审计的时候发生了什么。

### OpenSSL

同样是OpenSSL，同样在2008年，[OpenSSL 0.9.8i以及更早版本中没有正确的检查EVP_VerifyFinal函数的返回值，导致远程攻击者可以通过绕过证书的验证](http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2008-5077)。

```
--- lib/libssl/src/ssl/s3_srvr.c
+++ lib/libssl/src/ssl/s3_srvr.c
@@ -2009,7 +2009,7 @@ static int ssl3_get_client_certificate(S
    else
        {
        i=ssl_verify_cert_chain(s,sk);
-       if (!i)
+       if (i <= 0)
            {
            al=ssl_verify_alarm_type(s->verify_result);
            SSLerr(SSL_F_SSL3_GET_CLIENT_CERTIFICATE,SSL_R_NO_CERTIFICATE_RETURNED);

```

这可能是你想象中最严重的安全问题了吧？

### Android

这次是2010年，[修复细节](https://code.google.com/p/android-source-browsing/source/detail?spec=svn.platform--bootable--bootloader--legacy.734756ca3968b54e32acab867a05b10fc5e13d07&r=734756ca3968b54e32acab867a05b10fc5e13d07&repo=platform--bootable--bootloader--legacy)：

```
--- libc-a/memset.c
+++ libc-b/memset.c
@@ -1,6 +1,6 @@
 void *memset(void *_p, unsigned v, unsigned count)
 {
     unsigned char *p = _p;
-    while(count-- > 0) *p++ = 0;
+    while(count-- > 0) *p++ = v;
     return _p;
 }

```

这里也没有人编译的时候提示警告有个未使用的参数信息？

### Tarsnap

2011年，[借此重构AES-CTR代码](http://www.daemonology.net/blog/2011-01-18-tarsnap-critical-security-bug.html)：

```
--- tarsnap-autoconf-1.0.27/lib/crypto/crypto_file.c
+++ tarsnap-autoconf-1.0.28/lib/crypto/crypto_file.c
@@ -108,7 +108,7 @@

        /* Encrypt the data. */
        if ((stream =
-           crypto_aesctr_init(&encr_aes->key, encr_aes->nonce)) == NULL)
+           crypto_aesctr_init(&encr_aes->key, encr_aes->nonce++)) == NULL)
                goto err0;
        crypto_aesctr_stream(stream, buf, filebuf + CRYPTO_FILE_HLEN, len);
        crypto_aesctr_free(stream);

```

原文：[http://www.tedunangst.com/flak/post/a-brief-history-of-one-line-fixes](http://www.tedunangst.com/flak/post/a-brief-history-of-one-line-fixes)