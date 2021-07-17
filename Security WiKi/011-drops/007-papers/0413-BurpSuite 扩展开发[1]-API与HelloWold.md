# BurpSuite 扩展开发[1]-API与HelloWold

0x00 简介
=======

* * *

BurpSuite神器这些年非常的受大家欢迎，在国庆期间解了下Burp相关开发并写了这篇笔记。希望和大家分享一下JavaSwing和Burp插件相关开发。第一节仅简单的了解下API相关，后面会带着大家利用Netbeans开发我们自己的扩展以及各种有趣的小工具。

0x01 怎么学？
=========

* * *

第一个问题是我们应该怎么去写自己的Burp扩展？我们可以找一些现有的扩展学习下，或者参阅官方文档或者手册，其次才是google一下是否有相关的教程、文章进行学习。

google搜索：burp suite api，找到官方的API相关说明。

1.  http://portswigger.net/burp/extender/
    
2.  http://blog.portswigger.net/2012/12/draft-new-extensibility-api.html
    

![enter image description here](http://drops.javaweb.org/uploads/images/d39edfaf8cb66e451155947f9610af7aa94dd4b7.jpg)

You can:

1.  执行和修改 HTTP 请求和响应
    
2.  访问运行时的数据，比如：代理日志、目标站map和扫描问题
    
3.  启动自己的action，如扫描和网站爬行
    
4.  自定义扫描检测和注册扫描问题
    
5.  提供自定义Intruder payloads和payload处理
    
6.  查询和更新Suite-wide的目标作用域
    
7.  查询和更新session处理cookie jar
    
8.  实现自定义session处理action
    
9.  添加自定义的标签(tabs)和上下文菜单项到Burp 用户界面
    
10.  可使用自己的界面添加Burp的HTTP消息编辑器
    
11.  自定义Burp的HTTP消息编辑器处理Burp不支持的数据格式
    
12.  获取headers, parameters, cookies分析HTTP请求和响应
    
13.  读取或修改Burp配置设置
    
14.  保存或恢复Burp状态
    

0x02 学习API
==========

* * *

API下载地址：http://portswigger.net/burp/extender/api/burp_extender_api.zip

下载API后新建Eclipse项目导入API文件：

![enter image description here](http://drops.javaweb.org/uploads/images/f39510ccbdb2cbd2c5db34f6906a197698dbd527.jpg)

不急于动手写代码，先看下官方的Demo：

![enter image description here](http://drops.javaweb.org/uploads/images/4d53ef9ba98631b20c6f3fbfcc74114a78af40dd.jpg)

下载第一个HelloWorld解压它并复制BurpExtender.java到我们的项目当中：

![enter image description here](http://drops.javaweb.org/uploads/images/910c5b6269a466e2e580614e342a9e9f891b971e.jpg)

BurpExtender.java：

![enter image description here](http://drops.javaweb.org/uploads/images/c4eaaf464dd5cb25cdf8523ff1fdf1b6dbab92ea.jpg)

BurpExtender.java实现了IBurpExtender接口，而IBurpExtender仅定义了一个方法：registerExtenderCallbacks(注册扩展回调方法)：

```
public interface  IBurpExtender{
         /**
          * 这个方法将在扩展加载的时候.他将会注册一个
          *<code>IBurpExtenderCallbacks</code> 接口实例,可通过扩展
          * 实现各种调用
          *@param回调一个
          *<code>IBurpExtenderCallbacks</code>对象.
          */
         void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks);
}

```

在确认代码无任何错误后选中项目并导出为jar,建议安装一个打jar包的插件:Build Fat Jar这样你就可以非常方便的把整个项目打成一个jar包了.

![enter image description here](http://drops.javaweb.org/uploads/images/1fac81202f05935c75dea74d082006cbcd6aa4b6.jpg)

如果你和我一样从来都没有使用过BurpSuite，那么不妨先打开它把玩几分钟。在extender(扩展)标签当中看到了Burp的插件加载界面。

![enter image description here](http://drops.javaweb.org/uploads/images/902353703e9cae6a55ec0abc7e61f4f356587074.jpg)

Add我们刚打好的jar包，加载到Burp扩展中去。

![enter image description here](http://drops.javaweb.org/uploads/images/da0fd14bc12a14cc50a4a878192d203520e7d697.jpg)

这个时候可以看到我们的插件已经成功运行了，在LoadBurpExtension中的output标签已经看到了Hello output(stdout.println("Hello output");)

Errors标签也输出了Hello errors()stderr.println("Hello errors");

对应的错误信息(throw new RuntimeException("Hello exceptions");)。

插件名(callbacks.setExtensionName("Hello world extension");)，

以及提醒面板的信息Hello alerts(callbacks.issueAlert("Hello alerts");)。

![enter image description here](http://drops.javaweb.org/uploads/images/347d78f18856278651d5e09da0e9469c11db43fe.jpg)

获取到Burp混淆后的扩展加载类(自定义类加载器)：

![enter image description here](http://drops.javaweb.org/uploads/images/62fda718af39226fb1e4699a14f0a0b559cf730a.jpg)

如你所想，java加载外部扩展利用了URLClassLoader load外部的jar(对这感兴趣的朋友可以看下p2j上的相关文章:http://p2j.cn/?s=URLClassLoader&submit=Search)。

第一个HelloWorld很容易就搞定了，第二个Event listeners的Demo。所谓事件监听即你可以通过Burp的IBurpExtenderCallbacks去注册自己的监听方法。Demo只提供了四种事件(包含HTTP监听、代理、Scanner、状态监听)，所有的未列举的事件直接用Eclipse的快捷键提示就出来了：

![z](http://drops.javaweb.org/uploads/images/1eb7336b754098e19deb4c290afeaf9b84e249a2.jpg)

比如想要添加一个IScopeChangeListener很简单，让当前类实现IScopeChangeListener接口，注册ScopeChange事件(callbacks.registerScopeChangeListener(this);)重写其scopeChanged方法即可。

![enter image description here](http://drops.javaweb.org/uploads/images/a24177d5ff220af4067612d23ad02f81a4068a19.jpg)

设置本地浏览器代理后再次访问任意网站后回到扩展标签，选中我们的扩展程序可以看到监听中的请求已输出。

![enter image description here](http://drops.javaweb.org/uploads/images/e0bab84f005011fa540142158391c037bd5d02c5.jpg)

0x03 HelloWorld
===============

* * *

在编写扩展的时候一定要注意，你的包里面务必包含一个BurpExtender类可以有多个类实现IBurpExtender。 创建自己的Panel并加到Burp主窗体，AppPanel是我自己写的一个应用面板。我们可以通过实现ITab 重写getTabCaption和getUiComponent方法(当然实现IBurpExtender接口是必须的)将我们自己的ui嵌套到Burp当中。getTabCaption即获取获取标题，getUiComponent获取组件这里需要给Burp返回你封装的组件对象。

我们可以先写好JPanel再嵌入到Burp当中，这里提供了一个简单的ApplicationPanel小Demo:http://p2j.cn/?p=1512

```
package burp;

import java.awt.Component;

import javax.swing.JPanel;
import javax.swing.SwingUtilities;

public class BurpExtender implements IBurpExtender, ITab {

     private JPanel jPanel1;

     @Override
     public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks) {
          //设置扩展名
          callbacks.setExtensionName("应用中心");
          //创建我们的窗体
          SwingUtilities.invokeLater(new Runnable() {
               @Override
               public void run() {
                    //我们的主窗体
                    jPanel1 = new AppPanel();
                    //自定义我们的组件
                    callbacks.customizeUiComponent(jPanel1);
                    //添加标签到Burp主窗体
                    callbacks.addSuiteTab(BurpExtender.this);
               }
          });
     }

     @Override
     public String getTabCaption() {
          return "应用中心";
     }

     @Override
     public Component getUiComponent() {
          return jPanel1;
     }

}

```

效果图：

![enter image description here](http://drops.javaweb.org/uploads/images/a4a8df625b4e1a5763175abe28330309bb9e0fc0.jpg)