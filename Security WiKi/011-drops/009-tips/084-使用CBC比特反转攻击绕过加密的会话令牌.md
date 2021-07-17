# 使用CBC比特反转攻击绕过加密的会话令牌

0x01 什么是CBC比特反转技术？
==================

* * *

CBC模式的全称是密文分组链接模式（Cipher Block Chainning)，之所以叫这个名字，是因为密文分组是想链条一样相互连接在一起的.

如图所示：

![enter image description here](http://drops.javaweb.org/uploads/images/bfecc54e04e4c1d11d39d838b16863d4336ac994.jpg)

在CBC模式中，首先将明文分组与前一个密文分组进行XOR运算，然后再进行加密，当加密第一个明文分组时，由于不存在“前一个密文分组”，因此需要事先准备一个长度为一个分组的比特序列来代替“前一个密文分组”，这个比特序列称为初始化向量（Initialization vector),通常缩写为IV,如果每次都使用相同的初始化向量（IV），当用同一密钥对同一明文进行加密时，所得到的密码一定是相同的，所以每次加密时都会随机产生一个不同的比特序列来作为初始化向量，避免这种情况产生。

CBC比特反转攻击的目的是攻击者通过修改密文来操纵解密后的明文，攻击者会对初始化向量（IV）中的任意比特位进行反转（1变0，0变1），则明文分组（解密后得到的明文分组）中相应的比特也会被反转。比如一个叫admin的用户，登录，经过CBC模式加密后，token为"aaabbbccc999",现在有一个攻击者，叫john，登录，经过CBC模式加密后，token为cccbbbccc1111,现在john将token改为"ffcbbbccc1111"，发现登录名变成了_ohn，所以他知道token第一个位的ff转换成了_，经过几轮测试，他发现如果将token改为“7bcbbbccc1111”，则登录名变成了'aohn'，最后他通过发送token为7bdc995465到服务器，发现自己已经变成了admin。

0x02 攻击演示
=========

* * *

我这里演示是使用的是Owasp Mutilidae测试平台，通过依次点击左侧导航栏的”Owasp 2013” ，“Broken authentication and session management”，“Privilege escalation”,“view user privileges”，你能够看到这个挑战的目标是改变UID和GID到000，通过burpsuite已经抓到了IV，并把这个请求发送到burpsuite的Repeater，方便我们以后测试，如图

![enter image description here](http://drops.javaweb.org/uploads/images/a7a0205d09029c262bb3613daa7392ef40cd501c.jpg)

当前抓到的IV值为“6bc24fc1ab650b25b4114e93a98f1eba”

下面先改变“6bc24fc1ab650b25b4114e93a98f1eba”为“FFc24fc1ab650b25b4114e93a98f1eba”，观察变化，如图：

![enter image description here](http://drops.javaweb.org/uploads/images/5edf17612d6ac5e09742f93001c50bc61539d938.jpg)

发现Application ID部分有一个字符变了，接着转换字符，当IV为FFFFFFFFFF650b25b4114e93a98f1eba”时，发现User ID变成e00了。如图

![enter image description here](http://drops.javaweb.org/uploads/images/da30b640bb2d6f6ca289b25f771ef91274808565.jpg)

现在看看能不能影响到Group ID，当iv为FFFFFFFFFFFFFFFFb4114e93a98f1eba时，Group ID有变化了，如图

![enter image description here](http://drops.javaweb.org/uploads/images/d8539cd9220b176276e8b6c464db3297f191a0c1.jpg)

我们要改变的仅仅是userID和GroupID，把FFFFFFFFFFFFFFFFb4114e93a98f1eba依次还原，最终找到对应项时，iv为6bc24fc1FF650bFFb4114e93a98f1eba，如图

![enter image description here](http://drops.javaweb.org/uploads/images/9d89c349dba5cf02260ca68a03a773fb93aba780.jpg)

我们发现第一个FF对应的是USERID的e，e的十六进制编码是0x65,经过异或，0xFF xor 0x65 =0x9a,现在我们的目标是需要USERID都为0 (对应的十六进制是0x30)，所以0x9a xor 0x30 = 0xaa,我们提交iv为6bc24fc1aa650bFFb4114e93a98f1eba，USERID就是我们想要的结果了，如图

![enter image description here](http://drops.javaweb.org/uploads/images/24d956e167269ecc42acee9ee4f781f923980755.jpg)

然后我们让GROUPID也为0，则0xFF xor 0xeb = 0x14，0x30 xor 0x14 = 0x24，我们提交iv为6bc24fc1aa650b24b4114e93a98f1eba。如图

![enter image description here](http://drops.javaweb.org/uploads/images/35fd58607cb97ba81d4e9d5da8a9f5529f9eb3c4.jpg)

0x03 参考文档
=========

* * *

Bypassing encrypted session tokens using CBC bit flipping technique.

http://swepssecurity.blogspot.tw/2014/05/bypassing-encrypted-session-tokens.html

<<图解密码技术>>