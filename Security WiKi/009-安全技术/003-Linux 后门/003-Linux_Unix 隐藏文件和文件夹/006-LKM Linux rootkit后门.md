# LKM Linux rootkit后门

## 项目地址

https://github.com/f0rb1dd3n/Reptile

## 适用的系统

**Debian 9**：4.9.0-8-amd64

**Debian 10**：4.19.0-8-amd64

**Ubuntu 18.04.1 LTS**：4.15.0-38-generic

**Kali Linux**：4.18.0-kali2-amd64

**Centos 6.10**：2.6.32- 754.6.3.el6.x86_64

**Centos 7**：3.10.0-862.3.2.el7.x86_64

**Centos 8**：4.18.0-147.5.1.el8_1.x86_64

## 特征

* 赋予非特权用户以root权限
* 隐藏文件和目录
* 隐藏流程
* 隐藏自己
* 隐藏TCP / UDP连接
* 隐藏的引导持久性
* 文件内容篡改
* 一些混淆技术
* ICMP / UDP / TCP端口敲门后门
* 完整的TTY / PTY Shell，具有文件传输功能
* 客户处理爬行动物壳
* Shell每X次连接一次（不是默认值）

## 安装

```bash
apt install build-essential libncurses-dev linux-headers-$(uname -r)
git clone https://github.com/f0rb1dd3n/Reptile.git
cd Reptile
make menuconfig           # or 'make config' or even 'make defconfig'
make
make install

```

基于Debian：

```bash
apt install libreadline-dev

```

基于RHEL：

```bash
yum install readline-devel

```

要么

```
dnf install readline-devel

```

要编译它，只需在Reptile的主目录中运行**make client**，二进制文件就会在**输出**文件夹中。现在就可以`cd output`运行了`./client`！键入`help`以查看命令。

![](images/security_wiki/15905609620409.png)


还有另外两个二进制文件：`listener`和`packet`。该`client`二进制将处理`listener`和`packet`，但如果你愿意，你可以单独使用它们：

![](images/security_wiki/15905609705122.png)


### shell

该shell易于使用，当您建立连接后，只需键入`help`以查看命令。

* 它已经隐藏了它的过程和连接。
* 其连接已加密
* 里面有一个文件上传器和文件下载器。
* 您可以设置一个延迟，以在每次需要时接收反向连接。
* 如果运行，`shell`您将获得完整的TTY / PTY shell，如ssh。

![](images/security_wiki/15905609797860.png)


### 客户端（被控电脑中使用）

## 赋予非特权用户以root权限

要获得root特权，只需键入： `/reptile/reptile_cmd root`

## 隐藏文件，目录和内核模块

`reptile`名称中具有的所有文件和文件夹将被隐藏。您可以在安装之前进行配置。以下命令隐藏/取消隐藏文件，文件夹，进程和内核模块本身。

隐藏：`/reptile/reptile_cmd hide`
取消隐藏：`/reptile/reptile_cmd show`

## 隐藏流程

隐藏流程：`/reptile/reptile_cmd hide`
取消隐藏流程：`/reptile/reptile_cmd show`

## 隐藏TCP和UDP连接

隐藏：`/reptile/reptile_cmd conn hide`
隐藏：`/reptile/reptile_cmd conn show`

**注意：**默认情况下，TCP和UDP隐藏功能隐藏与IP的所有连接，而忽略PORT。如果您真的想通过PORT隐藏特定的连接，请转到代码并在Connectoin挂钩中查看一些注释。

## 文件内容篡改

标签之间的所有内容将被隐藏：

```bsah
#<reptile> 
content to hide 
#</reptile>

```

您可以在安装脚本中配置这些标签。

