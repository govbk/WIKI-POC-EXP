# Java安全编码之用户输入

0x00 安全引言
=========

* * *

1、传统Web应用与新兴移动应用
----------------

（1）传统Web应用：浏览器 HTTP 服务器  
（2）新兴移动应用：APP HTTP 服务器

从安全角度看，传统Web应用与新兴移动应用没有本质区别

2、Web应用安全的核心问题是什么？
------------------

**_用户提交的数据不可信_**是Web应用程序核心安全问题

用户可以提交**_任意输入_**

例如：

√ 请求参数->多次提交或者不提交  
√ 修改Cookie  
√ 修改HTTP信息头  
√ 请求顺序->跳过或者打乱

3、Web应用防御
---------

（1）完善的异常处理  
（2）监控  
（3）日志：记录重要业务、异常的详细请求信息

4、对输入的处理
--------

建议采用：白名单  
尽量避免：净化或黑名单

0x01 SQL注入
==========

* * *

1、原理：
-----

（1）合法输入：

```
id=1
SELECT * FROM users WHRER id='1';

```

（2）恶意注入：

```
id=1' or '1'='1
SELECT * FROM users WHRER id='1' or 'a'='a';

```

2、Java代码分析(JDBC)
----------------

（1）不合规代码(SQL参数拼接)

```
public class SQLInject {
    public static void main(String[] args)throws Exception{
        //正常输入
        select("1");
        // 恶意输入
        select("' or 'a'='a");
    }
    public static void  select(String id){
        //声明Connection对象
        Connection con;
        //驱动程序名
        String driver = "com.mysql.jdbc.Driver";
        //URL指向要访问的数据库名mydata
        String url = "jdbc:mysql://localhost:3306/mybatis";
        //MySQL配置时的用户名
        String user = "root";
        //MySQL配置时的密码
        String password = "budi";
        //遍历查询结果集
        try {
            //加载驱动程序
            Class.forName(driver);
            //1.getConnection()方法，连接MySQL数据库！！
            con = DriverManager.getConnection(url,user,password);
            if(!con.isClosed())
                System.out.println("Succeeded connecting to the Database!");
            //2.创建statement类对象，用来执行SQL语句！！
            Statement statement = con.createStatement();
            //要执行的SQL语句
            String sql = "select * from users where id='"+id+"'";
            //3.ResultSet类，用来存放获取的结果集！！
            ResultSet rs = statement.executeQuery(sql);
            System.out.println("-----------------");
            System.out.println("执行结果如下所示:");  
            System.out.println("-----------------"); 
            String age,name;
            while(rs.next()){
                //获取stuname这列数据
                name = rs.getString("name");
                //获取stuid这列数据
                age = rs.getString("age");
                //输出结果
                System.out.println(name + "\t" + age);
            }
            rs.close();
            con.close();
        } catch(ClassNotFoundException e) {   
            //数据库驱动类异常处理
            System.out.println("Sorry,can`t find the Driver!");   
            e.printStackTrace();   
            } catch(SQLException e) {
            //数据库连接失败异常处理
            e.printStackTrace();  
            }catch (Exception e) {
            // TODO: handle exception
            e.printStackTrace();
        }finally{
            System.out.println("数据库数据成功获取！！");
        }
    }
}

```

执行结果：

```
SQL Paramter:1
-----------------
budi    27
-----------------
SQL Paramter:' or 'a'='a
-----------------
budi    27
budisploit  28
-----------------

