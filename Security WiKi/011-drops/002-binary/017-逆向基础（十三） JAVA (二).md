# 逆向基础（十三） JAVA (二)

54.7 线性同余伪随机数生成器
----------------

* * *

这次来看一个简单的伪随机函数生成器，之前我在书中提到过一次。

```
public class LCG
{
    public static int rand_state;
    public void my_srand (int init)
    {
        rand_state=init;
    }
    public static int RNG_a=1664525;
    public static int RNG_c=1013904223;

    public int my_rand ()
    {
        rand_state=rand_state*RNG_a;
        rand_state=rand_state+RNG_c;
        return rand_state & 0x7fff;
    }
}

```

在上面的代码中我们可以看到开始的地方有两个类字段被初始化。不过java究竟是如何进行初始化的呢，我们可以通过javap的输出看到类构造的方式。

```
static {};
flags: ACC_STATIC
Code:
stack=1, locals=0, args_size=0
0: ldc #5 // int 1664525
2: putstatic #3 // Field RNG_a:I
5: ldc #6 // int 1013904223
7: putstatic #4 // Field RNG_c:I
10: return

```

从上面的代码我们可以直观的看出变量如何被初始化，RNG_a和iRNG_C分别占用了第三以及第四储存位，并使用puststatic指令将常量put进储存位置。

下面的my_srand()函数将输入值存储到rand_state中;

```
public void my_srand(int);
flags: ACC_PUBLIC
Code:
stack=1, locals=2, args_size=2
0: iload_1
1: putstatic #2 // Field ⤦
Ç rand_state:I
4: return

```

iload_1 取得输入值并将其压入栈。但为什么不用iload_0? 因为函数中可能使用了类字段，所以这个变量被作为第0个参数传递给了函数，我们可以看到rand_state字段在类中占用第二个储存位。之前的putstatic会从栈顶复制数据并且将其压入第二储存位。

现在的my_rand():

```
public int my_rand();
flags: ACC_PUBLIC
Code:
stack=2, locals=1, args_size=1
0: getstatic #2 // Field ⤦
Ç rand_state:I
3: getstatic #3 // Field RNG_a:I
6: imul
7: putstatic #2 // Field ⤦
Ç rand_state:I
10: getstatic #2 // Field ⤦
Ç rand_state:I
13: getstatic #4 // Field RNG_c:I
16: iadd
17: putstatic #2 // Field ⤦
Ç rand_state:I
20: getstatic #2 // Field ⤦
Ç rand_state:I
23: sipush 32767
26: iand
27: ireturn

```

它仅是加载了所有对象字段的值。并且用putstatic指令对rand_state的值进行更新。

因为之前我们通过putstatic指令将rand_state的值丢弃，所以在20行的位置，再次加载rand_state值。这种方式其实效率不高，不过我们还是要承认jvm在某些地方所做的优化还是很不错的。

54.8 条件跳转
---------

* * *

我们来举个条件跳转的栗子：

```
public class abs
{
    public static int abs(int a)
    {
        if (a<0)
            return -a;
        return a;
    }
}

```

* * *

```
public static int abs(int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=1, locals=1, args_size=1
0: iload_0
1: ifge 7
4: iload_0
5: ineg
6: ireturn
7: iload_0
8: ireturn

```

上面代码中ifge指令的作用是:当栈顶的值大于等于0的时候跳转到偏移位7，需要注意的是，任何的ifXX指令都会将栈中的值弹出用于进行比较。

现在来看另外一个例子

```
public static int min (int a, int b)
{
    if (a>b)
        return b;
    return a;
}

```

我们得到的是：

```
public static int min(int, int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=2, args_size=2
0: iload_0
1: iload_1
2: if_icmple 7
5: iload_1
6: ireturn
7: iload_0
8: ireturn

```

if_icmple会从栈中弹出两个值进行比较，如果第二个小于或者等于第一个，那么跳转到偏移位7.

我们看另一个max函数的例子：

```
public static int max (int a, int b)
{
    if (a>b)
        return a;
    return b;
}

```

