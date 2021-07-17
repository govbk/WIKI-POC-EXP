## 攻击 Weblogic 备忘录

### 0x00: 常见Weblogic

* WebLogic Server 11g（10.x 版本）

    **10.3.6 支持 JDK >= 1.6**

* WebLogic Server 12c（12.x 版本）

    **12.1.3 支持 JDK >= 1.7**

    **12.2.1 支持 JDK >= 1.8**

### 0x01: 主要攻击面

* #### T3反序列化

    CVE-2015-4852

    CVE-2016-0638

    CVE-2016-3510

    CVE-2017-3248

    CVE-2018-2628

    CVE-2018-3191

    CVE-2019-2890

* #### XMLDecoder反序列化

    CVE-2017-3248

    CVE-2017-3506

    CVE-2017-10271

    CVE-2019-2725

    CVE-2019-2729

* #### 控制台登录部署war

    `/console` （需要账号密码）

* #### T3协议部署war

    `https://github.com/quentinhardy/jndiat` （需要账号密码）

* #### 文件上传 getshell

    CVE-2018-2894

    CVE-2019-2618（需要账号密码）

* #### 文件读取

    CVE-2019-2615

* #### 内网请求(XXE/SSRF)

    CVE-2014-4210

    CVE-2018-3246

### 0x02: 常见漏洞相关路径

#### 一. console

```
# 常见密码 
weblogic/weblogic 
weblogic/weblogic123
weblogic/Weblogic123
weblogic/Oracle123
weblogic/Oracle@123

/console
/console/login/LoginForm.jsp
```

#### 二. _async

```
/_async/AsyncResponseService
/_async/AsyncResponseServiceHttps
/_async/AsyncResponseServiceJms
/_async/AsyncResponseServiceSoap12
/_async/AsyncResponseServiceSoap12Https
/_async/AsyncResponseServiceSoap12Jms
```

#### 三. wls-wsat

```
/wls-wsat/CoordinatorPortType
/wls-wsat/CoordinatorPortType11
/wls-wsat/ParticipantPortType
/wls-wsat/ParticipantPortType11
/wls-wsat/RegistrationPortTypeRPC
/wls-wsat/RegistrationPortTypeRPC11
/wls-wsat/RegistrationRequesterPortType
/wls-wsat/RegistrationRequesterPortType11
```

#### 四. 其他

```
/uddiexplorer/
/ws_utc/begin.do
/ws_utc/resources/setting/options/general
/bea_wls_management_internal2/wl_management
/bea_wls_deployment_internal/DeploymentService
```

### 0x03: 密文解密方法

解密的对象主要包括两种：

* 数据库连接字符串
* console登录用户名和密码

#### 一：数据库连接字符串位置

一般是在 `config/jdbc` 目录下的 `**jdbc.xml` 文件中

如：`/root/Oracle/Middleware/user_projects/domains/base_domain/config/jdbc/orcl-jdbc.xml`

#### 二：console登录用户名和密码位置

一般是在`security`目录

如：`/root/Oracle/Middleware/user_projects/domains/base_domain/security/boot.properties`

#### 三：密钥文件位置

即 `SerializedSystemIni.dat` 文件位置

如：`/root/Oracle/Middleware/user_projects/domains/base_domain/security/SerializedSystemIni.dat`

#### 主流解密方法：

1. **上传 jsp 脚本服务端解密**
2. **下载必要文件(以上三个)本地解密**

#### 参考文章：

[https://github.com/TideSec/Decrypt_Weblogic_Password](https://github.com/TideSec/Decrypt_Weblogic_Password)

### 0x04: 参考链接

[WebLogic 安全研究报告](https://paper.seebug.org/1012/)

[jndiat](https://github.com/quentinhardy/jndiat)

[Decrypt_Weblogic_Password](https://github.com/TideSec/Decrypt_Weblogic_Password)