```

（2）合规代码（参数化查询）

```
public class SQLFormat {
    public static void main(String[] args)throws Exception{
        select("1");
        select("' or 'a'='a");
    }
    public static void  select(String id){
        //声明Connection对象
        Connection con;
        //驱动程序名
        String driver = "com.mysql.jdbc.Driver";
        //URL指向要访问的数据库名mydata
        String url = "jdbc:mysql://localhost:3306/mybatis";
        //MySQL配置时的用户名
        String user = "root";
        //MySQL配置时的密码
        String password = "budi";
        //遍历查询结果集
        try {
            //加载驱动程序
            Class.forName(driver);
            //1.getConnection()方法，连接MySQL数据库！！
            con = DriverManager.getConnection(url,user,password);
            if(!con.isClosed())
                System.out.println("Succeeded connecting to the Database!");
            //2.//要执行的SQL语句
            String sql = "select * from users where id=?";
            //3.创建statement类对象，ResultSet类，用来存放获取的结果集！！
            PreparedStatement stmt = con.prepareStatement(sql);
            stmt.setString(1, id);
            ResultSet rs = stmt.executeQuery();
            System.out.println("-----------------");
            System.out.println("执行结果如下所示:");  
            System.out.println("-----------------"); 
            String age,name;
            while(rs.next()){
                //获取stuname这列数据
                name = rs.getString("name");
                //获取stuid这列数据
                age = rs.getString("age");
                //输出结果
                System.out.println(name + "\t" + age);
            }
            rs.close();
            con.close();
        } catch(ClassNotFoundException e) {   
            //数据库驱动类异常处理
            System.out.println("Sorry,can`t find the Driver!");   
            e.printStackTrace();   
            } catch(SQLException e) {
            //数据库连接失败异常处理
            e.printStackTrace();  
            }catch (Exception e) {
            // TODO: handle exception
            e.printStackTrace();
        }finally{
            System.out.println("数据库数据成功获取！！");
        }
    }
}

```

执行结果：

```
SQL Paramter:1
-----------------
budi    27
-----------------
SQL Paramter:' or 'a'='a
-----------------
-----------------

```

3、防范建议：
-------

√ 采用参数查询即预编译方式（**首选**）  
√ 字符串过滤

0x02 XML注入
==========

* * *

1、原理
----

（1）合法输入：

```
quantity=1
<item>
    <name>apple</name>
    <price>500.0</price>
    <quantity>1</quantity>
<item>

```

（2）恶意输入：

```
quantity=1</quantity><price>5.0</price><quantity>1
<item>
    <name>apple</name>
    <price>500.0</price>
    <quantity>1</quantity><price>5.0</price><quantity>1</quantity>
<item>

