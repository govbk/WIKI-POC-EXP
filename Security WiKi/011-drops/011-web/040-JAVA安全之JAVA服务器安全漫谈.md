# JAVA安全之JAVA服务器安全漫谈

0x00 前言
=======

* * *

本文主要针对JAVA服务器常见的危害较大的安全问题的成因与防护进行分析，主要为了交流和抛砖引玉。

0x01 任意文件下载
===========

* * *

### 示例

以下为任意文件下载漏洞的示例。

DownloadAction为用于下载文件的servlet。

```
<servlet>
    <description></description>
    <display-name>DownloadAction</display-name>
    <servlet-name>DownloadAction</servlet-name>
    <servlet-class>download.DownloadAction</servlet-class>
</servlet>

<servlet-mapping>
    <servlet-name>DownloadAction</servlet-name>
    <url-pattern>/DownloadAction</url-pattern>
</servlet-mapping>

```

在对应的download.DownloadAction类中，将HTTP请求中的filename参数作为待下载的文件名，从web应用根目录的download目录读取文件内容并返回，代码如下。

```
protected void doGet(HttpServletRequest request,
        HttpServletResponse response) throws ServletException, IOException {
    String rootPath = this.getServletContext().getRealPath("/");

    String filename = request.getParameter("filename");
    if (filename == null)
        filename = "";
    filename = filename.trim();

    InputStream inStream = null;

    byte[] b = new byte[1024];
    int len = 0;
    try {
        if (filename == null) {
            return;
        }
        // 读到流中
        // 本行代码未对文件名参数进行过滤，存在任意文件下载漏洞
        inStream = new FileInputStream(rootPath + "/download/" + filename);
        // 设置输出的格式
        response.reset();
        response.setContentType("application/x-msdownload");

        response.addHeader("Content-Disposition", "attachment; filename=\""
                + filename + "\"");
        // 循环取出流中的数据
        while ((len = inStream.read(b)) > 0) {
            response.getOutputStream().write(b, 0, len);
        }
        response.getOutputStream().close();
        inStream.close();
    } catch (Exception e) {
        e.printStackTrace();
    }
}

```

使用DownloadAction下载web应用根目录中的“download/test.txt”文件如下图所示。

