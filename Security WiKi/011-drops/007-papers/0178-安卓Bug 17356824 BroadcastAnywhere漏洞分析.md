# 安卓Bug 17356824 BroadcastAnywhere漏洞分析

0x00 背景
-------

* * *

2014年8月，retme分析了Android修复的一个漏洞，并命名为launchAnyWhere[1](http://static.wooyun.org/drops/20141114/201411142349151600381e6491632fbf4585e026a16460987036550cb34.rar)

在调试这个漏洞的时候，我发现Settings应用还存在一个类似漏洞，并在9月报告给了Android Security Team，标题为，Privilege escalation vulnerability in settings app of android 4.0 to 4.4 (leads to phishing sms), 并且很快得到了确认，Android官方也给了致谢[2](http://drops.wooyun.org/wp-content/uploads/2014/11/file00013.png)：

![enter image description here](http://drops.javaweb.org/uploads/images/d2e40df57d002d96d3dc53cd978bb903eaecdeff.jpg)

这个漏洞的Android ID是17356824，影响4.0.1到4.4.4之间的版本，时间跨度从2011年到2014年，应该说影响面非常广，根据今年11月Google的统计，这个区间的Android设备在全球的占比大约为90%。

![a](http://drops.javaweb.org/uploads/images/62104b819058e8caf05470d864a51bd3b05e4cc6.jpg)

retme给该漏洞起了一个很给力的名字broadcastAnywhere，与launchAnywhere相比，这两个漏洞的相同点在于：

1.  都是利用了addAccount这个机制，一个恶意app通过注册为account的authenticator并处理某账号类型，然后发送intent给settings app，让其添加该特定类型的账号。
    
2.  都是利用settings这个应用具有SYSTEM权限，诱使settings来发送一个高权限的intent。
    

不同点在于：

1.  本质原理不同：一个是恶意app返回一个intent被settings launch，另外一个是settings 发出一个pendingintent给恶意app，而恶意app利用pendingintent的特点来修改pendingitent的action与extras，并以settings的身份发出。
    
2.  漏洞代码位置不同：一个是accountmanger中，一个是settings中
    
3.  后果不同：launchAnywhere是以system权限启动activity，而broadcastAnywhere是一个system权限发送 broadcast。前者往往需要界面，而后者不需要界面。
    

本文是对retme分析的一个补充，同时也给大家分享一下在挖掘这个漏洞中的一些经验，当然为了完整性，我也尽量系统地描述相关的内容。由于时间仓促，难免有遗漏与不当之处，请各位不吝指正。

0x01 PendingIntent的风险
---------------------

* * *

关于PendingIntent，简单理解是一种异步发送的intent，通常被使用在通知Notification的回调，短消息SmsManager的回调和警报器AlarmManager的执行等等，是一种使用非常广的机制。对PendingIntent的深入分析，可以参考该文【4】：

但是关于PendingIntent的安全意义，讨论不多，在官方的开发文档中，特别注明：【5】：

By giving a PendingIntent to another application, you are granting it the right to perform the operation you have specified as if the other application was yourself (with the same permissions and identity). As such, you should be careful about how you build the PendingIntent: almost always, for example, the base Intent you supply should have the component name explicitly set to one of your own components, to ensure it is ultimately sent there and nowhere else.

从上面的英文来看，大意是当A设定一个原始Intent（base intent）并据此创建PendingIntent，并将其交给B时，B就可以以A的身份来执行A预设的操作（发送该原始Intent），并拥有A同样的权限与ID。因此，A应当小心设置这个原始Intent，务必具备显式的Component，防止权限泄露。

权限泄露的风险在于，B得到这个PendingIntent后，还可以对其原始Intent进行有限的修改，这样就可能以A的权限与ID来执行A未预料的操作。

但实际上，这里的限制很多，甚至有点鸡肋。因为本质上这个修改是通过Intent.fillIn来实现的，因此可以查看fillin的源码：

如下面源码所示，B可以修改的数据可以分成两类：

1 action，category，data，clipdata，package这些都可以修改，只要原来为空，或者开发者设置了对应的标志。

2 但selector与component，不论原来是否为空，都必须由开发者设置显式的标志才能修改

```
public int fillIn(Intent other, int flags) {
    int changes = 0;
    if (other.mAction != null
            && (mAction == null || (flags&FILL_IN_ACTION) != 0)) {//当本action为空或者开发者设置了FILL_IN_ACTION标志时，可以修改action
        mAction = other.mAction;
        changes |= FILL_IN_ACTION;
    }
    if ((other.mData != null || other.mType != null)
            && ((mData == null && mType == null)
                    || (flags&FILL_IN_DATA) != 0)) {//类似action，需要data与type同时为空
        mData = other.mData;
        mType = other.mType;
        changes |= FILL_IN_DATA;
    }
    if (other.mCategories != null
            && (mCategories == null || (flags&FILL_IN_CATEGORIES) != 0)) {//类似action
        if (other.mCategories != null) {
            mCategories = new ArraySet<String>(other.mCategories);
        }
        changes |= FILL_IN_CATEGORIES;
    }
    if (other.mPackage != null
            && (mPackage == null || (flags&FILL_IN_PACKAGE) != 0)) {//类似action
        // Only do this if mSelector is not set.
        if (mSelector == null) {
            mPackage = other.mPackage;
            changes |= FILL_IN_PACKAGE;
        }
    }
    // Selector is special: it can only be set if explicitly allowed,
    // for the same reason as the component name.
    if (other.mSelector != null && (flags&FILL_IN_SELECTOR) != 0) {//必须设置了FILL_IN_SELECTOR才可以修改selector
        if (mPackage == null) {//selector与package是互斥的
            mSelector = new Intent(other.mSelector);
            mPackage = null;
            changes |= FILL_IN_SELECTOR;
        }
    }
    if (other.mClipData != null
            && (mClipData == null || (flags&FILL_IN_CLIP_DATA) != 0)) {//类似action
        mClipData = other.mClipData;
        changes |= FILL_IN_CLIP_DATA;
    }
    // Component is special: it can -only- be set if explicitly allowed,
    // since otherwise the sender could force the intent somewhere the
    // originator didn't intend.
    if (other.mComponent != null && (flags&FILL_IN_COMPONENT) != 0) {//必须开发者设置FILL_IN_COMPONENT才可以修改component
        mComponent = other.mComponent;
        changes |= FILL_IN_COMPONENT;
    }
    mFlags |= other.mFlags;
    if (other.mSourceBounds != null
            && (mSourceBounds == null || (flags&FILL_IN_SOURCE_BOUNDS) != 0)) {
        mSourceBounds = new Rect(other.mSourceBounds);
        changes |= FILL_IN_SOURCE_BOUNDS;
    }
    if (mExtras == null) {//Extras数据被合并
        if (other.mExtras != null) {
            mExtras = new Bundle(other.mExtras);
        }
    } else if (other.mExtras != null) {
        try {
            Bundle newb = new Bundle(other.mExtras);
            newb.putAll(mExtras);
            mExtras = newb;
        } catch (RuntimeException e) {

```

而一般开发者都不会去显式设置这个标志（教材里没人这么教），所以通常情况下，B无法修改原始Intent的Component，而仅当原始Intent的action为空时，可以修改action。

所以大多数情况下，PendingIntent的安全风险主要发生在下面两个条件同时满足的场景下：

1.  构造PendingIntent时的原始Intent既没有指定Component，也没有指定action
2.  将PendingIntent泄露给第三方

原因是，如果原始Intent的Component与action都为空（“双无”Intent），B就可以通过修改action来将Intent发送向那些声明了intent filter的组件，如果A是一个有高权限的APP（如settings就具有SYSTEM权限），B就可以以A的身份做很多事情。

当然上面描述的是大多数情况。一些极端的情况下，比如某些情况下B虽然无法修改action将Intent发送到其他组件，但依然可以放入额外的数据，如果该组件本身接收数据时未考虑周全，也是存在风险的。

0x02 Settings中的PendingIntent漏洞
------------------------------

* * *

如果你阅读过retme关于launchAnywhere的分析【1】，就会了解Settings的addAccount机制：一个恶意APP可以注册一种独有的账号类型并成为该类型账号的认证者（Authenticator），通过发送Intent来促使Settings添加该类型账号时，Settings将调用恶意APP提供的接口。而这个过程，就不幸将一个“双无”PendingIntent发给了恶意APP。

看看安卓4.4.4的Settings中有漏洞的源码：可见一个mPendingIntent是通过new Intent()构造原始Intent的，所以为“双无”Intent，这个PendingIntent最终被通过AccountManager.addAccount方法传递给了恶意APP接口：

![enter image description here](http://drops.javaweb.org/uploads/images/955130cc044e075ff466cbc0c77816cd50053932.jpg)

在Android 5.0的源码中，修复方法是设置了一个虚构的Action与Component https://android.googlesource.com/platform/packages/apps/Settings/+/37b58a4%5E%21/#F0

![enter image description here](http://drops.javaweb.org/uploads/images/818026cb23ab390f420eb722294748d0b6c0cb0c.jpg)

最初报告这个漏洞给Android时，用的伪造短信的POC，也是retme博客中演示的。例如可以伪造10086发送的短信，这与收到正常短信的表象完全一致（并非有些APP申请了WRITE_SMS权限后直接写短信数据库时无接收提示）。后来又更新了一个Factory Reset的POC，可以强制无任何提示将用户手机恢复到出厂设置，清空短信与通信录等用户数据，恶意APP的接口代码片段如下：

```
@Override
public Bundle addAccount(AccountAuthenticatorResponse response, String accountType, String authTokenType, String[] requiredFeatures, Bundle options) throws NetworkErrorException {
//这里通过getParcelable(“pendingintent”)就获得了settings传过来的“双无”PendingIntent：

  PendingIntent test = (PendingIntent)options.getParcelable("pendingIntent"); 

  Intent newIntent2 = new Intent("android.intent.action.MASTER_CLEAR");
  try {
            test.send(mContext, 0, newIntent2, null, null);
  } catch (CanceledException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
  }

```

该攻击在一些国内的主流手机中测试成功。大多数情况下，攻击是自动的，无需用户干预，过程与launchAnywhere类似。

有意思的是，在小米手机中，如果用户未添加小米账号，那么该攻击需要用户干预才能成功：原因是MIUI修改了Settings程序，当添加账号时，对任意账号类型，除了对应的authenticator外，系统还提供“小米账号”供选择，由于不是单选，系统会弹出一个对话框供用户选择：

![enter image description here](http://drops.javaweb.org/uploads/images/d10a0b5cc4ef69519bfe09ff0e7bbd1be39b2566.jpg)

当然如果用户已经添加了小米账号，就只剩下一个选项，攻击就无需人工干预了。这部分的具体流程可以参考Android源码以及MIUI代码中Settings应用的ChooseAccountActivity.java部分，这里不再赘述。

另外，按照google官方文档，一个app要注册成为账号的authenticator，需要一个权限：android.permission.AUTHENTICATE_ACCOUNTS。 retme博客中的POC也申请了这些权限。但实际测试中发现，这个权限可以去掉。所以这个漏洞等同于一个无任何权限APP的提权漏洞。

0x03 类似漏洞的发现
------------

* * *

前面提到，这种漏洞大多数情况下，仅对“双无”Intent（无Action无Component）构造的PendingIntent有效。所以我们主要关注类似的场景。

一个发现类似漏洞的简单策略如下：

第一步：在一个method中，如果调用了下面方法之一，那么代表创建了PendingIntent，设定Priority为低：

```
static PendingIntent    getActivities(Context context, int requestCode, Intent[] intents, int flags)
static PendingIntent    getActivities(Context context, int requestCode, Intent[] intents, int flags, Bundle options)
static PendingIntent    getActivity(Context context, int requestCode, Intent intent, int flags)
static PendingIntent    getActivity(Context context, int requestCode, Intent intent, int flags, Bundle options)
static PendingIntent    getBroadcast(Context context, int requestCode, Intent intent, int flags)
static PendingIntent    getService(Context context, int requestCode, Intent intent, int flags)
public PendingIntent   createPendingResult(int requestCode, Intent data, int flags) 

```

第二步，分析该method中调用的方法，如果没有调用下面的方法，代表未设置Component，将Priority调高到中：

```
Intent(Context packageContext, Class<?> cls)
Intent(String action, Uri uri, Context packageContext, Class<?> cls)
Intent  setClass(Context packageContext, Class<?> cls)
Intent  setClassName(Context packageContext, String className)
Intent  setClassName(String packageName, String className)
Intent  setComponent(ComponentName component)

```

第三步，再分析该method中调用的方法，如果没有调用下面的方法，代表未设置action，很可能原始intent是“双无”intent，那么将Priority设置为高：

```
Intent(String action)
Intent(String action, Uri uri)
Intent  setAction(String action)

```

该策略出奇地简单，也会有一些误报。但实际执行该策略非常有效且不会有漏报。除了发现上面的Settings中的漏洞外，还可以发现Android源码（5.0版本也未修复）其他一些类似的地方，例如：

https://android.googlesource.com/platform/frameworks/opt/telephony/+/android-5.0.0_r6/src/java/com/android/internal/telephony/gsm/GsmServiceStateTracker.java

![enter image description here](http://drops.javaweb.org/uploads/images/90fe6ef72f1954e706448eb071ecc2f3b2662aa5.jpg)

这里，尽管普通APP无法访问其他APP的notification，但利用AccessiblyService或者 NotificationListenerService，一个APP可能可以获取其他notification中的pendingintent，导致权限泄露。

https://android.googlesource.com/platform/frameworks/base/+/android-5.0.0_r6/keystore/java/android/security/KeyChain.java

![enter image description here](http://drops.javaweb.org/uploads/images/9cfd2920a5b17b67f1ce97f61f448390e8707622.jpg)

这里，由于该PendingIntent通过一个非显式的Intent发送，恶意APP可以劫持这个Intent，从而导致权限泄露。

另外一种动态分析的方法是通过dumpsys来观察当前系统中的PendingIntent Record，例如5.0修复后，观察到的Settings发送的PendingIntent有了act与cmp属性，而5.0之前的为空。

![enter image description here](http://drops.javaweb.org/uploads/images/14ef3a59520efc737c4a713512b7944edd713549.jpg)

0x04 参考资料
---------

* * *

【1】launchAnywher：http://retme.net/index.php/2014/08/20/launchAnyWhere.html

【2】安卓官方致谢：https://source.android.com/devices/tech/security/acknowledgements.html

【3】broadcastAnywhere：http://retme.net/index.php/2014/11/14/broadAnywhere-bug-17356824.html

【4】PendingIntent的深入分析：http://my.oschina.net/youranhongcha/blog/196933

【5】官方对PendingIntent的解释：http://developer.android.com/reference/android/app/PendingIntent.html