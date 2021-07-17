# Wargama-leviathan Writeup

level 0
=======

* * *

这一关就是一个简单的游戏介绍，当然，还有明文的账号密码。打开网页就能看到，不再叙述。

level 0 -> 1
============

* * *

使用上一关得到的账号和密码，`ssh`登陆到目标机器。

![ssh_level1.png](http://drops.javaweb.org/uploads/images/3706039061c0f383223d333a2950b46f599fccfe.jpg)

在主目录下面，我们可以发现一个`.backup`文件夹，进入文件夹，发现了一个`html`文件，看样子是浏览器收藏夹文件。我猜测密码应该是在文件中以明文形式出现，用关键字`leviathan`进行搜索，立刻就能得到密码。`the password for leviathan1 is rioGegei8m`。这道题应该就是让你熟悉命令的。

![leviathan_password_level1](http://drops.javaweb.org/uploads/images/2cb658dce3978e8c6b893c77ad20f573e7ea04bb.jpg)

level 1 -> 2
============

* * *

使用上一个level得到的密码，ssh到下一个level。在这关的`home`目录里面，我们看到一个名为`check`的`set-uid`程序，执行程序，看看程序执行结果。

![leviathan_check_level1](http://drops.javaweb.org/uploads/images/d175a7c6c5cfbc9c424c40c3f2b4ec318a3526d0.jpg)

程序要求我们输入一个密码，好吧。我不知道该输入什么，猜想程序应该是将我们的输入和某个密码做比较，然后再执行。随便输入一个，观察结果。

![leviathan_check_failure_level1](http://drops.javaweb.org/uploads/images/f7c7d146847da239017a8a8f967ecb380d8e62f5.jpg)

打开`GDB`神器，看看它内部到底是个什么东西。

![leviathan_gdb_level1.png](http://drops.javaweb.org/uploads/images/89d0ed1a617c44a7df7b3d92c1db834df7183551.jpg)

从图中我们可以看看出来，程序三次调用`getchar()`，猜想，`password`应该是三个字符。`strcmp()`函数的一个参数是我们输入的字符的存储起始地址，另一个地址是`0x18(%esp)`，程序一开始在这里存储了一个值`0x786573`，然后将两个地址作为实参送入`strcmp()`，所以猜想，这里`0x18(%esp)`就是我们需要的密码。这个值正好是`sex`的十六进制格式，于是，得到密码是`sex`。输入程序，得到下一个level的密码。

![leviathan_crack_level1](http://drops.javaweb.org/uploads/images/16e2177dff8ae02db84e7983202e0ae282db7df1.jpg)

level 2 -> 3
============

* * *

在这个level的`home`目录里面，依然是一个`set-uid`的程序，执行程序得到如下结果，还是要使用神器`gdb`。

![leviathan_home_level2](http://drops.javaweb.org/uploads/images/a728880245dd88e4d4403c9f3a70dca9f72b1555.jpg)

使用`gdb`打开程序，这个程序主函数反汇编出来的结果有点长，不过貌似没有看到子函数调用，只有一个主函数。

![leviathan_gdb_level2](http://drops.javaweb.org/uploads/images/8e4f8283e87b5dd8308bdd87ed1ae99ede0b368b.jpg)

这个程序首先进行了参数检查，如果没有命令行参数输入，则打印出错信息，然后退出。之后使用`access()`进行文件权限检查，如果没有权限，则打印出错信息，然后退出。然后再使用`system()`函数执行`/bin/cat fileinput`这个命令。

![leviathan_error_level2](http://drops.javaweb.org/uploads/images/c0ecfb7c2a74945143195f459387fdbff2908b09.jpg)

*   根据`access()`的手册，`access() checks whether the calling process can access the file pathname. If **pathname** is a symbolic link, it is dereferenced.`

这就意味着我们不能利用`符号链接`来过这个权限检查。

从`gdb`的反汇编代码，我们可以得到，程序使用输入的命令行参数构造了`/bin/cat argv[1]`这个字符串，然后送入`system()`这个函数执行。于是我猜想到构造这么一个字符串`/bin/cat < /etc/leviathan_pass/leviathan2`。这样就可以通过权限检查，然后得到密码了。

*   构造一个文件，名为`<file`
*   构造一个符号链接，`file->/etc/leviathan_pass/leviathan2`

这样，系统进行权限检查的时候，则检查的是`<file`这个文件的权限，但是执行命令的时候却是`/bin/cat < file`这个命令。

![leviathan_pass_level2](http://drops.javaweb.org/uploads/images/32b82c17742d9768bcee32ad21f363a46f28abb8.jpg)

level 3 -> 4
============

* * *

还是一个`set-uid`程序，老流程走起，打开程序，看看它是那个小怪。

![leviathan_home_level3](http://drops.javaweb.org/uploads/images/416590cc90ea19847d7932ddf7a227a01906e532.jpg)

还是要`gdb`走起啊。

![leviathan_gdb_main_level3](http://drops.javaweb.org/uploads/images/4225584c92f517501bd0a7bfaa6362ea9a41e54d.jpg)

这里的`strcmp()`函数为什么调用我没有理解，或许是为了干扰吧，在`main()`函数中有一个`do_stuff()`函数调用，整个程序的逻辑应该在这个函数里面。

![leviathan_gdb_do_stuff_level3](http://drops.javaweb.org/uploads/images/3c4f7844c407266413746ae33a084dbcc751ba43.jpg)

可以看到，在`do_stuff()`函数中有`strcmp()`和`system()`等比较，`strcmp()`的其中一个实参来自于`fgets()`函数的返回结果，另一个参数存储在`-0x117(%ebp)`，从图中可以看出来，存储在`-0x117(%ebp)`的参数就是待匹配的密码。

![leviathan_gdb_pass_level3](http://drops.javaweb.org/uploads/images/7de27fb15df7823bad07e3f7e32dee0fce7b7568.jpg)

将密码输入到程序中，就可以得到一个**shell**，进而得到下一个level的密码。

![leviathan_pass_level3](http://drops.javaweb.org/uploads/images/c1876e9f4a4a8048cdd6db2fc073450319a07a7f.jpg)

level 4 -> 5
============

* * *

好吧，这一个level的文件在`.trash`文件夹中了，依旧是熟悉的流程。

![leviathan_home_level4](http://drops.javaweb.org/uploads/images/5e06ba5d04706d84bdc4cb5ebe19c535912f56d3.jpg)

从程序输出看，应该是密码被转换成二进制输出了，或者是加密之后转换成二进制输出，这个还是得要祭起`gdb`神器来帮忙了。

![leviathan_gdb_main_level4](http://drops.javaweb.org/uploads/images/1ff9058e2545b645f4749606b2cf2ca3a57e15cd.jpg)

从这个循环过程中，我们可以看到，程序对密码的每个字符，从最高位（符号位）开始计算，每次输出一个`字符0`或者`字符1`，所以可以得到，该`bin`程序是将密文的每个字符转换成二进制格式输出。单步调试的时候，程序在调用`fopen("/etc/leviathan_pass/leviathan5"， "r")`的时候返回错误，导致调试无法进行。看来，直接查看内存获得密码的方法是行不通了，只能写脚本，处理程序的输出了。

```
#!/usr/bin/env python
#coding=utf-8

if __name__ == "__main__":
        try:
                fp = open("log.txt", "r")
        except:
                print "file open error"
        for i in range(12):
                byte = fp.read(9).strip()
                value = (int(byte, 2)) & 0xFF
                #print value
                char = chr(value)
                print char,

```

> **`python`代码写得不是一丁点的丑，实在是因为用得不多！**

![leviathan_pass_level4](http://drops.javaweb.org/uploads/images/9b0766ccaca5c62aec5a626b85ef0dcdd6980053.jpg)

把密码中的空格剔除就是正确的密码了。

level 5 -> 6
============

* * *

还是熟悉的流程，熟悉的味道。

![leviathan_home_level5](http://drops.javaweb.org/uploads/images/921c7e8b8e173834065606b1b7ba41bf28321604.jpg)

似乎`/tmp/file.log`这个路径被硬编码到了程序中了，还是要看看这个程序到底做了什么事情。

![leviathan_gdb_main_level5](http://drops.javaweb.org/uploads/images/a6fd2e268e928abd2b43523bb0e523c914f1b864.jpg)

确实是被硬编码到了程序中去了，尝试着在该路径下建立一个指向密码文件的**符号链接**文件，发现居然成功了。

![leviathan_pass_level5](http://drops.javaweb.org/uploads/images/61d2286ffe2c045e7ed76ea3e9f7513beef8cf69.jpg)

好吧，这一个level实在是有点开玩笑啊。。。。

level 6 -> 7
============

* * *

哈哈，这个level似乎有不一样的味道，虽然还是熟悉的流程。

![leviathan_home_level6](http://drops.javaweb.org/uploads/images/a5f9aa2c19198de0871ef702403fa63c710a256b.jpg)

这里，这个`set-uid`程序需要输入一个`4 digit code`，懒得再去用`gdb`反汇编了，我估计也不太好反，做了混淆应该。干脆就来个爆破吧。

```
#!/usr/bin/env python
#coding=utf-8

import os

for pincode in range(10000):
        cmd = "~/leviathan6 %04d" %(pincode)
        # for debug
        #print "test %s" %(cmd)
        ret = os.popen(cmd).read()
        if ret.find("Wrong") == -1:
                print "maybe success in %s" %(cmd)

```

程序在`7123`那里停止了，我猜想是跑到了`shell`里面去了。尝试了一下，果然是这样的。

![leviathan_pass_level6](http://drops.javaweb.org/uploads/images/79858a900ac1cfb4c74e13eed2b97b2fbdeaaad4.jpg)

level 7
=======

* * *

`ssh`登陆到`level 7`

![leviathan_home_level7](http://drops.javaweb.org/uploads/images/46a3ae2fd4dff24baa0c0e6685d81e2b7dcb259b.jpg)

好吧，我纯粹是为了混一个邀请码，才写这个`writeup`的。要不然我肯定遵守这个规则！

end
===

* * *

Bingo！这个`wargame`就这样结束了，题目确实挺简单的，完全是为了新手学习，知道怎么玩`wargames`。

更多关于`wargames`的信息，请参考[这里](http://overthewire.org/wargames/)!