从下面可以看出代码都差不多，唯一的区别是最后两个iload指令（偏移位5和偏移位7）互换了。

```
public static int max(int, int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=2, args_size=2
0: iload_0
1: iload_1
2: if_icmple 7
5: iload_0
6: ireturn
7: iload_1
8: ireturn

```

更复杂的例子。。

```
public class cond
{
    public static void f(int i)
    {
        if (i<100)
            System.out.print("<100");
        if (i==100)
            System.out.print("==100");
        if (i>100)
            System.out.print(">100");
        if (i==0)
            System.out.print("==0");
    }
}

```

* * *

```
public static void f(int);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=1, args_size=1
0: iload_0
1: bipush 100
3: if_icmpge 14
6: getstatic #2 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
9: ldc #3 // String <100
11: invokevirtual #4 // Method java/io⤦
Ç /PrintStream.print:(Ljava/lang/String;)V
14: iload_0
15: bipush 100
17: if_icmpne 28
20: getstatic #2 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
23: ldc #5 // String ==100
25: invokevirtual #4 // Method java/io⤦
Ç /PrintStream.print:(Ljava/lang/String;)V
28: iload_0
29: bipush 100
31: if_icmple 42
34: getstatic #2 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
37: ldc #6 // String >100
39: invokevirtual #4 // Method java/io⤦
Ç /PrintStream.print:(Ljava/lang/String;)V
42: iload_0
43: ifne 54
46: getstatic #2 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
49: ldc #7 // String ==0
51: invokevirtual #4 // Method java/io⤦
Ç /PrintStream.print:(Ljava/lang/String;)V
54: return

```

if_icmpge出栈两个值，并且比较两个数值，如果第的二个值大于第一个，跳转到偏移位14，if_icmpne和if_icmple做的工作类似，但是使用不同的判断条件。

在行偏移43的ifne指令，它的名字不是很恰当，我更愿意把它命名为ifnz(if not zero 可能是冷笑话)(如果栈定的值不是0则跳转)，当不是0的时候，跳转到偏移54，如果输入的值不是另，如果是0，执行流程进入偏移46，并且打印字符串“==0”。

JVM没有无符号数据类型，所以，只能通过符号整数值进行比较指令操作。

54.9 传递参数值
----------

* * *

让我们稍微扩展一下min()和max()这个例子。

```
public class minmax
{
    public static int min (int a, int b)
    {
        if (a>b)
            return b;
        return a;
    }
    public static int max (int a, int b)
    {
        if (a>b)
            return a;
        return b;
    }
    public static void main(String[] args)
    {
        int a=123, b=456;
        int max_value=max(a, b);
        int min_value=min(a, b);
        System.out.println(min_value);
        System.out.println(max_value);
    }
}

```

下面是main()函数的代码。

```
public static void main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=5, args_size=1
0: bipush 123
2: istore_1
3: sipush 456
6: istore_2
7: iload_1
8: iload_2
9: invokestatic #2 // Method max:(II⤦
Ç )I
12: istore_3
13: iload_1
14: iload_2
15: invokestatic #3 // Method min:(II⤦
Ç )I
18: istore 4
20: getstatic #4 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
23: iload 4
25: invokevirtual #5 // Method java/io⤦
Ç /PrintStream.println:(I)V
28: getstatic #4 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
31: iload_3
32: invokevirtual #5 // Method java/io⤦
Ç /PrintStream.println:(I)V
35: return

```

栈中的参数被传递给其他函数，并且将返回值置于栈顶。

54.10位。
-------

* * *

java中的位操作其实与其他的一些ISA（指令集架构）类似：

```
public static int set (int a, int b)
{
    return a | 1<<b;
}

public static int clear (int a, int b)
{
    return a & (~(1<<b));
}

```

* * *

