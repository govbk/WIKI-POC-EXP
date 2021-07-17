# search-guard 在 Elasticsearch 2.3 上的运用

**Author：uni3orns**

参考内容：

*   [http://kibana.logstash.es/content/elasticsearch/auth/searchguard-2.html](http://kibana.logstash.es/content/elasticsearch/auth/searchguard-2.html)
*   [https://groups.google.com/forum/#!forum/search-guard](https://groups.google.com/forum/#!forum/search-guard)
*   [https://github.com/floragunncom/search-guard](https://github.com/floragunncom/search-guard)

此文章基于以下软件版本，不同版本可能略有差异：

*   elasticsearch 2.3.3
*   search-guard 2.3.3 RC1

0x00 背景
=======

* * *

Elasticsearch是一个基于Lucene构建的开源,分布式,RESTful搜索引擎，大量使用于各种场景，随着不断的发展，不可避免的会产生安全问题，一些危害比较大的漏洞比如CVE-2015-3337、CVE-2015-5531。面对这些漏洞（包括0day）的威胁，以及多业务使用使用同一套es集群的情况，使用一套认证授权系统就显得尤为必要。  
经过es1代到2代产品的过度，目前主流的方案就只有官方的shield以及开源search-guard，然而我厂比较扣。

0x01 search-guard
=================

* * *

search-guard 更新到2.x后跟 shield 配置上很相似，相比1.x的版本逻辑上更加松散。

searchguard 优点有：

*   节点之间通过 SSL/TLS 传输
*   支持 JDK SSL 和 Open SSL
*   支持热载入，不需要重启服务
*   支持 kibana4 及 logstash 的配置
*   可以控制不同的用户访问不同的权限
*   配置简单

0x02 安装
=======

* * *

安装search-guard-ssl

```
sudo bin/plugin install -b com.floragunn/search-guard-ssl/2.3.3.11

```

安装search-guard-2

```
sudo bin/plugin install -b com.floragunn/search-guard-2/2.3.3.0-rc1

```

0x03 证书
=======

* * *

根据自身情况修改官方脚本生成admin证书、node证书、根证书，将 node 证书和根证书放在 elasticsearch 配置文件目录下，同时将admin证书和根证书放到search-guard 配置文件目录下

**tips：证书需要统一生成**

0x04 配置 elasticsearch 支持 ssl
============================

* * *

elasticsearch.yml增加以下配置：

```
#############################################################################################
#                                       SEARCH GUARD                                        #
#                                       Configuration                                       #
#############################################################################################
# Add the following properties to your standard elasticsearch.yml
# (alongside with the SG SSL settings)
# This settings must always be the same on all nodes in the cluster

# This defines the DNs (distinguished names) of certificates
# to which admin privileges should be assigned
security.manager.enabled: false
searchguard.authcz.admin_dn:
  - "CN=kirk,OU=client,O=client,l=tEst, C=De"
# kirk是administrator，可以自行修改
# This is optional
# Only needed when impersonation is used
# Allow DNs (distinguished names) to impersonate as other users
#searchguard.authcz.impersonation_dn:
#  "CN=spock,OU=client,O=client,L=Test,C=DE":
#    - worf
#  "cn=webuser,ou=IT,ou=IT,dc=company,dc=com":
#    - user2
#    - user1

# Auditlog configuration:

searchguard.audit.type: internal_elasticsearch
#searchguard.audit.type: external_elasticsearch
#searchguard.audit.config.http_endpoints: ['localhost:9200','localhost:9201','localhost:9202']"
#searchguard.audit.config.index: auditlog # make sure you secure this index properly
#searchguard.audit.config.type: auditlog
#searchguard.audit.config.username: auditloguser
#searchguard.audit.config.password: auditlogpassword
#searchguard.audit.config.enable_ssl: false
#searchguard.audit.config.verify_hostnames: false
#searchguard.audit.config.enable_ssl_client_auth: false

# If Kerberos authentication should be used you have to configure this:

# The absolute path or relative path to config/ directory
# to krb5.conf file
#searchguard.kerberos.krb5_filepath: '/etc/krb5.conf'

# The absolute path or relative path to config/ directory
# to the keytab where the acceptor_principal credentials are stored.
#searchguard.kerberos.acceptor_keytab_filepath: 'eskeytab.tab'

#############################################################################################
#                                     SEARCH GUARD SSL                                      #
#                                       Configuration                                       #
#############################################################################################


#############################################################################################
# Transport layer SSL                                                                       #
#                                                                                           #
#############################################################################################
# Enable or disable node-to-node ssl encryption (default: true)
searchguard.ssl.transport.enabled: true
# JKS or PKCS12 (default: JKS)
searchguard.ssl.transport.keystore_type: JKS
# Relative path to the keystore file (mandatory, this stores the server certificates), must be placed under the config/ dir
searchguard.ssl.transport.keystore_filepath: node-1-keystore.jks
# 当前节点的证书，根据节点名字生成
# Alias name (default: first alias which could be found)
#searchguard.ssl.transport.keystore_alias: my_alias
# Keystore password (default: changeit)
#searchguard.ssl.transport.keystore_password: changeit

# JKS or PKCS12 (default: JKS)
searchguard.ssl.transport.truststore_type: JKS
# Relative path to the truststore file (mandatory, this stores the client/root certificates), must be placed under the config/ dir
searchguard.ssl.transport.truststore_filepath: truststore.jks
# Alias name (default: first alias which could be found)
#searchguard.ssl.transport.truststore_alias: my_alias
# Truststore password (default: changeit)
searchguard.ssl.transport.truststore_password: changeit
# Enforce hostname verification (default: true)
searchguard.ssl.transport.enforce_hostname_verification: true
# 如果没有证书服务器，需要设置为false，否则无法加入集群
# If hostname verification specify if hostname should be resolved (default: true)
searchguard.ssl.transport.resolve_hostname: true
# Use native Open SSL instead of JDK SSL if available (default: true)
searchguard.ssl.transport.enable_openssl_if_available: false

# Enabled SSL cipher suites for transport protocol (only Java format is supported)
# WARNING: Expert setting, do only use if you know what you are doing
# If you set wrong values here this this could be a security risk
#searchguard.ssl.transport.enabled_ciphers:
#  - "TLS_DHE_RSA_WITH_AES_256_CBC_SHA"
#  - "TLS_DHE_DSS_WITH_AES_128_CBC_SHA256"

# Enabled SSL protocols for transport protocol (only Java format is supported)
# WARNING: Expert setting, do only use if you know what you are doing
# If you set wrong values here this this could be a security risk  
#searchguard.ssl.transport.enabled_protocols:
#  - "TLSv1.2"

#############################################################################################
# HTTP/REST layer SSL                                                                       #
#                                                                                           #
#############################################################################################
# Enable or disable rest layer security - https, (default: false)
#searchguard.ssl.http.enabled: true
# JKS or PKCS12 (default: JKS)
#searchguard.ssl.http.keystore_type: PKCS12
# Relative path to the keystore file (this stores the server certificates), must be placed under the config/ dir
#searchguard.ssl.http.keystore_filepath: keystore_https_node1.jks
# Alias name (default: first alias which could be found)
#searchguard.ssl.http.keystore_alias: my_alias
# Keystore password (default: changeit)
#searchguard.ssl.http.keystore_password: changeit
# Do the clients (typically the browser or the proxy) have to authenticate themself to the http server, default is OPTIONAL
# To enforce authentication use REQUIRE, to completely disable client certificates use NONE
#searchguard.ssl.http.clientauth_mode: REQUIRE
# JKS or PKCS12 (default: JKS)
#searchguard.ssl.http.truststore_type: PKCS12
# Relative path to the truststore file (this stores the client certificates), must be placed under the config/ dir
#searchguard.ssl.http.truststore_filepath: truststore_https.jks
# Alias name (default: first alias which could be found)
#searchguard.ssl.http.truststore_alias: my_alias
# Truststore password (default: changeit)
#searchguard.ssl.http.truststore_password: changeit
# Use native Open SSL instead of JDK SSL if available (default: true)
#searchguard.ssl.http.enable_openssl_if_available: false

# Enabled SSL cipher suites for http protocol (only Java format is supported)
# WARNING: Expert setting, do only use if you know what you are doing
# If you set wrong values here this this could be a security risk
#searchguard.ssl.http.enabled_ciphers:
#  - "TLS_DHE_RSA_WITH_AES_256_CBC_SHA"
#  - "TLS_DHE_DSS_WITH_AES_128_CBC_SHA256"

# Enabled SSL protocols for http protocol (only Java format is supported)
# WARNING: Expert setting, do only use if you know what you are doing
# If you set wrong values here this this could be a security risk  
#searchguard.ssl.http.enabled_protocols:
#  - “TLSv1.2"

```

### 重启 elasticsearch

注意：任何修改elasticsearch.yml的操作都需要重启elasticsearch才能生效

### 配置文件介绍

searchguard 主要有5个配置文件在 plugins/search-guard-2/sgconfig 下：

**sg_config.yml:**

*   主配置文件不需要做改动

**sg_internal_users.yml:**

*   本地用户文件，定义用户密码以及对应的权限。例如：对于 ELK 我们需要一个 kibana 登录用户和一个 logstash 用户：
    
    ```
    kibana4:
      hash: $2a$12$xZOcnwYPYQ3zIadnlQIJ0eNhX1ngwMkTN.oMwkKxoGvDVPn4/6XtO
      #password is: kirk
      roles:
        - kibana4
    logstash:
      hash: $2a$12$xZOcnwYPYQ3zIadnlQIJ0eNhX1ngwMkTN.oMwkKxoGvDVPn4/6XtO
      roles:
        - logstash
    
    ```

密码可用plugins/search-guard-2/tools/hash.sh生成

**sg_roles.yml:**

*   权限配置文件，这里提供 kibana4 和 logstash 的权限样例
    
    ```
    #<sg_role_name>:
    #  cluster:
    #    - '<permission>'
    #  indices:
    #    '<indexname or alias>':
    #      '<type>':  
    #        - '<permission>'
    #      _dls_: '<querydsl query>'
    #      _fls_:
    #        - '<field>'
    #        - '<field>'
    sg_kibana4:
      cluster:
          - cluster:monitor/nodes/info
          - cluster:monitor/health
      indices:
        '*':
          '*':
            - indices:admin/mappings/fields/get
            - indices:admin/validate/query
            - indices:data/read/search
            - indices:data/read/msearch
            - indices:admin/get
            - indices:data/read/field_stats
        '?kibana':
          '*':
            - indices:admin/exists
            - indices:admin/mapping/put
            - indices:admin/mappings/fields/get
            - indices:admin/refresh
            - indices:admin/validate/query
            - indices:data/read/get
    sg_logstash:
      cluster:
        - indices:admin/template/get
        - indices:admin/template/put
      indices:
        'logstash-*':
          '*':
            - WRITE
            - indices:data/write/bulk
            - indices:data/write/delete
            - indices:data/write/update
            - indices:data/read/search
            - indices:data/read/scroll
            - CREATE_INDEX
    
    ```

**sg_roles_mapping.yml:**

*   定义用户的映射关系，添加 kibana 及 logstash 用户对应的映射：
    
    ```
    sg_logstash:
      users:
        - logstash
    sg_kibana4:
      backendroles:
        - kibana
      users:
        - kibana4
    
    ```

**sg_action_groups.yml:**

*   定义权限

### 加载配置并启用

```
sh plugins/search-guard-2/tools/sgadmin.sh -cn 集群名称（默认为elasticsearch，修改名称必须添加此参数） -h 127.0.0.1 -cd plugins/search-guard-2/sgconfig -ks plugins/search-guard-2/sgconfig/kirk-keystore.jks -kspass kspass -ts plugins/search-guard-2/sgconfig/truststore.jks  -tspass tspass -nhnv

```

如修改了searchguard，则需要重新加载配置执行

注意：search-guard配置的相关改动不需要重启elasticsearch，相关的配置实际上存储在searchguard 的indice下了

至此大家就可以安全的使用elasticsearch

关于ldap以及https的配置将在下一篇给出