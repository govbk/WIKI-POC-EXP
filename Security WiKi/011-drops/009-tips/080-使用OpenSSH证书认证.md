# 使用OpenSSH证书认证

0x00 摘要
-------

* * *

2010年三月，ssh证书认证悄然地包含到了OpenSSH5.4中。到了2014年，很多人对ssh证书依旧相当模糊，既没有得到广泛的理解，也没有得到广泛的使用。对于这样一个问题，我们可能会认为它实施起来要不是很难，就是很复杂。实际上这样做既不难，也不复杂，只是它没有得到较好的文档化的描述。 

本文的目标是以一种实际的方式向各位展示使用和管理ssh证书认证有多容易，无论是较小的还是较大的环境。

本文的创建用于解答笔者日常中遇到的一些ssh证书认证的问题，当然还增添了在学习过程中发现的一些东西。本文内容中也许会有点小差错，某些特性也没有提到，欢迎各位指正。

0x01 基本知识
---------

* * *

本文假设你已经了解：

```
基本的Unix/Linux服务器管理

```

SSH管理，包括但不限于：

```
a) 密钥生成
b) SSH公钥认证
c) 使用SSH代理
d) 使用口令加密密钥

```

基本的安全概念如：

```
不要直接以root身份登陆

```

0x02 SSH证书介绍
------------

* * *

证书是已有的ssh公钥认证系统的扩展，可被应用于任何已有的公钥和私钥对，也可以用于任何当前ssh支持的认证方法。

尽管(SSH证书认证)基于公钥认证，它同时也被设计来简化多台服务器之间密钥管理的复杂性。证书免除了对已知主机和经授权用户文件的需要，如果实现合理的话，只许更少的人力便能复制全部功能。

由于证书认证是公钥加密的一个扩展，它可以与OPenSSH支持的任意密钥类型和密钥大小的ssh2协同使用。这意味着如果你当前的OpenSSH支持的话，RSA、DSA、EC都能使用。方便起见，本文将使用默认的RSA-1024。

Tips:有些较老的操作系统虽然使用OpenSSH5.4或更高的版本，但是还是不支持EC。

0x03 证书 VS. 公钥
--------------

* * *

常规的公钥认证和证书认证之间有几点较大的不同，最大的不同就是证书验证上。

### 与其他公钥证书标准不同

SSH证书相比其他证书格式如x509、SSL中使用的PEM更为简单

```
a) 没有证书链，只有一个CA
b) 没有可疑的的商业签名授权(authority)
c) 除了CA签名外没有可信模式

```

### 主机认证

| 操作 | 公钥认证 | 证书认证 |
| :-: | :-: | :-: |
| 认证未知主机 | 初始登陆时询问用户是否接受主机秘钥 | 验证CA签发的主机证书 |
| 认证已知主机 | 将密钥和用户的已知主机文件对比 | 验证CA签发的主机证书 |
| 替换已知主机的密钥 | a) 入口必须从用户的已知主机文件中删除 b) 用户登录时会被问及是否接受新的主机秘钥 | 验证CA签发的主机证书 |
| 撤销密钥/证书 | 在用户的known_hosts文件中增加“@revoked”行 | 在用户的known_hosts文件中增加“@revoked”行 |

### 使用证书认证的好处

```
a) 用户可以认证之前没有登入过的主机
b) 无需再分发或管理已知的已知主机文件(例：puppet)
c) 可以无需用户干预实现服务器替换及密钥再生成
d) 除非什么地方出错了，用户在工作场合再也不会收到接受服务器密钥的提示
e) 通过搜索未签名的主机密钥可以发现不一致的主机

```

### 用户认证