```

2、Java代码分析
----------

（1）不合规代码（未进行安全检查）

```
public class XMLInject2 {
    public static void main(String[] args) {
        // 正常输入
        ArrayList<Map<String, String>> normalList=(ArrayList<Map<String, String>>) 
                ReadXML("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\inject\\normal.xml","price");
        System.out.println(normalList.toString());
        // 异常输入
        ArrayList<Map<String, String>> evilList=(ArrayList<Map<String, String>>) 
                ReadXML("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\inject\\evil.xml","price");
        System.out.println(evilList.toString());
    }
    private static List<Map<String,String>> ReadXML(String uri,String NodeName){
        try {
            //创建一个解析XML的工厂对象
            SAXParserFactory parserFactory=SAXParserFactory.newInstance();
            //创建一个解析XML的对象
            SAXParser parser=parserFactory.newSAXParser();
            //创建一个解析助手类
            MyHandler myhandler=new MyHandler(NodeName);
            parser.parse(uri, myhandler);
            return myhandler.getList();
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }
}

```

运行结果：

```
正常输入结果：[{price=500.0}]
恶意输入结果：[{price=500.0}, {price=5.0}]

```

（2）合规代码（利用schema安全检查）

```
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xs:element name="item">
    <xs:complexType>
        <xs:sequence>
            <xs:element name="name" type="xs:string"/>
            <xs:element name="price" type="xs:decimal"/>
            <xs:element name="quantity" type="xs:integer"/>
        </xs:sequence>
    </xs:complexType>
</xs:element>

```

测试代码

```
public class XMLFormat{
    public static void main(String[] args) {
        //测试正常输入
        test("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\inject\\normal.xml");
        //测试异常输入
        test("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\inject\\evil.xml");
    }
    private static void test(String file) {
        SchemaFactory schemaFactory = SchemaFactory
                .newInstance("XMLConstants.W3C_XML_SCHEMA_NS_URI");
        Schema schema;
        try {
            schema = schemaFactory.newSchema(new File("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\inject\\schema.xsd"));
            Validator validator = schema.newValidator();
            validator.setErrorHandler(new ErrorHandler() {
                public void warning(SAXParseException exception)
                        throws SAXException {
                    System.out.println("警告：" + exception);
                }
                public void fatalError(SAXParseException exception)
                        throws SAXException {
                    System.out.println("致命：" + exception);
                }
                public void error(SAXParseException exception) throws SAXException {
                    System.out.println("错误：" + exception);
                }
            });
            validator.validate(new StreamSource(new File(file)));
            System.out.println("解析正常");;
        } catch (SAXException e) {
            // TODO Auto-generated catch block
            //e.printStackTrace();
            System.out.println("解析异常");
        } catch (IOException e) {
            // TODO Auto-generated catch block
            //e.printStackTrace();
            System.out.println("解析异常");
        }
    }
}

```

运行结果：

```
正常输入........
解析正常
恶意输入........
错误：org.xml.sax.SAXParseException; systemId: file:/D:/JavaWorkspace/TestInput/src/cn/com/budi/xml/inject/evil.xml; lineNumber: 7; columnNumber: 10; cvc-complex-type.2.4.d: 发现了以元素 'price' 开头的无效内容。此处不应含有子元素。

```

3、防范建议：
-------

√ 文档类型定义（Document Type Definition，DTD）  
√ XML结构化定义文件（XML Schemas Definition）  
√ 白名单

0x03 XXE (XML external entity)
==============================

* * *

1、原理：
-----

（1）合法输入：

```
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE updateProfile [<!ENTITY lastname "Hello, Budi!">
<!ENTITY file SYSTEM "file:///D:/test.txt">]>
<users > 
    <firstname>&file</firstname> 
    <lastname>&lastname;</lastname> 
</users>

```

（2）恶意输入：

```
<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE updateProfile [<!ENTITY file SYSTEM "file:///D:/password.txt"> ]>
<users > 
    <firstname>&file;</firstname> 
    <lastname>&lastname;</lastname> 
</users>

```

2、Java代码分析
----------

（1）不合规代码（未安全检查外部实体）

```
public class XXEInject {
    private static void receiveXMLStream(InputStream inStream, MyDefaultHandler defaultHandler) {
        // 1.获取基于SAX的解析器的实例
        SAXParserFactory factory = SAXParserFactory.newInstance();
        // 2.创建一个SAXParser实例
        SAXParser saxParser = factory.newSAXParser();
        // 3.解析
        saxParser.parse(inStream, defaultHandler);
    }
    public static void main(String[] args) throws FileNotFoundException, ParserConfigurationException, SAXException, IOException{
        //正常输入
        receiveXMLStream(new FileInputStream("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\xxe\\inject\\normal.xml"), 
                          new MyDefaultHandler());
        //恶意输入
        receiveXMLStream(new FileInputStream("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\xxe\\inject\\evil.xml"), 
                          new MyDefaultHandler());
    }  
}

```

运行结果：

```
正常输入，等待解析......
<firstname>XEE TEST !!</firstname>
==========================
恶意输入，等待解析......
<firstname>OWASP BWA   root/owaspbwa
Metasploitable  msfadmin/msfadmin
Kali Liunx  root/wangpeng
</firstname>

```

（2）合规代码（安全检查外部实体）

```
public class CustomResolver implements EntityResolver{
    public InputSource resolveEntity(String publicId, String systemId) throws SAXException, IOException{
        //System.out.println("PUBLIC:"+publicId);
        //System.out.println("SYSTEM:"+systemId);
        System.out.println("引用实体检测....");
        String entityPath = "file:///D:/test.txt";
        if (systemId.equals(entityPath)){
            System.out.println("合法解析："+systemId);
            return new InputSource(entityPath);
        }else{
            System.out.println("非法实体："+systemId);
            return new InputSource();
        }
    }
}

```

测试代码

```
public class XXEFormat {
    private static void receiveXMLStream(InputStream inStream, MyDefaultHandler defaultHandler) {
        // 获取基于SAX的解析器的实例
        SAXParserFactory factory = SAXParserFactory.newInstance();
        // 创建一个SAXParser实例
        SAXParser saxParser;
        try {
            saxParser = factory.newSAXParser();
            //创建读取工具
            XMLReader reader = saxParser.getXMLReader();
            reader.setEntityResolver(new CustomResolver());
            reader.setErrorHandler(defaultHandler);
            InputSource is = new InputSource(inStream);
            reader.parse(is);
            System.out.println("\t成功解析完成!");
        } catch (ParserConfigurationException e) {
            // TODO Auto-generated catch block
            System.out.println("\t非法解析!");
        } catch (SAXException e) {
            // TODO Auto-generated catch block
            System.out.println("\t非法解析!");
        } catch (IOException e) {
            // TODO Auto-generated catch block
            System.out.println("\t非法解析!");
        }
    }
    public static void main(String[] args) throws ParserConfigurationException, SAXException, IOException{
        //正常输入
        System.out.println("正常输入，等待解析......");
        receiveXMLStream(new FileInputStream("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\xxe\\inject\\normal.xml"), 
                          new MyDefaultHandler());
        System.out.println("==========================");
        //恶意输入
        System.out.println("恶意输入，等待解析......");
        receiveXMLStream(new FileInputStream("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\xml\\xxe\\inject\\evil.xml"),  
                          new MyDefaultHandler());
    }
}

```

运行结果：

```
正常输入，等待解析......
引用实体检测....
合法解析：file:///D:/test.txt
    成功解析完成!
==========================
恶意输入，等待解析......
引用实体检测....
非法实体：file:///D:/password.txt
    非法解析!

```

3、防范建议：
-------

√ 白名单

0x04命令注入
========

* * *

1、原理：
-----

（1）正常输入：

```
dir

```

（2）恶意输入：

```
dir & ipconfig & net user budi budi /add & net localgroup Administrators admin /add

```

2、Java代码分析
----------

（1）非合规Window命令注入

```
public class OrderWinFault {
    public static void main(String[] args) throws Exception{
         //正常命令
        runOrder("dir");
         //恶意命令
        runOrder("dir & ipconfig & net user budi budi /add & net localgroup Administrators admin /add");
    }
    private static void runOrder(String order) throws IOException, InterruptedException{
        Runtime rt = Runtime.getRuntime();
        Process proc = rt.exec("cmd.exe /C "+order);
        int result = proc.waitFor();
        if(result !=0){
            System.out.println("process error: "+ result);
        }
        InputStream in = (result == 0)? proc.getInputStream() : proc.getErrorStream();
        BufferedReader reader=new BufferedReader(new InputStreamReader(in));
        StringBuffer  buffer=new StringBuffer();
        String line;
        while((line = reader.readLine())!=null){
            buffer.append(line+"\n");
        }
        System.out.print(buffer.toString());
    }
}

```

（2）非合规的Linux注入命令

```
public class OrderLinuxFault {
    public static void main(String[] args) throws Exception{
        // 正常命令
        runOrder("ls");
        // 恶意命令
        runOrder(" ls & ifconfig");
    }
    private static void runOrder(String order) throws IOException, InterruptedException{
        Runtime rt = Runtime.getRuntime();
        Process proc = rt.exec(new String [] {"sh", "-c", "ls "+order});
        int result = proc.waitFor();
        if(result !=0){
            System.out.println("process error: "+ result);
        }
        InputStream in = (result == 0)? proc.getInputStream() : proc.getErrorStream();
        BufferedReader reader=new BufferedReader(new InputStreamReader(in));
        StringBuffer  buffer=new StringBuffer();
        String line;
        while((line = reader.readLine())!=null){
            buffer.append(line+"\n");
        }
        System.out.print(buffer.toString());
    }
}

```

（3）合规编码（对命令安全检查）

```
public class OrderFormat {
    public static void main(String[] args) throws Exception{
        runOrder("dir");
        runOrder("dir & ipconfig & net user budi budi /add & net localgroup Administrators admin /add");
    }
    private static void runOrder(String order) throws IOException, InterruptedException{
        if (!Pattern.matches("[0-9A-Za-z@.]+", order)){
            System.out.println("存在非法命令");
            return;
        }
        Runtime rt = Runtime.getRuntime();
        Process proc = rt.exec("cmd.exe /C "+order);
        int result = proc.waitFor();
        if(result !=0){
            System.out.println("process error: "+ result);
        }
        InputStream in = (result == 0)? proc.getInputStream() : proc.getErrorStream();
        BufferedReader reader=new BufferedReader(new InputStreamReader(in));
        StringBuffer  buffer=new StringBuffer();
        String line;
        while((line = reader.readLine())!=null){
            buffer.append(line+"\n");
        }
        System.out.print(buffer.toString());
    }
}

```

3、防范建议：
-------

√ 白名单  
√ 严格权限限制  
√ 采用命令标号

0x05 压缩炸弹（zip bomb）
===================

* * *

（1）合法输入：

```
普通压缩比文件normal.zip

```

（2）恶意输入：

```
高压缩比文件evil.zip

```

![](http://drops.javaweb.org/uploads/images/373d6629cdb0175e639c3e1e6ff8a988545c1d3d.jpg)

2、Java代码分析
==========

```
public class ZipFault {
    static final  int BUFFER = 512;
    public static void main(String[] args) throws IOException{
        System.out.println("正常压缩文件.......");
        checkzip("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\zip\\normal.zip");
        System.out.println("恶意压缩文件.......");
        checkzip("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\zip\\evil.zip");
    }
    private static void checkzip(String filename) throws IOException{
        BufferedOutputStream dest = null;
        FileInputStream fls = new FileInputStream(filename);
        ZipInputStream zis = new ZipInputStream(new BufferedInputStream(fls));
        ZipEntry entry;
        long begin = System.currentTimeMillis();   
        while ((entry = zis.getNextEntry()) != null){
            System.out.println("Extracting:" + entry+"\t解压后大小："+entry.getSize());
            int count;
            byte data[] = new byte[BUFFER];
            FileOutputStream fos = new FileOutputStream("D:/"+entry.getName());
            dest = new BufferedOutputStream(fos, BUFFER);
            while ((count = zis.read(data, 0, BUFFER))!=-1){
                dest.write(data,0, count);
            }
            dest.flush();
            dest.close();
        }
        zis.close();
        long end = System.currentTimeMillis();   
        System.out.println("解压缩执行耗时:" + (end - begin) + " 豪秒");
    }
}

```

运行结果：

```
正常压缩文件.......
Extracting:normal.txt   解压后大小：17496386
解压缩执行耗时:382 豪秒
恶意压缩文件.......
Extracting:evil.txt 解压后大小：2000000000
解压缩执行耗时:25911 豪秒

```

（2）合规代码

```
public class ZipFormat {
    static final  int BUFFER = 512;
    static final int TOOBIG = 0x640000;
    public static void main(String[] args) throws IOException{
        checkzip("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\zip\\normal.zip");
        checkzip("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\zip\\evil.zip");
    }
    private static void checkzip(String filename) throws IOException{
        BufferedOutputStream dest = null;
        FileInputStream fls = new FileInputStream(filename);
        ZipInputStream zis = new ZipInputStream(new BufferedInputStream(fls));
        ZipEntry entry;
        long begin = System.currentTimeMillis();   
        while ((entry = zis.getNextEntry()) != null){
            System.out.println("Extracting:" + entry+"\t解压后大小："+entry.getSize());
            if (entry.getSize() > TOOBIG){
                System.out.println("压缩文件过大");
                break;
            }
            if (entry.getSize() == -1){
                System.out.println("文件大小异常");
            }
            int count;
            byte data[] = new byte[BUFFER];
            FileOutputStream fos = new FileOutputStream("D:/"+entry.getName());
            dest = new BufferedOutputStream(fos, BUFFER);
            while ((count = zis.read(data, 0, BUFFER))!=-1){
                dest.write(data,0, count);
            }
            dest.flush();
            dest.close();
        }
        zis.close();
        long end = System.currentTimeMillis();   
        System.out.println("解压缩执行耗时:" + (end - begin) + " 豪秒");
    }
}

```

运行结果：

```
正常文件.........
Extracting:normal.txt   解压后大小：17496386
解压缩执行耗时:378 豪秒
===================
恶意文件.........
Extracting:evil.txt 解压后大小：2000000000
压缩文件过大
解压缩执行耗时:0 豪秒

```

3、防范建议：
-------

√ 解压前检查解压后文件大小

0x06 正则表达式注入
============

* * *

1、原理：
=====

（1）合法输入

```
search=error

```

拼接后

```
(.*? +public\\[\\d+\\]+.*error.*)

```

（2）恶意输入

```
search=.*)|(.*

```

拼接后

```
(.*? +public\\[\\d+\\]+.*.*)|(.*.*)

```

2、Java代码分析
----------

（1）非合规代码（未进行安全检查）

```
public class RegexFault {
    /**
     * 以行为单位读取文件，常用于读面向行的格式化文件
     */
    public static void readFileByLines(String filename,String search) {
        File file = new File(filename);
        BufferedReader reader = null;
        String regex ="(.*? +public\\[\\d+\\] +.*"+search+".*)";
        System.out.println("正则表达式："+regex);
        try {
            reader = new BufferedReader(new FileReader(file));
            String tempString = null;
            int line = 1;
            System.out.println("查找开始......");
            // 一次读入一行，直到读入null为文件结束
            while ((tempString = reader.readLine()) != null) {
                //System.out.println("line " + line + ": " + tempString);
                if(Pattern.matches(regex, tempString)){
                    // 显示行号
                    System.out.println("line " + line + ": " + tempString);
                }
                line++;
            }
            reader.close();
            System.out.println("查找结束....");
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e1) {
                }
            }
        }
    }
    public static void   main(String[] args){
        //正常输入
        readFileByLines("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\regex\\regex.log","error");
        //恶意输入
       readFileByLines("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\regex\\regex.log",".*)|(.*");
    }
}

