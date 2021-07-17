# 逆向基础（十三） JAVA (一)

翻译书籍:Reverse Engineering for Beginners

作者:Dennis Yurichev

翻译者:糖果

54.1介绍
------

* * *

大家都知道，java有很多的反编译器（或是产生JVM字节码） 原因是JVM字节码比其他的X86低级代码更容易进行反编译。

a).多很多相关数据类型的信息。

b).JVM（java虚拟机）内存模型更严格和概括。

c).java编译器没有做任何的优化工作（JVM JIT不是实时），所以，类文件中的字节代码的通常更清晰易读。

JVM字节码知识什么时候有用呢？

a).文件的快速粗糙的打补丁任务，类文件不需要重新编译反编译的结果。

b).分析混淆代码

c).创建你自己的混淆器。

d).创建编译器代码生成器（后端）目标。

我们从一段简短的代码开始，除非特殊声明，我们用的都是JDK1.7

反编译类文件使用的命令，随处可见：`javap -c -verbase.`

在这本书中提供的很多的例子，都用到了这个。

54.2 返回一个值
----------

可能最简单的java函数就是返回一些值，oh，并且我们必须注意，一边情况下，在java中没有孤立存在的函数，他们是“方法”(method)，每个方法都是被关联到某些类，所以方法不会被定义在类外面， 但是我还是叫他们“函数” (function),我这么用。

```
public class ret
{
    public static int main(String[] args)
    {
        return 0;
    }
}

```

编译它。

```
javac ret.java

```

使用Java标准工具反编译。

```
javap -c -verbose ret.class

```

会得到结果：

```
public static int main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: iconst_0
1: ireturn

```

对于java开发者在编程中，0是使用频率最高的常量。 因为区分短一个短字节的 iconst_0指令入栈0，iconst_1指令（入栈），iconst_2等等，直到iconst5。也可以有iconst_m1, 推送-1。

就像在MIPS中，分离一个寄存器给0常数：3.5.2 在第三页。

栈在JVM中用于在函数调用时，传参和传返回值。因此， iconst_0是将0入栈，ireturn指令，（i就是integer的意思。）是从栈顶返回整数值。

让我们写一个简单的例子， 现在我们返回1234：

```
public class ret
{
    public static int main(String[] args)
    {
        return 1234;
    }
}

```

我们得到：

清单：

```
54.2:jdk1.7(节选) 
public static int main(java.lang.String[]); 
flags: ACC_PUBLIC, ACC_STATIC Code: stack=1, locals=1, args_size=1 0: sipush 1234 3: ireturn

```

sipush(shot integer)如栈值是1234,slot的名字以为着一个16bytes值将会入栈。 sipush(短整型) 1234数值确认时候16-bit值。

```
public class ret
{
    public static int main(String[] args)
    {
        return 12345678;
    }
}

```

更大的值是什么？

清单 54.3 常量区

```
...
#2 = Integer 12345678
...

```

5栈顶

```
public static int main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATI
Code:
stack=1, locals=1, args_size=1
0: ldc #2 // int 12345678
2: ireturn

```

操作码 JVM的指令码操作码不可能编码成32位数，开发者放弃这种可能。因此，32位数字12345678是被存储在一个叫做常量区的地方。让我们说（大多数被使用的常数（包括字符，对象等等车）） 对我们而言。

对JVM来说传递常量不是唯一的，MIPS ARM和其他的RISC CPUS也不可能把32位操作编码成32位数字，因此 RISC CPU（包括MIPS和ARM）去构造一个值需要一系列的步骤，或是他们保存在数据段中： 28。3 在654页.291 在695页。

MIPS码也有一个传统的常量区，literal pool(原语区) 这个段被叫做"lit4"(对于32位单精度浮点数常数存储) 和lit8(64位双精度浮点整数常量区)

布尔型

```
public class ret
{
    public static boolean main(String[] args)
    {
        return true;
    }
}

```

* * *

```
public static boolean main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: iconst_1

```

这个JVM字节码是不同于返回的整数学 ，32位数据，在形参中被当成逻辑值使用。像C/C++，但是不能像使用整型或是viceversa返回布尔型，类型信息被存储在类文件中，在运行时检查。

16位短整型也是一样。

```
public class ret
{

    public static short main(String[] args)
    {
        return 1234;
    }
}

```

* * *

```
public static short main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: sipush 1234
3: ireturn

```

还有char 字符型？

```
public class ret
{
    public static char main(String[] args)
    {
        return 'A';
    }
}

```

* * *

```
public static char main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: bipush 65
2: ireturn

```

bipush 的意思"push byte"字节入栈，不必说java的char是16位UTF16字符，和short 短整型相等，单ASCII码的A字符是65，它可能使用指令传输字节到栈。

让我们是试一下byte。

```
public class retc
{
    public static byte main(String[] args)
    {
        return 123;
    }
}

```

* * *

```
public static byte main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC

Code:
stack=1, locals=1, args_size=1
0: bipush 123
2: ireturn
909

```

