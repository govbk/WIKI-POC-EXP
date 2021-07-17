# BurpSuite插件开发指南之 Java 篇

此文接着[《BurpSuite插件开发指南之 API 下篇》](http://drops.wooyun.org/tools/14685)。在此篇中将会介绍如何使用Java 开发 BurpSuite 的插件，重点会介绍利用 Java 的 Swing 包开发带有 GUI 的 Burp 插件。

《BurpSuite 插件开发指南》系列文章如下：

*   [《BurpSuite插件开发指南之 API 篇》](http://drops.wooyun.org/tools/14040)
*   《BurpSuite插件开发指南之 Java 篇》
*   《BurpSuite插件开发指南之 Python 篇》

注：此系列文章是笔者利用业余时间所写，如有错误，望读者们及时指正，另外此系列文章属于入门级别的科普文，目的是普及Burp插件的编写技术。

0x00 Java 接口简介
==============

* * *

知其然更要知其所以然。在真正动手编写 Burp 插件之前，有必要对Burp提供的各个接口有一定的了解，同时要有一定的编程经验和能力。那么，在此篇中读者则有必要了解 Java 的接口技术。

接口（英文：Interface）在 Java 编程语言中是一个比较抽象的东西。熟悉 OOP 的同学可以用“类”的思想来理解接口。但是，要明白的是，类与接口有相似的地方同时也有很多不同的地方。

接口的声明
-----

接口的声明语法格式如下：

```
[可见度] interface 接口名称 [extends 其他的类名] {
        // 声明变量
        // 抽象方法
}

```

例如，Burp 的 接口声明原型如下：

```
package burp;

public interface IBurpExtender
{
    void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks);
}

```

接口的实现
-----

一个接口可以被另外一个接口继承，也可以被一个类实现。当类实现接口的时候，类要实现接口中所有的方法。否则，类必须声明为抽象的类。类使用implements关键字实现接口。在类声明中，Implements关键字放在class声明后面。不熟悉Java编程的读者要牢记这几点。

实现一个接口的语法如下：

```
... implements 接口名称[, 其他接口1, 其他接口2..., ...] ...

```

例如，编写 Burp 插件必须编写的 BurpExtender 类实现 IBurpExtender 和 IProxyListener 接口代码如下：

```
package burp;

public class BurpExtender implements IBurpExtender, IProxyListener{

    // 实现 IBurpExtender 接口的 registerExtenderCallbacks 方法
    @Override
    public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks) {
        // TODO here
    }

    // 实现 IProxyListener 接口的 processProxyMessage 方法
    @Override
    public void processProxyMessage(boolean messageIsRequest,
            IInterceptedProxyMessage message) {
        // TODO here
    }
}

```

需要注意的是，在Burp提供的接口文档中，并不是所有的接口都可以用类实现，只有在接口的描述中说明了“该接口可以被实现”时，所对应的接口才可以被你所编写的类实现其方法。

0x01 Java Swing 和 AWT 包简介
=========================

* * *

Java Swing 是 Java Foundation Classes（JFC）的一部分。在 Swing 中，包含了很多强大灵活的，跨平台的 GUI 控件。Swing 组件遵循(MVC)模型 - 视图 - 控制器架构，并提供了三个通用的顶层容器类 JFrame，JDialog 和 JApplet。在开发带有 GUI 的 BurpSuite 插件时，一般不会直接用到这三个顶层容器类，具体要看个人的设计和需求。

下面是一些最常用的控件：

*   JLabel 标签控件，JLabel 的对象是在容器中放置一个文本标签。
*   JButton 按钮控件。
*   JColorChooser 颜色选择控件，用于让用户操作和选择颜色。
*   JCheckBox 选择框控件，支持分组。
*   JRadioButton 单选框控件，支持分组。
*   JList 列表控件。
*   JComboBox 组合框控件。
*   JTextField 文本框控件。
*   JPasswordField 密码输入框控件。
*   JTextArea 多行文本控件。
*   ImageIcon 绘制图标的控件。
*   JScrollbar 滚动条控件，支持水平和垂直滚动。
*   JFileChooser 选择文件对话框。
*   JProgressBar 进度条控件。
*   JPanel 面板控件，此控件在开发插件时会经常用到。

Swing 是在 AWT 的基础上构建的一套新的图形界面系统，所以 AWT 是 Java 实现图形界面的基础，图形控件的事件监听和响应也是由 AWT 完成的。不过，编写 Burp 插件所用到的图形组件和事件并不多，很容易上手。

有关更多 GUI 组件的知识，请读者自行百度了解。在此不做过多阐述。

0x02 自定义 Burp UI 标签
===================

* * *

编写 GUI 的 Burp 插件在实际使用时更加易于操作和表达信息。当然，编写起来也十分简单，只需遵循一定的“套路”，就可以了。

最终编写好的基本的样式如下图所示：

![](http://drops.javaweb.org/uploads/images/97d609284d4608f87dd66a9638e528f7a0e6703e.jpg)

代码如下：

```
/*
 *  BurpSuite 插件开发指南之 Java 篇
 *  writend by Her0in 
 */
package burp;

import java.awt.Component;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.PrintWriter;
import javax.swing.JButton;
import javax.swing.JPanel;
import javax.swing.SwingUtilities;

public class BurpExtender implements IBurpExtender, ITab{

    public PrintWriter stdout;
    public IExtensionHelpers hps;
    public IBurpExtenderCallbacks cbs;

    public JPanel jPanelMain;

    @Override
    public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks)         {

        callbacks.setExtensionName("BurpExtender");

        this.hps = callbacks.getHelpers();
        this.cbs = callbacks;
        this.stdout = new PrintWriter(callbacks.getStdout(), true);

        this.stdout.println("hello burp!");

        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {

                jPanelMain = new JPanel();

                JButton jButton = new JButton("老司机,快点我!");

                jButton.addMouseListener(new MouseAdapter() {

                    @Override
                    public void mouseClicked(MouseEvent e){
                        stdout.println("哔...");
                    }

                });


                // 将按钮添加到 主面板 jPanelMain 中. 
                jPanelMain.add(jButton);

                // 设置自定义组件并添加标签
                cbs.customizeUiComponent(jPanelMain);
                cbs.addSuiteTab(BurpExtender.this);
            }
        });
    }

    // 实现 ITab 接口的 getTabCaption 方法
    @Override
    public String getTabCaption() {
        return "Burp 标签测试";
    }

    // 实现 ITab 接口的 getUiComponent 方法
    @Override
    public Component getUiComponent() {
        return jPanelMain;
    }
}

```

从上述代码中，读者也能够看到，Java 的 Swing 图形编程有点蛋疼，需要一层层的编写。首先需要添加一个 JPanel 上去，然后在这个 JPanel 中再添加图形组件，如果还有上层的图形组件，则需要再添加一个 Panel 类型的控件。

在这里有一个比较快速编写 Burp GUI插件的方法，先利用 NetBeans IDE 将图形界面拖拽式的写好，然后将上述显示控件的代码替换为显示这个 JFrame 的代码。之后编写相关的事件响应代码。

0x03 BurpSuite插件开发实例之 JSON 水坑 检测插件
==================================

* * *

本小节，笔者将会使用一个实例来“抛砖引玉”式的描述编写带有 GUI 的 Burp 插件。读者可以把关注点放在图形控件的放置顺序和事件处理上，可以无视 JSON 水坑检测的逻辑是否严谨以及误报率，准确率是否科学等问题。

最终编写好的插件如下图：

![](http://drops.javaweb.org/uploads/images/18a9daac3d5bc61ab23392dd3bc26922b71e6f44.jpg)

顶部的控件是一个表格列表控件，会放置检测到的结果。下面两个 ITextEditor 分别显示当前 HTTP 数据包的请求信息和响应信息。

代码就直接贴出来吧，如下：

```
/*
 *  BurpSuite 插件开发指南之 Java 篇
 *  writend by Her0in 
 */
package burp;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Rectangle;
import java.awt.event.ComponentEvent;
import java.awt.event.ComponentListener;
import java.io.PrintWriter;
import java.util.Vector;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTabbedPane;
import javax.swing.ScrollPaneConstants;
import javax.swing.SwingUtilities;

public class BurpExtender implements IBurpExtender, ITab, IHttpListener{

    public PrintWriter stdout;
    public IExtensionHelpers hps;
    public IBurpExtenderCallbacks cbs;

    public IRequestInfo iRequestInfo;
    public IResponseInfo iResponseInfo;

    public JPanel jPanel_top;
    public JTabbedPane jTabbedPane; 
    public JScrollPane jScrollPane;
    public JSplitPane jSplitPaneV;

    // 自己封装一个 Table 控件
    private Her0inTable jsonTable;

    //请求，响应信息显示
    public JPanel jPanel_reqInfo_left;
    public JPanel jPanel_respInfo_right;
    public JSplitPane jSplitPaneInfo;
    public ITextEditor iRequestTextEditor;
    public ITextEditor iResponseTextEditor;

    Boolean bFind = false;
    String strTags = "";

    @Override
    public void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks) {

        callbacks.setExtensionName("JSON 水坑检测");

        this.hps = callbacks.getHelpers();
        this.cbs = callbacks;
        this.stdout = new PrintWriter(callbacks.getStdout(), true);

        this.stdout.println("hello burp!");

        SwingUtilities.invokeLater(new Runnable() {
            @Override
            public void run() {

                // 初始化垂直分隔面板
                jSplitPaneV = new JSplitPane(JSplitPane.VERTICAL_SPLIT, true);
                jSplitPaneV.setDividerLocation(0.5);
                jSplitPaneV.setOneTouchExpandable(true);

                // 垂直分隔面板的顶部
                jPanel_top = new JPanel();
                // 设置垂直分隔面板顶部的子控件
                // 放置表格控件
                jTabbedPane = new JTabbedPane();

                // 初始化 Burp 提供的 ITextEditor 编辑器接口
                iRequestTextEditor = cbs.createTextEditor();
                iRequestTextEditor.setEditable(false);

                iResponseTextEditor = cbs.createTextEditor();
                iResponseTextEditor.setEditable(false);

                // 初始化 jsonTable
                jsonTable = new Her0inTable(iRequestTextEditor, iResponseTextEditor, stdout);

                // 最好放置一个 JScrollPane
                JScrollPane jScrollPane1 = new JScrollPane(jsonTable.getTab());
                jScrollPane1.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_AS_NEEDED);
                jScrollPane1.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED);

                jTabbedPane.scrollRectToVisible(new Rectangle(500, 70));
                jTabbedPane.addTab("JSON 水坑检测", jScrollPane1);

                jScrollPane = new JScrollPane(jTabbedPane);
                jScrollPane.setHorizontalScrollBarPolicy(ScrollPaneConstants.HORIZONTAL_SCROLLBAR_AS_NEEDED);
                jScrollPane.setVerticalScrollBarPolicy(ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED);
                jPanel_top.add(jScrollPane, BorderLayout.CENTER);
                jPanel_top.setLayout(null);

                // 添加componentResized事件 否则在改变Burp 主窗口大小时会错位
                jPanel_top.addComponentListener(new ComponentListener() {

                    @Override
                    public void componentShown(ComponentEvent e) {
                    }

                    @Override
                    public void componentResized(ComponentEvent e) {
                            if(e.getSource() == jPanel_top){
                                    jScrollPane.setSize(jPanel_top.getSize().width - 5,
                                                    jPanel_top.getSize().height - 5);                           
                                    jScrollPane.setSize(jPanel_top.getSize().width - 10,
                                                    jPanel_top.getSize().height - 10);
                            }
                    }

                    @Override
                    public void componentMoved(ComponentEvent e) {
                            // TODO Auto-generated method stub
                    }

                    @Override
                    public void componentHidden(ComponentEvent e) {
                            // TODO Auto-generated method stub  
                    }
                });

                // 设置垂直分隔面板底部的子控件

                // 显示请求/响应 信息的水平分隔面板初始化
                jSplitPaneInfo = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, true);
                jSplitPaneInfo.setDividerLocation(0.5);
                jSplitPaneInfo.setOneTouchExpandable(true); 

                // 初始化 请求，响应信息显示 面板                             
                jPanel_reqInfo_left = new JPanel();
                jPanel_respInfo_right = new JPanel();

                jPanel_reqInfo_left.setLayout(new BorderLayout());
                jPanel_respInfo_right.setLayout(new BorderLayout());

                // 将 Burp 提供的 ITextEditor 编辑器 添加到请求，响应信息显示 面板中
                jPanel_reqInfo_left.add(iRequestTextEditor.getComponent(),
                                BorderLayout.CENTER);
                jPanel_respInfo_right.add(iResponseTextEditor.getComponent(),
                                BorderLayout.CENTER);

                // 分别添加 请求，响应信息显示 面板 到 垂直分隔面板底部
                jSplitPaneInfo.add(jPanel_reqInfo_left, JSplitPane.LEFT);
                jSplitPaneInfo.add(jPanel_respInfo_right, JSplitPane.RIGHT);

                // 最后,为垂直分隔面板添加顶部面板和水平分隔面板
                jSplitPaneV.add(jPanel_top, JSplitPane.TOP);
                jSplitPaneV.add(jSplitPaneInfo, JSplitPane.BOTTOM);

                // 设置自定义组件并添加标签
                cbs.customizeUiComponent(jSplitPaneV);
                cbs.addSuiteTab(BurpExtender.this);
            }
        });

        callbacks.registerHttpListener(this);
    }

    // 实现 ITab 接口的 getTabCaption 方法
    @Override
    public String getTabCaption() {
        return "JSON 水坑检测";
    }

    // 实现 ITab 接口的 getUiComponent 方法
    @Override
    public Component getUiComponent() {
        return jSplitPaneV;
    }


    public void CheckJson(IHttpRequestResponse messageInfo) {
            try {
                this.iRequestInfo = this.hps.analyzeRequest(messageInfo);
                this.iResponseInfo = this.hps.analyzeResponse(messageInfo.getResponse());   
            } catch (Exception e) {
                return ;
            }

//            stdout.println(messageInfo.getHttpService().getHost());

            this.bFind = false;
            java.util.List<IParameter> listIParameters = iRequestInfo.getParameters();  
            strTags = "";
            for (IParameter param : listIParameters) {
                    String strName = param.getName().toLowerCase();
                    if(strName.indexOf("callback") != -1 || strName.indexOf("_callback") !=-1 ||
                                    strName.indexOf("cb") !=-1 || strName.indexOf("_cb") != -1 ||
                                    strName.indexOf("huidiao") !=-1 ){
                            strTags += "# find => " + strName;
                            this.bFind = true;
                    }
            }


            if(this.bFind){
                    Vector<String> vectorRow = new Vector<String>();
                    vectorRow.addElement(new String(Integer.toString(jsonTable.defaultTableModel.getRowCount())));
                    vectorRow.addElement(new String(this.iRequestInfo.getUrl().getHost()));
                    vectorRow.addElement(new String(this.iRequestInfo.getMethod()));
                    if(this.iRequestInfo.getUrl().getQuery() != null){
                            vectorRow.addElement(new String(this.iRequestInfo.getUrl().getPath() + "?" + this.iRequestInfo.getUrl().getQuery()));
                    }else{
                            vectorRow.addElement(new String(this.iRequestInfo.getUrl().getPath()));
                    }
                    vectorRow.addElement(new String(strTags));
                    jsonTable.defaultTableModel.addRow(vectorRow);
                    jsonTable.iHttpList.add(messageInfo);
            }
    }

    @Override
    public void processHttpMessage(int toolFlag, boolean messageIsRequest, IHttpRequestResponse messageInfo) {

        if (!messageIsRequest) {
            //JSON 检测
            this.CheckJson(messageInfo);
        }
    }
}

```