| 操作 | 公钥认证 | 证书认证 |
| :-: | :-: | :-: |
| 认证 | 用户的公钥来自每个服务器主机用户经授权的密钥文件 | 检查用户证书是否由CA签名 |
| 过期密钥/证书 | 不做强制 | 过期时间由管理员在签名时设置 |
| 登录用户名 | 服务器上的目标用户的公钥置于每个用户目录下的authorized_keys文件中 | 用户名可在签名时添加到证书中，也可由每个服务器上的AuthorizedPrinciples文件控制 |
| 限制(端口转发、强制命令等) | 可以在authorized_keys文件中(可被用户编辑)，可在每个服务器sshd_config的匹配用户/组块中 | 可在签名时加入证书中，可在每个服务器sshd_config的匹配用户/组块中，可在每个服务器”经授权的规则”中添加 |
| 撤销密钥/证书 | 可添加到每个服务器的RevokedKeys文件中或从服务器上每个受影响的authorized_keys文件移除 | 每个服务器上将证书添加到”RevokedKeys”文件中 |
| 替换用户的证书 | 服务器上authorized_keys文件必须可被编辑 | 将旧证书添加到服务器上已撤销的密钥文件或签名新的证书 |

使用证书认证的好处

```
a) 证书过期时间可由管理员在签名时设置，强制实施轮转策略 
b) 无需跨越多台主机管理已授权的证书 
c) 不用担心恶意用户编辑或添加内容到未管理的经授权文件 
d) 在签名时更容易限制某些用户的权限 
e) 无需从已授权密钥文件中移除已吊销的密钥 
f) 证书签名时可以限制用户使用指定的用户名 

```

0x04 让它工作起来
-----------

* * *

实现ssh证书认证要比SSL证书容易得多，最难的地方是决定签名用户和服务器是使用单个CA密钥还是使用两个CA密钥——服务器和用户各一个

我们推荐使用两个独立的密钥用于签名的用户和服务器，以便让不同的角色来管理每一个功能：例如，一个系统管理员可以登录服务器密钥，而安全管理员可以登录该用户的密钥。

下面的例子中服务器和用户使用各自的证书授权

### 服务器授权

激活服务器授权仅需4个步骤

#### 1. 创建服务器CA

在你的证书授权服务器上运行下列命令：

```
~ $ # Lets start with good organization
~ $ mkdir -p ssh_cert_authorita/server_ca
~ $ cd ysh_cert_authority/server_ca/

~/ssh_cert_authority/server_ca $ # Now lets generate our server certificate authority keypair
~/ssh_cert_authority/server_ca $ ssh-keygen -f server_ca -C "companyname_server_ca"
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
wour identification has been saved in server_ca.
Your public key has been saved in server_ca.pub.
The key fingerprint is:
21:f6:9f:5d:ec:75:2e:df:c0:6b:5e:9d:5b:97:d8:19 "companyname_server_ca"

~/ssh_cert_authority/server_ca $ # The resulting files
~/ssh_cert_authority/server_ca $ ls -l
total 8
-rw------- 1 username username 1675 Aug 16 14:12 server_ca
-rw-r--r-- 1 username username  409 Aug 16 14:12 server_ca.pub

```

Tips:强烈建议不仅使用密码，还要使用强密码。任何用这个密钥签名的人都能添加受信任的服务器访问到你的网络。

#### 2. 签名主机密钥

既然证书认证是公钥认证的一个扩展，你可以使用已有的

```
/etc/ssh/ssh_host*key.pub

```

ssh主机密钥。举例来说，任何类型的ssh主机密钥都可以。

在你的证书授权服务器上运行如下命令：