也许会问，位什么费事用两个16位整型当32位用？为什么char数据类型和短整型类型还使用char.

答案很简单，为了数据类型的控制和代码的可读性。char也许本质上short相同，但是我们快速的掌握它的占位符，16位的UTF字符，并且不像其他的integer值符。使用 short,为各位展现一下变量的范围被限制在16位。在需要的地方使用boolean型也是一个很好的主意。代替C样式的int也是为了相同的目的。

在java中integer的64位数据类型。

```
public class ret3
{
    public static long main(String[] args)
    {
        return 1234567890123456789L;
    }
}

```

清单54.4常量区

```
...
#2 = Long 1234567890123456789l
...
public static long main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=1, args_size=1
0: ldc2_w #2 // long ⤦
Ç 1234567890123456789l
3: lreturn

```

64位数也被在存储在常量区，ldc2_w 加载它，lreturn返回它。 ldc2_w指令也是从内存常量区中加载双精度浮点数。（同样占64位）

```
public class ret
{
    public static double main(String[] args)
    {
        return 123.456d;
    }
}

```

清单54.5常量区

```
...
#2 = Double 123.456d
...
public static double main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=1, args_size=1
0: ldc2_w #2 // double 123.456⤦
Ç d
3: dreturn
dreturn 代表 "return double"

```

最后，单精度浮点数：

```
public class ret
{
    public static float main(String[] args)
    {
        return 123.456f;
    }
}

```

清单54.6 常量区

```
...
#2 = Float 123.456f
...
public static float main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: ldc #2 // float 123.456f
2: freturn

```

此处的ldc指令使用和32位整型数据一样，从常量区中加载。freturn 的意思是"return float"

那么函数还能返回什么呢？

```
public class ret
{
    public static void main(String[] args)
    {
        return;
    }
}

```

* * *

```
public static void main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=0, locals=1, args_size=1
0: return

```

这以为着，使用return控制指令确没有返回实际的值，知道这一点就非常容易的从最后一条指令中演绎出函数（或是方法）的返回类型。

54.3 简单的计算函数
------------

* * *

让我们继续看简单的计算函数。

```
public class calc
{
    public static int half(int a)
    {
        return a/2;
    }
}

```

这种情况使用icont_2会被使用。

```
public static int half(int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=1, args_size=1
0: iload_0
1: iconst_2
2: idiv
3: ireturn

```

iload_0 将零给函数做参数，然后将其入栈。iconst_2将2入栈，这两个指令执行后，栈看上去是这个样子的。

```
+---+
TOS ->| 2 |
+---+
| a |
+---+

```

idiv携带两个值在栈顶， divides 只有一个值，返回结果在栈顶。

```
+--------+
TOS ->| result |
+--------+

```

ireturn取得比返回。 让我们处理双精度浮点整数。

```
public class calc
{
    public static double half_double(double a)
    {
        return a/2.0;
    }
}

```

清单54.7 常量区

```
...
#2 = Double 2.0d
...
public static double half_double(double);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=4, locals=2, args_size=1
0: dload_0
1: ldc2_w #2 // double 2.0d
4: ddiv
5: dreturn

```

类似，只是ldc2_w指令是从常量区装载2.0，另外，所有其他三条指令有d前缀，意思是他们工作在double数据类型下。

我们现在使用两个参数的函数。

```
public class calc
{
    public static int sum(int a, int b)
    {
        return a+b;
    }
}

```

* * *

```
public static int sum(int, int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=2, args_size=2
0: iload_0
1: iload_1
2: iadd
3: ireturn

```

iload_0加载第一个函数参数（a)，iload_2 第二个参数(b)下面两条指令执行后，栈的情况如下：

```
+---+
TOS ->| b |
+---+
| a |
+---+

```

iadds 增加两个值，返回结果在栈顶。

```
+--------+ TOS ->| result | +--------+

```

让我们把这个例子扩展成长整型数据类型。

```
public static long lsum(long a, long b)
{
    return a+b;
}

```

我们得到的是：

```
public static long lsum(long, long);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=4, locals=4, args_size=2
0: lload_0
1: lload_2
2: ladd
3: lreturn

```

第二个（load指令从第二参数槽中，取得第二参数。这是因为64位长整型的值占用来位，用了另外的话2位参数槽。）

稍微复杂的例子

```
public class calc
{
    public static int mult_add(int a, int b, int c)
    {
        return a*b+c;
    }
}

```

* * *

```
public static int mult_add(int, int, int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=3, args_size=3
0: iload_0
1: iload_1
2: imul
3: iload_2
4: iadd
5: ireturn

```

第一是相乘，积被存储在栈顶。

```
+---------+
TOS ->| product |
+---------+

```

iload_2加载第三个参数（C）入栈。

```
+---------+
TOS ->| c |
+---------+
| product |
+---------+

```

现在iadd指令可以相加两个值。

54.4 JVM内存模型
------------

* * *

