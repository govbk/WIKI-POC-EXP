# SNORT入侵检测系统

0x00 一条简单的规则
============

* * *

`alert tcp 202.110.8.1 any -> 122.111.90.8 80 (msg:”Web Access”; sid:1)`

*   alert：表示如果此条规则被触发则告警
*   tcp：协议类型
*   ip地址：源/目的IP地址
*   any/80：端口号
*   ->：方向操作符，还有<>双向。
*   msg：在告警和包日志中打印消息
*   sid：Snort规则id …

这条规则看字面意思就很容易理解。Snort就是利用规则来匹配数据包进行实时流量分析，网络数据包记录的网络入侵检测/防御系统(Network Intrusion Detection/Prevention System),也就是NIDS/NIPS。

0x01 SNORT目录结构
==============

* * *

建议将Snort的目录结构配置成如下：

```
/etc/snort
 ├── barnyard2.conf      barnyard2日志分析工具配置文件
 ├── snort.conf          snort配置文件（关键）
 ├── threshold.conf      事件过滤配置文件
 ├── classification.config 规则分类配置文件(classtype)
 ├── reference.config      外部参考配置文件(reference)
 ├── gen-msg.map      generate id 和 msg 对应关系map
 ├── sid-msg.map      snort id 和 msg对应关系map
 ├── unicode.map      预处理器http_inspect编码翻译文件
 ├── preproc_rules       预处理器及解码器规则集
 │ ├── decoder.rules  
 │ ├── preprocessor.rules
 │ └── sensitive-data.rules
 ├── rules               Snort规则集（关键）
 │  ├── web-iis.rules 
 │  ├── web-php.rules
 More…
 ├── so_rules            Share Object规则集
 │  ├── browser-ie.rules
 │  ├── browser-other.rules    
 More…

```

0x02 snort.conf配置文件
===================

* * *

```
此文件是配置snort的核心文件，包括以下几部分：
  1) Set the network variables.  设置各类网络地址，规则中易于使用
  2) Configure the decoder      设置解码器
  3) Configure the base detection engine  设置基础检测引擎
  4) Configure dynamic loaded libraries   设置动态链接库
  5) Configure preprocessors     设置预处理器
  6) Configure output plugins    设置输出插件
  7) Customize your rule set     设置自定义规则
  8) Customize preprocessor and decoder rule set设置预处理、解码器规则
  9) Customize shared object rule set 设置共享对象规则集

```

0x03 SNORT体系结构
==============

* * *

![Paste_Image.png](http://drops.javaweb.org/uploads/images/996e5c4e7af5f24853cfd14d0deba9bc53129aa1.jpg)

*   数据包嗅探模块，主要负责监听网络数据包，并根据TCP/IP协议解析数据包。
*   预处理模块，1.包重组预处理器，它的作用是为了防止攻击信息被拆分到多个包中而 逃避了Snort的检测；2.协议编码预处理器，它的功能是把数据包协议解码成一个统一的格式，再传送给检测模块；3.协议异常检测预处器。
*   检测引擎模块，当预处理器把数据包送过来后，检测引擎将这些数据包与三维链表形式的检测规则进行匹配，一旦发现数据包中的内容和某条规则相匹配，就通知报警模块。
*   报警/日志模块，检测引擎将数据包传送给报警模块后，报警模块会根据规则定义（alert，log..）对其进行不同的处理（数据库，日志）。

下面分别详细介绍这四大模块。

0x04 解码模块与预处理模块
===============

* * *

4.1 模块介绍
--------

由于解码模块和预处理模块功能类似，都是在规则检测引擎之前对数据包的处理，所以两个模块一并介绍。 解码模块主要是将从监控网络当中抓取的原始网络数据包，按照各个网络协议栈从下至上进行解码，并将解码数据保存到各个对应的数据结构当中，最后交由预处理模块进行处理。

解码后的数据包经过预处理之后才能被主探测引擎进行规则匹配。预处理器的主要用来应对一些IDS攻击手段。其作用包括：

1)针对可疑行为检查包或修改包，以便探测引擎能对其正确解释。 2)负责对流量标准化，以便探测引擎能精确匹配特征。

目前已知的IDS逃避技术主要有：

1)– 多态URL编码； 2)– 多态shellcode； 3)– 会话分割； 4)– IP碎片；

