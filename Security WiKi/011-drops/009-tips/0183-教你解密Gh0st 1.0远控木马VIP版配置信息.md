# 教你解密Gh0st 1.0远控木马VIP版配置信息

0x00 简介
-------

* * *

Gh0st是一款非常优秀的开源远程控制软件，由红狼小组的Cooldiyer开发。开源3.6发布后一段时间，作者对其进行大量重写并发布1.0 Alpha，这个版本是有VIP的，我也有幸收集到一套。 当你拿到一个别人的免杀木马你想做什么，学习免杀方法？而你由发现你拿到的样本你手头的控制端可以完美兼容，你想把配置信息修改了写个专版生成器吗？想？那就跟我来吧！（其实你看完文章也不会写，我也没有写过）

![enter image description here](http://drops.javaweb.org/uploads/images/78394697c5d601ab166af7a908b7492e416a487a.jpg)

0x01 分析过程
---------

* * *

本文用到的Ollydbg快捷键：

```
F9 运行程序/继续运行
F8 步过代码，遇到CALL容易跑飞建议少用
F7 跟进，不容易跑飞程序。
F2 下断点，然后F9可以跳过一些代码段。
F4 执行到所选行，常用。

```

想写生成器吗，前提条件要先把配置信息加密解密算法给解了，这里我从服务端exe入手，就不从生成器上下手了，毕竟我们多数情况只有服务端exe样本。

![enter image description here](http://drops.javaweb.org/uploads/images/e62a3ee3a1fd0a03dc4b464f701f31a35404305e.jpg)

注意看生成器下面“GH0STC+用户配置信息+GH0STC”，这就是我们要解密的字符串。假如我们现在才抓到服务端exe怎么找配置？一般情况能直观快速找到的，1、写在资源文件里面 2、写在exe、dll尾部附加数据上。（我写DRAT的时候这两种都试过），我们用C32ASM工具16进制编辑。拖到最后发现文件尾部有配置信息。大家是否觉得有点简单…… 难的篇幅太大不在本文考虑范围内。

![enter image description here](http://drops.javaweb.org/uploads/images/eb3db0a29e0e9c1dec8dffeb5d8105ae2ea6d213.jpg)

下面我们用动态调试工具Ollydbg打开，设置CreateFileW函数断点，这里我用工具直接设置，你也可以使用bp CreateFileW命令设置。为什么要这么做？它要读取自身配置肯定要“打开自己”所以断点设置在这个函数最合适，当然也有其他方法不在本文讨论范围，然后按F9把程序运行起来。

![enter image description here](http://drops.javaweb.org/uploads/images/7d4195488c93facad4fdb5ed4395952b1565ba47.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/b5dbbdbc41f8b685b5d295286566c6c2f3b0296e.jpg)

如上图所示的时候（如果不是的话继续按F9），我们按ALT+F9返回程序，按几下F8向下走。看到ReadFile函数还有CloseHandle、字符GH0STC，这个时候就说明程序已经把“配置”读取完了，正常情况下应该准备进入解密了。所以下面出现的CALL调用都要非常注意（一般要按F7进入，不要再按F8了可能会跳过关键）

![enter image description here](http://drops.javaweb.org/uploads/images/78c3ec92fd9d5adbff836f444fd84066c2d4cb6a.jpg)

看到这个CALL，我们用F7跟进，然后按多个F8直到下一个CALL。

```
004015F3  |.  E8 88FEFFFF   CALL server.00401480
n……
……
……

```

![enter image description here](http://drops.javaweb.org/uploads/images/d2f4396c1b865cb20de9fdc6f2084f0987cf8df0.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/deff6ced2e72f9b8b225c8046e19a7a769cbda08.jpg)

看到关键算法CALL（00401527，至于怎么判断的我只能说我事先做过功课了，实践中大家要多试试），我们还是用F7跟进（其他无用部分你可以用F2+F9或F4跳过即可）。

```
00401527  |.  E8 B4FEFFFF   CALL server.004013E0

```

在F7跟入就可以看到

![enter image description here](http://drops.javaweb.org/uploads/images/17b71579c2c364cbf753c77ce30765e20af5d565.jpg)

```
00401404  |> /8A1401        /MOV DL,BYTE PTR DS:[ECX+EAX]
00401407  |. |80EA 08       |SUB DL,8
0040140A  |. |80F2 20       |XOR DL,20
0040140D  |. |881401        |MOV BYTE PTR DS:[ECX+EAX],DL
00401410  |. |41            |INC ECX
00401411  |. |3BCE          |CMP ECX,ESI
00401413  |.^\7C EF         \JL SHORT server.00401404

```

这是解密算法关键部分记下地址，我们这里换个工具用IDA看看这个函数（004013E0）。 提示：IDA快速跳转地址快捷键是”G”，

![enter image description here](http://drops.javaweb.org/uploads/images/23c7520d87a7129d5f03b6fb1cd5bfeba04ad916.jpg)

转过去以后我喜欢用F5插件（Hex-Rays Decompiler），这里我直接按F5看C代码了（这部分操作就不截图装B了，事实是也没什么需要好截的）。

![enter image description here](http://drops.javaweb.org/uploads/images/f052b2defab68d98ff0793c170b2c8987c5225f5.jpg)

对比下OD里面的汇编代码慢慢品，你会发现关键代码就两行。

```
00401407  |.  80EA 08       |SUB DL,8
0040140A  |.  80F2 20       |XOR DL,20

```

有一个字符，减8和异或20的操作。

```
for (i = 0; i < len; i++)
{
    data[i] -= 0x8;
    data[i] ^= 0x20;
}

```

到这里我们已经找到关键算法部分，你可能没弄明白还是不知道怎么办。看下图的现成工具，实在懒的话自己百度找，或者你找一下gh0st 3.6开源代码然后差不多的改改就能用来解密了。

0x02 课后作业
---------

* * *

留下三个作业给喜欢折腾的同学： 1、继续看下004010D0函数作用（看了没看明白看下3.6代码）

2、对比一下gh0st 3.6加密解密字符和1.0有什么区别（其实最关键部分我已经说了，其他都是除了头尾“GH0STC”不一样其他没变化）

3、写个配套生成器，还是参考3.6代码改改就行。

我这里就不发样本和其他附件了，有需要的来“暗组”论坛。你想要的这里都有！

下面在附上1.0字符串解密核心代码： decode.h

```
static char base64[] = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";

static int pos(char c)
{
  char *p;
  for(p = base64; *p; p++)
    if(*p == c)
      return p - base64;
  return -1;
}

int base64_decode(const char *str, char **data)
{
  const char *s, *p;
  unsigned char *q;
  int c;
  int x;
  int done = 0;
  int len;
  s = (const char *)malloc(strlen(str));
  q = (unsigned char *)s;
  for(p=str; *p && !done; p+=4){
      x = pos(p[0]);
      if(x >= 0)
          c = x;
      else{
          done = 3;
          break;
      }
      c*=64;

      x = pos(p[1]);
      if(x >= 0)
          c += x;
      else
          return -1;
      c*=64;

      if(p[2] == '=')
          done++;
      else{
          x = pos(p[2]);
          if(x >= 0)
              c += x;
          else
              return -1;
      }
      c*=64;

      if(p[3] == '=')
          done++;
      else{
          if(done)
              return -1;
          x = pos(p[3]);
          if(x >= 0)
              c += x;
          else
              return -1;
      }
      if(done < 3)
          *q++=(c&0x00ff0000)>>16;

      if(done < 2)
          *q++=(c&0x0000ff00)>>8;
      if(done < 1)
          *q++=(c&0x000000ff)>>0;
  }

  len = q - (unsigned char*)(s);

  *data = (char*)realloc((void *)s, len);

  return len;
}

char* MyDecode(char *str)
{
    int     i, len;
    char    *data = NULL;
    len = base64_decode(str, &data);

    for (i = 0; i < len; i++)
    {
        data[i] -= 0x8;
        data[i] ^= 0x20;
    }
    return data;
}

```

[gh0st附件](http://drops.wooyun.org/wp-content/uploads/2014/11/gh0st%E9%99%84%E4%BB%B6.zip)