```
~/ssh_cert_authority/server_ca $ # 为拷贝主机密钥和证书留个地方
~/ssh_cert_authority/server_ca $ mkdir -p host_certs
~/ssh_cert_authority/server_ca $ cd host_certs

~/ssh_cert_authority/server_ca/host_certs $ # 从主机下载主机密钥
~/ssh_cert_authority/server_ca/host_certs $ scp -rp example.host.net:/etc/ssh/ssh_host_rsa_key.pub example.host.net.pub
ssh_host_rsa_key.pub                                                                   100%  396     0.4KB/s   00:00    

~/ssh_cert_authority/server_ca/host_certs $ # 签名主机密钥
~/ssh_cert_authority/server_ca/host_certs $ ssh-keygen -s ../server_ca -I example.host.net -h -n example.host.net,96.126.102.173,2600:3c01::f03c:91ff:fe69:87a2 example.host.net.pub 
Signed host key example.host.net-cert.pub: id "example.host.net" serial 0 for example.host.net,123.45.67.89,2600:dead:beef:cafe:::87a2 valid forever

~/ssh_cert_authority/server_ca/host_certs $ # 结果文件
~/ssh_cert_authority/server_ca/host_certs $ ls -l
total 8
-rw-r--r-- 1 username username 1430 Aug 16 14:19 example.host.net-cert.pub
-rw-r--r-- 1 username username  396 Jul 14 20:19 example.host.net.pub

~/ssh_cert_authority/server_ca/host_certs $ # 将证书考回服务器
~/ssh_cert_authority/server_ca/host_certs $ scp -rp example.host.net-cert.pub root@example.host.net:/etc/ssh/ssh_host_rsa_key-cert.pub
example.host.net-cert.pub                                                           100% 1430     1.4KB/s   00:00

```

Tips：

```
保留CA的所有公钥及证书，如果你需要撤销它们，最好复制一份 

创建服务器证书时，注意 –l 、–h、 –n 选项的用法 

1) -n 选项只能指向相关的主机名、IP地址，空格、通配符或任意名字会导致可互换的服务器证书 
2) -l 选项可以是用于标识这个证书的任意文本，而且你没必要使用和上面同样的格式 
3) -h 选项标明证书为主机证书

```

#### 3. 改变服务器配置

```
HostCertificate /etc/ssh/ssh_host_rsa_key-cert.pub

```

保存/etc/ssh/sshd_config保存完毕后，重启sshd

#### 4. 客户端配置改变

复制`server_ca.pub`中的文本，进入你的`~/.ssh/known_hosts`(或`/etc/ssh/known_hosts`)文件，参考：

```
@cert-authority *.host.net,123.45.67.* ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDVifNRc+EN4b9g/ygWRCIvV1qw0aR33qzkutIA6C3MzHidaXe6tO4Q35YqrP2UUhOdcl2g8nO7BNSSHkjrFyEnyNqkpgHYcDzUdpE6XGS6rNcjrmLajf1CRvUBvFD0ceu//z6HL1dpE347AHSZbFxHT6NdhscdEd/Bd5c1aVyS+dUdiGX4U9YdgTN2lM8zQy5rJo+siFyHmtqXh1ZVBBC+VBF6ZPzMkxvkJmAp4eWCQJOZLIybcNZlyuXrs1bXV0X0ZIIL2j/gYC2gJPO1FUTKRcqzo/fQ/m6hAhxMMpTTgI92FiE/QOfOk5+MmgfTOqsF0us2TJ5mrSIE9o/3DQsj "companyname_server_ca"

```

Tips：

```
a) 删除 known_host 中与”example.host.net”相关的host
b) 该文件的格式遵循标准的known_hosts格式，但要注意通配符匹配整个域和IP地址范围。

```

#### 5. 测试服务器认证

```
~ $ ssh -v username@example.host.net
...
debug1: Server host key: RSA-CERT 39:aa:3f:bb:eb:24:11:93:15:b1:63:2f:de:ad:be:ef
debug1: Host 'example.host.net' is known and matches the RSA-CERT host certificate.
...

```

### 用户认证

用户认证不会比服务器认证更难

#### 1. 创建用户CA

在你的证书授权服务器上运行下列命令：

