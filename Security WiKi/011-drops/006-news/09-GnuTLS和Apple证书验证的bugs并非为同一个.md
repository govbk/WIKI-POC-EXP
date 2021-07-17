# GnuTLS和Apple证书验证的bugs并非为同一个

![enter image description here](http://drops.javaweb.org/uploads/images/d281c4e4d64b4863dfd0c3287bde00b56a6d63d2.jpg)

GnuTLS的bug与Apple goto fail的bug都导致了验证TLS和SSL证书问题，但是他们两个实际上并非是同一个，虽然都是把假的证书也当成有效的证书。

霍普金斯大学的一位密码学教授说：“GnuTLS是一个编码错误，返回了错误的变量，而苹果可能是一个剪切和粘贴的失误。”

goto命令在这两个bug当中都出现了，goto fail语句是C语言遇到错误的时候一个标准执行流程。判断证书是否有效的代码应该返回一个true或者false的布尔值。但是这个GnuTLS的bug，返回的是一个负数的特殊错误代码。

这个bug就是当其中的一个函数返回一个负数的错误代码，这个错误代码当做一个布尔型，而不是真正的一个数字，但是布尔型的判断当中，只要是非0就是true，因此，这个错误在布尔判断中当成了真，形成了这个bug。

这个GnuTLS的bug是被Red Hat审计出来的，GnuTLS 是一个安全通讯库，实现了 SSL、TLS 和 DTLS 协议和相关技术。提供了简单的 C 语言编程接口用来访问这些安全通讯协议，提供解析和读写 X.509、PKCS #12、OpenPGP 和其他相关结构。特点是可移植性和高效。使用并没有OpenSSL广泛，也没有部署在iOS设备上，但是在Linux和很多开源程序当中有使用。

原文：[http://threatpost.com/goto-aside-gnutls-and-apple-bugs-are-not-the-same/104626](http://threatpost.com/goto-aside-gnutls-and-apple-bugs-are-not-the-same/104626)