Snort主要包含以下三类预处理器（举例说明）：

1)包重组预处理器：

*   frag3：IP分片重组和攻击监测。
*   stream：维持TCP流状态，进行会话重组。

2)协议规范化预处理器：

*   http_inspect：规范HTTP流。
*   rpcDecode：规范RPC调用。

3)异常检测预处理器：

*   ARP spoof：检测ARP欺骗。
*   sfPortscan：检测端口扫描。

4.2 模块配置
--------

配置分两个步骤，都是在snort.conf中配置。

1.snort.conf的2)和5)中配置解码器或者预处理参数。

2.snort.conf的8)中启用检测规则。

### 4.2.1 解码器配置举例

1.配置解码器

```
config disable_decode_alerts   关闭decode告警。
config enable_decode_oversized_alerts
      如果一个包（IP,UDP,TCP）长度长于length字段，则告警。
# Stop generic decode events

```

格式为`config docoder [option]`,使用`#`作为注释

2.启用解码器检测规则

`include $PREPROC_RULE_PATH/decoder.rules`

snort.conf文件中使用include关键词包含配置文件和规则文件。

3.在decoder.rules中我们找到了检测IP长度异常的规则。

`alert ( msg:"DECODE_IPV4_DGRAM_GT_IPHDR"; sid:6; gid:116; rev:1; metadata:rule-type decode;classtype:protocol-command-decode; )`

### 4.2.2 预处理器http_insepect配置举例

1.下面是http_inspect默认的配置

```
preprocessor http_inspect: global iis_unicode_map                            unicode.map 1252 compress_depth 65535 decompress_depth 65535
#unicode.map是http_inspect解码unicode时的解码文件。
preprocessor http_inspect_server: server default \
http_methods { GET POST PUT SEARCH MKCOL ...} \
    ...  
    enable_cookie        #将http请求或响应中的cookie提取到缓存，用于后面规则匹配。
    normalize javascript #对标签中的js脚本解码。
    ...

```

2.启用预处理器规则

`#include $PREPROC_RULE_PATH/preprocessor.rules`

下面是一条解码器规则：

`alert ( msg:"DECODE_TCP_INVALID_OFFSET"; sid:46; gid:116; rev:1; metadata:rule-type decode; reference:cve,2004-0816; classtype:bad-unknown; )`

发现这条规则和之前看到的不一样，它没有源/目的IP，端口等信息，说明这条规则是由解码器自动触发的，用户不需要干预。 一般我们也不需要去修改解码器或者预处理器的规则，只需要去snort.conf中添加、配置或者删除插件即可。

0x05检测引擎模块
==========

* * *

规则结构 alert tcp 202.110.8.1 any -> 122.111.90.8 80 (msg:”Web Access”; sid:1) |---||---||---||---||---||---||---||---||---||--规则头---||---||---||---||---||---||---||---||--||---||---||---||-规则选项---||---||---||---||-|

5.1 规则头
-------

动作：

在snort中有五种动作：alert、log、pass、activate和dynamic.

```
  1)Alert：       生成一个告警，然后记录（log）这个包。
  2)Log：         记录这个包。
  3)Pass：        丢弃这个包。
  4)Activate： alert并且激活另一条dynamic规则。
  5)Dynamic：保持空闲直到被一条activate规则激活，被激活后就作为一条log规则执行。

```

协议：

Snort当前可分析的协议有四种：TCP,UDP,ICMP和IP。将来可能会更多，例如：ARP、IGRP、GRE、OSPF、RIP、IPX等。

IP地址：

1)地址就是由直接的ip地址或一个CIDR块组成的。也可以指定ip地址列表，一个ip地址列表由逗号分割的ip地址和CIDR块组成，并且要放在方括号内 [,]。 2)否定操作符用`!`表示。 3)关键字“any”可以被用来定义任何地址。

例如：

`alert tcp ![192.168.1.0/24,10.1.1.0/16] any -> 192.168.2.1 80(msg:”notice!”;content|xxxx|;)`

方向操作符：

方向操作符`->`

表示规则所施加的流的方向。方向操作符左边的ip地址和端口号被认为是流来自的源主机，方向操作符右边的ip地址和端口信息是目标主机，还有一个双向操作符`<>`。

端口号：