```
~ $ # Lets start with good organization
~ $ mkdir -p ssh_cert_authority/user_ca
~ $ cd ssh_cert_authority/user_ca

~/ssh_cert_authority/user_ca $ # 生成我们的服务器证书授权密钥对
~/ssh_cert_authority/user_ca $ ssh-keygen -f user_ca -C "companyname_user_ca"
Generating public/private rsa key pair.
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in user_ca.
Your public key has been saved in user_ca.pub.
The key fingerprint is:
90:67:8a:ed:b6:53:0a:bd:06:f0:71:ce:fb:89:b9:3e "companyname_user_ca"

~/ssh_cert_authority/user_ca $ # 结果文件
~/ssh_cert_authority/user_ca $ ls -l
total 8
-rw------- 1 username username 1679 Aug 16 18:14 user_ca
-rw-r--r-- 1 username username  407 Aug 16 18:14 user_ca.pub

~/ssh_cert_authority/user_ca $ # 把user_ca.pub复制到服务器上
~/ssh_cert_authority/user_ca $ scp -rp user_ca.pub root@example.host.net:/etc/ssh
user_ca.pub                                                                            100%  407     0.4KB/s   00:00

```

Tips:强烈建议不仅使用密码，还要使用强密码。任何用这个密钥签名的人都能访问你网络中所有服务器上的任意用户。

#### 2. 签名用户密钥

让一个用户创建一个ssh公钥集，并获得他们公钥的拷贝

恢复用户公共SSH密钥的拷贝，执行如下命令：

```
~/ssh_cert_authority/user_ca $ # 我们需要一个地方存放签名的证书
~/ssh_cert_authority/user_ca $ mkdir -p user_certs
~/ssh_cert_authority/user_ca $ cd user_certs/

~/ssh_cert_authority/user_ca/user_certs $ # 以使用公钥为例
~/ssh_cert_authority/user_ca/user_certs $ cp ~/.ssh/id_rsa.pub username.pub

~/ssh_cert_authority/user_ca/user_certs $ # Sign the key
~/ssh_cert_authority/user_ca/user_certs $ ssh-keygen -s ../user_ca -I user_full_name -n root,loginname username.pub 
Signed user key username-cert.pub: id "user_full_name" serial 0 for root,loginname valid forever

~/ssh_cert_authority/user_ca/user_certs $ # 结果文件
~/ssh_cert_authority/user_ca/user_certs $ ls -l
total 8
-rw-r--r-- 1 username username 1525 Aug 16 22:01 username-cert.pub
-rw------- 1 username username  411 Aug 16 22:00 username.pub

~/ssh_cert_authority/user_ca/user_certs $ # 复制证书到用户的~/.ssh/文件夹下
~/ssh_cert_authority/user_ca/user_certs $ cp username-cert.pub ~/.ssh/id_rsa-cert.pub

```

Tips：

```
保留CA的所有公钥和证书，如果你需要撤销它们，最好复制一份 
当创建服务器证书时，你不能否认–l、–n 选项的使用 

a) -n 选项只能指向相关的登陆用户名，空格、通配符名字会允许任何有效用户账户的登录，除非在服务端有其他的严格限制。在本例中，用户名使用root和loginname
b) -l 选项可以是用于标识这个证书任意文本，而且你没必要使用和上面一样的格式

```

#### 3. 服务器配置改变

在你想激活证书认证的每台服务器上将如下代码添加至`/etc/ssh/sshd_config`

```
TrustedUserCAKeys /etc/ssh/user_ca.pub

```

保存sshd_config文件，重启sshd

#### 4. 测试用户认证

从服务上所有的经授权密钥文件中删除用户公钥

运行如下命令：

```
~ $ ssh -v username@example.host.net
...
debug1: identity file /home/username/.ssh/id_rsa-cert type 4
debug1: Offering RSA-CERT public key: /home/username/.ssh/id_rsa
debug1: Server accepts key: pkalg ssh-rsa-cert-v01@openssh.com blen 1101
...

```

另外，如果你开启了调试记录，你会看到如下日志：

```
Jul 18 23:22:03 localhost sshd[9603]: debug1: list_hostkey_types: ssh-rsa,ssh-rsa-cert-v01@openssh.com [preauth]
Jul 18 23:22:03 localhost sshd[9603]: Accepted certificate ID "user_username" signed by RSA CA d2:c0:6c:08:2b:e4:b4:f2:cd:56:22:66:de:ad:be:ef via /etc/ssh/user_ca.pub

```

0x05 更进一步
---------

* * *

