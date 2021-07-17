# 那些年做过的ctf之加密篇

最近ctf做的比较多，顺便整理一下做个笔记，大概有加密篇、隐写篇、逆向破解和web方向的几篇文章，整理出来之后会陆续发出来。

0x01 Base64
===========

* * *

> Base64:`ZXZhbCgkX1BPU1RbcDRuOV96MV96aDNuOV9qMXVfU2gxX0oxM10pNTU2NJC3ODHHYWJIZ3P4ZWY=`

Base64编码要求把3个8位字节（3*8=24）转化为4个6位的字节（4*6=24），之后在6位的前面补两个0，形成8位一个字节的形式。 如果剩下的字符不足3个字节，则用0填充，输出字符使用'='，因此编码后输出的文本末尾可能会出现1或2个'='

Base32: Base32和Base64相比只有一个区别就是，用32个字符表示256个ASC字符，也就是说5个ASC字符一组可以生成8个Base字符，反之亦然。

在线编解码：[http://base64.xpcha.com/](http://base64.xpcha.com/)

0x02 希尔密码
=========

* * *

> 希尔密码：密文：`22,09,00,12,03,01,10,03,04,08,01,17`（明文：`wjamdbkdeibr`）

解题思路：使用的矩阵是 1 2 3 4 5 6 7 8 10

原文链接：[http://bobao.360.cn/ctf/learning/136.html](http://bobao.360.cn/ctf/learning/136.html)

百度百科：[http://baike.baidu.com/link?url=R6oWhCdKvzlG8hB4hdIdUT1cZPbFOCrpU6lJAkTtdiKodD7eRTbASpd_YVfi4LMl7N8yFyhVNOz5ki6TC7_5eq](http://baike.baidu.com/link?url=R6oWhCdKvzlG8hB4hdIdUT1cZPbFOCrpU6lJAkTtdiKodD7eRTbASpd_YVfi4LMl7N8yFyhVNOz5ki6TC7_5eq)

0x03 栅栏密码
=========

* * *

> 栅栏密码：把要加密的明文分成N个一组，然后把每组的第1个字连起来，形成一段无规律的话。

密文样例：`tn c0afsiwal kes,hwit1r  g,npt  ttessfu}ua u  hmqik e {m,  n huiouosarwCniibecesnren.`

解密程序：

```
char s[]= "tn c0afsiwal kes,hwit1r  g,npt  ttessfu}ua u  hmqik e {m,  n huiouosarwCniibecesnren.";  
char t[86]= "";  
int i,j,k;
k=0;
for (i=0;i<17;i++)  
{  
      for(j=0;j<5;j++)  
      {  
                t[k++]= ch[j*17+i];  
      }  
}  
for(i=0;i<85;i++)
{
    printf("%c",t[i]);
}  

```

原文链接：[http://blog.csdn.net/shinukami/article/details/45980629](http://blog.csdn.net/shinukami/article/details/45980629)

0x04 凯撒密码
=========

* * *

> 凯撒密码：通过把字母移动一定的位数来实现加密和解密。明文中的所有字母都在字母表上向后（或向前）按照一个固定数目进行偏移后被替换成密文。

密文样例：`U8Y]:8KdJHTXRI>XU#?!K_ecJH]kJG*bRH7YJH7YSH]*=93dVZ3^S8*$:8"&:9U]RH;g=8Y!U92'=j*$KH]ZSj&[S#!gU#*dK9\.`

解题思路：得知是凯撒加密之后，尝试进行127次轮转爆破：

```
lstr="""U8Y]:8KdJHTXRI>XU#?!K_ecJH]kJG*bRH7YJH7YSH]*=93dVZ3^S8*$:8"&:9U]RH;g=8Y!U92'=j*$KH]ZSj&[S#!gU#*dK9\."""  
  
for p in range(127):  
    str1 = ''  
    for i in lstr:  
        temp = chr((ord(i)+p)%127)  
        if 32<ord(temp)<127 :  
            str1 = str1 + temp   
            feel = 1  
         else:  
             feel = 0  
             break  
     if feel == 1:  
         print(str1)

```

原文链接：[http://blog.csdn.net/shinukami/article/details/46369765](http://blog.csdn.net/shinukami/article/details/46369765)

0x05 Unicode
============

* * *

密文样例：`\u5927\u5bb6\u597d\uff0c\u6211\u662f\u0040\u65e0\u6240\u4e0d\u80fd\u7684\u9b42\u5927\u4eba\uff01\u8bdd\u8bf4\u5fae\u535a\u7c89\u4e1d\u8fc7\`

在线解密：[tool.chinaz.com/Tools/Unicode.aspx](http://tool.chinaz.com/Tools/Unicode.aspx)

0x06 brainfuck
==============

* * *

类型：

```
++++++++++[>+++++++>++++++++++>+++>+<<<<-]
>++.>+.+++++++..+++.>++.<<+++++++++++++++.
>.+++.------.--------.>+.>.

```

利用BFVM.exe直接解密

用法`loadtxt 1.txt`

在线解密：[http://www.splitbrain.org/services/ook](http://www.splitbrain.org/services/ook)

0x07 摩斯密码
=========

* * *

密文样例：`--  ---  .-.  ...  .`

*   [http://www.jb51.net/tools/morse.htm](http://www.jb51.net/tools/morse.htm)
*   [http://msjm.yinxiulei.cn/](http://msjm.yinxiulei.cn/)

0x08 jsfuck
===========

* * *

密文中 `()[]{}!+`

在线解密：

*   [www.jsfuck.com](http://www.jsfuck.com/)
*   [http://patriciopalladino.com/files/hieroglyphy/](http://patriciopalladino.com/files/hieroglyphy/)

0x09 培根密码
=========

* * *

培根所用的密码是一种本质上用二进制数设计的。不过，他没有用通常的0和1来表示，而是采用a和b。

百科：[http://baike.baidu.com/link?url=acaeI3babB7MogPQFh98rDAVSwHfPwh-HnEFTb9cx7DZ5Nz4MkMA14H4SDjBNnOdBsJpliNYa1vnfikQGqvA7K](http://baike.baidu.com/link?url=acaeI3babB7MogPQFh98rDAVSwHfPwh-HnEFTb9cx7DZ5Nz4MkMA14H4SDjBNnOdBsJpliNYa1vnfikQGqvA7K)

0x0A 猪圈密码又称共济会密码
================

* * *

百度百科：[http://baike.baidu.com/link?url=yN39kWG2pGd9XHo3RjeUAbd7xs0QlnJ2uHzCJfxC03V-fJcQUdfcJ-WuGoAkKGFVE0AxFK4-98wa4FtzvxRA0_](http://baike.baidu.com/link?url=yN39kWG2pGd9XHo3RjeUAbd7xs0QlnJ2uHzCJfxC03V-fJcQUdfcJ-WuGoAkKGFVE0AxFK4-98wa4FtzvxRA0_)

0x0B CRC32
==========

* * *

密文样例：`4D1FAE0B`

```
import zlib
def crc32(st):
    crc = zlib.crc32(st)
    if crc > 0:
      return "%x" % (crc)
    else:
      return "%x" % (~crc ^ 0xffffffff)

```

原文链接：[http://blog.csdn.net/ab748998806/article/details/46382017](http://blog.csdn.net/ab748998806/article/details/46382017)

对于其他一些未知密文，可尝试到下列几个网站转换试试，看看运气

*   [http://web.chacuo.net/charsetuuencode](http://web.chacuo.net/charsetuuencode)
*   [http://blog.csdn.net/ab748998806/article/details/46368337](http://blog.csdn.net/ab748998806/article/details/46368337)