1)端口号可以用几种方法表示，包括any端口、静态端口定义、范围、以及通过否定操作符。 2)静态端口定义表示一个单个端口号，例如111表示portmapper，23表示telnet，80表示http等等。 3)端口范围用范围操作符“:”表示.比如，`80:`,`:1024`,`80:1024`

5.2 规则选项
--------

规则选项分为四大类：

1)General rule option 通用规则选项 2)Payload detection rule option 负载检测规则选项 3)Non-Payload detection rule option 非负载检测规则选项 4)Post detection rule option 后检测规则选项

### 5.2.1 General rule option通用规则选项

**sid**

```
   snort id ,这个关键字被用来识别snort规则的唯一性（说的其实严禁，后面会有补充）。sid 的范围是如下分配的：          

```

*   <100 保留做将来使用
*   100-1000,000 包含在snort发布包中
*   >1000,000 作为本地规则使用

**msg**

```
      标示一个消息，但是规则中的msg不起作用，sid和msg的对应关系查阅sid-msg.map。

```

**_sid-msg.map_**

格式：`sid || msg`

例子：`384 || PROTOCOL-ICMP PING`在/etc/snort/rules/protocol-icmp.ruls中我们找到了这条规则：`alert icmp $EXTERNAL_NET any -> $HOME_NET any (msg:"PROTOCOL-ICMP PING"; icode:0; itype:8; metadata:ruleset community; classtype:misc-activity; sid:384; rev:8;)`

此文件作用是将sid与msg的一一对应，否则，在告警中会出现下图中第一条的现象。