上述步骤是证书认证的基础，接下来我们会涵盖一些更细节的特性。

### 撤销密钥和证书

授予访问你的服务器很棒，但是你必须要有权利撤销这种访问

下面的方法同样适用于公钥认证，目前它们是撤销ssh证书的唯一方式

#### 1. 撤销用户密钥

启用用户取消功能，将如下代码添加至你服务器的`/etc/ssh/sshd_config`：

```
RevokedKeys /etc/ssh/ssh_revoked_keys

```

然后输入如下命令：

```
~ $ # 如果文件不存在且对sshd不可读，**all** 用户将没有访问权限
~ $ sudo touch /etc/ssh/ssh_revoked_keys
~ $ sudo chmod 644 /etc/ssh/ssh_revoked_keys.

```

一旦完成，重启sshd

当需要从服务器撤销用户访问权限时，简单地添加其公钥或证书到`/etc/ssh/ssh_revoked_keys`中。文件格式同authorized_keys密钥类似，一个密钥或证书占一行

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDL8HShSFKdY3Tox9U+gUotTFlRedPxI5zSrU6KiZEXA8i+37BtB0yp502q3Dx1MmXBF8Pqa+xEQ9DOgtragDwX0V7ieOjvRSB83w2Orj9cdMj8U6WluU2T+QlD2JtVmOp0Skg4k3AENIN9J0rmnxvmuCZa2G5f+6DGp/pW5kk9FfNv1xaAOgy3yfExD2w5cEHZfztajbTuCE6z9aNxU96ZHvXdV6Z8M3xkkea6IUU3XCyg+lB/qSq+KoBoByzwZSJ6BfA7x63okq57K6XsPp4GuVukq0OmDk9ZLpqmeC8esWhniA+2DwmjdaFa1k9K/bpCy4mVLhqTgwkU9u8rxaCd username@hostname
ssh-rsa-cert-v01@openssh.com AAAAHHNzaC1yc2EtY2VydC12MDFAb3BlbnNzaC5jb20AAAAgcrHTa3GDn51GnAnGuuFz//tS+NsIk0pP16nEglh4/08AAAADAQABAAABAQCxl7RSkZwRW0igzKUGUqkthFvH8Su3m0G1kWC4YBQht9TkXsSsWVW5FGbIGrYWy2JOJngAKTk6T82ySiuJnMA2esEW4thZ5kp8MgdCcMuqUGfFXxkHHF0cnzY0AWSD3z8WvuGVEWDTtIUpBqiW/ZvVZgVpHViqGF8AAbiFL2iRdG4D5g35ydFs0Gujn38zfyJLRVK/AQtqS9yzh6wRfgOu0/QXI/pYVV4imuXgQCsouW/gSItvg5Qdp8tyaA0hYJA7XHD6DCxr3RplT1XrsIMuROY1nSqTq0wpXl7XPM6aLOts63uPypumMIuq5kqX+5NBd+C6gDnEU7Xedce+Ch/LAAAAAAAAAAAAAAABAAAADnVzZXJfZnVsbF9uYW1lAAAADAAAAAh1c2VybmFtZQAAAAAAAAAA//////////8AAAAAAAAAggAAABVwZXJtaXQtWDExLWZvcndhcmRpbmcAAAAAAAAAF3Blcm1pdC1hZ2VudC1mb3J3YXJkaW5nAAAAAAAAABZwZXJtaXQtcG9ydC1mb3J3YXJkaW5nAAAAAAAAAApwZXJtaXQtcHR5AAAAAAAAAA5wZXJtaXQtdXNlci1yYwAAAAAAAAAAAAABFwAAAAdzc2gtcnNhAAAAAwEAAQAAAQEAy/B0oUhSnWN06MfVPoFKLUxZUXnT8SOc0q1OiomRFwPIvt+wbQdMqedNqtw8dTJlwRfD6mvsREPQzoLa2oA8F9Fe4njo70UgfN8Njq4/XHTI/FOlpblNk/kJQ9ibVZjqdEpIOJNwBDSDfSdK5p8b5rgmWthuX/ugxqf6VuZJPRXzb9cWgDoMt8nxMQ9sOXBB2X87Wo207ghOs/WjcVPemR713VemfDN8ZJHmuiFFN1wsoPpQf6kqviqAaAcs8GUiegXwO8et6JKueyul7D6eBrlbpKtDpg5PWS6apngvHrFoZ4gPtg8Jo3WhWtZPSv26QsuJlS4ak4MJFPbvK8WgnQAAAQ8AAAAHc3NoLXJzYQAAAQBza5ekUSM6/HKNNxfsPsynW6XNVblHdWuWGdFdHU+xo5y+MqPhkOcHEK3g3MZ5xQ75CSBeNPmd+ivIAUr7czwnWE7gJF/0q2ft3tahp+t9vOV7bvTQDf6afnSOwFRWVhoUC0OItHVQ5DphL+QuUsRtq/1a99DuhhNoqO7RJeNvgWwhnPI9LuTZ/wdJGxBsY0d1bS/3ktFtPPdbQNBWcQG8ShwdJj3XM5eKkzUNrjm1CfSi4fyVWX53gx6+dKxwlg7rI1GuZ14is3ZEb6oSk++P4MrSsqeIhKiE0QLNp6kXi8qwdYX93VrI+pD9mv7qLU3h22JvQUKnuWNvdJJuQATZ username@hostname

