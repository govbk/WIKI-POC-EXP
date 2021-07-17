# Android SO逆向2-实例分析

0x00 概述
=======

* * *

[TOC]

这篇文章主要介绍几个简单的例子，来逆向分析so，当然有些破解可以在smali里直接修改，但是这里均采用逆向so的方式。

0x01 ARM—HEX转换
==============

1.将ARM指令转换为Hex时，可以使用工具Arm_Asm，如下图：

![img](http://drops.javaweb.org/uploads/images/8c7396054b32a2c59665eb2c42fdb91a5992d640.jpg)

2.可以根据ARM参考手册，手动转换。比如add的指令格式如下：

![img](http://drops.javaweb.org/uploads/images/27f6c842f16bc65ebeb0fb961318f26788616b77.jpg)

当执行add r0,#1时，Rdn为0，imm8为1，所以二进制为00110000 00000001，转换为16进制就是3001，所以Hex code就是0130

3.百度文库上有人上传了一份整理好的thumb指令集，如果不想到ARM参考手册上找，可以看看这个。

```
v is immed_value
n is Rn
m is Rm
s is Rs
r is register_list
c is condition      

表一：按指令字母升序排列
0100 0001 01mm mddd -- ADC Rd,Rm
0001 110v vvnn nddd -- ADD Rd,Rn,#immed_3
0011 0ddd vvvv vvvv -- ADD Rd,#immed_8
0001 100m mmnn nddd -- ADD Rd,Rn,Rm
0100 0100 hhmm mddd -- ADD Rd,Rm   h1h2,h1 is msb for Rd,h2 is msb for Rm
1010 0ddd vvvv vvvv -- ADD Rd,PC,#immed_8*4
1010 1ddd vvvv vvvv -- ADD Rd,SP,#immed_8*4
1011 0000 0vvv vvvv -- ADD SP,#immed_7*4
0100 0000 00mm mddd -- AND Rd,Rm
0001 0vvv vvmm mddd -- ASR Rd,Rm,#immed_5
0100 0001 00ss sddd -- ASR Rd,Rs
1101 cccc vvvv vvvv -- Bcc signed_immed_8
1110 0vvv vvvv vvvv -- B   signed_immed_11
0100 0011 10mm mddd -- BIC Rd,Rm
1011 1110 vvvv vvvv -- BKPT immed_8
111h hvvv vvvv vvvv -- BL(X) immed_11
0100 0111 1hmm mSBZ -- BLX Rm
0100 0111 0Hmm mSBZ -- BX Rm
0100 0010 11mm mnnn -- CMN Rn,Rm
0010 1nnn vvvv vvvv -- CMP Rn,#immed_8
0100 0010 10mm mnnn -- CMP Rn,Rm
0100 0101 hhmm mnnn -- CMP Rn,Rm
0100 0000 01mm mddd -- EOR Rd,Rm
1100 1nnn rrrr rrrr -- LDMIA Rn!,reg_list
0110 1vvv vvnn nddd -- LDR Rd,[Rn+#immed_5*4]
0101 100m mmnn nddd -- LDR Rd,[Rn,Rm]
0100 1ddd vvvv vvvv -- LDR Rd,[PC+#immed_5*4]
1001 1ddd vvvv vvvv -- LDR Rd,[SP,#immed_8*4]
0111 1vvv vvnn nmmm -- LDRB Rd,[Rn,#immed_5*4]
0101 110m mmnn nddd -- LDRV Rd,[Rn,Rm]
1000 1vvv vvnn nddd -- LDRH Rd,[Rn,#immed_5*2]
0101 101m mmnn nddd -- LDRH Rd,[Rn,Rm]
0101 011m mmnn nddd -- LDRSB Rd,[Rn,Rm]
0101 111m mmnn nddd -- LDRSH Rd,[Rn,Rm]
0000 0vvv vvmm mnnn -- LSL Rd,Rm,#immed_5
0100 0000 10ss sddd -- LSL Rd,Rs
0000 1vvv vvmm mddd -- LSR Rd,Rm,#immed_5
0100 0000 11ss sddd -- LSR Rd,Rs
0010 0ddd vvvv vvvv -- MOV Rd,#immed_8
0001 1100 00nn nddd -- MOV Rd,Rn
0100 0110 hhmm mddd -- MOV Rd,Rm
0100 0011 01mm mddd -- MUL Rd,Rm
0100 0011 11mm mddd -- MVN Rd,Rm
0100 0010 01mm mddd -- NEG Rd,Rm
0100 0011 00mm mddd -- ORR Rd,Rm
1011 110R rrrr rrrr -- POP reg_list
1011 010R rrrr rrrr -- PUSH reg_list
0100 0001 11ss sddd -- ROR Rd,Rs
0100 0001 10mm mddd -- SBC Rd,Rm
1100 0nnn rrrr rrrr -- STMIA Rn!,reg_list
0110 0vvv vvnn nddd -- STR Rd,[Rn,#immed_5*4]
0101 000m mmnn nddd -- STR Rd,[Rn,Rm]
1001 0ddd vvvv vvvv -- STR Rd,[SP,#immed_8*4]
0111 0vvv vvnn nddd -- STRB Rd,[Rn,#immed_5]
0101 010m mmnn nddd -- STRB Rd,[Rn,Rm]
1000 0vvv vvnn nddd -- STRH Rd,[Rn,#immed_5*2]
0101 001m mmnn nddd -- STRH Rd,[Rn,Rm]
0001 111v vvnn nddd -- SUB Rd,Rn,#immed_3
0011 1ddd vvvv vvvv -- SUB Rd,#immed_8
0001 101m mmnn nddd -- SUB Rd,Rn,Rm
1011 0000 1vvv vvvv -- SUB Sp,#immed_7*4
1101 1111 vvvv vvvv -- SWI immed_8
0100 0010 00mm mnnn -- TST Rn,Rm

表二：按指令机器码升序排列
0000 0vvv vvmm mnnn -- LSL Rd,Rm,#immed_5
0000 1vvv vvmm mddd -- LSR Rd,Rm,#immed_5
0001 0vvv vvmm mddd -- ASR Rd,Rm,#immed_5
0001 100m mmnn nddd -- ADD Rd,Rn,Rm
0001 101m mmnn nddd -- SUB Rd,Rn,Rm
0001 110v vvnn nddd -- ADD Rd,Rn,#immed_3
0001 111v vvnn nddd -- SUB Rd,Rn,#immed_3
0001 1100 00nn nddd -- MOV Rd,Rn
0010 0ddd vvvv vvvv -- MOV Rd,#immed_8
0010 1nnn vvvv vvvv -- CMP Rn,#immed_8
0011 0ddd vvvv vvvv -- ADD Rd,#immed_8
0011 1ddd vvvv vvvv -- SUB Rd,#immed_8
0100 0000 00mm mddd -- AND Rd,Rm
0100 0000 01mm mddd -- EOR Rd,Rm
0100 0000 10ss sddd -- LSL Rd,Rs
0100 0000 11ss sddd -- LSR Rd,Rs
0100 0001 00ss sddd -- ASR Rd,Rs
0100 0001 01mm mddd -- ADC Rd,Rm
0100 0001 10mm mddd -- SBC Rd,Rm
0100 0001 11ss sddd -- ROR Rd,Rs
0100 0010 00mm mnnn -- TST Rn,Rm
0100 0010 01mm mddd -- NEG Rd,Rm
0100 0011 00mm mddd -- ORR Rd,Rm
0100 0010 10mm mnnn -- CMP Rn,Rm
0100 0010 11mm mnnn -- CMN Rn,Rm
0100 0011 01mm mddd -- MUL Rd,Rm
0100 0011 10mm mddd -- BIC Rd,Rm
0100 0011 11mm mddd -- MVN Rd,Rm
0100 0100 hhmm mddd -- ADD Rd,Rm   h1h2,h1 is msb for Rd,h2 is msb for Rm
0100 0101 hhmm mnnn -- CMP Rn,Rm
0100 0110 hhmm mddd -- MOV Rd,Rm
0100 0111 0Hmm mSBZ -- BX Rm
0100 0111 1hmm mSBZ -- BLX Rm
0100 1ddd vvvv vvvv -- LDR Rd,[PC+#immed_5*4]
0101 000m mmnn nddd -- STR Rd,[Rn,Rm]
0101 001m mmnn nddd -- STRH Rd,[Rn,Rm]
0101 010m mmnn nddd -- STRB Rd,[Rn,Rm]
0101 011m mmnn nddd -- LDRSB Rd,[Rn,Rm]
0101 100m mmnn nddd -- LDR Rd,[Rn,Rm]
0101 101m mmnn nddd -- LDRH Rd,[Rn,Rm]
0101 110m mmnn nddd -- LDRV Rd,[Rn,Rm]
0101 111m mmnn nddd -- LDRSH Rd,[Rn,Rm]
0110 0vvv vvnn nddd -- STR Rd,[Rn,#immed_5*4]
0110 1vvv vvnn nddd -- LDR Rd,[Rn+#immed_5*4]
0111 1vvv vvnn nmmm -- LDRB Rd,[Rn,#immed_5*4]
0111 0vvv vvnn nddd -- STRB Rd,[Rn,#immed_5]
1000 0vvv vvnn nddd -- STRH Rd,[Rn,#immed_5*2]
1000 1vvv vvnn nddd -- LDRH Rd,[Rn,#immed_5*2]
1001 0ddd vvvv vvvv -- STR Rd,[SP,#immed_8*4]
1001 1ddd vvvv vvvv -- LDR Rd,[SP,#immed_8*4]
1010 0ddd vvvv vvvv -- ADD Rd,PC,#immed_8*4
1010 1ddd vvvv vvvv -- ADD Rd,SP,#immed_8*4
1011 0000 0vvv vvvv -- ADD SP,#immed_7*4
1011 0000 1vvv vvvv -- SUB Sp,#immed_7*4
1011 010R rrrr rrrr -- PUSH reg_list
1011 110R rrrr rrrr -- POP reg_list
1011 1110 vvvv vvvv -- BKPT immed_8
1100 0nnn rrrr rrrr -- STMIA Rn!,reg_list
1100 1nnn rrrr rrrr -- LDMIA Rn!,reg_list
1101 cccc vvvv vvvv -- Bcc signed_immed_8
1101 1111 vvvv vvvv -- SWI immed_8
1110 0vvv vvvv vvvv -- B   signed_immed_11
111h hvvv vvvv vvvv -- BL(X) immed_11

```

0x02 示例
=======

* * *

先对上篇文章中的switch分支进行逆向。

getSwitch()的代码如下：

```
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetSwitch_getSwitch
  (JNIEnv *, jclass, jint a, jint b, jint i){
    switch (i){
        case 1:
            return a + b;
            break;
        case 2:
            return a - b;
            break;
        case 3:
            return a * b;
            break;
        case 4:
            return a / b;
            break;
        default:
            return a + b;
            break;
        }
}

```

1.逆向APK后，使用IDA打开libs目录下的libHelloJNI.so，alt+t找到GetSwitch函数

![img](http://drops.javaweb.org/uploads/images/24238e49131aa0f65de41dda21e6cd722f16ff34.jpg)

![img](http://drops.javaweb.org/uploads/images/8cbbca3c7ba6e851a6eb62ba0286da1187d834db.jpg)

2.当我们传入的参数是4，2，2是，执行的是a - b,所以返回的结果是2

![img](http://drops.javaweb.org/uploads/images/15b4241f0595d5ef066a128094cca8db5b7a1060.jpg)

3.现在，我们将a - b改为a + b，就是要返回结果为6，找到i=2的减法分支，计算add ro,r2,r3的hex为D018

![img](http://drops.javaweb.org/uploads/images/acd2ee2ef2139fd4cf7ae2b5ae7e06ec9c75f5e8.jpg)

4.然后切换到Hex View，修改Hex为D018，再回到图形模式时，可以看到SUBS R0,R2,R3已经更改为ADDS R0,R2,R3了

![img](http://drops.javaweb.org/uploads/images/2d4b08ec558de2ef7472f71548c5d9334ffeda15.jpg)

![img](http://drops.javaweb.org/uploads/images/4098902e2ab841d1710abe694d1cc7e3c2f8e966.jpg)

5.使用010editor，ctrl+g跳转到104A的地址，修改Hex为D018，然后保存。

![img](http://drops.javaweb.org/uploads/images/c92c6e5d700be11fe06bc1d8ffc0a5435fb246ca.jpg)

6.重新编译成APK，运行时，发现结果已经变为6了。

![img](http://drops.javaweb.org/uploads/images/66b8cad8947c4ca599cdba20931e7c403aa5cb6c.jpg)

0x03 内购破解
=========

* * *

1.正常情况下，购买金币时，是需要付费的，因为使用的是模拟器，所以显示付费失败。

![img](http://drops.javaweb.org/uploads/images/64d08b358e37ca9076e361e0a137edcf0cf1c47b.jpg)

2.从smali中找到相应的so，IDA打开。找到函数GameCoin，先F5看一下，看到关键点GameMain::GameCoin = v3 + v1,就是当前游戏的金币数量，对应的汇编为：ADDS R0,R0,R6

![img](http://drops.javaweb.org/uploads/images/4f3bfbf8bd08eb6828a600387c8b52ad3b4b43bc.jpg)

![img](http://drops.javaweb.org/uploads/images/98d54c434592a020954ad30ff5637587fa038d47.jpg)

3.我们知道R0是返回值，R6是计算出的当前金币数，所以我们把此处改为ADDS R0,#255，所以每次都会增加255个金币，Hex为FF30

![img](http://drops.javaweb.org/uploads/images/90754b2838efa404d8e2c19374c9664d93917d7a.jpg)

![img](http://drops.javaweb.org/uploads/images/ca56bed756d2d50518275353901c25f23ce86e80.jpg)

4.修改后，初始金币为10，点击一次后，增加了255个。

![img](http://drops.javaweb.org/uploads/images/93c4fdcb2b22e3748451148fa0c99969582eec4f.jpg)

![img](http://drops.javaweb.org/uploads/images/7a09104e8f0e0c0aa19ec668b8312eaa48388d3e.jpg)

0x04 加密解密
=========

* * *

这篇文章是从吾爱破解([http://www.52pojie.cn/thread-396463-1-1.html](http://www.52pojie.cn/thread-396463-1-1.html))看到的，作者是adslxyz。

准备工具：

1.  IntelliJ IDEA
2.  baksmali
3.  AndroidKiller
4.  IDA6.6
5.  Fiddler
6.  一台Android真机(或者模拟器)
7.  eclipse

手机连上wifi，与电脑处于同一局域网，然后设置好Fiddler，具体步骤不详述。打开宝宝树孕育6.2.1版本，进入登陆窗口，输入账号密码点登陆，在电脑查看封包。可以得到请求URL:`http://www.babytree.com/api/muser/login`

```
POST：android_id=d77c45cb6182db0e&build_serial=mmmm&local_ts=1438682239&source_channel=pc_pregnancy_tongyong_app_140729&longitude=122.535462&latitude=35.582332&phone_number=buROv8rMh50AdCj7mYdAZwWv9YEpsIR2mClGrO43QK6E5GHko7aEZwtZMT%2F2nvyuUCYsFtx%2Bkz1kwpthbRlpZecGXjkbyaaeIE4ocYjolDyLXLduydRCjnG%2Bk9OEfBr3QCShaiJ2Z%2BeDQIeqgTssdlzZqzFfpHzsg3oWpdF3RbMLF3O93RzGWntJgkgvzjzK7BfwvRF8p8o6Se2l7mX7malpYrn35H2kh4mEAaLaBGoj2naCxcSXCn6X6w9za6hofkhogCtB7PpY6pulzY%2BOhejwG1jdoCpqRxcctRcsFPWNz72SD8Mmqkq6wRVeLYX5ZIoWNafwEJuPobuRtmvhQzg%3D%3D&version=6.2.1&imei=90000451032112&secret=b8a310e750c8af5187197c279a7e0241&email=zLkZURsmEpT8fGCGGNADu2KAZ79zkZI3b%2FMBDh5i1vCAbvFmKoGu7L4nBPsOvnzzsnWtuOJipiITnoRQ5w%2FNTy%2FvEx%2BX%2FO8Ff8jcU2qBAXTzGgd0x1lZ8PsGuan0944ax5n1douoaTC370Hv4A%2F58IhP8rhcQWnO4FzFol8FC%2FXQ%2Fd1%2FoAQOycwdLeBUm0JJ5tRKiaT2nBwD1z7Dn1CShswWCNN2zDCvYgtJ7Ig3JIQipUahL9OaR%2FQnzUzk%2BmaC%2Fm6iRr1q4wkiz9lexJkXFHf1g5VuFqshCNgxdgeDw%2BZHuagedfj5MakZD96Lj%2BtZtRf6GhaLbY29tSL65EdSgsg%3D%3D&password=AhOxbuypr6JYDgpP%2Fw%2BLhVlfzwusSMOaE0137YBOvOAZkk%2BbCHwzfduzqsjasx6zrhZUkZv3aoZ27HDIFAebdgsRS9lh2eeuxXiIxZdkaVPy47UNMdLHo1fFnuUEOCbE144H%2FL%2B2EeY%2BjbE8Ebjg0gXuZ7ziNZ%2Bmrgt4%2FrN8YbizcbyCx7A%2Fue3GD3p58GV3ztnlxWp9d4D1IlMT5V%2B8qxi3VDpQMr0Ghi4MaDTkH%2FV8fcRSCBqutHTDsEs%2F5AfBgksHFT6Dcxl3tpBIIfdgEmU4EZ%2BpqLqVxVFLdjPA0MJOhzE36P8NqTPiKEXzTuJcmaaS5qU34d2dHGYP2wc7Dg%3D%3D&client_type=android&app_id=pregnancy&mac=5c%3A51%5A57%3A55%3A26%3A4d&client_baby_status=1&bpreg_brithday=2100-01-01

```

分析可知：`phone_number`,`password`,`email`,`secret`四个参数为加密，其他参数均为固定或者地理位置信息等参数。所以此次目标就为这4个参数

1.  先把apk拖入AndroidKiller进行分析，可知无壳。
2.  根据先前分析，可在AndroidKiller中搜索相应字符串查找我们感兴趣的函数搜索`muser\login`,可知登陆的函数在`com.babytree.platform.api.muser`中的`login.smali`中。由图可知Login.java的父类是ApiBase,可以猜想,所有Api的请求所公共的函数都会在此类中生成。关键地方找一个就行,本次分析主要还是以动态调试为主.
3.  用baksmali将apk反编译成.smali文件
4.  然后打开IntelliJ IDEA,创建一个java工程.将上一步反编译出的smali文件导入到src文件夹中。如图:
    
    ![img](http://drops.javaweb.org/uploads/images/dbe4307fb3bb949712dca2693e6a6e53aef3cd74.jpg)
    
5.  然后打开eclipse，切换到DDMS视图,选中手机,查看其端口,如图:
    
    ![img](http://drops.javaweb.org/uploads/images/ee77cb775acac94dbaf27deb6babb6dadf0206ad.jpg)
    
    图上可以看到,目标应用的端口为8631.
    
6.  切换到IntelliJ IDEA,选择Run-Configurations.
    
7.  然后新建一个Remote,填写端口为8631,然后选择source using module's classpath为我们之前创建的项目,点击OK
    
8.  接下来在IntelliJ IDEA中打开Login.smali,快速浏览一下,选择一个感兴趣的地方下断点,这里我选择.method protected a()Ljava/lang/String;在函数起始处下断点后,在手机中输入账号密码,点击登陆,可以看到断点成功断下,如图所示:
    
    ![img](http://drops.javaweb.org/uploads/images/403647dfb5bd8751c9eb8646db5598354ed64979.jpg)
    
    从图中可以看到,左下角为函数的调用堆栈,从 登陆按钮 按下(OnClick),到api.user.login整个的调用过程。展开右下角的p0,可以看到此时已经生成了3个参数,
    
    ![img](http://drops.javaweb.org/uploads/images/bacef17783c1c133c76f0929d1709eee45670215.jpg)
    
    说明在断点之前,参数已经生成好了。所以我们按照函数的调用栈,挨个查看调用过的函数。查阅一番后可以发现。Login对象是在LoginActivity中的.method public a(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)V方法创建的。在new-instance v0, Lcom/babytree/platform/api/muser/Login;处下断点，重新点击登陆按钮，如图:
    
    ![img](http://drops.javaweb.org/uploads/images/e01e1495ff34faa113fd20f2f4f66f8c54e5a733.jpg)
    
    此时v1.v2.v3寄存器分别出现了加密的结果，由上可知，分别对应`phone_number`,`password`,`email`三个参数。
    
    所以加密的函数应该就在上面。往上下断点,重新来一次观察一下加密的过程。
    
    可知：
    
    ```
    iget-object v0, p0, Lcom/babytree/apps/pregnancy/activity/LoginActivity;->u:Ljava/lang/String;
    
    ```
    
    这一句函数调用之后,v0是一串固定字符串。
    
    ```
    invoke-static {p1, v0}, Lcom/babytree/apps/pregnancy/h/a;->a(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;
    
    ```
    
    调用之后,v1为加密结果。查看a函数:
    
    ![img](http://drops.javaweb.org/uploads/images/42b4d8b7a3605eb76e7987f02313cb28281bc3e5.jpg)
    
    为RSA加密，所以之前的v0就是RSA的pubKey了。在a函数中下断点，看一看加密的参数是什么:
    
    ![img](http://drops.javaweb.org/uploads/images/a3a660b21780db09c3ad2492448dde485258896d.jpg)
    
    一切尽收眼底。由此可知`phone_number`,`password`,`email`三个参数的算法。
    
9.  接下来找`secret`的算法。
    
    回到AndroidKiller搜索关键字，定位到`com/babytree/platform/api/ApiCommonParams;`大致看一下，这个是API通用参数生成的类。且加载了一个so：api_encrypt.so在`secret`关键字附近看一下，调用了so的`invoke-static {v1, v2}, Lcom/babytree/platform/api/ApiCommonParams;->nativeGetParam(Landroid/content/Context;Ljava/util/List;)Ljava/lang/String;`方法。
    
    我们先在这句上面下个断点，看看传给so函数的是什么参数。断点断下后，看到传递给so的参数是一个List,POST参数中除`secret`之外的所有参数。参数知道了，调用点知道了。分析一下so，看看需不需要动态调试。载入ida，找到调用的nativeGetParam函数。大致看一下，发现又调用了java的md5函数，好了，调试so的步骤剩下了。
    
    ![img](http://drops.javaweb.org/uploads/images/346588523c6aa61dfe6c4f58ac0a05b87492fe68.jpg)
    
    回到IntelliJ IDEA,在getMD5Str处下断点,继续调试:
    
    ![img](http://drops.javaweb.org/uploads/images/2431b23eb0657778f18d7f26c95c4e0cec3f24ba.jpg)
    
    很快我们可以知道,p0中就是进行md5的参数啦。
    
    分析一下可知，`secret`就是 MD5(时间戳+所有参数排序+&asdf12341dfas!@#$%()(Ujjlasdflasdfj;asjdf23412313kljajsdflasjdflasjdflajsdf;lajsdf2342234sdfsdfffds)
    

总结:

动态调试apk的方式让我们了解apk运作的过程，通过动静结合的分析方式，快速找到想要的东西～

0x05 签名校验
=========

* * *

将关键代码放到so中，在底层获取签名信息并验证。因为获取和验证的方法都封闭在更安全的so库里面，能够起到一定意义上的保护作用。实例如下：

1.  在程序中搜索getSignature,发现并没有调用此函数的地方,猜测在so文件中,搜索loadLibrary。
    
    ![img](http://drops.javaweb.org/uploads/images/af5b64c43bf044569bcc7b681716b34014a2773e.jpg)
    
2.  在代码中可以查找,可以找到调用的是signaturex.so
    
3.  使用IDA打开signaturex.so,然后搜索getSiganture,找到调用此函数的地方。从代码中可以看到,此函数调用了org.cocos2dx.cpp.AppActivity.getSignature
    
    ![img](http://drops.javaweb.org/uploads/images/5558728109bf42fbe66d4c1ea7d987fb581deedf.jpg)
    
    ![img](http://drops.javaweb.org/uploads/images/c6ab60c2b3706e45dc4686f358d35ce8aa9c38d1.jpg)
    
4.  查看F5代码,发现此函数是判断签名的函数,然后我们双击此函数的调用者,部分代码如下。
    
    ![img](http://drops.javaweb.org/uploads/images/b67c42548b7f223894942a5a8d988d6889abba20.jpg)
    
5.  从上图可以看出,只需要修改BEQ loc_11F754,让其不跳转到jjni——>error,就可以绕过签名校验。 查看HEX,使用010editor跳到0011F73E,修改D0为D1。成功绕过签名校验。
    
    ![img](http://drops.javaweb.org/uploads/images/d3f02f45cc54f7d5b13d6380d7df74daba0fb3dc.jpg)