```

运行结果：

```
正常输入......
正则表达式：(.*? +public\[\d+\] +.*error.*)
line 5: 10:48:08 public[48964] Backup failed with error: 19
============================
恶意输入......
正则表达式：(.*? +public\[\d+\] +.*.*)|(.*.*)
line 1: 10:47:03 private[423] Successful logout name: budi ssn: 111223333
line 2: 10:47:04 public[48964] Failed to resolve network service
line 3: 10:47:04 public[1] (public.message[49367]) Exited with exit code: 255
line 4: 10:47:43 private[423] Successful login name: budisploit ssn: 444556666
line 5: 10:48:08 public[48964] Backup failed with error: 19

```

（2）合规代码（进行安全检查）

```
public class RegexFormat {
    /**
     * 检测是否存在非法字符
     * @param search
     */
    private static boolean validate(String search){
        for (int i = 0; i< search.length(); i++){
            char ch = search.charAt(i);
            if(!(Character.isLetterOrDigit(ch) || ch ==' ' || ch =='\'')){
                System.out.println("存在非法字符，查找失败....");
                return false;
            }
        }
        return true;
    }
    /**
     * 以行为单位读取文件，常用于读面向行的格式化文件
     */
    public static void readFileByLines(String filename,String search) {
        if(!validate(search)){
            return;
        }
        File file = new File(filename);
        BufferedReader reader = null;
        String regex ="(.*? +public\\[\\d+\\] +.*"+search+".*)";
        System.out.println("正则表达式："+regex);
        try {
            reader = new BufferedReader(new FileReader(file));
            String tempString = null;
            int line = 1;
            System.out.println("查找开始......");
            // 一次读入一行，直到读入null为文件结束
            while ((tempString = reader.readLine()) != null) {
                //System.out.println("line " + line + ": " + tempString);
                if(Pattern.matches(regex, tempString)){
                    // 显示行号
                    System.out.println("line " + line + ": " + tempString);
                }
                line++;
            }
            reader.close();
            System.out.println("查找结束....");
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            if (reader != null) {
                try {
                    reader.close();
                } catch (IOException e1) {
                }
            }
        }
    }
    public static void   main(String[] args){
        //正常输入
        System.out.println("正常输入......");
        readFileByLines("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\regex\\regex.log","error");
        System.out.println("============================");
        //恶意输入
        System.out.println("恶意输入......");
       readFileByLines("D:\\JavaWorkspace\\TestInput\\src\\cn\\com\\budi\\regex\\regex.log",".*)|(.*");
    }
}