![p1](http://drops.javaweb.org/uploads/images/5dd9430cf0dcb90d6f50d63bc47b4cf6f5a5126d.jpg)

由于在DownloadAction类中没有对filename参数值进行检查，因此产生了任意文件下载漏洞。

使用DownloadAction下载web应用根目录中的“WEB-INF/web.xml”文件如下图所示。

![p2](http://drops.javaweb.org/uploads/images/e77a47242b4241465f6161652343e87336fcf4bf.jpg)

### 原因分析

从上述示例可以看出，在JAVA web程序的下载文件相关的代码中，若不对HTTP请求中的待下载文件名进行检查，则有可能产生任意文件下载漏洞。

java.io.File对象有两个方法可以用于获取文件对象的路径，getAbsolutePath与getCanonicalPath。

查看JDK 1.6 API中上述两个方法的说明。

getAbsolutePath

> 返回此抽象路径名的绝对路径名字符串。
> 
> 如果此抽象路径名已经是绝对路径名，则返回该路径名字符串，这与 getPath() 方法一样。如果此抽象路径名是空抽象路径名，则返回当前用户目录的路径名字符串，该目录由系统属性 user.dir 指定。否则，使用与系统有关的方式解析此路径名。在 UNIX 系统上，根据当前用户目录解析相对路径名，可使该路径名成为绝对路径名。在 Microsoft Windows 系统上，根据路径名指定的当前驱动器目录（如果有）解析相对路径名，可使该路径名成为绝对路径名；否则，可以根据当前用户目录解析它。

getCanonicalPath

> 返回此抽象路径名的规范路径名字符串。
> 
> **规范路径名是绝对路径名，并且是惟一的。规范路径名的准确定义与系统有关。如有必要，此方法首先将路径名转换为绝对路径名，这与调用 getAbsolutePath() 方法的效果一样，然后用与系统相关的方式将它映射到其惟一路径名。这通常涉及到从路径名中移除多余的名称（比如 "." 和 ".."）、解析符号连接（对于 UNIX 平台），以及将驱动器号转换为标准大小写形式（对于 Microsoft Windows 平台）。**
> 
> 每个表示现存文件或目录的路径名都有一个惟一的规范形式。每个表示不存在文件或目录的路径名也有一个惟一的规范形式。不存在文件或目录路径名的规范形式可能不同于创建文件或目录之后同一路径名的规范形式。同样，现存文件或目录路径名的规范形式可能不同于删除文件或目录之后同一路径名的规范形式。

使用以下代码在Windows环境测试上述两个方法。

```
public static void main(String[] args) {
    getFilePath("C:/Windows/System32/calc.exe");
    getFilePath("C:/Windows/System32/drivers/etc/../../notepad.exe");
}

private static void getFilePath(String filename) {
    File f = new File(filename);

    try {       
        System.out.println("getAbsolutePath: " + filename + " " + f.getAbsolutePath());
        System.out.println("getCanonicalPath: " + filename + " " + f.getCanonicalPath());
    } catch (Exception e) {
        e.printStackTrace();
    }
}

```

输出结果如下。

```
getAbsolutePath: C:/Windows/System32/calc.exe C:\Windows\System32\calc.exe
getCanonicalPath: C:/Windows/System32/calc.exe C:\Windows\System32\calc.exe
getAbsolutePath: C:/Windows/System32/drivers/etc/../../notepad.exe C:\Windows\System32\drivers\etc\..\..\notepad.exe
getCanonicalPath: **C:/Windows/System32/drivers/etc/../../notepad.exe C:\Windows\System32\notepad.exe**

```

使用以下代码在Linux环境测试上述两个方法。

```
public static void main(String[] args) {
    getFilePath("/etc/hosts");
    getFilePath("/etc/rc.d/init.d/../../hosts");
}

private static void getFilePath(String filename) {
    File f = new File(filename);

    try {       
        System.out.println("getAbsolutePath: " + filename + " " + f.getAbsolutePath());
        System.out.println("getCanonicalPath: " + filename + " " + f.getCanonicalPath());
    } catch (Exception e) {
        e.printStackTrace();
    }
}

```

输出结果如下。

```
getAbsolutePath: /etc/hosts /etc/hosts
getCanonicalPath: /etc/hosts /etc/hosts
getAbsolutePath: /etc/rc.d/init.d/../../hosts /etc/rc.d/init.d/../../hosts
getCanonicalPath: **/etc/rc.d/init.d/../../hosts /etc/hosts**

```

可以看出，当File对象的文件路径中包含特殊字符时，JAVA能够按照操作系统的规范对其进行相应的处理。在Windows与Linux环境中，..均代表上一级目录，因此使用..能够访问上一级目录，导致任意文件读取漏洞产生。

### 防护方法

可在处理下载的代码中对HTTP请求中的待下载文件参数进行过滤，防止出现..等特殊字符，但可能需要处理多种编码方式。

**也可在生成File对象后，使用getCanonicalPath获取当前文件的真实路径，判断文件是否在允许下载的目录中，若发现文件不在允许下载的目录中，则拒绝下载。**

0x02 恶意文件上传
===========

* * *

当攻击者利用恶意文件上传漏洞时，通常会向服务器上传jsp木马并访问，可以直接控制服务器。

### 示例

以下为恶意文件上传的示例。

upload目录中的upload.jsp为处理文件上传的jsp文件，内容如下。

```
<form name="form1" action="<%=request.getContextPath()%>/strutsUploadFileAction_signle.action"
    method="post" enctype="multipart/form-data"><input type="file" name="file4upload"
        size="30"> <br> <input type="submit"
        value="submit_signle" name="submit">
</form>

```

strutsUploadFileAction_signle为处理文件上传的struts的action，内容如下。

```
<action name="strutsUploadFileAction_signle" method="upload_signle" class="strutsUploadFile">
    <result name="success">upload/success.jsp</result>
    <result name="fail">upload/fail.jsp</result>
</action>

```

strutsUploadFile为处理文件上传的Spring的bean，内容如下。

```
<bean id="strutsUploadFile" class="strutsTest.StrutsUploadFileAction">
</bean>

```

strutsTest.StrutsUploadFileAction为处理文件上传的JAVA类，在其中会检查上传的文件名是否以“.jpg”结尾，代码如下。

```
// 注意，并不是指前端jsp上传过来的文件本身，而是文件上传过来存放在临时文件夹下面的文件
private File file4upload;

// 提交过来的file的名字
private String file4uploadFileName;

// 提交过来的file的MIME类型
private String file4uploadContentType;

public String upload_signle() throws Exception {

    return uploadCommon(file4upload, file4uploadFileName);
}

private String uploadCommon(File file, String fileName) throws Exception {
    boolean success = false;
    try {
        String newFileName = "";

        String webPath = ServletActionContext.getServletContext()
                .getRealPath("/");

        String allowedType = ".jpg";
        String fileName_new = fileName.toLowerCase();

        // 本行代码有判断文件类型是否为".jpg"，但存在文件名截断问题
        if(fileName_new.length() - fileName_new.lastIndexOf(allowedType) != allowedType.length()) {
            file.delete();
            ActionContext.getContext().put("reason", "file type is not: " + allowedType);
            return "fail";
        }

        newFileName = webPath + "uploadDir/" + fileName;
        File dest = new File(newFileName);
        if (dest.exists())
            dest.delete();
        success = file.renameTo(dest);
    } catch (Exception e) {
        success = false;
        e.printStackTrace();
        throw e;
    }

    return success ? "success" : "fail";
}

```

打开upload.jsp，选择文件“a.jpg”进行上传。

![p3](http://drops.javaweb.org/uploads/images/cdc999f5a0ce707931b095e5009dc4d363629fa9.jpg)

使用fiddler抓包并拦截，将filename参数修改为“a.jsp#.jpg”后的HTTP请求数据如下。

![p4](http://drops.javaweb.org/uploads/images/0bbcca2234957f01487795f8bf750392bb281048.jpg)

使用十六进制形式查看HTTP请求数据如下。

![p5](http://drops.javaweb.org/uploads/images/25272a8abafc1be232fe7b907ad7010307cf8ac8.jpg)

将#对应的字节修改为0x00并发送HTTP请求数据。

![p6](http://drops.javaweb.org/uploads/images/95193ab7e5512612076a0a42265effca1d09f561.jpg)

完成文件上传后，查看保存上传文件的目录，可以看到文件上传成功，生成的文件为“a.jsp”。

![p7](http://drops.javaweb.org/uploads/images/7040c2b10e740733627150ccaf7816d7b07fa1ba.jpg)

### 原因分析

从上述示例中可以看出，在上传文件时产生了文件名截断的问题。

使用以下代码测试JAVA写文件的文件名截断问题，使用0x00至0xff间的字符作为文件名生成文件。

```
public static void main(String[] args) {
    String java_version = System.getProperty("java.version");

    new File(java_version).mkdirs();    

    String filename = "a.jsp#a.jpg";
    for(int i=0; i<=0xff; i++) {
        String filename_replace = java_version + "/" + i + "-" + filename.replace('#', (char)i);
        File f = new File(filename_replace);
        try {
            f.createNewFile();
        } catch (Exception e) {
            System.out.println("error: " + i);
            e.printStackTrace();
        }
    }
}   

```

### Windows环境文件名截断问题测试

在Windows 7，64位环境，使用JDK1.5执行上述代码生成文件的结果如下。

![p8](http://drops.javaweb.org/uploads/images/2125d32e566481c9ba04e36fe3148400756f6493.jpg)

可以看到使用JDK1.5执行时，除0x00外，冒号“:”（ASCII码十进制为58）也会产生文件名截断问题。

JDK1.6与JDK1.5执行结果相同。

![p9](http://drops.javaweb.org/uploads/images/f0d0d4915b608538803c5bb9e54b43e21c0950cf.jpg)

JDK1.7也与JDK1.5执行结果相同。

![p10](http://drops.javaweb.org/uploads/images/8de48f5f67d7a05c5183e02f18a5342b47924398.jpg)

JDK1.8与JDK1.5执行结果不同，仅有冒号会产生文件名截断问题，0x00不会产生文件名截断问题，可能是JDK1.8已修复该问题。

![p11](http://drops.javaweb.org/uploads/images/5ce2416f09343822831856fd241cca7276c9b3be.jpg)

使用Procmon查看上述过程中java.exe进程执行的写文件操作。

JDK1.5、1.6、1.7的监控结果相同，监控结果如下。

JDK1.5~1.7，当文件名中包含0x00时，java.exe在执行写文件操作时，会将0x00及之后的字符串丢弃，使用0x00之前的字符串作为文件名写文件。

![p12](http://drops.javaweb.org/uploads/images/6bf3ce8ea281160963950db27a6dbf3e48cbdfcc.jpg)

JDK1.5~1.7，当文件名包含冒号时，java.exe在执行写文件操作时，不会将冒号及之后的字符串丢弃。

![p13](http://drops.javaweb.org/uploads/images/baab5841a88684ede2d2ea042897224ce21ac8c2.jpg)

JDK1.8的监控结果如下。

JDK1.8，当文件名中包含0x00时，java.exe不会执行写文件的操作。

![p14](http://drops.javaweb.org/uploads/images/81a389ca7f655ff35278a07e3b0be679809d4f04.jpg)

与JDK1.5~1.7一样，JDK1.8当文件名包含冒号时，java.exe在执行写文件操作时，不会将冒号及之后的字符串丢弃。截图略。

虽然java.exe在写文件时不会将冒号及之后的字符串丢弃，但在Windows环境下仍然出现了文件名截断的问题。

在Windows中执行“echo 1>abc:123”命令，可以看到生成的文件名为“abc”，冒号及之后的字符串被丢弃，造成了文件名截断。这是Windows特性导致的，与JAVA无关。

### Linux环境文件名截断问题测试

在Linux RedHat 6.4环境，使用JDK1.6执行上述代码生成文件的结果如下。

![p15](http://drops.javaweb.org/uploads/images/b2d06d88d919ca538b97bcb20a1a606e073a4967.jpg)

JDK1.6，文件名中包含0x00时同样出现了文件名截断问题（文件名中包含ASCII码为92的反斜杠“\”时，生成的文件会产生在子目录中，但不会导致文件类型的变化）。

**综上所述，JDK1.5-1.7存在0x00导致的文件名截断问题，与操作系统无关。冒号在Windows环境会导致文件名截断问题，与JAVA无关。**

使用File对象的getCanonicalPath方法获取JAVA在文件名中包含0x00至0xff的字符时，生成文件时的实际文件路径，代码如下。

```
public static void main(String[] args) {
    String java_version = System.getProperty("java.version");

    String filename = "a.jsp#a.jpg";
    for(int i=0; i<=0xff; i++) {
        String filename_replace = java_version + "/" + i + "-" + filename.replace('#', (char)i);
        File f = new File(filename_replace);
        try {       
            System.out.println("getCanonicalPath " + f.getCanonicalPath());
        } catch (Exception e) {
            System.out.println("error: " + i);
            e.printStackTrace();
        }
    }
}   

```

### Windows环境执行getCanonicalPath方法的结果

在Windows 7，64位环境，使用JDK1.5~1.7执行上述代码使用getCanonicalPath方法获取文件实际路径的结果相同，结果如下。

JDK1.5执行getCanonicalPath方法的结果。

![p16](http://drops.javaweb.org/uploads/images/699b49395893047863a24ec851389333e7ab9fd4.jpg)

JDK1.6执行getCanonicalPath方法的结果。

![p17](http://drops.javaweb.org/uploads/images/9ef2f950287b80286d7744daa4fe00cedbbfdf56.jpg)

JDK1.7执行getCanonicalPath方法的结果。

![p18](http://drops.javaweb.org/uploads/images/0e6c95148894168ba0b643123c9db82d7e43052d.jpg)

可以看到JDK1.5~1.7使用getCanonicalPath方法获取文件实际路径时，当文件名中包含0x00时，获取到的文件实际路径中0x00及之后的字符串已被丢弃。

在Windows 7，64位环境，使用JDK1.8执行getCanonicalPath方法的结果如下。

![p19](http://drops.javaweb.org/uploads/images/5fec52b9914bbe379cd0262a79f9ae3557439c05.jpg)

可以看到JDK1.8使用getCanonicalPath方法获取文件实际路径时，当文件名中包含0x00时，会出现java.io.IOException异常，异常信息为“Invalid file path”。

### Linux环境执行getCanonicalPath方法的结果

在Linux RedHat 6.4环境，使用JDK1.6执行上述代码的结果与Windows环境相同，截图略。

### 防护方法

以下的防护方法可以根据实际需求进行组合，相互之间没有冲突。

### 无效的防护方法

使用String对象的endsWith方法无法判断出文件生成时的实际文件名，使用以下代码进行证明。

```
public static void main(String[] args) {
    String java_version = System.getProperty("java.version");

    String filename = "a.jsp#a.jpg";
    for(int i=0; i<=0xff; i++) {
        String filename_replace = java_version + "/" + i + "-" + filename.replace('#', (char)i);
        if(filename_replace.endsWith(".jpg")) {
            System.out.println("yes: " + filename_replace);
        }
    }
}   

```

执行结果如下。

![p20](http://drops.javaweb.org/uploads/images/49fec3eb840799278d31835dc3baad91e36805ee.jpg)

当文件名为“a.jsp[特定字符]a.jpg”形式时，无论[特定字符]是否为0x00，使用String对象的endsWith方法对文件名进行检测，均认为是以“.jpg”结尾。

### 针对0x00进行检测

当文件名中包含0x00时，使用String对象的indexOf(0)方法执行结果非-1，可以检测到0x00的存在。但需考虑不同编码情况下0x00的形式。

### 检测实际的文件名

**使用File对象的getCanonicalPath方法获取上传文件的实际文件名，若检测到文件名的后缀不是允许的类型（0x00截断，小于JDK1.8），或出现java.io.IOException异常（0x00截断，JDK1.8），或包含冒号（Windows环境中需处理），则说明需要拒绝本次文件上传。**

### 修改保存上传文件的目录

上述的防护思路是防止攻击者将jsp文件上传至服务器中，本防护思路是防止攻击者上传的jsp文件被编译为class文件。

当JAVA中间件收到访问web应用目录中的jsp文件请求时，会将对应的jsp文件编译为class文件并执行。若将保存上传文件的目录修改为非web应用目录，当JAVA中间件收到访问上传文件的请求时，即使被访问的文件为jsp文件，JAVA中间件也不会将jsp文件编译为成class文件并执行，可以防止攻击者利用上传jsp木马控制服务器。

将保存上传文件的目录修改为非web应用目录的操作很简单，将处理文件上传代码中保存文件的目录修改为非web应用目录即可。进行该修改后，还可以使用共享目录解决多实例应用上传文件的问题。

将保存上传文件的目录修改为非web应用目录后，会导致无法使用原有方式访问上传的文件（例如文件上传目录原本为web应用目录中的upload目录，可直接使用http://[IP]:[PORT]/xxx/upload/xxx进行访问。将upload目录移动到非web应用目录后，无法再使用原有URL访问上传的文件）。可通过以下两种方法解决。

使用Servlet/action/.do请求访问上传文件，可参考前文中的download.DownloadAction类。本方法的影响面较大，不推荐使用。

除上述方法外，还可使用filter拦截HTTP请求处理，当HTTP请求访问文件上传目录中的文件时，读取对应的文件内容并返回（例如原本上传目录为web应用目录中的upload目录，可直接使用http://[IP]:[PORT]/xxx/upload/xxx进行访问。将upload目录移动到非web应用目录后，对HTTP请求处理进行拦截，当请求以“/xxx/upload”开头时，从文件上传目录中读取对应的文件内容并返回）。本方法可使用原本的URL访问上传文件，影响面较小，推荐使用。示例代码如下。

在web.xml中使用filter拦截HTTP请求处理。

```
<filter>
    <filter-name>testFilter</filter-name>
    <filter-class>test.TestFilter</filter-class>
</filter>

<filter-mapping>
    <filter-name>testFilter</filter-name>
    <url-pattern>/*</url-pattern>
</filter-mapping>

```

对应的test.TestFilter类代码如下。

```
private static String IF_MODIFIED_SINCE = "If-Modified-Since";
private static String LAST_MODIFIED = "Last-Modified";

private static String startFlag = "/testDownload/upload/";
private static String storePath = "C:/Users/Public";

public void doFilter(ServletRequest request, ServletResponse response,
        FilterChain chain) throws IOException, ServletException {
    HttpServletRequest httpRequest = (HttpServletRequest) request;
    // 获取浏览器访问的URL，形式如/test/upload/xxx.jpg
    String requestUrl = httpRequest.getRequestURI();
    System.out.println("requestUrl: " + requestUrl);

    if (requestUrl != null) {
        // 判断是否访问upload目录的文件，若是则从对应的存储目录读取并返回
        if (requestUrl.startsWith(startFlag)) {
            try {
                returnFileContent(requestUrl, (HttpServletRequest) request,
                        (HttpServletResponse) response);
            } catch (Exception e) {
                // TODO Auto-generated catch block
                e.printStackTrace();
            }
            return;
        }
    }

    chain.doFilter(request, response);
    return;
}

// 当访问web应用特定目录下的文件时，重定向到实际存储这些文件的目录
private void returnFileContent(String url, HttpServletRequest request,
        HttpServletResponse response) throws Exception {
    java.io.InputStream in = null;
    java.io.OutputStream outStream = null;
    try {
        response.setHeader("Content-Type", "text/plain");// 若不返回text/plain类型，浏览器无法正常识别文件类型
        String filePath = url.substring(startFlag.length() - 1);// 获取被访问的文件的URL
        String filePath_decode = URLDecoder.decode(filePath, "UTF-8");// 经过url解码之后的文件URL

        // 生成最终访问的文件路径
        // StorePath形式如C:/xxx/xxx，filePath_decode开头有/
        String targetfile = storePath + filePath_decode;
        System.out.println("targetfile: " + targetfile);
        File f = new File(targetfile);
        if (!f.exists() || f.isDirectory()) {
            System.out.println("文件不存在: " + targetfile);
            response.sendError(HttpServletResponse.SC_NOT_FOUND);// 返回错误信息，显示统一错误页面
            return;
        }
        // 判断上送的HTTP头是否有If-Modified-Since字段
        String modified = request.getHeader(IF_MODIFIED_SINCE);
        //获取文件的修改时间
        String modified_file = getFileModifiedTime(f);
        if (modified != null) {
            // 上送的HTTP头有If-Modified-Since字段，判断与对应文件的修改时间是否相同
            if(modified.equals(modified_file)) {
                //上送的文件时间与文件实际修改时间相同，不需返回文件内容
                response.setStatus(HttpServletResponse.SC_NOT_MODIFIED);//返回304状态
                outStream = response.getOutputStream();
                outStream.close();
                outStream.flush();
                outStream = null;
                return;
            }
        }
        // 文件无缓存，或文件有修改，需要在返回的HTTP头中添加文件修改时间
        response.setHeader(LAST_MODIFIED, modified_file);

        // 读取文件内容
        in = new FileInputStream(f);
        outStream = response.getOutputStream();
        byte[] buf = new byte[1024];
        int bytes = 0;
        while ((bytes = in.read(buf)) != -1)
            outStream.write(buf, 0, bytes);
        in.close();
        outStream.close();
        outStream.flush();
        outStream = null;
    } catch (Throwable ex) {
        ex.printStackTrace();
    } finally {
        if (in != null) {
            in.close();
            in = null;
        }
        if (outStream != null) {
            outStream.close();
            outStream = null;
        }
    }
}

// 获取指定文件的修改时间
private String getFileModifiedTime(File file) {
    SimpleDateFormat sdf = new SimpleDateFormat("EEE, dd MMM yyyy HH:mm:ss z", Locale.US);
    sdf.setTimeZone(TimeZone.getTimeZone("GMT"));
    return sdf.format(file.lastModified());
}

```

上述示例代码中，保存上传文件的目录为“C:/Users/Public”，当HTTP请求以“/testDownload/upload/”开头时，说明需要访问上传文件。

上述修改方法接管了JAVA中间件对原本上传目录的静态资源的访问请求，导致浏览器的缓存机制不可用。为了保证浏览器的缓存机制可用，上述代码中进行了专门处理。当HTTP请求头中不包含“If-Modified-Since”参数时，或“If-Modified-Since”对应的文件修改时间小于实际文件修改时间时，将文件的内容返回给浏览器，并在返回的HTTP头中加入“Last-Modified”参数返回文件修改时间，使浏览器对该文件进行缓存。当HTTP请求头的“If-Modified-Since”对应的文件修改时间等于实际文件修改时间时，不返回文件内容，将返回的HTTP码设为304，告知浏览器访问的文件无修改，可使用缓存。

以下为上述代码的测试结果。

web应用的目录中无upload目录。

![p21](http://drops.javaweb.org/uploads/images/d1ae9a191880ce0df260136f20bfff6ba95ed052.jpg)

文件上传目录“C:/Users/Public”中有以下文件。

![p22](http://drops.javaweb.org/uploads/images/e0bca2d2f649f7383298ad058ebfded158d6008b.jpg)

访问文本文件正常。

![p23](http://drops.javaweb.org/uploads/images/bd3f048c0a84bcf5183964897731016bde83efb5.jpg)

访问图片正常。

![p24](http://drops.javaweb.org/uploads/images/a20e98e438cd08f83e61a44822b69c4d4fd63937.jpg)

访问音频文件正常。

![p25](http://drops.javaweb.org/uploads/images/0c90a613b3732f31932e006c768c123ed49c8e2e.jpg)

访问jsp文件只返回文件本身的内容，不会被编译成class文件并执行。

![p26](http://drops.javaweb.org/uploads/images/a030c83dcc1fad41a826b2d50969effd6c30de4f.jpg)

使用fiddler查看访问记录，浏览器缓存机制正常。

![p27](http://drops.javaweb.org/uploads/images/86504ba23f61df079413e5fb08ee8ecf3ac438fb.jpg)

### 修改web应用目录权限

将文件上传目录移出web应用目录后，JAVA中间件在运行过程中，web应用目录及其中的文件一般不会被修改。可在JAVA中间件启动后，将web应用目录设为JAVA中间件不可写；当需要进行版本更新或维护时，停止JAVA中间件后，将web应用目录设为JAVA中间件可写。通过上述限制，可严格地防止web应用目录被上传jsp木马等恶意文件。

可将JAVA中间件使用a用户启动，将web应用的目录对应用户设为b用户，JAVA中间件启动后，将web应用的目录设为a用户只读。需要进行版本更新或维护时，停止JAVA中间件后，将web应用的目录设为a用户可读写。对于某些JAVA中间件在运行过程中可能需要进行写操作的文件或目录，可单独设置权限。可将对web应用的权限修改操作在JAVA中间件启停脚本中调用，减少操作复杂度。

Windows的权限设置较复杂且速度较慢，使用上述的防护方法时会比较麻烦。

0x03 SQL注入
==========

* * *

### PreparedStatement与Statement

众所周知，在JAVA中使用PreparedStatement替代Statement可以防止SQL注入。

在oracle数据库中进行以下测试。

首先创建测试用的数据库表并插入数据。

```
create table test_user
(
username varchar2(100),
pwd varchar2(100)
);

Insert into TEST_USER
   (USERNAME, PWD)
 Values
   ('aaa', 'bbb');
COMMIT;

```

使用以下JAVA代码进行测试。

```
private Connection conn = null;

public dbtest2(String url, String username, String password)
        throws ClassNotFoundException, SQLException {
    try {
        Class.forName("oracle.jdbc.driver.OracleDriver");
        conn = DriverManager.getConnection(url, username, password);
    } catch (Exception e) {
        // TODO: handle exception
        e.printStackTrace();
    }
}

public void closeDb() throws SQLException {
    conn.close();
}

public void executeStatement(String username, String pwd)
        throws SQLException {
    String sql = "SELECT * FROM TEST_USER where username='" + username
            + "' and pwd='" + pwd + "'";
    System.out.println("executeStatement-sql: " + sql);
    java.sql.Statement stmt = conn.createStatement();
    ResultSet rs = stmt.executeQuery(sql);
    showResultSet(rs);
    stmt.close();
}

public void executePreparedStatement(String username, String pwd)
        throws SQLException {
    java.sql.PreparedStatement stmt = conn
            .prepareStatement("SELECT * FROM TEST_USER where username=? and pwd=?");
    stmt.setString(1, username);
    stmt.setString(2, pwd);
    ResultSet rs = stmt.executeQuery();
    showResultSet(rs);
    stmt.close();
}

public void showResultSet(ResultSet rs) throws SQLException {
    ResultSetMetaData meta = rs.getMetaData();
    StringBuffer sb = new StringBuffer();
    int colCount = meta.getColumnCount();
    for (int i = 1; i <= colCount; i++) {
        sb.append(meta.getColumnName(i)).append("[")
                .append(meta.getColumnTypeName(i)).append("]").append("\t");
    }
    while (rs.next()) {
        sb.append("\r\n");

        for (int i = 1; i <= colCount; i++) {
            sb.append(rs.getString(i)).append("\t");
        }
    }
    // 关闭ResultSet
    rs.close();

    System.out.println(sb.toString());
}

public static void main(String[] args) throws SQLException {
    try {
        dbtest2 db = new dbtest2(
                "jdbc:oracle:thin:@192.xxx.xxx.xxx:1521:xxx",
                "xxx", "xxx");

        db.executeStatement("aaa", "bbb");
        db.executeStatement("aaa", "' or '2'='2");

        db.executePreparedStatement("aaa", "bbb");
        db.executePreparedStatement("aaa", "' or '2'='2");

        db.closeDb();
    } catch (ClassNotFoundException e) {
        // TODO Auto-generated catch block
        e.printStackTrace();
    }
}

```

执行结果如下。

```
1 db.executeStatement("aaa", "bbb");对应的结果  
executeStatement-sql: SELECT * FROM TEST_USER where username='aaa' and pwd='bbb'

USERNAME[VARCHAR2]  PWD[VARCHAR2]  
aaa bbb 

2 db.executeStatement("aaa", "' or '2'='2");对应的结果  
executeStatement-sql: SELECT * FROM TEST_USER where username='aaa' and pwd='' or '2'='2'

USERNAME[VARCHAR2]  PWD[VARCHAR2]  
aaa bbb 

3 db.executePreparedStatement("aaa", "bbb");对应的结果  
USERNAME[VARCHAR2]  PWD[VARCHAR2]  
aaa bbb 

4 db.executePreparedStatement("aaa", "' or '2'='2");对应的结果  
USERNAME[VARCHAR2]  PWD[VARCHAR2]  

```

可以看到使用Statement时，将查询参数设为“username='aaa' and pwd='bbb'”使用正常的查询条件能查询到对应的数据。将查询参数设为“username='aaa' and pwd='' or '2'='2'”能够利用SQL注入查询到对应的数据。

使用PreparedStatement时，使用正常的查询条件同样能查询到对应的数据，使用能使Statement产生SQL注入的查询条件无法再查询到数据。

使用Wireshark对刚才的数据库操作抓包并查看网络数据。

查找select语句对应的数据包如下。

![p28](http://drops.javaweb.org/uploads/images/22cb8e4885ec79b60b950cbd0210a703e4bfabe0.jpg)

db.executeStatement("aaa", "bbb");对应的数据包如下，可以看到查询语句未使用oracle绑定变量方式，使用正常查询条件查询到了数据。

![p29](http://drops.javaweb.org/uploads/images/33208164f8071f2e067f95c035beb76fa8aeeef4.jpg)

db.executeStatement("aaa", "' or '2'='2");对应的数据包如下，可以看到查询语句未使用oracle绑定变量方式，利用SQL注入查询到了数据。

![p30](http://drops.javaweb.org/uploads/images/bbafb681426b3ba83c33d0102c419fe14a2ce1fc.jpg)

db.executePreparedStatement("aaa", "bbb");对应的数据包如下，可以看到查询语句使用了oracle绑定变量方式，使用正常查询条件查询到了数据。

![p31](http://drops.javaweb.org/uploads/images/e69711e519a0154a4e0e884cebc927089a3cd9fe.jpg)

db.executePreparedStatement("aaa", "' or '2'='2");对应的数据包如下，可以看到查询语句使用了oracle绑定变量方式，SQL注入未生效，无法查询到对应数据。

![p32](http://drops.javaweb.org/uploads/images/81a55352fb94e80bd5d9bc752598f1d1e642b09c.jpg)

在JAVA中使用PreparedStatement访问oracle数据库时，除了能防止SQL注入外，还能使oracle服务器降低硬解析率，降低系统开销，减少内存碎片，提高执行效率。

刚才执行的sql语句在oracle的v$sql视图中产生的数据如下。

![p33](http://drops.javaweb.org/uploads/images/73f0b2985b952ccc4f208ea95c6ad2bf6805837e.jpg)

### ibatis

当使用ibatis作为持久化框架时，也需要考虑SQL注入的问题。使用ibatis产生SQL注入主要是由于使用不规范。

### `$`与`#`

在ibatis中使用#时，与使用PreparedStatement的效果相同，不会产生SQL注入；在ibatis中使用$时，与使用Statement的效果相同，会产生SQL注入。

继续使用刚才的数据库表TEST_USER进行测试，再插入一条数据如下。

```
Insert into TEST_USER
   (USERNAME, PWD)
 Values
   ('123', '456');
COMMIT;

```

将log4j中的数据库相关日志级别设为DEBUG。

```
log4j.logger.com.ibatis=DEBUG
log4j.logger.com.ibatis.common.jdbc.SimpleDataSource=DEBUG
log4j.logger.com.ibatis.common.jdbc.ScriptRunner=DEBUG
log4j.logger.com.ibatis.sqlmap.engine.impl.SqlMapClientDelegate=DEBUG
log4j.logger.java.sql.Connection=DEBUG
log4j.logger.java.sql.Statement=DEBUG
log4j.logger.java.sql.PreparedStatement=DEBUG
log4j.logger.java.sql.ResultSet=DEBUG

```

首先使用#与$测试执行判断条件为“=”的sql语句时的情况。

在ibatis对应的xml文件中配置了语句test_right与test_wrong如下。

```
<select id="test_right" resultClass="java.util.HashMap"
    parameterClass="java.util.HashMap">
    select * from test_user where username = #username#
</select>

<select id="test_wrong" resultClass="java.util.HashMap"
    parameterClass="java.util.HashMap">
    select * from test_user where username = '$username$'
</select>

```

在JAVA代码中执行上述语句如下。

```
HashMap hs = new HashMap();

hs.put("username", "' or '1'='1");

List<Object> list1 = queryListSql("test_right",hs);
logger.info("test-list1: " + list1);

List<Object> list2 = queryListSql("test_wrong",hs);
logger.info("test-list2: " + list2);

```

log4j中执行test_right语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username = ?  
[DEBUG] Executing Statement:    select * from test_user where username = ?    
[DEBUG] Parameters: [' or '1'='1]  
[DEBUG] Types: [java language=".lang.String"][/java]  
[DEBUG] ResultSet  
[INFO ] test-list1: []  

```

log4j中执行test_wrong语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username = '' or '1'='1'  
[DEBUG] Executing Statement:    select * from test_user where username = '' or '1'='1'  
[DEBUG] Parameters: []  
[DEBUG] Types: []  
[DEBUG] ResultSet  
[DEBUG] Header: [USERNAME, PWD]  
[DEBUG] Result: [aaa, bbb]  
[DEBUG] Result: [123, 456]  
[INFO ] test-list2: [{PWD=bbb, USERNAME=aaa}, {PWD=456, USERNAME=123}]  

```

可以看到使用#可以防止SQL注入，使用$会产生SQL注入。

执行test_right语句时产生的数据包如下。

![p34](http://drops.javaweb.org/uploads/images/b76d504c0c1834fd84a07bf7dcd5a19b8192db09.jpg)

执行test_wrong语句时产生的数据包如下。

![p35](http://drops.javaweb.org/uploads/images/ca70c271b46a98e049b1075cc3d998a717a304ca.jpg)

### like

在使用ibatis执行判断条件为“like”的操作时，较容易误用$导致产生SQL注入问题。

**当需要使用like时，应用使用“xxx like '%' || #xxx# || '%'”，而不应使用“xxx like '%$xxx$%'”（以oracle数据库为例）。**

使用以下代码进行验证测试。

在ibatis对应的xml文件中配置了语句test_like_right与test_like_wrong如下。

```
<select id="test_like_right" resultClass="java.util.HashMap"
    parameterClass="java.util.HashMap">
    select * from test_user where username like '%' || #username# || '%'
</select>

<select id="test_like_wrong" resultClass="java.util.HashMap"
    parameterClass="java.util.HashMap">
    select * from test_user where username like '$username$'
</select>

```

在JAVA代码中执行上述语句如下。

```
HashMap hs = new HashMap();

hs.put("username", "' or '1'='1");

List<Object> list3 = queryListSql("test_like_right",hs);
logger.info("test-list3: " + list3);

List<Object> list4 = queryListSql("test_like_wrong",hs);
logger.info("test-list4: " + list4);

```

log4j中执行test_like_right语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username like '%' || ? || '%'  
[DEBUG] Executing Statement:    select * from test_user where username like '%' || ? || '%'  
[DEBUG] Parameters: [' or '1'='1]  
[DEBUG] Types: [java language=".lang.String"][/java]  
[DEBUG] ResultSet  
[INFO ] test-list3: []  

```

log4j中执行test_like_wrong语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username like '' or '1'='1'   
[DEBUG] Executing Statement:    select * from test_user where username like '' or '1'='1'  
[DEBUG] Parameters: []  
[DEBUG] Types: []  
[DEBUG] ResultSet  
[DEBUG] Header: [USERNAME, PWD]  
[DEBUG] Result: [aaa, bbb]  
[DEBUG] Result: [123, 456]  
[INFO ] [{PWD=bbb, USERNAME=aaa}, {PWD=456, USERNAME=123}]  

```

执行语句时test_like_right产生的数据包如下。

![p36](http://drops.javaweb.org/uploads/images/5b46065dfd3f39f3e42800238eb13760615081db.jpg)

执行语句时test_like_wrong产生的数据包如下。

![p37](http://drops.javaweb.org/uploads/images/91ac2f7b55f0435ad2d77f575ad3287cbee6c317.jpg)

### in

在使用ibatis处理判断条件为“in”的操作时，同样容易误用$导致SQL注入问题。

当需要使用in时，可使用以下方法。

java代码。

```
String[] xxx_list = new String[] {"xx1","xx2"};
HashMap hs = new HashMap();
hs.put("xxx", xxx_list);
//hs为sql语句查询参数

```

xml中的语句配置。

```
<select id="" resultClass="java.util.HashMap"
parameterClass="java.util.HashMap">
    ...
    <dynamic prepend=" and ">
        <isNotEmpty prepend=" and  " property="xxx">
            (xxx in
                <iterate open="(" close=")" conjunction="," property="xxx">#xxx[]#</iterate>
            )
        </isNotEmpty>
    </dynamic>
    ...
</select>

```

**当需要使用in时，不应使用“in ('$xxx$')”。**

在ibatis对应的xml文件中配置了语句test_in_right与test_in_wrong如下。

```
<select id="test_in_right" resultClass="java.util.HashMap"
    parameterClass="java.util.HashMap">
    select * from test_user where username in
    <iterate open="(" close=")" conjunction="," property="username">#username[]#</iterate>
</select>

<select id="test_in_wrong" resultClass="java.util.HashMap"
    parameterClass="java.util.HashMap">
    select * from test_user where username in ('$username$')
</select>

```

在JAVA代码中执行上述语句如下。

```
String[] username_list = new String[] {"') or ('1'='1"};
hs.put("username", username_list);

List<Object> list5 = queryListSql("test_in_right",hs);
logger.info("test-list5: " + list5);

HashMap hs = new HashMap();

hs.put("username", "') or ('1'='1");

List<Object> list6 = queryListSql("test_in_wrong",hs);
logger.info("test-list6: " + list6);

```

log4j中执行test_in_right语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username in   (?)  
[DEBUG] Executing Statement:    select * from test_user where username in   (?)  
[DEBUG] Parameters: [') or ('1'='1]  
[DEBUG] Types: [java language=".lang.String"][/java]  
[DEBUG] ResultSet  
[INFO ] test-list5: []  

```

log4j中执行test_in_wrong语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username in ('') or ('1'='1')  
[DEBUG] Executing Statement:    select * from test_user where username in ('') or ('1'='1')  
[DEBUG] Parameters: []  
[DEBUG] Types: []  
[DEBUG] ResultSet  
[DEBUG] Header: [USERNAME, PWD]  
[DEBUG] Result: [aaa, bbb]  
[DEBUG] Result: [123, 456]  
[INFO ] test-list6: [{PWD=bbb, USERNAME=aaa}, {PWD=456, USERNAME=123}]  

```

执行test_in_right语句时产生的数据包如下。

![p38](http://drops.javaweb.org/uploads/images/e9dcb9b2da24aee3b2bddd2dd82de7ae6970bd85.jpg)

执行test_in_wrong语句时产生的数据包如下。

![p39](http://drops.javaweb.org/uploads/images/e398072259f61784d956a5ac03851f62ea8c35ef.jpg)

在ibatis中在执行包含like或in的语句时，使用#也是能正常查询到数据的。

在JAVA代码中使用正确的查询条件执行test_like_right与test_in_right语句如下。

```
HashMap hs = new HashMap();

hs.put("username", "aaa");

List<Object> list7 = queryListSql("test_like_right",hs);
logger.info("test-list7: " + list7);

String[] username_list2 = new String[] {"aaa","123"};
hs.put("username", username_list2);

List<Object> list8 = queryListSql("test_in_right",hs);
logger.info("test-list8: " + list8);

```

log4j中使用正确的查询条件执行test_like_right语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username like '%' || ? || '%'  
[DEBUG] Executing Statement:    select * from test_user where username like '%' || ? || '%'  
[DEBUG] Parameters: [aaa]  
[DEBUG] Types: [java language=".lang.String"][/java]  
[DEBUG] ResultSet  
[DEBUG] Header: [USERNAME, PWD]  
[DEBUG] Result: [aaa, bbb]  
[INFO ] test-list7: [{PWD=bbb, USERNAME=aaa}]  

```

log4j中使用正确的查询条件执行test_in_right语句时的相关日志如下。

```
[DEBUG] Preparing Statement:    select * from test_user where username in   (?,?)  
[DEBUG] Executing Statement:    select * from test_user where username in   (?,?)  
[DEBUG] Parameters: [aaa, 123]  
[DEBUG] Types: [java 1="java.lang.String" language=".lang.String,"][/java]  
[DEBUG] ResultSet  
[DEBUG] Header: [USERNAME, PWD]  
[DEBUG] Result: [aaa, bbb]  
[DEBUG] Result: [123, 456]  
[INFO ] test-list8: [{PWD=bbb, USERNAME=aaa}, {PWD=456, USERNAME=123}]  

```

使用正确的查询条件执行test_like_right语句时产生的数据包如下。

![p40](http://drops.javaweb.org/uploads/images/1e372163cd092d8c7f1037c36dc50aa5078b1dcd.jpg)

使用正确的查询条件执行test_in_right语句时产生的数据包如下。

![p41](http://drops.javaweb.org/uploads/images/8e16e6c3753b8fb468c57594311aa0cb9e0ce425.jpg)

上述全部语句执行时在oracle的v$sql视图中产生的数据如下。

![p42](http://drops.javaweb.org/uploads/images/955e332d7f12c514fc4ff2c145833b10ebaed2e7.jpg)

0x04 其他问题
=========

* * *

### 错误页

在web.xml中定义error-page，防止当出现错误时暴露服务器信息。

示例如下。

```
<error-page>
    <error-code>404</error-code>
    <location>xxx.jsp</location>
</error-page>

<error-page>
    <error-code>500</error-code>
    <location>xxx.jsp</location>
</error-page>

```

### 仅允许已登录用户的访问

当用户访问jsp或Servlet/action/.do时，需要判断当前用户是否已登录且具有相应权限，防止出现越权使用。

0x05 后记
=======

* * *

以上为本人的一点总结，难免存在错误之处，大牛请轻喷。