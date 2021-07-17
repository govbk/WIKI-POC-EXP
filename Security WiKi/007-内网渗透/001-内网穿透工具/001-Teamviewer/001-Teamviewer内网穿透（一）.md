# Teamviewer内网穿透（一）

这里利用的原理是强行给对方机子安装上teamviwer，然后自动把tv的远程连接的密码生成到程序目录下的vtr.txt里面中，随即用自己本机的tv连接就行了

## Github地址

https://github.com/ianxtianxt/teamview

## 复现流程

Github下载完之后，传入受害机中(我这里是本地虚拟机，就直接演示了)

如图

![](images/15897756877380.png)


### 1、运行TV_V2.exe

会自己在受害机中装一个tv

会在当前目录下生成如下三个文件

![](images/15897756802508.png)


### 2、运行生成的gps.exe文件

运行后会生成vtr.txt，这里面有ID和通行证

咱们给他装的teamviewer的密码就被读出来啦

连接！

![](images/15897756734904.png)