```

运行结果：

```
============================
正常输入......
正则表达式：(.*? +public\[\d+\] +.*error.*)
line 5: 10:48:08 public[48964] Backup failed with error: 19
============================
恶意输入......
存在非法字符，查找失败....

```

3、防范建议：
-------

√ 白名单

0x07 未净化输入
==========

* * *

（1）日志记录

正常输入：

```
budi

```

日志记录：

```
User Login Successed for: budi

```

恶意输入：

```
budi \nUser Login Successed for: administrator

```

日志记录：

```
User Login Failed for: budi 
User Login Successed for: administrator

```

（2）更新用户名

正常输入：

```
username=budi

```

SQL查询：

```
SELECT * FROM users WHRER id='budi';

```

恶意输入：

```
username=budi' or 'a'='a

```

SQL查询：

```
SELECT * FROM users WHRER id='budi' or 'a'='a';

```

2、Java代码分析
----------

（1）非合规代码（未安全检查）

```
public class LogFault {
    private static void writeLog( boolean isLogin,String username){
        if(isLogin){
            System.out.println("User Login Successed for: "+username);
        }else{
            System.out.println("User Login Failed for: "+username);
        }
    }
    public static void main(String[] args){
        String test1= "budi";
        System.out.println("正常用户登录成功后，记录日志.....");
        //正常用户登录成功后，记录日志
        writeLog(true, test1);
        //恶意用户登录失败，记录日志
        String test2 = "budi \nUser Login Successed for: administrator";
        System.out.println("恶意用户登录失败，记录日志.....");
        writeLog(false, test2);
    }
}