```

Tips:

```
a) 这阻断了系统范围公钥和证书的使用
b) 公钥更为理想化，因为它们更小，除了会阻断证书认证还会阻断公钥
c) 这里证书同样能工作良好，但是如果它在authorized_keys文件中它不会阻断公钥

```

  

```
Jul 19 00:27:26 localhost sshd[11546]: error: WARNING: authentication attempt with a revoked RSA-CERT key 6d:59:82:70:2b:93:dc:57:a6:c6:1f:64:de:ad:be:ef

```

#### 2. 撤销服务器密钥

服务器密钥得从用户的已知主机文件中撤销，或者在`/etc/ssh/known_hosts`使用：

```
@revoked * ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDc9wlKYUzWZcfvPOa0L+h6Wbb/k9yJgXbnqa3VF+ucdwmBSiT3zBMAjqjFMnN3MuI4oig3SqkIXKPWn0QgFoV4d3G4opzs/OdZ6WLyxLwYQBggUQDg4QhKuHDltIR/BMxYlhB20ngmkaiBiK+Q4ThFRpW7FElOsuZ3rgJq559PgkFeFMY06oyzUMaSshFM84U/1zrVL4BgdnZBcJn018psem5kSkd0Gxm+ao1TuEnMGeArVMFiG9Hq1o2E+QGp1euE4YYQtR533fyZ8BSTE9ThLkmTXgU31dn1irFatBrBENm7TnIVmNT410NqV5J9zDME4NAnuEVwNWtq65rZkgut root@localhost

```

Tips：

```
a) 通配符会阻止主机密钥被任何主机使用 
b) 上面的情况中，公钥和证书都能工作，不过公钥更小且更有效 
c) 当和个别已知主机入口一起工作时，简单地删除一个入口并不会阻止密钥被再次使用 

```

示例：

```
~ $ ssh example.host.net
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@       WARNING: REVOKED HOST KEY DETECTED!               @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
The RSA host key for example.host.net is marked as revoked.
This could mean that a stolen key is being used to impersonate this host.
RSA host key for example.host.net was revoked and you have requested strict checking.
Host key verification failed.

```

### 证书控制

签名一个证书时，管理员可以直接实行证书控制，在没有重签名的情况下证书不能被改变

#### 1. 证书过期

大多数组织使用密码过期策略，许多情况下需求密码和证书过期，遗憾的是目前仅有特设方法执行ssh密钥轮换。

使用证书，一个过期日期在签名时会加载到证书中，可以使用ssh时间格式-V选项完成

```
~/ssh_cert_authority/user_ca/user_certs $ # Expiration in 52 weeks
~/ssh_cert_authority/user_ca/user_certs $ ssh-keygen -s ../user_ca -I user_full_name -n root,loginname -V +52w username.pub