![Paste_Image.png](http://drops.javaweb.org/uploads/images/71dd944c878c7c29b0c9b1a88c2a4af4da06f8a8.jpg)

此文件用于自定义规则中sid与msg的对应和在snort自有规则中自定义告警信息。 上图中`Snort Alert[1:1000015:0]`其中内容对应为`Snort alert[gid:sid:rev]`。这说明一个规则需要这三个因素才能确定,之前说只有sid唯一标示一条规则是不严谨的。

**gid**

```
 generate id，作用是为了说明这条规则是snort的哪部分触发的。比如是由解码器、预处理器还是Snort自有规则等。
 查看/usr/local/share/doc/snort/generators文件（此文件不是配置文件）：

rules_subsystem       1 # Snort Rules Engine
rpc_decode            106 # RPC Preprocessor(预处理器)
stream4               111 # Stream4 preprocessor（预处理器）
ftp                   125 # FTP decoder（解码器）
...                   ...

```

decoder和preprocessor的gid就不一一列举，可以看到Snort Rule Engine的gid为1，自定义规则和snort自有规则（也就是/etc/snort/rules目录下的规则）gid默认是1。但是这里我们获知decoder和preprocessor也是有sid的。 举例说明：

/etc/snort/rules/protocol-icmp.rules中的一条规则：

`alert icmp $EXTERNAL_NET any -> $HOME_NET any (msg:“PROTOCOL-ICMP Traceroute”; icode:0; itype:30; metadata:ruleset community; classtype:misc-activity; sid:456; rev:8;)`

gid默认为1

/etc/snort/preproc_rules/decoder.rules中的一条规则：

`alert ( msg:"DECODE_IP6_EXCESS_EXT_HDR"; sid:456; gid:116; rev:1; metadata:rule-type decode; classtype:misc-activity; )`

可以看到两条规则的sid是相同的，所以还需要gid来区分。

**_gen-msg.map_**

这个文件和sid-msg.map作用类似，在逻辑上应该是包含了sid-msg.map（sid-msg.map相当于默认gid为1）

格式：`generatorid || alertid(sid) || MSG`

例子：

```
1   || 1 || snort general alert
129 || 2 || stream5: Data on SYN packet
116 || 271 || snort_decoder: WARNING: IPv6 header claims to not be IPv6
116 || 456 || snort_decoder: WARNING: too many IPV6 extension headers #例子
...

```

拿**gid**中第二条规则举例，如果此条规则被触发，则会报`snort_decoder: WARNING: too many IPV6 extension headers`告警，而不是`DECODE_IP6_EXCESS_EXT_HDR`。所以规则中的msg仅仅起到标示作用，告警msg需要在sid-msg.map和gen-msg.map这两个文件中对应查找。

**rev**

这个关键字是被用来识别规则修改的版本，需要和sid,gid配合使用。 这样就介绍完了gid，sid，rev三个确定规则唯一的元素。

**reference**

外部攻击参考，这个关键字允许规则包含一个外面的攻击识别系统。这个插件目前支持几种特定的系统，这些插件被输出插件用来提供一个关于产生报警的额外信息的连接。

![Paste_Image.png](http://drops.javaweb.org/uploads/images/6624c1932f7fb9f8c75d54de5765a5f9cd18140f.jpg)

**_reference.config_**

格式：`config reference: system URL`

例子：`config reference: cve http://cve.mitre.org/cgi-bin/cvename.cgi?name=`定义了一些外部安全网站的网址。比如规则中定义reference: cve,1001,那么就像在上面的网址后面添加了1001，`http://cve.mitre.org/cgi-bin/cvename.cgi?name=1001`，最后点击告警中的[cve]，就会跳转到相应的网址。注：reference也需要在sid-msg.map中与sid对应，否则不起作用，类比msg。

**classtype**

规则类别标识。这个关键字把报警分成不同的攻击类。通过使用这个关键字和使用优先级，用户可以指定规则类中每个类型所具有的优先级。

**priority**

设置classtype的优先级。classtype和priority是配合使用的，classification.config文件将其联系起来。

**_classification.config_**

格式：`config classification:shortname,short description,priority`

例子：`config classification: attempted-admin,Attempted Administrator Privilege Gain,1`写在此文件中的都是默认值，priority关键词可以在规则中重写优先级。 例子：`alert tcp any any -> any 80 (msg:"EXPLOIT ntpdx overflow"; dsize:>128; classtype:attempted-admin; priority:10 );`

**metadata**

可以在规则中添加自定义的信息，一般以键值对的形式出现。

> 通用规则选项只是对一条规则进行标示，分类等操作，并没有进行实际的过滤检测。

### 5.2.2 Payload Detection Rule Options 负载检测规则选项

**content**

content是Snort重要的关键词之一。它规定在数据包的负载中搜索指定的样式。它的选项数据可以包含混合的文本和二进制数据。二进制数据一般包含在管道符号中“|”，表示为字节码（bytecode），也就是将二进制数据的十六进制形式。

```
alert tcp any any -> any 139 (content:"|5c 00|P|00|I|00|P|00|E|00 5c|";)
alert tcp any any -> any 80 (content:!“GET”;)

```

content还有很多修饰符：

```
Nocase            content字符串大小写不敏感
rawbytes          直接匹配原始数据包
Depth             匹配的深度
Offset            开始匹配的偏移量
Distance          两次content匹配的间距
Within            两次content匹配之间至多的间距  
http_cookie       匹配cookie
http_raw_cookie   匹配未经normalize的cookie
http_header       匹配header
http_raw_header   匹配未经normalize的header
http_method       匹配method
http_url          匹配url
http_raw_url      匹配日在未经normalize的url中
http_stat_code    匹配状态码中匹配
http_stat_msg     匹配状态信息
http_encode       匹配编码格式

```

http开头的修饰符需要配合前面介绍过的预处理器http_inspect一起使用。

**pcre**

```
允许用户使用与PERL语言相兼容的正则表达式。

```

格式`pcre:[!]"(/<regex>/|m<delim><regex><delim>)[ismxAEGRUBPHMCOIDKY]`

例子：  
`alert tcp any any -> any 80 (content:“/foo.php?id="; pcre:"/\/foo.php?id=[0-9]{1,10}/iU";)`正则的细节查阅snort_manual。

**protected_content**

将content中的查询内容使用hash算法加密，保护规则的私密性。`protected_content:[!]"<content hash>", length:orig_len[, hash:md5|sha256|sha512];`

**rawbytes**

忽略解码器及预处理器的操作，直接匹配原始网络包。

> 上面只列举出了一些常用的payload detection rule option，更多的关键词查阅snort_manual。

### 5.2.3 Non-Payload Detection Rule Option非负载检测规则选项

```
Fragoffset                IP 偏移量
Ttl                       IP 生存时间
Tos                       IP 服务类型
Id                        IP 标识
Ipopts                    IP 可选项
Fragbits                  IP 标志
Dsize                     数据包负载量
Flags                     TCP flags
Seq                       TCP seq
Ack                       TCP ack
Window                    TCP window
Icmp_id                   ICMP ID

```

此类规则选项都是对数据包帧结构中特殊字段的匹配。

### 5.2.4 Post-Detection Rule Option后检测规则选项

```
Logto                     输出日志路径
Session                   从TCP会话中获取用户数据
Resp                      通过发送响应结束恶意的请求
React                     不仅仅记录触发规则的特定数据包
Tag                       不仅仅记录触发规则的特定数据包
Activates                 activate动作
Activates_by              dynamic动作
Count                     dynamic规则被触发后可以匹配的包的数目
Replace                   替换content内容
Detection-filter          检测过滤

```

5.3 检测引擎模块配置
------------

1.在/etc/rules目录下的*.rules文件中写规则。 2.snort.conf 7)中include对应规则。

```
include $RULE_PATH/local.rules
#include $RULE_PATH/app-detect.rules
#include $RULE_PATH/attack-responses.rules
#include $RULE_PATH/backdoor.rules
#include $RULE_PATH/bad-traffic.rules
#include $RULE_PATH/blacklist.rules

```

0x06 Snort告警/日志模块
=================

* * *

6.1 输出模块配置
----------

snort.conf 6):Configure output plugins 设置日志路径`config logdir：/var/log/snort`设置输出格式为unified2：`output unified2: filename snort.log, limit 128`

