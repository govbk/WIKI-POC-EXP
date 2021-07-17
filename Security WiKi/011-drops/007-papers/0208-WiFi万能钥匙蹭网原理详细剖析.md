# WiFi万能钥匙蹭网原理详细剖析

0x00 wifi万能钥匙究竟有没有获取root之后偷偷上传密码？
=================================

* * *

本次测试版本号为3.2.3，首先通过可疑shell语句定位到疑问的问题代码：类名com.snda.wifilocating.f.ba

![Alt text](http://drops.javaweb.org/uploads/images/ea244024eaa9e6e2f714b2d8ce5b6de19b53d729.jpg)

这段代码的作用是在有了root权限的情况下 将系统的wifi.conf拷贝出来到应用自己的目录，并赋予其全局可读写权限（其实这是个漏洞了...）。

对其做cross-ref查找引用之后可以发现，该函数主要在两个地方被直接调用。一个是com.snda.wifilocating.e.av：

![Alt text](http://drops.javaweb.org/uploads/images/dbd3db1239f4ab1086743879fa92c43a85fecaf2.jpg)

这是一个api接口，主要功能是用于用户注册了之后备份自己的ap密码，同时在![Alt text](http://drops.javaweb.org/uploads/images/3d1b77e3ab77d40a1f32ecd9b8fb1d948fc98f27.jpg)WpaConfUploadActivity直接调用、GetBackupActivity中间接调用。第一个Activity在分析的版本中已经被从AndroidManifest中删除，而第二个Activity则是用户备份私有wifi时的对应的界面。这证实了备份的时候密码确实会被上传，而且从下文来看这个密码是完全可逆的。

不过在使用过程中，该应用并没有其他可疑的root行为操作。笔者打开了SuperSu的root执行监控，短暂的使用过程中也只发现了执行了上述的这一条命令。

![Alt text](http://drops.javaweb.org/uploads/images/f5ea3d703d4020e4a120aae3b2bb6cb7a7cacab6.jpg)

0x01 Android系统Wifi连接API概述
=========================

* * *

Android系统通过WifiManager类来提供对Wifi的扫描、连接接口。应用在请求相应权限之后可以扫描、连接、断开无线等。在连接无线功能中，客户端基本上只要指定SSID，Pre-shared-key（即密码），就可以用代码的方式连接无线。连接一个WPA(2)无线典型代码如下，

```
wifiConfiguration.SSID = "\"" + networkSSID + "\"";
wifiConfiguration.preSharedKey = "\"" + networkPass + "\"";
wifiConfiguration.hiddenSSID = true;
wifiConfiguration.status = WifiConfiguration.Status.ENABLED;
wifiConfiguration.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.TKIP);
wifiConfiguration.allowedGroupCiphers.set(WifiConfiguration.GroupCipher.CCMP);
wifiConfiguration.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.WPA_PSK);
wifiConfiguration.allowedPairwiseCiphers.set(WifiConfiguration.PairwiseCipher.TKIP);
wifiConfiguration.allowedPairwiseCiphers.set(WifiConfiguration.PairwiseCipher.CCMP);
wifiConfiguration.allowedProtocols.set(WifiConfiguration.Protocol.RSN);
wifiConfiguration.allowedProtocols.set(WifiConfiguration.Protocol.WPA);

int res = wifiManager.addNetwork(wifiConfiguration);
Log.d(TAG, "### add Network returned " + res);

```

0x02 wifi万能钥匙是怎么连接上无线的，密码从哪里来？
==============================

* * *

这也是争议较大的地方，首先该应用肯定是有云端存储了很多密码，因为应用会引导用户备份自己的密码，但这些密码有没有被滥用我们在客户端就不得而知了。在2月底的这次测试中，笔者先私有备份了自己建立的测试无线（注意不是分享），然后使用另外一个手机安装该客户端测试，该客户端的API请求接口并没有返回这个测试的无线的密码。不过这也可能只是个例说明不了什么，还是建议各位自行测试，但注意测试前清除保存的无线并给测试无线设定一个弱密码以免真的泄露了自己的密码。

无线密码获取分析
--------

* * *

回到正题，笔者通过代理拦截到了该应用获取wifi密码的请求。应用发送目标的ssid，mac信息向云端做查询，获取到的密码到本地之后并不是明文的，而是一个AES加密。首先为了证明其在本地最终还是会以明文出现，先取了个巧，没有去逆这个算法（虽然逆下也不会很困难），而是直接hook了系统添加无线的代码（回忆上文里密码就在NetworkConfiguration.preSharedKey里）。

部分HOOK代码：

```
            Class wifimgr = XposedHelpers.findClass(
                    "android.net.wifi.WifiManager",
                    lpparam.classLoader);
            XposedBridge.hookAllMethods(wifimgr, "addNetwork",
                    new XC_MethodHook() {

                        @Override
                        protected void beforeHookedMethod(MethodHookParam param)
                                throws Throwable {
                            WifiConfiguration configuration = (WifiConfiguration) param.args[0];
                            if(configuration.preSharedKey != null)
                            {

                                Log.e("FUCKFUCK", "psk: "+configuration.preSharedKey);
                            }
                        }
                    });

            XposedBridge.hookAllMethods(wifimgr, "updateNetwork",
                    new XC_MethodHook() {

                        @Override
                        protected void beforeHookedMethod(MethodHookParam param)
                                throws Throwable {
                            WifiConfiguration configuration = (WifiConfiguration) param.args[0];
                            if(configuration.preSharedKey != null)
                            {

                                Log.e("FUCKFUCK", "psk: "+configuration.preSharedKey);
                            }
                        }
                    });
            }

```

这是一个万能钥匙上传wifi ssid以及mac以请求密码的截图：

![Alt text](http://drops.javaweb.org/uploads/images/d18dd596a8a084b4aae587f95ba4716f8a860541.jpg)

响应截图：

![Alt text](http://drops.javaweb.org/uploads/images/560bd1d82c77c8189e71ac433775a0c0cefc25ec.jpg)

密码以AES可逆加密的形式通过pwd这个json key传递了回来。

同时，在其尝试通过这个密码连接目标无线的时候，本地hook模块也获取到了真实的明文密码：

![Alt text](http://drops.javaweb.org/uploads/images/ee04728e4ace19dc68767e89221a98ece4d52f76.jpg)

个人备份分析
------

* * *

而个人备份模块，也就是直接会读取wifi.conf的模块，是通过findprivateap和saveprivateap这两个json api method进行，具体的http请求逻辑在com.snda.wifilocating.e.av中可以找到，这个类也基本上囊括了所有万能钥匙的api请求逻辑。

备份时的请求：把整个wifi.conf全部上传了上去。![Alt text](http://drops.javaweb.org/uploads/images/e4cd4e857b6d5e359eb43e4eed6e075cda45f59d.jpg)

而恢复备份时，只是将密码从云端拖了下来。

其他连接方式分析
--------

* * *

除此之外，Wifi万能钥匙还自带了2000条的数据库记录在ap8.db中，记录了常见的弱密码。![Alt text](http://drops.javaweb.org/uploads/images/8a294ac14c1f1d09503392482b0375fb9a14445f.jpg)例如![Alt text](http://drops.javaweb.org/uploads/images/7df30171b91472cb5fc59355cdfafaa2cf68158f.jpg)

这些密码用在所谓的“深度连接”功能中，其实按代码逻辑来看就是一个wifi密码爆破，每次在字典中尝试10个密码。看下logcat就很明显。

```
I/wpa_supplicant( 884): wlan0: WPA: 4-Way Handshake failed - pre-shared key may be incorrect
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-TEMP-DISABLED id=1 ssid="aaaaaaaaa" auth_failures=2 duration=20
D/SupplicantStateTracker( 818): Failed to authenticate, disabling network 1
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-REENABLED id=1 ssid="aaaaaaaaa"
I/wpa_supplicant( 884): wlan0: Trying to associate with 5c:a4:8a:4d:09:a0 (SSID='aaaaaaaaa' freq=2412 MHz)
I/wpa_supplicant( 884): wlan0: Associated with 5c:a4:8a:4d:09:a0
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-DISCONNECTED bssid=5c:a4:8a:4d:09:a0 reason=23
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-TEMP-DISABLED id=1 ssid="aaaaaaaaa" auth_failures=1 duration=10
I/wpa_supplicant( 884): wlan0: WPA: 4-Way Handshake failed - pre-shared key may be incorrect
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-TEMP-DISABLED id=1 ssid="aaaaaaaaa" auth_failures=2 duration=20
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-REENABLED id=1 ssid="aaaaaaaaa"
I/wpa_supplicant( 884): wlan0: Trying to associate with 5e:aa:aa:aa:aa:aa (SSID='aaaaaaaaa' freq=2462 MHz)
I/wpa_supplicant( 884): wlan0: Associated with 5e:aa:aa:aa:aa:aa
D/dalvikvm(13893): GC_CONCURRENT freed 356K, 4% free 18620K/19220K, paused 9ms+2ms, total 29ms
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-DISCONNECTED bssid=5e:aa:aa:aa:aa:aa reason=23
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-TEMP-DISABLED id=1 ssid="aaaaaaaaa" auth_failures=1 duration=10
I/wpa_supplicant( 884): wlan0: WPA: 4-Way Handshake failed - pre-shared key may be incorrect
I/wpa_supplicant( 884): wlan0: CTRL-EVENT-SSID-TEMP-DISABLED id=1 ssid="aaaaaaaaa" auth_failures=2 duration=20

```

Wifi密码加解密分析
-----------

* * *

当然真正去逆向加密代码也不是很困难，简单的搜寻即可得到解密代码：（部分直接从反编译的代码中抠出，风格未做修饰）

```
public class AESFun {

      String a =//略去;
      String b = //略去;
      String c = //略去;

      Cipher cipher;
      IvParameterSpec spec;
      SecretKeySpec secretKeySpec;
      void init() throws NoSuchAlgorithmException, NoSuchPaddingException {
            spec = new IvParameterSpec(b.getBytes());
            secretKeySpec = new SecretKeySpec(a.getBytes(), "AES");
            cipher = Cipher.getInstance("AES/CBC/NoPadding");
      }

      public final String b(String arg7) throws Exception {
        byte[] array_b1;
        byte[] array_b = null;
        int i = 2;
        String string = null;
        {
            try {
                this.cipher.init(2, secretKeySpec, spec);
                Cipher cipher = this.cipher;
                if(arg7 != null && arg7.length() >= i) {
                    int i1 = arg7.length() / 2;
                    array_b = new byte[i1];
                    int i2;
                    for(i2 = 0; i2 < i1; ++i2) {
                        String string1 = arg7.substring(i2 * 2, i2 * 2 + 2);
                        array_b[i2] = ((byte)Integer.parseInt(string1, 0x10));
                    }
                }

                array_b1 = cipher.doFinal(array_b);
            }
            catch(Exception exception) {
                StringBuilder stringBuilder = new StringBuilder("[decrypt] ");
                string = exception.getMessage();
                StringBuilder stringBuilder1 = stringBuilder.append(string);
                string = stringBuilder1.toString();
                exception.printStackTrace();
                throw new Exception(string);
            }

            string = new String(array_b1);
        }

        return string;
    }

```

将API请求中获取的16进制pwd字段代入解密程序，得到的结果是如下格式：[length][password][timestamp]的格式，如下图所示，中间就是目标无线明文密码。

![Alt text](http://drops.javaweb.org/uploads/images/1325c3cad5ddfe888b722d3d625c8f99dec06699.jpg)

此外接口请求中有一个sign字段是加签，事实上是把请求参数合并在一起与预置的key做了个md5，细节就不赘述了。这两个清楚了之后其实完全可以利用这个接口实现一个自己的Wifi钥匙了。

0x03 总结
=======

* * *

此版本的WiFi万能钥匙不会主动把root之后手机保存的无线密码发向云端但在做备份操作（安装时默认勾选自动备份）时会发送，当有足够的用户使用该应用时，云端就拥有了一个庞大的WiFi数据库，查询WiFi的密码时，应用会发送目标的ssid，mac信息向云端做查询，获取到的密码到本地之后并不是明文的，而是一个AES加密，本地解密后连接目标WiFi。同时内置了常见的2000条WiFi弱口令，在云端没有该WiFi密码的时候，可以尝试爆破目标的密码。