```

运行结果：

```
正常用户登录成功后，记录日志.....
User Login Successed for: budi
恶意用户登录失败，记录日志.....
User Login Failed for: budi 
User Login Successed for: administrator

```

（2）合规代码（安全检查）

```
public class LoginFormat {
    private static void writeLog( boolean isLogin,String username){
        if(!Pattern.matches("[A-Za-z0-9_]+", username)){
            System.out.println("User Login Failed for Unknow User");
        }else   if(isLogin){
            System.out.println("User Login Successed for: "+username);
        }else{
            System.out.println("User Login Failed for: "+username);
        }
    }
    public static void main(String[] args){
        String test1= "budi";
        System.out.println("正常用户登录成功后，记录日志.....");
        writeLog(true, test1);
        String test2 = "budi \nUser Login Successed for: administrator";
        System.out.println("恶意用户登录失败，记录日志.....");
        writeLog(false, test2);
    }
}

```

运行结果：

```
正常用户登录成功后，记录日志.....
User Login Successed for: budi
恶意用户登录失败，记录日志.....
User Login Failed for Unknow User

```

3、防范建议：
-------

√ 先检测用户输入，强烈建议直接拒绝带非法字符的数据

0x08 路径遍历
=========

* * *

　1、原理：
------

（1）正常输入：

```
john.txt