**_barnyard2.conf_**

barnyard2的作用是将unified2格式的数据存入数据库 设置与snort日志关联`config waldo_file:/var/log/snort/barnyard.waldo`设置数据库`output database: log, mysql, user=snort password=123456 dbname=snort host=localhost`

6.2 数据库
-------

ER图

![Paste_Image.png](http://drops.javaweb.org/uploads/images/a1e334c2b1cf67b493fe4217716089ed3da10e8f.jpg)

**schema**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/5bc830fe34663aa7dcdf78e3df3d1ec10a7b60d5.jpg)

```
vseq：数据库模式ID
ctime：数据库创建时间

```

信息表，和其他数据库内容上没有联系

**sensor**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/e9dcd2fac2cba2ce165a2120efaf796eb96b7379.jpg)

```
sid：传感器代号
hostname：传感器所属的用户名称
Interface：传感器对应的网络接口
filter：对应传感器的过滤原则
detail：表示传感器监测模式，记录模式详细程度的级别        
encoding：包含数据存在形式
last_cid： 对应每个sid即传感器捕获告警的最后一个值

```

**detail**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/873f90096df1f9d8229837c610dd6e58b62e0f25.jpg)

```
0-fast快速检测
1-full全面检测

```

传感器sensor的检测级别。

**encoding**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/21abec8a2bafbf785d121b9a9fe3a94389d0ef75.jpg)

```
0- Hex
1- base64
2- asci

```

数据包中数据的存在形式。

**event**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/fc7fdd2bb982559f73a6fb2ee74cd4503bc7e756.jpg)

```
sid：sensor id，传感器id。
cid；event id   事件id。sid和cid共同作为主码，其中cid是在sid的基础上进行排序的。每个sid对应自己的cid排序。
signature：对应signature表格中的sig_id选项，表明这条告警事件所属的规则形式的告警对应哪一类rules。
timestamp：对应告警事件发生的系统时间。

```

最核心的一张表，告警的每一条数据都会存储在event表中，一条event数据就代表一个包。

**signature**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/550d89de565a6617a2cbf945cf3644bf9db1b44b.jpg)

```
sig_id： 总数代表发生告警种类的总数。是告警种类的主码。唯一标识一条规则。
sig_name：告警名称。对应每条alert语句的Msg。
sig_class_id：对应sig_class表格中的sig_class_id.代表告警种类的大类信息。
sig_priority：告警的优先级
sig_rev：版本号
sig_sid：snort id   
sig_gid：generate id 

```

存储snort规则的一张表，可以看到sig_sid,sig_gid,sig_rev分别对应规则中的sid,gid,rev。注意规则中的snort id和数据库中的 sensor id注意区分。

**sig_reference**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/8a0789ed00e514623a0216b955c94790b69691d6.jpg)

```
sig_id：对应的告警种类。
ref_id：对应reference表格中的主码
ref_seq：参考序列号

```

提供报警种类信息signature的参考信息。将signature与reference联系起来的表格。