```
public static int set(int, int);
  flags: ACC_PUBLIC, ACC_STATIC
  Code:
    stack=3, locals=2, args_size=2
    0: iload_0
    1: iconst_1
    2: iload_1
    3: ishl
    4: ior
    5: ireturn

public static int clear(int, int);
  flags: ACC_PUBLIC, ACC_STATIC
  Code:
    stack=3, locals=2, args_size=2
    0: iload_0
    1: iconst_1
    2: iload_1
    3: ishl
    4: iconst_m1
    5: ixor
    6: iand
    7: ireturn

```

iconst_m1加载-1入栈，这数其实就是16进制的0xFFFFFFFF，将0xFFFFFFFF作为XOR-ing指令执行的操作数。起到的效果就是把所有bits位反向，（A.6.2在1406页）

我将所有数据类型，扩展成64为长整型。

```
public static long lset (long a, int b)
{
    return a | 1<<b;
}
public static long lclear (long a, int b)
{
    return a & (~(1<<b));
}

```

* * *

```
public static long lset(long, int);
  flags: ACC_PUBLIC, ACC_STATIC
  Code:
    stack=4, locals=3, args_size=2
    0: lload_0
    1: iconst_1
    2: iload_2
    3: ishl
    4: i2l
    5: lor
    6: lreturn
public static long lclear(long, int);
  flags: ACC_PUBLIC, ACC_STATIC
  Code:
    stack=4, locals=3, args_size=2
    0: lload_0
    1: iconst_1
    2: iload_2
    3: ishl
    4: iconst_m1
    5: ixor
    6: i2l
    7: land
    8: lreturn

```

代码是相同的，但是操作64位值的指令的前缀变成了L，并且第二个函数参数还是int类型，当32位需要升级为64位值时，会使用i21指令把整型扩展成64位长整型.

54.11循环
-------

* * *

```
public class Loop
{
    public static void main(String[] args)
    {
        for (int i = 1; i <= 10; i++)
        {
            System.out.println(i);
        }
    }
}

```

* * *

```
public static void main(java.lang.String[]);
flags: ACC_PUBLIC, ACC_STATIC
Code:
stack=2, locals=2, args_size=1
0: iconst_1
1: istore_1
2: iload_1
3: bipush 10
5: if_icmpgt 21
8: getstatic #2 // Field java/⤦
Ç lang/System.out:Ljava/io/PrintStream;
11: iload_1
12: invokevirtual #3 // Method java/io⤦
Ç /PrintStream.println:(I)V
15: iinc 1, 1
18: goto 2
21: return

```

icont_1将1推入栈顶，istore_1将其存入到局部数组变量的储存位1。

可以注意到没有使用第0个储存位，因为main()函数只有一个指向其的引用的参数(String数组)，就位于第0号槽中。

因此，本地变量i 总是在第1储存位中。 在行偏移3和行偏移5的位置，指令将i和10进行比较。如果i大于10，执行流将进入偏移21，之后函数会结束，如果i小于或等于10，则调用println。我们可以看到i在偏移11进行了重新加载，用于调用println。

多说一句，我们调用pringln打印数据类型是整型，我们看注释，“i，v”，i的意思是整型，v的意思是返回void。

当println函数结束时，i进入偏移15，通过指令iinc将参数槽1的值，数值1与本地变量相加。

goto指令就是跳转，它跳转偏移2，就是循环体的开始地址.

下面让我们来处理更复杂的例子

```
public class Fibonacci
{
    public static void main(String[] args)
    {
        int limit = 20, f = 0, g = 1;
        for (int i = 1; i <= limit; i++)
        {
            f = f + g;
            g = f - g;
            System.out.println(f);
        } 
    }
}

```

* * *

```
￼public static void main(java.lang.String[]);
  flags: ACC_PUBLIC, ACC_STATIC
  Code:
    stack=2, locals=5, args_size=1
       0: bipush        20
       2: istore_1
       3: iconst_0
       4: istore_2
       5: iconst_1
       6: istore_3
       7: iconst_1
       8: istore        4
      10: iload         4
      12: iload_1
      13: if_icmpgt     37
      16: iload_2
      17: iload_3
      18: iadd
      19: istore_2
      20: iload_2
      21: iload_3
      22: isub
      23: istore_3
      24: getstatic     #2

```

