## Netsh helper

`netsh`（全称：`Network Shell`） 是`windows`系统本身提供的功能强大的网络配置命令行工具，它可以添加自定的dll从而拓展其功能，我们可以使用`netsh add helper yourdll.dll`来添加拓展功能，添加了之后，在启动`netsh`的时候就会加载我们dll文件

添加自定义`helper dll`
关于`helper dll`的编写可以参考这个项目：[链接](https://github.com/outflanknl/NetshHelperBeacon)

我们可以使用两种方式来添加helper：

1. 通过cmd添加helper

    ```bash
    netsh add helper test.dll

    ```

![](images/security_wiki/15906335515350.png)


1. 通过注册表添加helper
    其位置为：`HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NetSh`，创建一个键，名称随便，键值为我们dll的路径

![](images/security_wiki/15906335587507.png)


效果如下：

![82a4281dbd8f4b99be3fc4d0aaddc05e](images/security_wiki/82a4281dbd8f4b99be3fc4d0aaddc05e.gif)