**reference**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/4a95f6ac65a21ee97e7c3a9da50f01131a3b79e8.jpg)

```
Ref_id：主码
Ref_system_id：对应reference_system表格
Ref_tag：规则中 cve,bugtraq 后面的参数

```

**reference_system**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/f099eb4bac7e24ef52aa0623619974b9288de85f.jpg)

```
ref_system_id：主码
ref_system_name：reference system的名字，如cve，url等。

```

**sig_class**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/61907df2b942e2d7a96e48e420056ee6e205a6db.jpg)

```
sig_class_id：分类编号
sig_class_name：分类名称

```

signature告警种类的分类信息。

**iphdr**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/092be4a21b553dce6c00860b02da4a2fdbe8420d.jpg)

**tcphdr**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/fcdc69671983878f80542b0ba37a9d644518c08d.jpg)

**udphdr**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/2432756e80143d4825a35d34b6721b1eb90c9be0.jpg)

**icmphdr**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/39a467e87ad5fc50877788c4c551b8bbe518a08c.jpg)

**data**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/e7e4822a9c812f9417ea79485590231d9b4e3c9c.jpg)

```
data_payload：数据包有效载荷

```

规则中协议为tcp时，data_payload中是tcp后面的内容

规则中协议为icmp时，data_payload中是icmp协议中的data字段值

**opt**

![Paste_Image.png](http://drops.javaweb.org/uploads/images/89fb193a2fde50fccaf34e89f3c3ff086d035f4e.jpg)

IP和OPT的option。

参考文献：

*   [[1] CentOS6.6下基于snort+barnyard2+base的入侵检测系统的搭建](http://wenku.baidu.com/view/1d38ae4d2cc58bd63186bddf?fr=prin)
*   [2](http://upload-images.jianshu.io/upload_images/764908-5d6ab8767d56c9f8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)基于Snort的C_S模式的IDS的设计与应用_王会霞.caj
*   [[3] Snort 笔记1 - 3种模式简介](http://blog.csdn.net/jo_say/article/details/6330477)
*   [[4] Snort.conf 分析](http://blog.csdn.net/jo_say/article/details/6302367)
*   [[5] Snort 入侵检测系统简介](http://www.jianshu.com/p/113345bbf2f7)
*   [[6] Snort部署及端口扫描检测试验总结](http://wenku.baidu.com/view/0810a3bf3186bceb18e8bb3b?fr=prin)
*   [[7] Barnyard create_mysql](https://github.com/firnsy/barnyard2/blob/master/schemas/create_mysql)
*   [[8] Snort mysql概述](http://www.jianshu.com/p/b047101f93a2)
*   [[9] Snort响应模块总结-实时监听-数据库分析](http://wenku.baidu.com/link?url=On2WXmk0bTqt985TWqvFD-iqiMRKktAUWOfhmZcZjKRa7YbDju-fjSgv4m_JvPW69-94Et-x2H-ZHoDj2KMoSg7rCYs6xIS8x9ntL7eKucC)
*   [[10] Snort数据表项含义及ER图](http://www.andrew.cmu.edu/user/rdanyliw/snort/acid_db_er_v102.html)
*   [[11] 上文的中文翻译](http://m.blog.csdn.net/blog/shuaihuiminps/5082641)
*   [[12] Snort rules概述](http://www.jianshu.com/writer#/notebooks/1640991/notes/2062809/preview)
*   [[13] Snort安装配置与NIDS规则编写](http://www.cnblogs.com/lasgalen/p/4512755.html?utm_source=tuicool)
*   [[14] Snort 笔记2 - 规则编写](http://blog.csdn.net/jo_say/article/details/6335640)
*   [[15] 撰写一组SNORT规则防御SQL注入](http://bbs.chinaunix.net/thread-1211897-1-1.html)
*   [[16] Snort规则中的逻辑关系](http://www.jianshu.com/p/9d11a3e039e9)
*   [[17] Snort_manual.pdf 官方文档中文翻译](http://www.jianshu.com/p/a87086078728)
*   [[18] Snort sid-msg.map文件概述](http://www.jianshu.com/p/6de14a787868)
*   [[19] Snort classification.config文件概述](http://www.jianshu.com/p/e031003dfcff)
*   [[20] Snort reference.config文件概述](http://www.jianshu.com/p/d08bfe6210bf)n