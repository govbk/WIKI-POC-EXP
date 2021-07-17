# BurpSuite插件开发指南之 API 下篇

0x00 前言
=======

* * *

此文是接着[《BurpSuite插件开发指南之 API 上篇》](http://drops.wooyun.org/tools/14040)所写，此篇中将要介绍的 API 和上篇有着紧密的联系，所以建议读者可以将上下篇作为一个整体去看待。

《BurpSuite 插件开发指南》系列文章如下：

*   《BurpSuite插件开发指南之 API 篇》
*   《BurpSuite插件开发指南之 Java 篇》
*   《BurpSuite插件开发指南之 Python 篇》

0x01 API 参考
===========

* * *

### IMessageEditor

**public interface IMessageEditor**

此接口被用于使用 Burp 的 HTTP 消息编辑框的实例提供扩展功能，以便扩展插件可以在它自己的 UI 中使用消息编辑框，扩展插件可以通过调用**IBurpExtenderCallbacks.createMessageEditor()**获得此接口的实例。

此接口提供了以下方法：

```
// 此方法返回了编辑器的 UI 组件，扩展插件可以将其添加到自己的 UI 中
java.awt.Component  getComponent()

// 此方法用于获取当前已显示的消息，此消息可能已被用户修改
byte[]  getMessage()

// 此方法返回了用户当前所选择的数据
byte[]  getSelectedData()

// 此方法用于决定当前的消息是否可被用户修改
boolean isMessageModified()

// 此方法用于将一个 HTTP 消息显示在编辑器中
void    setMessage(byte[] message, boolean isRequest)

```

注： 此接口需要与**IMessageEditorTabFactory**等相关接口一起使用。

Demo code：

```
请见 IMessageEditorTabFactory 的实例代码。

```

### IMessageEditorController

**public interface IMessageEditorController**

此接口被用于**IMessageEditor**获取当前显示的消息的细节。创建了 Burp 的 HTTP 消息编辑器实例的扩展插件可以有选择的实现**IMessageEditorController**接口，当扩展插件需要当前消息的其他信息时，编辑器将会调用此接口（例如：发送当前消息到其他的 Burp 工具中）。扩展通过**IMessageEditorTabFactory**工厂提供自定义的编辑器标签页，此工厂的**createNewInstance**方法接受一个由该工厂所生成的每一个标签页的**IMessageEditorController**对象的引用，当标签页需要当前消息的其他信息时，则会调用该对象。

此方法提供了以下方法：

```
// 此方法用于获取当前消息的 HTTP 服务信息
IHttpService    getHttpService()

// 此方法用于获取当前消息的 HTTP 请求（也有可能是一个响应消息）
byte[]  getRequest()

// 此方法用于获取当前消息的 HTTP 响应（也有可能是一个请求消息）
byte[]  getResponse()

```

Demo code：

```
请见 IMessageEditorTabFactory 的实例代码。

```

### IMessageEditorTab

**public interface IMessageEditorTab**

扩展插件通过注册**IMessageEditorTabFactory**工厂，此工厂的**createNewInstance**返回一个当前接口的实例，Burp 将会在其 HTTP 消息编辑器中创建自定义的标签页。

此接口提供了如下方法：

```
// 此方法返回当前显示的消息
byte[]  getMessage()

// 此方法用于获取当前已被用户选择的数据
byte[]  getSelectedData()

// 此方法返回自定义标签页的标题
java.lang.String    getTabCaption()

// 此方法返回自定义标签页内容的组件
java.awt.Component  getUiComponent()

// 此方法用于指示在显示一个新的 HTTP 消息时，是否启用自定义的标签页
boolean isEnabled(byte[] content, boolean isRequest)

// 此方法用于决定当前显示的消息是否可被用户修改
boolean isModified()

// 此方法可以显示一个新的消息或者清空已存在的消息
void    setMessage(byte[] content, boolean isRequest)

```

Demo code：

```
请见 IMessageEditorTabFactory 的实例代码。

```

### IMessageEditorTabFactory

**public interface IMessageEditorTabFactory**

扩展可以实现此接口，并且可以调用**IBurpExtenderCallbacks.registerMessageEditorTabFactory()**注册一个自定义的消息编辑器标签页的工厂。扩展插件可以在 Burp 的 HTTP 编辑器中渲染或编辑 HTTP 消息。

此接口提供了一个方法：

```
// Burp 将会对每一个 HTTP 消息编辑器调用一次此方法，此工厂必须返回一个新的 IMessageEditorTab 对象
IMessageEditorTab   createNewInstance(IMessageEditorController controller, boolean editable)

```

Demo code：

```
package burp;

import java.awt.Component;
import java.io.PrintWriter;

public class BurpExtender implements IBurpExtender, IMessageEditorTabFactory{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;
    private IBurpExtenderCallbacks callbacks;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.callbacks = callbacks;
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerMessageEditorTabFactory(this);
    }

    @Override
    public IMessageEditorTab createNewInstance(
            IMessageEditorController controller, boolean editable) {
        // 返回 IMessageEditorTab 的实例
        return new iMessageEditorTab();
    }

    class iMessageEditorTab implements IMessageEditorTab{

        // 创建一个新的文本编辑器
        private ITextEditor iTextEditor = callbacks.createTextEditor();

        @Override
        public String getTabCaption() {
            // 设置消息编辑器标签页的标题
            return "测试 MessageEditorTab";
        }

        @Override
        public Component getUiComponent() {
            // 返回 iTextEditor 的组件信息，当然也可以放置其他的组件
            return iTextEditor.getComponent();
        }

        @Override
        public boolean isEnabled(byte[] content, boolean isRequest) {
            // 在显示一个新的 HTTP 消息时，启用自定义的标签页
            // 通过 content 和 isRequest 也可以对特定的消息进行设置
            return true;
        }

        @Override
        public void setMessage(byte[] content, boolean isRequest) {
            // 把请求消息里面的 data 参数进行 Base64 编码操作
            // 这里并未处理参数中没有 data 时的异常
            IParameter parameter = helpers.getRequestParameter(content, "data");
            stdout.println("data = " + parameter.getValue());
            iTextEditor.setText(helpers.stringToBytes(helpers.base64Encode(parameter.getValue())));
        }

        @Override
        public byte[] getMessage() {
            // 获取 iTextEditor 的文本
            return iTextEditor.getText();
        }

        @Override
        public boolean isModified() {
            // 允许用户修改当前的消息
            return true;
        }

        @Override
        public byte[] getSelectedData() {
            // 直接返回 iTextEditor 中选中的文本
            return iTextEditor.getSelectedText();
        }

    }
}

```

加载上述代码生成的插件后，会显示自定义的标签页和文本编辑器。

**注意：官网提供的自定义消息编辑器的代码有误！**

![pic](http://drops.javaweb.org/uploads/images/0a9c5456def8603316c5186a557aba4b46603f10.jpg)

### IParameter

**public interface IParameter**

此接口用于操控 HTTP 请求参数，开发者通过此接口可以灵活的获取请求或响应里的参数。

```
// 此方法用于获取参数名称
java.lang.String    getName()

// 此方法用于获取在 HTTP 请求里面的最后一个参数的名称
int getNameEnd()

// 此方法用于获取在 HTTP 请求里面的第一个参数的名称
int getNameStart()

// 此方法用于获取参数类型，参数的类型在 IParameter 接口中有定义
byte    getType()

// 此方法用于获取参数的值
java.lang.String    getValue()

// 此方法用于获取最后一个参数的值
int getValueEnd()

// 此方法用于获取第一个参数的值
int getValueStart()

```

Demo code：

```
package burp;

import java.io.PrintWriter;
import java.util.List;

public class BurpExtender implements IBurpExtender, IHttpListener{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;
    private IBurpExtenderCallbacks callbacks;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.callbacks = callbacks;
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerHttpListener(this);
    }

    @Override
    public void processHttpMessage(int toolFlag, boolean messageIsRequest,
            IHttpRequestResponse messageInfo) {
        // 获取请求中的参数
        if(messageIsRequest){
            IRequestInfo iRequestInfo = helpers.analyzeRequest(messageInfo);
            // 获取请求中的所有参数
            List<IParameter> iParameters = iRequestInfo.getParameters();
            for (IParameter iParameter : iParameters) {
                if(iParameter.getType() == IParameter.PARAM_URL)
                    stdout.println("参数：" + iParameter.getName() + " 在 URL中");
                    stdout.println("参数：" + iParameter.getName() + " 的值为：" + iParameter.getValue());
            }
        }

    }
}

```

加载上述代码生成的插件后，执行效果如下图所示：

![pic](http://drops.javaweb.org/uploads/images/63a688cd419fa8be81a63bf878d1708619a0d850.jpg)

### IProxyListener

**public interface IProxyListener**

扩展可以实现此接口，并且可以通过调用**IBurpExtenderCallbacks.registerProxyListener()**注册一个代理监听器。在代理工具处理了请求或响应后会通知此监听器。扩展插件通过注册这样一个监听器，对这些消息执行自定义的分析或修改操作。

此接口提供了一个很常用的方法：

```
// 当代理工具处理 HTTP 消息时则会调用此方法
void    processProxyMessage(boolean messageIsRequest, IInterceptedProxyMessage message)

```

Demo code：

```
package burp;

import java.io.PrintWriter;
public class BurpExtender implements IBurpExtender, IProxyListener{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;
    private IBurpExtenderCallbacks callbacks;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.callbacks = callbacks;
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerProxyListener(this);
    }

    @Override
    public void processProxyMessage(boolean messageIsRequest,
            IInterceptedProxyMessage message) {
            // TODO here
    }
}

```

### IRequestInfo

**public interface IRequestInfo**

此接口被用于获取一个 HTTP 请求的详细信息。扩展插件可以通过调用**IExtensionHelpers.analyzeRequest()**获得一个 IRequestInfo 对象。

此接口提供了以下方法：

```
// 此方法用于获取 HTTP body 在请求消息中的起始偏移量
int getBodyOffset()

// 此方法用于获取请求消息的 HTTP 类型
byte    getContentType()

// 此方法用于获取请求中包含的 HTTP 头
java.util.List<java.lang.String>    getHeaders()

// 此方法用于获取请求的 HTTP 方法
java.lang.String    getMethod()

// 此方法用于获取请求中包含的参数
java.util.List<IParameter>  getParameters()

// 此方法用于获取请求中的 URL
java.net.URL    getUrl()

```

Demo code:

```
package burp;

import java.io.PrintWriter;

public class BurpExtender implements IBurpExtender, IHttpListener{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerHttpListener(this);
    }

    @Override
    public void processHttpMessage(int toolFlag, boolean messageIsRequest,
            IHttpRequestResponse messageInfo) {
        // 打印出请求的 Url 和 响应码
        if(messageIsRequest){
            stdout.println(helpers.bytesToString(messageInfo.getRequest()));
        }
        else{
            IResponseInfo responseInfo = helpers.analyzeResponse(messageInfo.getResponse());
            short statusCode = responseInfo.getStatusCode();
            stdout.printf("响应码 => %d\r\n", statusCode);
        }
    }
}

```

加载上述代码生成的插件后，执行效果如下图所示：

![pic](http://drops.javaweb.org/uploads/images/2fd2e705fdb1df5b95fa101a991853ecf80b0cfb.jpg)

### IResponseInfo

**public interface IResponseInfo**

此接口被用于获取一个 HTTP 请求的详细信息。扩展插件可以通过调用**IExtensionHelpers. analyzeResponse()**获得一个 IResponseInfo 对象。

```
// 此方法用于获取 HTTP body 在响应消息中的起始偏移量
int getBodyOffset()

// 此方法用于获取响应消息中设置的 HTTP Cookie
java.util.List<ICookie> getCookies()

// 此方法用于获取包含在响应消息中的 HTTP 头
java.util.List<java.lang.String>    getHeaders()

// 此方法用于获取根据 HTTP 响应判断出的 MIME 类型
java.lang.String    getInferredMimeType()

// 此方法用于获取 HTTP 响应头中指示的 MIME 类型
java.lang.String    getStatedMimeType()

// 此方法用于获取 HTTP 状态码
short   getStatusCode()

```

Demo code:

```
package burp;

import java.io.PrintWriter;

public class BurpExtender implements IBurpExtender, IHttpListener{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerHttpListener(this);
    }

    @Override
    public void processHttpMessage(int toolFlag, boolean messageIsRequest,
            IHttpRequestResponse messageInfo) {
        // 打印出请求的 Url 和 响应码
        if(messageIsRequest){
            stdout.println(helpers.bytesToString(messageInfo.getRequest()));
        }
        else{
            IResponseInfo responseInfo = helpers.analyzeResponse(messageInfo.getResponse());
            short statusCode = responseInfo.getStatusCode();
            stdout.printf("响应码 => %d\r\n", statusCode);
        }
    }
}

```

### IScanIssue

**public interface IScanIssue**

此接口用于获取 Scanner 工具扫描到的问题的细节。扩展可以通过注册一个**IScannerListener**或者是 通过调用**IBurpExtenderCallbacks.getScanIssues()**获取扫描问题的细节。扩展同样可以通过注册**IScannerCheck**接口或者是调用**IBurpExtenderCallbacks.addScanIssue()**方法来自定义扫描问题，此时扩展需要提供它对此接口的实现。

此接口提供了以下方法：

```
// 此方法返回扫描问题的信任等级
java.lang.String    getConfidence()

// 此方法返回生成扫描问题所对应的 HTTP 消息
IHttpRequestResponse[]  getHttpMessages()

// 此方法返回生成扫描问题所对应的 HTTP 服务信息
IHttpService    getHttpService()

// 此方法返回指定扫描问题类型的背景描述信息
java.lang.String    getIssueBackground()

// 此方法返回指定的扫描问题的详细信息
java.lang.String    getIssueDetail()

// 此方法返回扫描问题类型的名称
java.lang.String    getIssueName()

// 此方法返回扫描问题类型的数字标志符
int getIssueType()

// 此方法返回指定扫描问题的解决方式的背景描述信息
java.lang.String    getRemediationBackground()

// 此方法返回指定扫描问题的解决方式的背景详情
java.lang.String    getRemediationDetail()

// 此方法返回扫描问题的错误等级
java.lang.String    getSeverity()

// 此方法返回生成扫描问题对应的 URL 信息
java.net.URL    getUrl()

```

Demo code:

```
请见 IScannerListener 的实例代码。

```

### IScannerCheck

**public interface IScannerCheck**

扩展可以实现此接口，之后可以通过调用**IBurpExtenderCallbacks.registerScannerCheck()**注册一个自定义的 Scanner 工具的检查器。Burp 将会告知检查器执行“主动扫描”或“被动扫描”，并且在确认扫描到问题时给出报告。

```
// 当自定义的Scanner工具的检查器针对同一个 URL 路径报告了多个扫描问题时，Scanner 工具会调用此方法
int consolidateDuplicateIssues(IScanIssue existingIssue, IScanIssue newIssue)

// Scanner 工具会对每一个可插入的点执行“主动扫描”
java.util.List<IScanIssue>  doActiveScan(IHttpRequestResponse baseRequestResponse, IScannerInsertionPoint insertionPoint)

// Scanner 工具会对每一个可插入的点执行“被动扫描”
java.util.List<IScanIssue>  doPassiveScan(IHttpRequestResponse baseRequestResponse)

```

Demo code：

```
package burp;

import java.io.PrintWriter;
import java.util.List;

public class BurpExtender implements IBurpExtender, IScannerCheck{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerScannerCheck(this);
    }

    @Override
    public List<IScanIssue> doPassiveScan(
            IHttpRequestResponse baseRequestResponse) {
        // TODO here
        return null;
    }

    @Override
    public List<IScanIssue> doActiveScan(
            IHttpRequestResponse baseRequestResponse,
            IScannerInsertionPoint insertionPoint) {
        // TODO here
        return null;
    }

    @Override
    public int consolidateDuplicateIssues(IScanIssue existingIssue,
            IScanIssue newIssue) {
        // TODO here
        return 0;
    }
}

```

### IScannerInsertionPoint

**public interface IScannerInsertionPoint**

此接口被用于定义一个用于Scanner工具检查器扫描的插入点。扩展可以通过注册**IScannerCheck**获得此接口实例，或者通过注册**IScannerInsertionPointProvider**创建一个 Burp 所使用的扫描检查器实例。

```
// 此方法用于使用指定的 payload 在插入点构建一个请求
byte[]  buildRequest(byte[] payload)

// 此方法返回插入点的基本值
java.lang.String    getBaseValue()

// 此方法返回插入点的名称
java.lang.String    getInsertionPointName()

// 此方法返回插入点的类型，插入点类型在IScannerInsertionPoint接口中定义
byte    getInsertionPointType()

// 当使用指定的 payload 替换到插入点时，此方法可以决定 payload 在请求中的偏移量
int[]   getPayloadOffsets(byte[] payload)

```

Demo code:

```
请见 IScannerCheck 的实例代码。  

```

### IScannerInsertionPointProvider

**public interface IScannerInsertionPointProvider**

扩展可以实现此接口并且可以通过调用**IBurpExtenderCallbacks.registerScannerInsertionPointProvider()**注册自定义扫描插入点的工厂。

此接口提供了以下方法：

```
// 当扫描请求为“主动扫描”时， Scanner 工具将会调用此方法，并且提供者应该提供一个自定义插入点的列表以便用于扫描
java.util.List<IScannerInsertionPoint>  getInsertionPoints(IHttpRequestResponse baseRequestResponse)

```

### IScannerListener

**public interface IScannerListener**

扩展可以实现此接口，并且可以通过调用**IBurpExtenderCallbacks.registerScannerListener()**注册一个 Scanner 工具的监听器。当 Scanner 工具扫描到新的问题时，会通知此监听器。扩展通过注册这样的监听器用于针对扫描问题自定义的分析和记录。

此接口提供了以下方法：

```
// 当一个新的扫描问题被添加到 Burp 的Scanner工具的扫描结果中时，此方法将被 Burp 调用
void    newScanIssue(IScanIssue issue)

```

Demo code：

```
package burp;

import java.io.PrintWriter;

public class BurpExtender implements IBurpExtender, IScannerListener{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerScannerListener(this);
    }

    @Override
    public void newScanIssue(IScanIssue issue) {
        // TODO Auto-generated method stub
        stdout.println("扫描到新的问题 :");
        stdout.println("url => " + issue.getUrl());     
        stdout.println("详情 => " + issue.getIssueDetail());  
    }
}

```

加载上述代码生成的插件后，执行效果如下图所示：

![pic](http://drops.javaweb.org/uploads/images/21a9cf89f45f7d6c791097438fdbb9cae1bd70eb.jpg)

### IScanQueueItem

**public interface IScanQueueItem**

此接口被用于获取在 Burp 的 Scanner 工具中激活的扫描队列里的项目详情。扩展可以通过调用**IBurpExtenderCallbacks.doActiveScan()**获得扫描队列项目的引用。

```
// 此方法可以取消扫描队列项目中的扫描状态
void    cancel()

// 获取扫描队列项目生成的问题的细节
IScanIssue[]    getIssues()

// 此方法返回扫描队列项目发生错误时的网络错误号
int getNumErrors()

// 此方法返回扫描队列项目的攻击插入点的数量
int getNumInsertionPoints()

// 此方法返回扫描队列项目已经发出的请求的数量
int getNumRequests()

// 此方法返回扫描队列项目中已经完成扫描的百分比
byte    getPercentageComplete()

// 此方法返回扫描队列项目的状态描述
java.lang.String    getStatus()

```

### IScopeChangeListener

**public interface IScopeChangeListener**

扩展可以实现此接口并且可以通过调用**IBurpExtenderCallbacks.registerScopeChangeListener()**注册一个 Target 工具下的 scope 变化监听器。当 Burp 的 Target 工具下的 scope 发生变化时，将会通知此接口。

此接口提供了以下方法：

```
// 当 Burp 的 Target 工具下的 scope 发生变化时，将会调用此方法。
void    scopeChanged()

```

Demo code:

```
package burp;

import java.io.PrintWriter;

public class BurpExtender implements IBurpExtender, IScopeChangeListener{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        callbacks.registerScopeChangeListener(this);
    }

    @Override
    public void scopeChanged() {
        // 手动添加或右键菜单添加目标到 scope 列表，就会执行此方法
        stdout.println("scope 有变化！");
    }
}

```

加载上述代码生成的插件后，执行效果如下图所示：

![pic](http://drops.javaweb.org/uploads/images/65d66d7a94c66db38d4552f20e3ba11b47b185ca.jpg)

### ISessionHandlingAction

**public interface ISessionHandlingAction**

扩展可以实现此方法并且可以通过调用**IBurpExtenderCallbacks.registerSessionHandlingAction()**注册一个自定义的会话操作动作。每一个已注册的会话操作动作在会话操作规则的UI中都是可用的，并且用户可以选择其中一个作为会话操作行为的规则。用户可以选择直接调用操作，也可以按照宏定义调用操作。

此接口调用了如下方法：

```
// 此方法由 Burp 调用获取会话操作行为的名称
java.lang.String    getActionName()

// 当会话操作行为被执行时会调用此方法
void    performAction(IHttpRequestResponse currentRequest, IHttpRequestResponse[] macroItems)

```

### ITab

**public interface ITab**

此接口用于自定义的标签页，调用**IBurpExtenderCallbacks.addSuiteTab()**方法可以在 Burp 的 UI 中显示自定义的标签页。

```
// 此方法用于获取自定义标签的标题文本
java.lang.String    getTabCaption()

// Burp 调用此方法获取自定义标签页显示的组件
java.awt.Component  getUiComponent()

```

Demo code：

```
package burp;

import java.awt.Component;
import java.io.PrintWriter;

import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

public class BurpExtender implements IBurpExtender, ITab{

    public PrintWriter stdout;
    public IExtensionHelpers helpers;

    private JPanel jPanel1;
    private JButton jButton1;

    @Override
    public void registerExtenderCallbacks(final IBurpExtenderCallbacks callbacks){

        this.stdout = new PrintWriter(callbacks.getStdout(), true);
        this.helpers = callbacks.getHelpers();
        callbacks.setExtensionName("Her0in");
        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {
                 //创建一个 JPanel
                 jPanel1 = new JPanel();
                 jButton1 = new JButton("点我");

                 // 将按钮添加到面板中
                 jPanel1.add(jButton1);

                 //自定义的 UI 组件
                 callbacks.customizeUiComponent(jPanel1);
                 //将自定义的标签页添加到Burp UI 中
                 callbacks.addSuiteTab(BurpExtender.this);
            }
       });
    }

    @Override
    public String getTabCaption() {
        // 返回自定义标签页的标题
        return "Her0in";
    }

    @Override
    public Component getUiComponent() {
        // 返回自定义标签页中的面板的组件对象
        return jPanel1;
    }
}

```

加载上述代码生成的插件后，执行效果如下图所示：

![pic](http://drops.javaweb.org/uploads/images/e1edab979d2e118f6b7a508c0a0d58c1ffd5599b.jpg)

### ITempFile

**public interface ITempFile**

此接口用于操作调用**IBurpExtenderCallbacks.saveToTempFile()**创建的临时文件。

```
// 删除临时文件，此方法已过时
void    delete()

// 此方法用于获取临时文件内容的缓冲区
byte[]  getBuffer()

```

### ITextEditor

**public interface ITextEditor**

此接口用于扩展 Burp 的 原始文本编辑器，扩展通过调用**IBurpExtenderCallbacks.createTextEditor()**获得一个此接口的实例。

```
// 此方法返回用于扩展添加自定义的编辑器的 UI 组件
java.awt.Component  getComponent()

// 此方法用于获取当前的已选择的文本
byte[]  getSelectedText()

// 此方法用于获取用户在已显示的文本中选择的边界
int[]   getSelectionBounds()

// 此方法用于获取当前已显示的文本
byte[]  getText()

// 此方法用于指示用户是否对编辑器的内容做了修改
boolean isTextModified()

// 此方法用于决定当前的编辑器是否可编辑
void    setEditable(boolean editable)

// 此方法用于更新编辑器下边的搜索框的搜索表达式
void    setSearchExpression(java.lang.String expression)

// 此方法用于更新编辑器中当前已显示的文本
void    setText(byte[] text)

```

Demo code:

`请见 IMessageEditorTabFactory 的实例代码。`