```

（2）恶意输入：

```
../../a.txt"

```

2、Java代码分析
----------

（1）非合规代码（未安全检查）

```
public class PathFault {
    public static void main(String[] args) throws IOException{
        System.out.println("合法输入.......");
        readFile("john.txt");
        System.out.println("\n恶意输入.......");
        readFile("../../a.txt");
    }
    private static void readFile(String path) throws IOException{
        File f = new File("F://passwords//"+path);
        String absPath = f.getAbsolutePath();
        FileOutputStream fls = new FileOutputStream(f);
        System.out.print("绝对路径："+absPath);
        if(!isInSecureDir(Paths.get(absPath))){
            System.out.println("->非安全路径");
            return;
        }
        System.out.print("->安全路径");
    }
    private static boolean isInSecureDir(Path path){
        if(!path.startsWith("F://passwords//")){
            return false;
        };
        return true;
    }
}

```

运行结果：

```
合法输入.......
绝对路径：F:\passwords\john.txt->安全路径
恶意输入.......
绝对路径：F:\passwords\..\..\a.txt->安全路径

```

（2）合规代码（先统一路径表示）

```
public class PathFormat {
    public static void main(String[] args) throws IOException{
        System.out.println("合法输入.......");
        readFile("john.txt");
        System.out.println("/n恶意输入.......");
        readFile("../../a.txt");
    }
    private static void readFile(String path) throws IOException{
        File f = new File("F://passwords//"+path);
        String canonicalPath = f.getCanonicalPath();
        System.out.println("绝对路径"+canonicalPath);
        FileInputStream fls = new FileInputStream(f);
        if(!isInSecureDir(Paths.get(canonicalPath))){
            System.out.print("非安全路径");
            return;
        }
        System.out.print("安全路径");
    }
    private static boolean isInSecureDir(Path path){
        if(!path.startsWith("F://passwords//")){
            return false;
        };
        return true;
    }
}

```

运行结果：

```
合法输入.......
绝对路径F:\passwords\john.txt->安全路径
恶意输入.......
绝对路径F:\a.txt->非安全路径

```

3、防范建议
------

√　严格的权限限制->安全管理器  
√　getCanonicalPath()在所有平台上对所有别名、快捷方式、符号链接采用统一的解析。

0x09 格式化字符串
===========

* * *

1、原理：
-----

（1）正常输入：

`11`

正常拼接：

```
System.out.printf("11 did not match! HINT: It was issued on %1$te rd of some month\n", c);

```

（2）恶意输入：

```
%1$tm或%1$te或%1$tY

```

恶意拼接：

```
System.out.printf("%1$tm did not match! HINT: It was issued on %1$te rd of some month\n", c);

