# APK签名校验绕过

0x01 Android签名机制
================

* * *

将APK重命名为zip文件，然后可以看到有个META-INF的文件夹，里面有三个文件，分别名为MANIFEST.MF、CERT.SF和CERT.RSA，这些就是使用signapk.jar生成的签名文件。

1、 MANIFEST.MF文件：

程序遍历update.apk包中的所有文件(entry)，对非文件夹非签名文件的文件，逐个生成SHA1的数字签名信息，再用Base64进行编码。具体代码见这个方法：

```
private static Manifest addDigestsToManifest(JarFile jar)

```

关键代码是

```
for (JarEntry entry: byName.values()) {
     String name = entry.getName();
     if (!entry.isDirectory() && !name.equals(JarFile.MANIFEST_NAME) &&
         !name.equals(CERT_SF_NAME) && !name.equals(CERT_RSA_NAME) &&
         (stripPattern == null ||!stripPattern.matcher(name).matches())){
         InputStream data = jar.getInputStream(entry);
         while ((num = data.read(buffer)) > 0) {
         md.update(buffer, 0, num);
       }
       Attributes attr = null;
       if (input != null) attr = input.getAttributes(name);
       attr = attr != null ? new Attributes(attr) : new Attributes();
       attr.putValue("SHA1-Digest", base64.encode(md.digest()));
       output.getEntries().put(name, attr);
    }
}

```

之后将生成的签名写入MANIFEST.MF文件。关键代码如下：

```
Manifest manifest = addDigestsToManifest(inputJar);
je = new JarEntry(JarFile.MANIFEST_NAME);
je.setTime(timestamp);
outputJar.putNextEntry(je);
manifest.write(outputJar);

```

2、 生成CERT.SF文件：

对前一步生成的Manifest，使用SHA1-RSA算法，用私钥进行签名。关键代码如下：

```
Signature signature = Signature.getInstance("SHA1withRSA");
signature.initSign(privateKey);
je = new JarEntry(CERT_SF_NAME);
je.setTime(timestamp);
outputJar.putNextEntry(je);
writeSignatureFile(manifest,
new SignatureOutputStream(outputJar, signature));

```

3、 生成CERT.RSA文件：

生成MANIFEST.MF没有使用密钥信息，生成CERT.SF文件使用了私钥文件。那么我们可以很容易猜测到，CERT.RSA文件的生成肯定和公钥相关。 CERT.RSA文件中保存了公钥、所采用的加密算法等信息。核心代码如下：

```
je = new JarEntry(CERT_RSA_NAME);
je.setTime(timestamp);
outputJar.putNextEntry(je);
writeSignatureBlock(signature, publicKey, outputJar);

```

在程序中获取APK的签名时，通过signature方法进行获取，如下：

```
packageInfo = manager.getPackageInfo(pkgname,PackageManager.GET_SIGNATURES);
signatures = packageInfo.signatures;
for (Signature signature : signatures) {
    builder.append(signature.toCharsString());
}
signature = builder.toString();

```

所以一般的程序就是在代码中通过判断signature的值，来判断APK是否被重新打包过。

0x02 签名绕过方式
===========

* * *

在讲签名绕过的方式前，需要先明确DEX校验和签名校验：

1.将apk以压缩包的形式打开删除原签名后，再签名，安装能够正常打开，但是用IDE（即apk改之理，会自动反编译dex）工具二次打包，却出现非正常情况的，如：闪退/弹出非正版提示框。可以确定是dex文件的校验

2、将apk以压缩包的形式打开删除原签名再签名，安装之后打开异常的，则基本可以断定是签名检验。如果在断网的情况下同样是会出现异常，则是本地的签名检验；如果首先出现的是提示网络没有连接，则是服务器端的签名校验.

2.1.Java层校验
-----------

获取签名信息和验证的方法都写在android的java层。实例如下：

1、使用APKIDE反编译APK，不做任何操作，然后直接回编译，安装后运行,提示如下：

