# 浅谈PHP弱类型安全

0x00 弱类型初探
==========

* * *

没有人质疑php的简单强大，它提供了很多特性供开发者使用，其中一个就是弱类型机制。

在弱类型机制下 你能够执行这样的操作

```
<?php
$var = 1;
$var = array();
$var = "string";
?>

```

php不会严格检验传入的变量类型，也可以将变量自由的转换类型。

比如 在$a == $b的比较中

*   $a = null; $b = false; //为真
*   $a = ''; $b = 0; //同样为真

然而，php内核的开发者原本是想让程序员借由这种不需要声明的体系，更加高效的开发，所以在**几乎所有内置函数以及基本结构**中使用了很多松散的比较和转换，防止程序中的变量因为程序员的不规范而频繁的报错，然而这却带来了安全问题。

0x02 知识预备 php内核之zval结构
======================

* * *

在PHP中声明的变量，在ZE中都是用结构体zval来保存的

zval的定义在zend/zend.h

```
typedef struct _zval_struct zval;  

struct _zval_struct {  
    /* Variable information */  
    zvalue_value value;     /* value */  
    zend_uint refcount__gc;  
    zend_uchar type;    /* active type */  
    zend_uchar is_ref__gc;  
};  

typedef union _zvalue_value {  
    long lval;  /* long value */  
    double dval;    /* double value */  
    struct {  
        char *val;  
        int len;  
    } str;  
    HashTable *ht;  /* hash table value */  
    zend_object_value obj;  
} zvalue_value;

```

其中php通过type判断变量类型 存入value

如上也就是php内核中弱类型的封装，也是我们后面讲的所有东西的原理和基础。

0x03变量的强制转换
===========

* * *

通过刚刚的了解，我们知道zval.type决定了存储到zval.value的类型。

当源代码进行一些未限制类型的比较，或数学运算的时候，可能会导致zval.type的改变，同时影响zval.value的内容改变。

当int遇上string
------------

##### cp.1 数学运算

当php进行一些数学计算的时候

```
var_dump(0 == '0'); // true
var_dump(0 == 'abcdefg'); // true  
var_dump(0 === 'abcdefg'); // false
var_dump(1 == '1abcdef'); // true 

```

当有一个对比参数是整数的时候，会把另外一个参数强制转换为整数。

相当于对字符串部分

intval再和整数部分比较,其实也就是改变了zval.type的内容 尤为注意的是，'1assd'的转换后的值是1，而‘asdaf’是0

也说明了intval会从第一位不是数字的单位开始进行

所有也有

```
var_dump(intval('3389a'));//输出3389

```

这个例子就告诉我们，永远不要相信下面的代码

```
if($a>1000){
    mysql_query('update ... .... set value=$a')
}

```

你以为这时候进入该支的万无一失为整数了

其实$a可能是1001/**/union...

#### cp.2 语句条件的松散判断

举个例子  
php的switch使用了松散比较. $which会被自动intval变成0  
如果每个case里面没有break ，就会一直执行到包含，最终执行到我们需要的函数，这里是成功包含

```
<?php
if (isset($_GET['which']))
{
        $which = $_GET['which'];
        switch ($which)
        {
        case 0:
        case 1:
        case 2:
                require_once $which.'.php';
                break;
        default:
                echo GWF_HTML::error('PHP-0817', 'Hacker NoNoNo!', false);
                break;
        }

```

#### cp.3 函数的松散判断

```
var_dump(in_array("abc", $array));

```

in_array — 检查数组中是否存在某个值 参数

needle 待搜索的值。

Note: 如果 needle 是字符串，则比较是区分大小写的。 haystack 这个数组。

strict 如果第三个参数 strict 的值为 TRUE 则 in_array() 函数还会检查 needle 的类型是否和 haystack 中的相同。

可以看到，只有加了strict才会对类型进行严格比较， 那么我们再次把整形和字符串进行比较呢？

```
var_dump(in_array("abc", $array1));</br>
var_dump(in_array("1bc", $array2));

```

它遍历了array的每个值，并且作"=="比较（“当设置了strict 用===”）

结果很明显了

如果array1里面有个值为0，那么第一条返回就会为真//intval('abc')=0

如果array2里面有个值为1，那么第二条就会为真//intval('1bc')=1

array_search也是一样的原理

这里的应用就很广泛了，

很多程序员都会检查数组的值，

那么我们完全可以用构造好的int 0或1 骗过检测函数，使它返回为真

总结一下，**在所有php认为是int的地方输入string，都会被强制转换**，比如

```
$a = 'asdfgh'；//字符串类型的a</br>
echo $a[2]；  //根据php的offset 会输出'd'</br>
echo $a[x]；  //根据php的预测，这里应该是int型，那么输入string，就会被intval成为0 也就是输出'a'

```

### 当数组遇上string

这一个例子我是在德国的一个ctf中遇到，很有意思  
前面我们讲的都是string和int的比较

那么array碰上int或者是string会有什么化学反应？

由php手册我们知道

Array转换整型int/浮点型float会返回元素个数；

转换bool返回Array中是否有元素；转换成string返回'Array'，并抛出warning。

那么实际应用是怎样的呢？

```
if(!strcmp($c[1],$d) && $c[1]!==$d){
...
}

```

可以发现，这个分支通过strcmp函数比较要求两者相等且“==”要求两者不相等才能进入。

strcmp() 函数比较两个字符串。

该函数返回：

```
0 - 如果两个字符串相等
<0 - 如果 string1 小于 string2
>0 - 如果 string1 大于 string2

```

这里的strcmp函数实际上是将两个变量转换成ascii 然后做数学减法，返回一个int的差值。

也就是说键入'a'和'a'进行比较得到的结果就是0

那么如果让$array和‘a’比较呢？

```
http://localhost:8888/1.php?a[]=1
var_dump(strcmp($_GET[a],'a'));

```

这时候php返回了null！

也就是说，我们让这个函数出错从而使它恒真，绕过函数的检查。  
下面给出一张松散比较的表格  

![](http://drops.javaweb.org/uploads/images/300a9ab1118b03246830166942f7fb415f20cbc1.jpg)  

0x04时时防备弱类型
===========

* * *

作为一个程序员，弱类型确实给程序员书写代码带来了很大的便利，但是也让程序员忘记了  
$array =array();的习惯。  
都说一切输入都是有害的

那么其实可以说一切输入的类型也是可疑的，永远不要相信弱类型的php下任何比较函数，任何数学运算。否则，你绝对是被php出卖的那一个。