# Mysql报错注入原理分析(count()、rand()、group by)

0x00 疑问
=======

* * *

一直在用mysql数据库报错注入方法，但为何会报错？

![](http://drops.javaweb.org/uploads/images/c9f5b008a50c9c737217acd2b133e77c48e38a90.jpg)

百度谷歌知乎了一番，发现大家都是把官网的结论发一下截图，然后执行sql语句证明一下结论，但是没有人去深入研究为什么rand不能和order by一起使用，也没彻底说明三者同时使用报错的原理。

![](http://drops.javaweb.org/uploads/images/ea3655d46556d5a12e0f5d0505e0ddca580bf166.jpg)

0x01 位置问题？
==========

* * *

`select count(*),(floor(rand(0)*2))x from information_schema.tables group by x;`这是网上最常见的语句,目前位置看到的网上sql注入教程,`floor`都是直接放`count(*)`后面，为了排除干扰，我们直接对比了两个报错语句，如下图

![](http://drops.javaweb.org/uploads/images/83cc7dbcb699ec42c2ae6da2cd74b08be5f13681.jpg)

由上面的图片，可以知道报错跟位置无关。

0x02 绝对报错还是相对报错？
================

* * *

是不是报错语句有了`floor(rand(0)*2)`以及其他几个条件就一定报错？其实并不是如此，我们先建建个表，新增一条记录看看，如下图：

![](http://drops.javaweb.org/uploads/images/060fa523567ac3f253385cec1a493e5082518384.jpg)

确认表中只有一条记录后，再执行报错语句看看，如下图：

![](http://drops.javaweb.org/uploads/images/d460da9382ad5546997b487ee654564d2392ab49.jpg)

多次执行均未发现报错。

然后我们新增一条记录。

![](http://drops.javaweb.org/uploads/images/0a844d6582ec6cdfec503f3a054af0427028bf9f.jpg)

然后再测试下报错语句

![](http://drops.javaweb.org/uploads/images/7c14ff0c7d646e8f78213c9a1cd3435d9354a2a6.jpg)

多次执行并没有报错

OK 那我们再增加一条

![](http://drops.javaweb.org/uploads/images/24358f070299bc8bcfbfead12b19e7f61caa8190.jpg)

执行报错语句

![](http://drops.javaweb.org/uploads/images/284d5a1f03a86289067f0685c7ce6fe98f88a4d9.jpg)

ok 成功报错

由此可证明`floor(rand(0)*2)`报错是有条件的，记录必须3条以上，而且在3条以上必定报错，到底为何？请继续往下看。

0x03 随机因子具有决定权么(rand()和rand(0))
===============================

* * *

为了更彻底的说明报错原因，直接把随机因子去掉，再来一遍看看，先看一条记录的时候，如下图:

![](http://drops.javaweb.org/uploads/images/ddb2d98fdf0a7de36176b5d28326afd3b79da12d.jpg)

一条记录的话 无论执行多少次也不报错

然后增加一条记录。

两条记录的话 结果就变成不确定性了

![](http://drops.javaweb.org/uploads/images/cbc5fb8df7b342a58e4e7a861b2022cd82077f8d.jpg)

![](http://drops.javaweb.org/uploads/images/3978efd2c305ca50400d8023fd48eddd97e811f1.jpg)

![](http://drops.javaweb.org/uploads/images/8b6bd7f55f5e31503a841f04f9ae8fadf52ed761.jpg)

随机出现报错。

然后再插入一条

三条记录之后，也和2条记录一样进行随机报错。

由此可见报错和随机因子是有关联的，但有什么关联呢，为什么直接使用`rand()`，有两条记录的情况下就会报错，而且是有时候报错，有时候不报错，而`rand(0)`的时候在两条的时候不报错，在三条以上就绝对报错？我们继续往下看。

0x04 不确定性与确定性
=============

* * *

前面说过，`floor(rand(0)*2)`报错的原理是恰恰是由于它的确定性，这到底是为什么呢？从0x03我们大致可以猜想到，因为`floor(rand()*2)`不加随机因子的时候是随机出错的，而在3条记录以上用`floor(rand(0)*2)`就一定报错，由此可猜想`floor(rand()*2)`是比较随机的，不具备确定性因素，而`floor(rand(0)*2)`具备某方面的确定性。

为了证明我们猜想，分别对`floor(rand()*2)`和`floor(rand(0)*2)`在多记录表中执行多次(记录选择10条以上)，在有12条记录表中执行结果如下图：

![](http://drops.javaweb.org/uploads/images/4e7c1588fa4c23213685cd680ca9591bc65b1307.jpg)

连续3次查询，毫无规则，接下来看看`select floor(rand(0)*2) from &#96;T-Safe&#96;;`，如下图：

![](http://drops.javaweb.org/uploads/images/15f6460a498c3d44834f89808210e723ffca16f8.jpg)

可以看到`floor(rand(0)*2)`是有规律的，而且是固定的，这个就是上面提到的由于是确定性才导致的报错，那为何会报错呢，我们接着往下看。

0x05 count与group by的虚拟表
=======================

* * *

使用`select count(*) from &#96;T-Safe&#96; group by x;`这种语句的时候我们经常可以看到下面类似的结果：

![](http://drops.javaweb.org/uploads/images/178bcec37db547b4a3a199983fd3d3c0dc4c3b35.jpg)

可以看出 test12的记录有5条

与`count(*)`的结果相符合，那么mysql在遇到`select count(*) from TSafe group by x;`这语句的时候到底做了哪些操作呢，我们果断猜测mysql遇到该语句时会建立一个虚拟表(实际上就是会建立虚拟表)，那整个工作流程就会如下图所示：

1.  先建立虚拟表，如下图(其中key是主键，不可重复):

![](http://drops.javaweb.org/uploads/images/72929abb8700d0b857580edebb031c8322f98c6c.jpg)

2.开始查询数据，取数据库数据，然后查看虚拟表存在不，不存在则插入新记录，存在则`count(*)`字段直接加1，如下图:

![](http://drops.javaweb.org/uploads/images/dd19d70809479c905c1121c834fbab196beb4b97.jpg)

由此看到 如果key存在的话就+1， 不存在的话就新建一个key。

那这个和报错有啥内在联系，我们直接往下来，其实到这里，结合前面的内容大家也能猜个一二了。

0x06 floor(rand(0)*2)报错
=======================

* * *

其实mysql官方有给过提示，就是查询的时候如果使用`rand()`的话，该值会被计算多次，那这个“被计算多次”到底是什么意思，就是在使用`group by`的时候，`floor(rand(0)*2)`会被执行一次，如果虚表不存在记录，插入虚表的时候会再被执行一次，我们来看下`floor(rand(0)*2)`报错的过程就知道了，从0x04可以看到在一次多记录的查询过程中`floor(rand(0)*2)`的值是定性的，为011011…(记住这个顺序很重要)，报错实际上就是`floor(rand(0)*2)`被计算多次导致的，具体看看`select count(*) from TSafe group by floor(rand(0)*2);`的查询过程：

1.查询前默认会建立空虚拟表如下图:

![](http://drops.javaweb.org/uploads/images/19145f4b9c35b1e9da343a730aa7f3959aa1dee0.jpg)

2.取第一条记录，执行`floor(rand(0)*2)`，发现结果为0(第一次计算),查询虚拟表，发现0的键值不存在，则`floor(rand(0)*2)`会被再计算一次，结果为1(第二次计算)，插入虚表，这时第一条记录查询完毕，如下图:

![](http://drops.javaweb.org/uploads/images/83c0898dd5e4dcfae13e5631a42271241a6256e2.jpg)

3.查询第二条记录，再次计算`floor(rand(0)*2)`，发现结果为1(第三次计算)，查询虚表，发现1的键值存在，所以`floor(rand(0)*2)`不会被计算第二次，直接`count(*)`加1，第二条记录查询完毕，结果如下:

![](http://drops.javaweb.org/uploads/images/498f3319031b312c34badca719486ae79877b408.jpg)

4.查询第三条记录，再次计算`floor(rand(0)*2)`，发现结果为0(第4次计算)，查询虚表，发现键值没有0，则数据库尝试插入一条新的数据，在插入数据时`floor(rand(0)*2)`被再次计算，作为虚表的主键，其值为1(第5次计算)，然而1这个主键已经存在于虚拟表中，而新计算的值也为1(主键键值必须唯一)，所以插入的时候就直接报错了。

5.整个查询过程`floor(rand(0)*2)`被计算了5次，查询原数据表3次，所以这就是为什么数据表中需要3条数据，使用该语句才会报错的原因。

0x07 floor(rand()*2)报错
======================

* * *

由0x05我们可以同样推理出不加入随机因子的情况，由于没加入随机因子，所以`floor(rand()*2)`是不可测的，因此在两条数据的时候，只要出现下面情况，即可报错，如下图:

![](http://drops.javaweb.org/uploads/images/e5fb3b67b5643f77a71f94bdf7d52cb90b0756db.jpg)

最重要的是前面几条记录查询后不能让虚表存在0,1键值，如果存在了，那无论多少条记录，也都没办法报错，因为`floor(rand()*2)`不会再被计算做为虚表的键值，这也就是为什么不加随机因子有时候会报错，有时候不会报错的原因。如图：

![](http://drops.javaweb.org/uploads/images/70b2d2f0069e64b2113bae484685fd0ed1f211a4.jpg)

当前面记录让虚表长成这样子后，由于不管查询多少条记录，`floor(rand()*2)`的值在虚表中都能找到，所以不会被再次计算，只是简单的增加`count(*)`字段的数量，所以不会报错，比如`floor(rand(1)*2)`，如图：

![](http://drops.javaweb.org/uploads/images/0ffbb16ad0a03eec99893417a29391068172a610.jpg)

在前两条记录查询后，虚拟表已经存在0和1两个键值了，所以后面再怎么弄还是不会报错。

总之报错需要`count(*)`，`rand()`、`group by`，三者缺一不可。