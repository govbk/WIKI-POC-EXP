# 一个PC上的“WormHole”漏洞

**Danny_Wei@腾讯玄武实验室**

0x00 前言
=======

* * *

最近安全界关注的焦点WormHole是一类不安全的开发习惯所导致的，在PC上类似问题也毫不罕见，只不过很多风险被微软默认自带的防火墙缓解了。希望本文和众多关于WormHole的讨论能获多或少地提高一些开发人员的安全意识。

下面要介绍的问题可导致的后果和WormHole非常类似：影响上亿用户、访问一个端口发送一条指令就可以让目标系统下载一个程序并执行。

该问题已于2015年9月29日被修复。在修复前，存在于所有使用预装Windows系统的ThinkPad、ThinkCentre、ThinkStation以及Lenovo V/B/K/E系列电脑。

0x01 背景
=======

* * *

联想ThinkVantage System Update软件用于帮助用户从联想的服务器中直接下载并安装软件、驱动、BIOS的更新，极大的简化了用户更新系统的难度和工作量。其被默认预装在联想的多款产品中。

Lenovo System Update可根据不同的网络环境及配置通过多种方式下载软件及更新，其中一种方式为通过文件共享下载，而UNCServer.exe则是完成此功能的主程序，UNCServer.exe随System Update主程序启动，并建立本地服务端等待主程序连接。在早期版本中，甚至System Update主程序退出后，UNCServer.exe也仍然保持运行状态。

0x02 问题描述
=========

* * *

在System Update的5.6.0.34版本中，UNCServer.exe通过.NET的Remoting机制，通过TCP服务器提供多种功能。

.NET Remoting发展自DCOM，是一项比较老的.NET分布式处理技术。它序列化服务端的对象和数据并导出，客户端通过HTTP、TCP、IPC信道跨越进程边界实现对服务端对象的引用。然而Remoting的序列化机制会隐式导出对象所有的方法和属性，客户端一旦获得服务端导出的对象引用，即可调用服务端对象提供的所有方法。因此Remoting机制容易引入安全漏洞，且不建议将Remoting服务终端导出给不受信任的客户端。

UNCServer导出的Connector对象提供Connect、DownloadBean、IsFileExist、IsFolderExist、GetFilesInFolder、GetSubFolder、QueryFile、LaunchIE功能。客户端可以连接并获取其引出对象，进行文件下载、应用程序执行等操作。

其中LaunchIE并未对参数进行任何验证，可以用来启动任意进程，其实现代码如下：

```
case UNCAction.LaunchIE:
        string fileName = (string) eventObj;
        try{
            Process.Start(fileName);
        }
        catch{
        }
        this.connector.Current = (object) true;
    break;

```

同时，虽然System Update在防火墙策略中只添加了UNCServer的出站规则，但由于UNCServer缺少必要的配置，使其绑定在0.0.0.0:20050上。因此在缺乏防火墙保护的情况下，任何机器都可与其建立连接，最终使用其提供的DownloadBean和LaunchIE功能实现远程下载程序并执行。

UNCServer建立服务端信道并导出对象的代码如下：

```
IDictionary properties = (IDictionary) new Hashtable();
properties[(object) "name"] = (object) "tvsuuncchannel";
properties[(object) "priority"] = (object) 2;
properties[(object) "port"] = (object) 20050;
this.channel = new TcpServerChannel(properties, (IServerChannelSinkProvider) new BinaryServerFormatterSinkProvider());
ChannelServices.RegisterChannel((IChannel) this.channel, false);
this.status = new object();
this.connector = new Connector();
RemotingServices.Marshal((MarshalByRefObject) this.connector, "Connector");
this.connector.UNCEvent += new Connector.UNCEventHandler(this.connector_UNCEvent);

```

0x03 修复
=======

* * *

联想在2015/9/29日放出的System Update 5.7.0.13修复了包括此问题在内的多个漏洞。其重新实现了LaunchIE、LaunchHelp功能，对其创建进程的参数进行了验证。并加强了服务端的配置，使其绑定在127.0.0.1:20050，阻止了远程请求。修复后的部分代码如下：

```
case UNCAction.LaunchIE:
        try{
            tring str = (string) eventObj;
            Uri result;
            if (Uri.TryCreate(str, UriKind.Absolute, out result) && (result.Scheme == Uri.UriSchemeHttp || result.Scheme == Uri.UriSchemeHttps))
                Process.Start(str);
        }
        catch{
        }
        this.connector.Current = (object) true;
    break;    


IDictionary properties = (IDictionary) new Hashtable();
properties[(object) "name"] = (object) "tvsuuncchannel";
properties[(object) "priority"] = (object) 2;
properties[(object) "port"] = (object) 20050;
properties[(object) "rejectRemoteRequests"] = (object) true;
properties[(object) "bindTo"] = (object) "127.0.0.1";
this.channel = new TcpServerChannel(properties, (IServerChannelSinkProvider) new BinaryServerFormatterSinkProvider());
ChannelServices.RegisterChannel((IChannel) this.channel, false);
this.status = new object();
this.connector = new Connector();
RemotingServices.Marshal((MarshalByRefObject) this.connector, "Connector");
this.connector.UNCEvent += new Connector.UNCEventHandler(this.connector_UNCEvent);

```

0x04 小结
=======

* * *

Remoting作为上一代的.NET分布式处理技术，由于设计时的安全缺陷早已被微软的WCF技术取代。如果应用程序仍在使用Remoting技术进行分布式处理或通信，应意识到其潜在的安全问题，稍有不当则可能引入安全漏洞。