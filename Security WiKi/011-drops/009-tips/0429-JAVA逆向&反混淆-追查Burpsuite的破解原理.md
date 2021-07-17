# JAVA逆向&反混淆-追查Burpsuite的破解原理

0x00 摘要：
--------

* * *

本系列文章通过对BurpLoader的几个版本的逆向分析，分析Burpsuite的破解原理，分析Burpsuite认证体系存在的安全漏洞。

0x01 JD-GUI的用途与缺陷：
------------------

* * *

JD-GUI是一款从JAVA字节码中还原JAVA源代码的免费工具，一般情况下使用这款工具做JAVA逆向就足够了，但是由于其原理是从JAVA字节码中按照特定结构来还原对应的JAVA源代码，因此一旦字节码结构被打乱（比如说使用混淆器），那么JD-GUI就会失去它的作用，如图为使用JD-GUI打开Burpsuite时的显示：

![enter image description here](http://drops.javaweb.org/uploads/images/c127d6bc907b93cd27e40b3837e7eeb6de62bc13.jpg)

显然，JD-GUI没能还原JAVA源代码出来，因为Burpsuite使用了混淆器打乱了字节码结构 所以，JD-GUI适用于‘没有使用混淆器’的JAVA字节码，而缺陷是一旦字节码结构被打乱，则无法发挥它的作用

0x02 字节码分析：
-----------

* * *

Java的字节码并不像普通的二进制代码在计算机中直接执行，它通过JVM引擎在不同的平台和计算机中运行。

![enter image description here](http://drops.javaweb.org/uploads/images/207695ac811e3dcdfe28af7069db0db634c76da5.jpg)

JVM是一个基于栈结构的虚拟计算机，使用的是JVM操作码（及其助记符），在这一点上和普通二进制反汇编的过程非常相似。 对Java字节码进行反编译其实非常简单，JDK内置的Javap工具即可完成这项任务。

示例：对Javar.class进行反编

![enter image description here](http://drops.javaweb.org/uploads/images/995ef2662c85bba3784fff6eae68e8d7108562ef.jpg)

注意javap的-c参数是显示详细代码，否则只显示method，而按照java的老规矩Javar不要加后缀名 同时你也可以使用eclipse的插件Bytecode Visualizer来反编译字节码

![enter image description here](http://drops.javaweb.org/uploads/images/e4d66dacb7e2036b95e52cbba883f02dcbf3b3d2.jpg)

注意右面的流程图，大家在上程序设计导论课时都画过吧，现在发现它的用途了吧，一眼就看出是一个if-else结构，前两句定义i变量，然后取i=2压栈常数1，比对i和1以后就都java.lang.system.out了，一个输出wooyun，一个输出lxj616。

0x03 老版本的BurpLoader分析：
----------------------

* * *

随着Burpsuite的更新，BurpLoader也在跟着进行更新，我们从老版本的BurpLoader入手，简要分析一下之前老版本的burpsuite破解原理。 本处选用了1.5.01版本的BurpLoader进行分析 首先试着用JD-GUI载入BurpLoader：

![enter image description here](http://drops.javaweb.org/uploads/images/4f094cedb51aa8b31e68b4b3a0a40aa5a9b383b1.jpg)

成功还原了BurpLoader源代码，只可惜由于是对burpsuite的patch，所以burpsuite的混淆在burploader里仍然可读性极差，不过可以推断burploader本身没有使用混淆工具。

```
public static void main(String[] args)
  {
    try
    {
      int ret = JOptionPane.showOptionDialog(null, "This program can not be used for commercial purposes!", "BurpLoader by larry_lau@163.com", 0, 2, null, new String[] { "I Accept", "I Decline" }, null);
      //显示选择对话框：这程序是出于学习目的写的，作者邮箱larry_lau(at)163.com 
      if (ret == 0)  //选择我同意
      {
        //以下用到的是java反射机制，不懂反射请百度
        for (int i = 0; i < clzzData.length; i++)
        {
          Class clzz = Class.forName(clzzData[i]);
          //是burpsuite的静态类（名字被混淆过了，也没必要列出了）
          Field field = clzz.getDeclaredField(fieldData[i]);
         //静态类中的变量也被混淆过了，也不必列出了
          field.setAccessible(true);
        //访问private必须先设置这个，不然会报错

          field.set(null, strData[i]);
        //把变量设置成strData（具体那一长串到底是什么暂不讨论）
        }

        Preferences prefs = Preferences.userNodeForPackage(StartBurp.class);
        //明显preferences是用来存储设置信息的
        for (int i = 0; i < keys.length; i++)
        {
          // key和val能猜出是什么吧
          String v = prefs.get(keys[i], null);
          if (!vals[i].equals(v))
          {
            prefs.put(keys[i], vals[i]);
          }
        }
        StartBurp.main(args);
      }
    }
    catch (Exception e)
    {
      JOptionPane.showMessageDialog(null, "This program can only run with burpsuite_pro_v1.5.01.jar", "BurpLoader by larry_lau@163.com", 
        0);
    }
  }
}

```

因此，BurpLoader的原理就是伪造有效的Key来通过检测，Key的输入是通过preference来注入的，而我猜测它为了固定Key的计算方法，通过反射把一些环境变量固定成常量了

0x04 新版本的BurpLoader分析：
----------------------

* * *

以下用1.6beta版的BurpLoader进行分析： 首先用JD-GUI尝试打开BurpLoader：

![enter image description here](http://drops.javaweb.org/uploads/images/fe55ee57c4803fda7bc990b273a773d59ffb1aa1.jpg)

看来这个版本的BurpLoader对字节码使用了混淆，这条路走不通了 于是直接读字节码吧！

![enter image description here](http://drops.javaweb.org/uploads/images/1e7327a2c03239985a6f86bd9c02f65470a9ce33.jpg)

大家可以看到这里的字符串都是混淆过的，每一个都jsr到151去解密

![enter image description here](http://drops.javaweb.org/uploads/images/9fd76c83db54e9eb9f8da1e0faec6987cd809b63.jpg)

这段解密代码特点非常明显，一个switch走5条路，给221传不同的解密key，这不就是Zelix KlassMaster的算法吗？ 简单的异或而已，轻松写出解密机：

```
public class Verify {
    private static String decrypt(String str) {
        char key[] = new char[] {73,25,85,1,29};
        char arr[] = str.toCharArray();
        for (int i = 0; i < arr.length; i++) {
            arr[i] ^= key[i % 5];
        }
        return new String(arr);
    }

    public static void main (String args[]) {
        System.out.println(decrypt("%x'sdgu4t3#x#`egj\"hs.7%m|/7;hp+l&/S t7tn\5v:j\'}_dx%"));
    }
}

```

里面的5个密钥就是上图bipush的传参，别忘了iconst_1的那个1 解密出来是：`larry.lau.javax.swing.plaf.nimbus.NimbusLook:4`

其实这里解密出字符串没有什么用处，因为我们已经拿到老版本的源代码了，不过在别的软件逆向分析中可能会非常有用

0x05 总结&POC
-----------

* * *

以下为我修改后的BurpLoader，其中的恶意代码我已经去除，并将修改前的原值输出，大家可以在添加burpsuite jar包后编译运行这段代码

```
package stratburp;

import burp.StartBurp; 
import java.lang.reflect.Field; 
import java.util.prefs.Preferences; 
import javax.swing.JOptionPane; 

public class startburp 
{ 

  private static final String[] clzzData = { "burp.ecc", "burp.voc", "burp.jfc",  
    "burp.gtc", "burp.zi", "burp.q4c", "burp.pid", "burp.y0b" }; 

  private static final String[] fieldData = { "b", "b", "c", "c", "c", "b", "c", "c" }; 
  private static final String errortip = "This program can only run with burpsuite_pro_v1.5.01.jar"; 
  private static final String[] keys = { "license1", "uG4NTkffOhFN/on7RT1nbw==" }; 

  public static void main(String[] args) 
  { 
    try 
    { 
        for (int i = 0; i < clzzData.length; i++) 
        { 
          Class clzz = Class.forName(clzzData[i]); 
          Field field = clzz.getDeclaredField(fieldData[i]); 
          field.setAccessible(true); 

          //field.set(null, strData[i]); 
          System.out.println(field.get(null));
        } 

        Preferences prefs = Preferences.userNodeForPackage(StartBurp.class); 
        for (int i = 0; i < keys.length; i++) 
        { 
          String v = prefs.get(keys[i], null); 
          System.out.println(prefs.get(keys[i], null));
        } 
        StartBurp.main(args); 
    } 
    catch (Exception e) 
    { 
      JOptionPane.showMessageDialog(null, "This program can only run with burpsuite_pro_v1.5.01.jar", "Notice",0); 
    } 
  } 
}

```

其效果如截图所示

![enter image description here](http://drops.javaweb.org/uploads/images/445a1bbcd0ab988e799e9545b5d4930edf64ac60.jpg)

其中前8行输出为之前BurpLoader恶意修改的目标原值（对我的计算机而言），同一台设备运行多少遍都是不变的，后面的key由于我之前运行过BurpLoader因此是恶意修改后的值（但是由于前8行没有修改因此不能通过Burpsuite验证），可见BurpLoader其实是使用了同一个密钥来注册所有不同计算机的，只不过修改并固定了某些参与密钥计算的环境变量而已，这大概就是Burpsuite破解的主要思路了，至于最初能用的license是怎么计算出来的，我们以后再研究