X86和其他低级环境系统使用栈传递参数和存储本地变量，JVM稍微有些不同。

主要体现在： 本地变量数组（LVA）被用于存储到来函数的参数和本地变量。iload_0指令是从其中加载值，istore存储值在其中，首先，函数参数到达：开始从0 或者1(如果0参被this指针用。)，那么本地局部变量被分配。

每个槽子的大小都是32位，因此long和double数据类型都占两个槽。

操作数栈（或只是"栈"），被用于在其他函数调用时，计算和传递参数。不像低级X86的环境，它不能去访问栈，而又不明确的使用pushes和pops指令，进行出入栈操作。

54.5 简单的函数调用
------------

* * *

mathrandom()返回一个伪随机数，函数范围在「0.0...1.0)之间，但对我们来说，由于一些原因，我们常常需要设计一个函数返回数值范围在「0.0...0.5)

```
public class HalfRandom
{
    public static double f()
    {
        return Math.random()/2;
    }
}

```

常量区

```
...
#2 = Methodref #18.#19 // java/lang/Math.⤦
Ç random:()D
6(Java) Local Variable Array

#3 = Double 2.0d
...
#12 = Utf8 ()D
...
#18 = Class #22 // java/lang/Math
#19 = NameAndType #23:#12 // random:()D
#22 = Utf8 java/lang/Math
#23 = Utf8 random
public static double f();
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=4, locals=0, args_size=0
0: invokestatic #2 // Method java/⤦
Ç lang/Math.random:()D
3: ldc2_w #3 // double 2.0d
6: ddiv
7: dreturn

```

java本地变量数组 916 静态执行调用math.random()函数，返回值在栈顶。结果是被0.5初返回的，但函数名是怎么被编码的呢？ 在常量区使用methodres表达式,进行编码的，它定义类和方法的名称。第一个methodref 字段指向表达式，其次，指向通常文本字符（"java/lang/math"） 第二个methodref表达指向名字和类型表达式，同时链接两个字符。第一个方法的名字式字符串"random",第二个字符串是"()D",来编码函数类型，它以为这两个值（因此D是字符串）这种方式1JVM可以检查数据类型的正确性：2）java反编译器可以从被编译的类文件中修改数据类型。

最后，我们试着使用"hello，world！"作为例子。

```
public class HelloWorld
{
    public static void main(String[] args)
    {
        System.out.println("Hello, World");
    }
}

```

常量区

917 常量区的ldc行偏移3，指向"hello，world！"字符串，并且将其入栈，在java里它被成为饮用，其实它就是指针，或是地址。

```
...
#2 = Fieldref #16.#17 // java/lang/System.⤦
Ç out:Ljava/io/PrintStream;
#3 = String #18 // Hello, World
#4 = Methodref #19.#20 // java/io/⤦
Ç PrintStream.println:(Ljava/lang/String;)V
...
#16 = Class #23 // java/lang/System
#17 = NameAndType #24:#25 // out:Ljava/io/⤦
Ç PrintStream;
#18 = Utf8 Hello, World
#19 = Class #26 // java/io/⤦
Ç PrintStream
#20 = NameAndType #27:#28 // println:(Ljava/⤦
Ç lang/String;)V
...
#23 = Utf8 java/lang/System
#24 = Utf8 out
#25 = Utf8 Ljava/io/PrintStream;
#26 = Utf8 java/io/PrintStream
#27 = Utf8 println
#28 = Utf8 (Ljava/lang/String;)V
...
public static void main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=1, args_size=1
0: getstatic #2 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
3: ldc #3 // String Hello, ⤦
Ç World
5: invokevirtual #4 // Method java/io⤦
Ç /PrintStream.println:(Ljava/lang/String;)V
8: return

```

常见的invokevirtual指令，从常量区取信息，然后调用pringln()方法，貌似我们知道的println()方法，适用于各种数据类型，我这种println()函数版本，预先给的是字符串类型。

但是第一个getstatic指令是干什么的？这条指令取得对象信息的字段的一个引用或是地址。输出并将其进栈，这个值实际更像是println放的指针，因此，内部的print method取得两个参数，输入1指向对象的this指针，2）"hello，world"字符串的地址，确实，println()在被初始化系统的调用，对象之外，为了方便，javap使用工具把所有的信息都写入到注释中。

54.6 调用beep()函数
---------------

* * *

这可能是最简单的，不使用参数的调用两个函数。

```
public static void main(String[] args)
{
    java.awt.Toolkit.getDefaultToolkit().beep();
};

```

* * *

```
public static void main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: invokestatic #2 // Method java/⤦
Ç awt/Toolkit.getDefaultToolkit:()Ljava/awt/Toolkit;
3: invokevirtual #3 // Method java/⤦
Ç awt/Toolkit.beep:()V
6: return

```

首先，invokestatic在0行偏移调用javaawt.toolkit. getDefaultTookKit()函数,返回toolkit类对象的引用，invokedvirtualIFge指令在3行偏移，调用这个类的beep（）方法。