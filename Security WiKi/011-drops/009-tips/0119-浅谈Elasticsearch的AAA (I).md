# 浅谈Elasticsearch的AAA (I)

0x00 前言
=======

* * *

Elasticsearch（以下简称es）被越来越多的公司广泛使用，而其本身安全问题也备受关注，最近出现的安全问题比较多，例如影响比较大的漏洞有CVE-2014-3120和CVE-2015-1427。

这些漏洞和es本身没有认证授权机制有很大关系，同时公司内部多业务使用使用同一套es集群的情况非常多，如何做好认证授权的管理的问题尤为凸显。

官方竟然将安全模块Shield作为收费模块，所以普及率并不高。本着为公司省下仨瓜俩枣的精神寻找其他的解决方案。实现过程中走了一些弯路，记录下来以方便其他遇到这些问题的同仁。

0x01 需求
=======

* * *

随着es的普及，对安全的需求越来越多，例如：

*   账号认证，解决es匿名访问的问题。
*   授权管理，对不同的账号按照不同维度分配（主要是索引）访问权限。
*   只读权限，此条需求来源于 ：某个Dashboard想分享给其他人，但又不想让其他人有权限修改。
*   统一认证，单点登录。

0x02 方案选择
=========

* * *

需求已确定，经过一番寻找得到以下几种方案备选。、

*   `elasticsearch-http-basic`:优点：此方案部署简单快速，可以解决从无到有的过程，实现了账号认证和ip白名单认证功能，缺点：功能单一，只解决了#1需求。
*   `kibana-authentication-proxy`:优点：此方案是针对kibana实现的认证，优点是该方案支持“`Google OAuth2, BasicAuth(multiple users supported) and CAS Authentication`”解决了需求#4中的单点登录的需求，配合方案#1中的ip白名单能基本解决需求#1和#4.缺点：目前只支持到kibana3。
*   `Shield`：优点：功能强大，文档丰富。缺点：收费。
*   `search-guard`：优点：功能丰富的免费模块，能够很好的解决需求中所有问题（除了#4中的单点登录）。缺点：部署和配置稍复杂，文档较少，门槛较高。

大家应该能猜到最终的选择了，没错就是方案#4。

0x03 安装和配置
==========

* * *

### 准备工作

目前官方对es1.5和1.6支持比较好，两个版本安装方法不同，

*   _es 1.5_：

直接使用插件安装 ，

```
 bin/plugin -i com.floragunn/search-guard/0.5

```

*   _es1.6_：

首先需要安装maven，

```
wget http://mirror.bit.edu.cn/apache/maven/maven-3/3.3.3/binaries/apache-maven-3.3.3-bin.tar.gz

```

解压后将bin目录添加到环境变量PATH中。

下载编译相关依赖

> git clone -b es1.6 https://github.com/floragunncom/search-guard.git cd search-guard mvn package -DskipTests bin/plugin -u file:./target/search-guard-16-0.6-SNAPSHOT.jar -i search-guard

### 配置

`Search guard`配置分为2部分，一部分是`elasticsearch.yml`以及`logging.yml`文件。另一部分存储在es中。

1.  `elasticsearch.yml`主要内容包括`search guard`的一些开关，`ssl`支持的配置，认证方式，权限控制的`filter`等。 下面我们来完成一个最小化的配置： 直接将git中`searchguard_config_template.yml`内容粘贴到`elasticsearch.yml`， 然后打开

> searchguard.allow_all_from_loopback: true

以方便本地调试。 另外需要注意的一个选项是

> searchguard.key_path: /path/key

`searchguard_node.key`文件的路径。 默认配置已开启basic认证，

> searchguard.authentication.authentication_backend.impl: com.floragunn.searchguard.authentication.backend.simple.SettingsBasedAuthenticationBackend searchguard.authentication.authorizer.impl: com.floragunn.searchguard.authorization.simple.SettingsBasedAuthorizator searchguard.authentication.http_authenticator.impl: com.floragunn.searchguard.authentication.http.basic.HTTPBasicAuthenticator

设置用户名和密码

