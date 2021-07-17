# linux下tomcat安全配置

0x00 删除默认目录
===========

* * *

安装完tomcat后，删除`$CATALINA_HOME/webapps`下默认的所有目录文件

```
rm -rf /srv/apache-tomcat/webapps/*

```

0x01 用户管理
=========

* * *

如果不需要通过web部署应用，建议注释或删除tomcat-users.xml下用户权限相关配置

![p1](http://drops.javaweb.org/uploads/images/588e048b5241142b149265db0f10fef5b52344e1.jpg)

0x02 隐藏tomcat版本信息
=================

* * *

**方法一**

修改`$CATALINA_HOME/conf/server.xml`,在Connector节点添加server字段，示例如下

![p2](http://drops.javaweb.org/uploads/images/1cd616d60e92cfd07dd7060f852eb8d6f16d7861.jpg)

![p3](http://drops.javaweb.org/uploads/images/1114e7a72de0f9c556b87d99c24ff928f9a3af2c.jpg)

**方法二**

修改`$CATALINA_HOME/lib/catalina.jar::org/apache/catalina/util/ServerInfo.properties`

默认情况下如图

![p4](http://drops.javaweb.org/uploads/images/086df866e8051fbb0b2c2350ef0a77ff8e4a955d.jpg)

![p5](http://drops.javaweb.org/uploads/images/f57ef9f4e719a780fabbd859e150faf85241af7a.jpg)

用户可自定义修改server.info字段和server.number字段，示例修改如下图所示。

![p6](http://drops.javaweb.org/uploads/images/90518975aafdbaa41413d3504923774faf142c65.jpg)

![p7](http://drops.javaweb.org/uploads/images/ce23f85abdba01e18dfab52f1aeb8be56e39a643.jpg)

0x03 关闭自动部署
===========

* * *

如果不需要自动部署，建议关闭自动部署功能。在`$CATALINA_HOME/conf/server.xml`中的host字段，修改`unpackWARs="false" autoDeploy="false"`。

![p8](http://drops.javaweb.org/uploads/images/5ba937c9234374239b2a587a51acf1514b10a9b5.jpg)

0x03 自定义错误页面
============

* * *

修改web.xml,自定义40x、50x等容错页面，防止信息泄露。

![p9](http://drops.javaweb.org/uploads/images/b239cc27b79dc03321a9696f45fa440d386ad0a1.jpg)

0x05 禁止列目录（高版本默认已禁止）
====================

* * *

修改web.xml

![p10](http://drops.javaweb.org/uploads/images/8edfbf4e6836c02075ad8c38fb085a9878572045.jpg)

0x06 AJP端口管理
============

* * *

AJP是为 Tomcat 与 HTTP 服务器之间通信而定制的协议，能提供较高的通信速度和效率。如果tomcat前端放的是apache的时候，会使用到AJP这个连接器。前端如果是由nginx做的反向代理的话可以不使用此连接器，因此需要注销掉该连接器。

![p11](http://drops.javaweb.org/uploads/images/fbd055edc0c54157d125072b11cd3343c7482522.jpg)

0x07 服务权限控制
===========

* * *

tomcat以非root权限启动，应用部署目录权限和tomcat服务启动用户分离，比如tomcat以tomcat用户启动，而部署应用的目录设置为nobody用户750。

0x08 启用cookie的HttpOnly属性
========================

* * *

修改`$CATALINA_HOME/conf/context.xml`，添加`<Context useHttpOnly="true">`,如下图所示

![p12](http://drops.javaweb.org/uploads/images/63035dccb8436d87cfb1164c4388fe7365074fe5.jpg)

测试结果

![p13](http://drops.javaweb.org/uploads/images/d46217a6558ced1b7f09f9e2a9b4f511c8e63a1f.jpg)

![p14](http://drops.javaweb.org/uploads/images/c35292f5d890cde77a479a1c65cfa7592026c1e1.jpg)

配置cookie的secure属性，在web.xml中sesion-config节点配置cooker-config，此配置只允许cookie在加密方式下传输。

![p15](http://drops.javaweb.org/uploads/images/2e4d423328a090acbffb134315c6ea01b4a2f46b.jpg)

测试结果

![p16](http://drops.javaweb.org/uploads/images/e5c32b63121e2b6b05eb067733e6af1af0f9d603.jpg)