```

2、Java代码分析
----------

（1）非合规代码：

```
public class DateFault {
    static Calendar c = new GregorianCalendar(2016, GregorianCalendar.MAY, 23);
    public static void main(String[] args){
        //正常用户输入
        System.out.println("正常用户输入.....");
        format("11");
        System.out.println("非正常输入获取月份.....");
        format("%1$tm");
        System.out.println("非正常输入获取日.....");
        format("%1$te");
        System.out.println("非正常输入获取年份.....");
        format("%1$tY");
    }
    private static void format(String month){
        System.out.printf(month+" did not match! HINT: It was issued on %1$te rd of some month\n", c);
    }
}

```

运行结果：

```
11 did not match! HINT: It was issued on 23rd of some month
非正常输入获取月份.....
05 did not match! HINT: It was issued on 23rd of some month
非正常输入获取日.....
23 did not match! HINT: It was issued on 23rd of some month
非正常输入获取年份.....
2016 did not match! HINT: It was issued on 23rd of some month

```

（2）合规代码：

```
public class DateFormat {
    static Calendar c = new GregorianCalendar(2016, GregorianCalendar.MAY, 23);
    public static void main(String[] args){
        //正常用户输入
        System.out.println("正常用户输入.....");
        format("11");
        System.out.println("非正常输入获取月份.....");
        format("%1$tm");
        System.out.println("非正常输入获取日.....");
        format("%1$te");
        System.out.println("非正常输入获取年份.....");
        format("%1$tY");
    }
    private static void format(String month){
        System.out.printf("%s did not match! HINT: It was issued on %1$te rd of some month\n", month, c);
    }
}

```

运行结果：

```
正常用户输入.....
11 did not match! HINT: It was issued on 
                      Exception in thread "main" java.util.IllegalFormatConversionException: e != java.lang.String

```

3、防范建议：
-------

√　对用户输入进行安全检查  
√　在格式字符串中，杜绝使用用户输入参数

0x0A 字符串标准化
===========

* * *

1、原理：
-----

（1）合法输入：

```
username=budi

```

（2）恶意输入一：

```
username=/><script>alert(1)</script>
username=/\uFE65\uFE64script\uFE65alert(1) \uFE64/script\uFE65

```

（3）恶意输入二：

```
username=A\uD8AB
username=A?

```

2、Java代码分析
----------

（1）非合规代码（先检查再统一编码）

```
public class EncodeFault {
    public static void main(String[] args){
        System.out.println("未编码的非法字符");
        check("/><script>alert(2)</script>");
        System.out.println("Unicode编码的非法字符");
        check("/\uFE65\uFE64script\uFE65alert(1) \uFE64/script\uFE65");
    }
    public static void check(String s){
        Pattern pattern = Pattern.compile("[<>]");
        Matcher matcher = pattern.matcher(s);
        if (matcher.find()){
            System.out.println(s+"->存在非法字符");
        }else{
            System.out.println(s+"->合法字符");
        }
        s = Normalizer.normalize(s, Form.NFC);
    }
}

```

运行结果：

```
未编码的非法字符
/><script>alert(2)</script>->存在非法字符
Unicode编码的非法字符
/﹥﹤script﹥alert(1) ﹤/script﹥->合法字符

```

（3）合规代码（先统一编码再检查）

```
public class EncodeFormat {
    public static void main(String[] args){
        System.out.println("未编码的非法字符");
        check("/><script>alert(2)</script>");
        System.out.println("Unicode编码的非法字符");
        check("/\uFE65\uFE64script\uFE65alert(1)\uFE64/script\uFE65");
    }
    public static void check(String s){
        s = Normalizer.normalize(s, Form.NFC);
        // 用\uFFFD替代非Unicode编码字符
        s = s.replaceAll("^\\p{ASCII}]", "\uFFFD");
        Pattern pattern = Pattern.compile("[<>]");
        Matcher matcher = pattern.matcher(s);
        if (matcher.find()){
            System.out.println(s+"->存在非法字符");
        }else{
            System.out.println(s+"->合法字符");
        }
    }
}

```

运行结果：

```
未编码的非法字符
/><script>alert(2)</script>->存在非法字符
Unicode编码的非法字符
/><script>alert(1)</script>->存在非法字符

```

3、防范建议：
-------

√　先按指定编码方式标准化字符串，再检查非法输入  
√　检测非法字符

0x0B 最后总结
=========

* * *

*   从安全角度看，移动应用与传统Web应用没有本质区别。
*   安全的Web应用必须处理好两件事：
    1.  处理好用户的输入（HTTP请求）
    2.  处理好应用的输出（HTTP响应）

参考文献: 《Java安全编码标准》