> searchguard.authentication.settingsdb.user.: password searchguard.authentication.settingsdb.user.admin: adminpass searchguard.authentication.settingsdb.user.user: userpass
> ===========================================================================================================================================================================

给用户分配角色，`admin`为超级管理员，角色为`root`，`user`为只读用户橘色。

> searchguard.authentication.authorization.settingsdb.roles.:searchguard.authentication.authorization.settingsdb.roles.admin: ["root"] searchguard.authentication.authorization.settingsdb.roles.user: ["readonly"]
> =================================================================================================================================================================================================================

设置`filter`，我设置两个权限，`readonly`和`deny`权限， readonly的filter只允许读操作，以及kibana必须的两个操作，禁止写操作。

> searchguard.actionrequestfilter.names: ["readonly","deny"] searchguard.actionrequestfilter.readonly.allowed_actions: ["indices:data/read/_","indices:admin/exists","indices:admin/mappings/_"] searchguard.actionrequestfilter.readonly.forbidden_actions: ["indices:data/write/*"]

`deny filter`禁止所有的操作。

> searchguard.actionrequestfilter.deny.allowed_actions: [] searchguard.actionrequestfilter.deny.forbidden_actions: ["cluster:_", "indices:_"]

`logging.yml`最后加入

> logger.com.floragunn: DEBUG

开启`search guard`的调试级别，以方便调试。 至此文件配置部分基本完成，下面设置`ACL`，将刚配置的`roles`，`filters`和`indices`关联起来。

> curl -XPUT 'http://localhost:9200/searchguard/ac/ac?pretty' -d ' {"acl": [ { "**Comment**": "这条是DEFAULT规则，必须要有，默认的权限是readonly", "filters_bypass": [], "filters_execute": ["actionrequestfilter.readonly"] }, { "**Comment**": "root角色的账号可以绕过所有的filter", "roles": [ "root" ], "filters_bypass": ["_"], "filters_execute": [] }, { "**Comment**": "readonly角色对于logstash_的索引没有权限访问", "roles" : ["readonly"], "indices": ["logstash*"], "filters_bypass": [], "filters_execute": ["actionrequestfilter.deny"] }, { "**Comment**": "readonly角色对于logs和.kibana索引有只读的权限", "roles" : ["readonly"], "indices": ["logs",".kibana"], "filters_bypass": [""], "filters_execute": ["actionrequestfilter.readonly"] }
> 
> ]}'

为了看着方便，JSON格式化后是这个样子

```
{
    "acl": [
        {
            "Comment": "这条是DEFAULT规则，必须要有，默认的权限是readonly",
            "filters_bypass": [],
            "filters_execute": [
                "actionrequestfilter.readonly"
            ]
        },
        {
            "Comment": "root角色的账号可以绕过所有的filter",
            "roles": [
                "root"
            ],
            "filters_bypass": [
                ""
            ],
            "filters_execute": []
        },
        {
            "Comment": "readonly角色对于logstash的索引没有权限访问",
            "roles": [
                "readonly"
            ],
            "indices": [
                "logstash*"
            ],
            "filters_bypass": [],
            "filters_execute": [
                "actionrequestfilter.deny"
            ]
        },
        {
            "Comment": "readonly角色对于logs和.kibana索引有只读的权限",
            "roles": [
                "readonly"
            ],
            "indices": [
                "logs",
                ".kibana"
            ],
            "filters_bypass": [
                ""
            ],
            "filters_execute": [
                "actionrequestfilter.readonly"
            ]
        }
    ]
}

```

这样我就做到了关键数据索引`logstash*`只允许`admin`用户访问，而`user`账号可以对`logs`和`kibana`进行只读操作，大家可以自行测试。 这里顺便解决了`kibana`本身没有权限控制的问题，对于`dashborad`展示分享给`user`用户，也不用担心他们会对图标设置进行误操作而影响其他用户使用。

0x04 总结
=======

* * *

其实`search guard`的功能远不止以上介绍的这些，例如细化到字段或者文档级别的ACL；节点之间通过SSL同步数据；使用ladp或者AD账号进行验证等功能希望后续能给大家带来介绍。

愿本文能起到抛砖引玉的效果。