~/ssh_cert_authority/user_ca/user_certs $ # Expiration in 180 days
~/ssh_cert_authority/user_ca/user_certs $ ssh-keygen -s ../user_ca -I user_full_name -n root,loginname -V +180d username.pub

```

#### 2. 登录名

正如签名提到的，可以使用-n选项强制使用证书中的登录名和服务器名

对用户来说，这限制了用户在远程服务器上指定的登录名，一般来说，这应该是一个单用户名，但是在一些环境中可能需要多个用户名

下面的例子允许单个证书上的多个登录名：

```
~/ssh_cert_authority/user_ca/user_certs $ ssh-keygen -s ../user_ca -I user_full_name -n loginname,anothername,thirdname username.pub

```

#### 3. 选项(仅限用户证书)

对于用户证书

对用户证书而言，签名时可以直接构建好几个选项到证书中。一般来说，这些选项运用于/etc/sshd_config或经授权的密钥文件中，这些选项是：

```
a) clear：假设没有默认选项 
b) force-command=(command)：强制远程命令执行 
c) 默认许可的：代理转发/无代理转发 
d) 默认许可的：端口转发/无端口转发 
e) 默认许可的：pty/无pty 
f) 默认许可的：permit-user-rc/no-user-rc 
g) 默认许可的：x11转发/无x11转发 
h) 源地址=(地址列表)：限制源地址，这些地址中的证书为有效 

```

示例：

```
~/ssh_cert_authority/user_ca/user_certs $ ssh-keygen -s ../user_ca -I user_full_name -n login \
  -O clear \ # Clear all default options, including forwarding of all kinds
  -O force-command=/some/specific/command \ # force execution of a specific command
  -O source-address=10.22.72.0/24 \ # limit logins from specific source addresses
  username.pub

```

上面的例子限制了只能在特定的服务器上自动化批处理，不允许pty，转发，并强制特定的命令

0x06 已知的问题
----------

* * *

### 证书版本问题

随着OpenSSH6.x的发布，证书的更新导致和OpenSSH 5.x之间存在兼容性问题

OpenSSH6.x生成的证书在OpenSSH 5.x上需要使用选项”-t v00”才能运行，例如：

```
$ ssh-keygen -t v00 -s ca_key -I key_id host_key.pub

```

OpenSSH 6.x似乎向后兼容OpenSSH 5.x生成的证书

### SSH客户端兼容性

除了OpenSSH，如果有的话，仅有少数客户端支持基于认证的证书

尽管大多数常见或不常见的操作系统都运行OpenSSH，也还是有使用其他客户端的。举例来说，Windows上非常流行的Putty，它至今都不支持证书认证。许多使用ssh的商业应用不支持证书认证，例如Rapid7的Nexpose

因此，如果可以的话，有些环境可能会比较难以强制实行只基于认证的证书

### CA密钥安全

集中化的密钥管理简化了认证管理流程，不幸的是这同时也简化了攻击面，攻击者只许获得CA密钥的管理就能获得对全网的访问

因此，CA密钥的管理必须处于高安全等级，如果可能的话，将它们存储在网络无法访问的地方，并千万千万确保它们被加密了

0x07 参考资料
---------

* * *

本文根据收集来的OpenSSH手册信息进行组织，它们可能会更详尽而且内容以后也会比本文更新

[sshd_config – OpenSSH SSH daemon configuration file](http://www.openbsd.org/cgi-bin/man.cgi?query=sshd_config&sektion=5)

[sshd – OpenSSH SSH daemon](http://www.openbsd.org/cgi-bin/man.cgi?query=sshd&sektion=8)

[ssh-keygen – authentication key generation, management and conversion](http://www.openbsd.org/cgi-bin/man.cgi?query=ssh-keygen&sektion=1)

原文：[Using OpenSSH Certificate Authentication](http://neocri.me/documentation/using-ssh-certificate-authentication/)