![enter image description here](http://drops.javaweb.org/uploads/images/a4f10d28ecc84b93162caef09254e2434b8e8a4f.jpg)

2、在APKIDE中搜索signatures(或者搜索错误提示),定位到签名验证的代码处。

![enter image description here](http://drops.javaweb.org/uploads/images/1930503bbda85ad3bd5b55c9b896321c8988a40d.jpg)

3、此处就是获取签名的，然后找程序判断签名的地方，进行修改，如下图，if-nez是进行判断的地方，将ne修改为eq。即if-eqz v2, :cond_0。则程序就可以绕过本地的签名交易。

![enter image description here](http://drops.javaweb.org/uploads/images/f95e608f75394ff9bc6690b4177781f790a8937f.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/9d74da3064aa86ff4d2b05ca97595ac19b48cda1.jpg)

2.2.NDK校验
---------

将关键代码放到so中，在底层获取签名信息并验证。因为获取和验证的方法都封闭在更安全的so库里面，能够起到一定意义上的保护作用。实例如下：

1、使用APKIDE反编译APK，不做任何操作，然后直接回编译，安装后运行,程序直接退出，无任何提示。

2、在APKIDE中搜索signatures(或者搜索错误提示),定位到签名验证的代码处。

![enter image description here](http://drops.javaweb.org/uploads/images/934dad05caa99cf597988146dd3d6f954c8c80e6.jpg)

3、使⽤用JD-GUI打开AppActivity，可以看到,此处是获取包名,然后进⾏行MD5计算。

![enter image description here](http://drops.javaweb.org/uploads/images/8c0349e8b7d921e6a297e7f427202d8b29ad0a2c.jpg)

4.在程序中搜索getSignature,发现并没有调⽤用此函数的地⽅方,猜测在so⽂文件中,搜索loadLibrary。

![enter image description here](http://drops.javaweb.org/uploads/images/9c673a5987eeac5b65822cb1d761886c5a88cf42.jpg)

5.在代码中可以查找,可以找到调⽤用的是libcocos2dcpp.so

6.使⽤用IDA打开libcocos2dcpp.so,然后搜索getSiganture,找到调⽤用此函数的地方。

![enter image description here](http://drops.javaweb.org/uploads/images/3ad6d93c59505a3a5e1268b29caf3efc678161c4.jpg)

从代码中可以看到,此函数调⽤用了org.cocos2dx.cpp.AppActivity.getSignature

![enter image description here](http://drops.javaweb.org/uploads/images/26c8bd07e3252d1b04935cbc28272347f32e170a.jpg)

7、查看F5代码,发现此函数是判断签名的函数,然后我们双击此函数的调⽤者,部分代码如下。

![enter image description here](http://drops.javaweb.org/uploads/images/675b13ff5f4d0d9f4d8eb79817aa641cc334b2aa.jpg)

8、从上图可以看出,只需要修改BEQ loc_11F754,让其不跳转到jjni——>error,就可以绕过签名校验。 查看HEX,使⽤010editor跳到0011F73E,修改D0为D1。成功绕过签名校验。

![enter image description here](http://drops.javaweb.org/uploads/images/362802f61195f0a7ac54d3c7555e04c4384c7338.jpg)

2.3.服务器验证
---------

在android的java层获取签名信息，上传服务器在服务端进行签名然后返回验证结果。

如下图，网络验证时，如果网络没连接，一般都会提示错误。

![enter image description here](http://drops.javaweb.org/uploads/images/26ea02c25ca25865caeaab8ef00b5b62bdeb8d7d.jpg)

既然是网络验证，肯定要把验证信息发送到服务端，然后进行验证，先看个简单的实例，下次会有个难度大的。

1、手机配置好抓包，然后抓包。第一种图是正常的APK的时候的数据包，第二个图是反编译的APK的数据包，通过对比，发现cookie中的public_key不一样，那么我们替换一下，发现可以正常使用APK的功能了。

![enter image description here](http://drops.javaweb.org/uploads/images/669431b81a2f6efb099d5133d559ab5bc7fb31d9.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/1be4de52340b28758490642d884b3375b8c68792.jpg)

2、将正确的public_key添加到APK中。打开反编译的代码，搜索signatures，定位到签名的代码。

![enter image description here](http://drops.javaweb.org/uploads/images/6b325600e229bf315b8519e27f5437ce225033b8.jpg)

可以看到，代码将signatures的值传递到V4中，然后传递到Utils->mPublicKey函数中，于是我们将正确的public_key传给V4。

![enter image description here](http://drops.javaweb.org/uploads/images/92fc174363447dc6da6b21f1e1e5a7a4d844531a.jpg)

然后重新打包，重新安装就可以了。

0x03.总结
=======

* * *

java层的校验很容易就可以破解掉，在so层实现校验相对来说分析会更难点，而网络验证，如果仅仅是字符串的比较，那么也很容易破解掉。

码子码的太累了。。

后面还有几篇正在写的文章，包括so分析等等。

摘抄： http://www.blogjava.net/zh-weir/archive/2011/07/19/354663.html