# JBoss Administration Console 弱口令 Getshell

### 一、漏洞简介

Administration Console 存在默认密码 admin admin 我们可以登录到后台部署war包getshell

### 二、漏洞影响

全版本

### 三、复现过程

1、点击Administration console

![](images/15890723305079.png)


2、输入弱口令 admin admin 进去

3、点击Web application ,然后点击右上角的add

![](images/15890723387425.png)


4、把文件传上去即可getshell

![](images/15890723453479.png)


![](images/15890723488040.png)
