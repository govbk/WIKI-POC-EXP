# weblogic爆破

### 一、部署weblogic

现有的redhat环境7.0,jdk版本1.7。

![](images/15893749059040.png)


### 二、weblogic下载

操作系统：RedHat7

weblogic版本：10.3.6

### 三、安装weblogic

1、weblogic安装

创建一个用户


```bash
useradd weblogic
passwd weblogic
chmod a+x wls1036_generic.jar
su weblogic
java -jar wls1036_generic.jar -mode=console
```

出现问题

![](images/15893749298249.png)


提示空间内存大小不够，清理空间再下一步。

![](images/15893749359234.png)



```bsah
[root@localhostsrc]# cd /usr/lib/jvm/java-1.7.0-openjdk-1.7.0.51-2.4.5.5.el7.x86_64
```

![](images/15893749462831.png)


修改 commEnv.sh 文件


```bash
JAVA_HOME="/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.9.x86_64/ jre"
```

![](images/15893749616118.png)


2、启动weblogic


```bash
[weblogic@localhostroot]$cd /home/weblogic/Oracle/Middleware/user_projects/domains/base_domain/
[weblogic@localhost base_domain]$ ./startWebLogic.sh
```

![](images/15893749887291.png)


在目录/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.79.x86_64中找不到JRE

编辑setDomainEnv.sh

![](images/15893749947492.png)


重新启动weblogic服务

![](images/15893750021043.png)


### 四、破解weblogic控制台密码

第一步 将用户名和密码保存到boot.properties文件中


```bash
[root@localhost security]# pwd

/home/weblogic/Oracle/Middleware/user_projects/domains/base_domain/servers/AdminServer/security
```
在adminserver目录下创建security目录，并创建文件boot.properties


```bash
Username=weblogic
Password=weblogic123
```

第二步 重新启动WebLogic服务


```
[root@localhost bin]# ./startWebLogic.sh&
```

![](images/15893750294356.png)


已经加密

第三步 暴力破解

1.java和javac的版本一致

![](images/15893750349835.png)


2.编译WebLogicPasswordDecryptor.java

![](images/15893750407587.png)


3.破解密码

![](images/15893750484082.png)
