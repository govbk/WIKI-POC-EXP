# Browser Security-同源策略、伪URL的域

### 同源策略

* * *

#### 同源策略的文档模型

同源策略（Same Origin policy，SOP），也称为单源策略（Single Origin policy），它是一种用于Web浏览器编程语言（如JavaScript和Ajax）的安全措施，以保护信息的保密性和完整性。

同源策略能阻止网站脚本访问其他站点使用的脚本，同时也阻止它与其他站点脚本交互。

| 原始资源 | 要访问的资源 | 非IE浏览器 | IE浏览器 |
| :-- | :-- | :-: | :-: |
| http://example.com/a/ | http://example.com/b/ | 可以访问 | 可以访问 |
| http://example.com/ | http://www.example.com/ | 主机不匹配 | 主机不匹配 |
| http://example.com/a/ | https://example.com/a/ | 协议不匹配 | 协议不匹配 |
| http://example.com:81/ | http://example.com/ | 端口不匹配 | 可以访问 |

同源策略一开始是为了管理DOM之间的访问，后来逐渐扩展到Javascript对象，但并非是全部。

例如非同源的脚本之间可以调用location.assign()和location.replace()。

同源策略在提高了安全性，但同时也降低了灵活性。

例如很难将login.example.com与payments.example.com两个域之间的数据可以方便的传送。

介绍两种解决方式：document.domain和postMessage()。

javascript允许子域之间使用顶级域名。

例如login.example.com和payments.example.com都可以进行如下设置：

```
document.domain="example.com"

```

设置这个属性之后，子域之间可以方便的通信，需注意的是协议和端口号必须相同。

<table cellspacing="0" class="drops_data_table" style="box-sizing: border-box; border-collapse: separate; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><font color="#4241FF" style="box-sizing: border-box;">原始资源</font></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><font color="#4241FF" style="box-sizing: border-box;"></font></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><font color="#4241FF" style="box-sizing: border-box;">访问的资源</font></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><font color="#4241FF" style="box-sizing: border-box;"></font></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><font color="#4241FF" style="box-sizing: border-box;">结果</font></td></tr><tr style="box-sizing: border-box;"><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><b style="box-sizing: border-box; font-weight: 700;">URL</b></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><b style="box-sizing: border-box; font-weight: 700;">document.domain</b></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><b style="box-sizing: border-box; font-weight: 700;">URL</b></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><b style="box-sizing: border-box; font-weight: 700;">document.domain</b></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"></td></tr><tr style="box-sizing: border-box;"><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.example.com/</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://payments.example.com/</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">可以访问</td></tr><tr style="box-sizing: border-box;"><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.example.com/</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">https://payments.example.com/</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">协议不匹配</td></tr><tr style="box-sizing: border-box;"><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://payments.example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://example.com/</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><b style="box-sizing: border-box; font-weight: 700;">(不设置)</b></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">拒绝访问</td></tr><tr style="box-sizing: border-box;"><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.example.com/</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);"><b style="box-sizing: border-box; font-weight: 700;">(不设置)</b></td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">http://www.example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">example.com</td><td valign="top" style="box-sizing: border-box; padding: 0px 3px; border-bottom: 1px solid rgb(224, 224, 224); border-right: 1px solid rgb(224, 224, 224);">拒绝访问</td></tr></tbody></table>

postMessage()是HTML5的一个API接口，由于比较新，所以在IE6和IE7中不支持。 1 向另外一个iframe发送消息：

```
var message = 'Hello' + (new Date().getTime());
    window.parent.frames[1].postMessage(message, '*');

```

iframe1.html需要向iframe2.html发送消息，也就是第二个iframe，所以是window.parent.frames[1]。

如果是向父页面发送消息就是window.parent。

postMessage这个函数接收二个参数，缺一不可，第一个参数即你要发送的数据。

第二个参数是非常重要，主要是出于安全的考虑，一般填写允许通信的域名。

这里为了简化，所以使用’*'，即不对访问的域进行判断。

2 另外一个iframe监听消息事件：

```
iframe2.html中写个监听message事件，当有消息传到iframe2.html时就会触发这个事件。
var onmessage = function(e) {
    var data = e.data,p = document.createElement('p');
    p.innerHTML = data;
    document.getElementById('display').appendChild(p);
};
 //监听postMessage消息事件
if (typeof window.addEventListener != 'undefined') {
    window.addEventListener('message', onmessage, false);
 } else if (typeof window.attachEvent != 'undefined') {
    window.attachEvent('onmessage', onmessage);
}

```

如果你有加域名限,比如下面的代码：

```
window.parent.frames[1].postMessage(message, 'http://www.test.com');

```

就要在onmessage中追加个判断：

```
if(event.origin !== 'http://www.test.com') return;

```

#### XMLHttpRequest的同源策略

一个简单的同步XMLHttpRequest请求：

```
var x = new XMLHttpRequest();
x.open("POST", "/some_script.cgi", false);
x.setRequestHeader("X-Random-Header", "Hi mom!");
x.send("...POST payload here...");
alert(x.responseText);

```

XMLHttpRequest请求严格遵守同源策略，非同源不可以请求。

这个API也做过很多测试与改进，下面列出之前的测试方法：

```
var x = new XMLHttpRequest();
x.open("POST", "http://www.example.com/", false);
// 定义发送内容长度为7
x.setRequestHeader("Content-Length", "7");
// 构造的http请求。
x.send(
"Gotcha!\n" +
"GET /evil_response.html HTTP/1.1\n" +
"Host: www.bunnyoutlet.com\n\n"
);

```

现在的浏览器都不存在上面的隐患，包括基本都禁用了TRACE方法，防止httponly的cookie泄漏问题等。

#### Web Storage的同源策略

Web Storage是由Mozilla的工程师在Firefox1.5中加入的，并且加入了HTML5中，现在的浏览器都支持，除了IE6与IE7。

JavaScript可以通过localStorage与sessionStorage对Web Storage进行创建，检索和删除：

```
localStorage.setItem("message", "Hi mom!"); 
alert(localStorage.getItem("message")); 
localstorage.removeItem("message");

```

localStorage对象可以长时间保存，并且遵守同源策略。

但是在IE8中localStorage会把域名相同但是协议分别为HTTP和HTTPS的内容放在一起，IE9中已修改。

在Firefox中，localStorage没有问题，但是sessionStorage也是会把域名相同的HTTP与HTTPS放在一起。

#### Cookie的安全策略

设置Cookie总结

<table cellspacing="0" cellpadding="0" style="box-sizing: border-box; border-collapse: collapse; border-spacing: 0px; background-color: transparent; border-top: 1px solid rgb(224, 224, 224); border-left: 1px solid rgb(224, 224, 224);"><tbody style="box-sizing: border-box;"><tr style="box-sizing: border-box;"><td rowspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 45.5px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;"><b style="box-sizing: border-box; font-weight: 700;">在foo.example.com设置cookie，domain设置为：</b><br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;"><b style="box-sizing: border-box; font-weight: 700;">最终cookie的范围</b><br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.9px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;"><b style="box-sizing: border-box; font-weight: 700;">非IE浏览器</b><br style="box-sizing: border-box;"></p></td><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.4px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;"><b style="box-sizing: border-box; font-weight: 700;">IE浏览器</b><br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">设置为空<br style="box-sizing: border-box;"></p></td><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.9px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">foo.example.com（一个域）<br style="box-sizing: border-box;"></p></td><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.4px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">＊.foo.example.com<br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">bar.foo.example.com<br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">cookie设置失败，设置的域是当前域的一个子域<br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">foo.example.com<br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">*.foo.example.com<br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">baz.example.com<br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">cookie设置失败，域名不匹配<br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">example.com<br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">*.example.com<br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">ample.com<br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">cookie设置失败，域名不匹配<br style="box-sizing: border-box;"></p></td></tr><tr style="box-sizing: border-box;"><td valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 188.6px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">.com<br style="box-sizing: border-box;"></p></td><td colspan="2" valign="middle" style="box-sizing: border-box; padding: 4px; border-width: 2px; border-style: solid; border-color: rgb(0, 0, 0); width: 387.3px; height: 17.8px;"><p style="box-sizing: border-box; margin: 0px; font-size: 12px; font-family: Helvetica; min-height: 14px;">设置失败，域名太广，存在安全风险。</p></td></tr></tbody></table>

Cookie中的path参数可以设定指定目录的cookie。

例如设定domain为example.com，path为/some/path/ 在访问下面url的时候会带上设定的cookie：

http://foo.example.com/some/path/subdirectory/hello_world.txt

存在一定的安全风险，因为path的设定没有考虑到同源策略。

httponly属性可以防止通过document.cookie的API访问设定的cookie。

secure属性设定后只有在通过https传输时才会带上设定的cookie，可以防止中间人攻击。

#### Adobe Flash

AllowScriptAccess参数：用来控制flash通过ExternallInterface.call()函数调用javascript的时的限制。

有三个值：always，never和sameorigin，最后一个值只允许同域的JavaScript操作（08年之前默认为always，现在默认为sameorigin）。

AllowNetworking参数：用来控制flash与外部的网络通讯。

可选的值为：all（允许使用所有的网络通讯，默认值），internal（flash不能与浏览器通讯如navigateToURL，但是可以调用其他的API），none（禁止任何的网络通讯）

#### 本地文件

由于本地文件都是通过file:协议进行访问的，由于不存在host，所以无法遵循同源策略。

所以本地保存的一个HTML文件，在浏览器中通过file:协议访问后，可以通过XMLHttpRequest或DOM对本地其他文件进行操作。

与此同时，也可以对互联网的其他资源做同样的操作。各浏览器厂商意识到这个问题，并努力做了修改：

测试代码：

1.html（1.txt随机写一些字符串即可）

```
<script>
function createXHR(){
  return window.XMLHttpRequest?
  new XMLHttpRequest():
  new ActiveXObject("Microsoft.XMLHTTP");
}
function getlocal(url){
  xmlHttp = createXHR();
  xmlHttp.open("GET",url,false);
  xmlHttp.send();
  result = xmlHttp.responseText;
  return result;
}
function main(){
  url = "file://路径/1.txt";
  alert(url);
  result = getlocal(url);
  alert(result);
}
main();
</script>

```

结论：

```
1 Chrome浏览器（使用WebKit内核的浏览器）
完全禁止跨文档的XMLHttpRequest和DOM操作，并禁止了document.cookie和<meta http-equiv="Set-Cookie" ...>的操作。
2 Firefox
允许访问同目录与子目录里的文件。也可通过document.cookie与<meta http- equiv="Set-Cookie" ...>设定cookie，file:协议下cookie共享，storage也是。
3 IE7及以上
允许本地文件之间的访问，但是在执行JavaScript之前会有一个提示，用户点击通过之后可以执行，cookie域Firefox类似，但是file:协议下不支持storage。
4 IE6
允许本地文件的访问，同时也允许对http协议的访问，cookie也是一样。

```

### 伪URL的域

* * *

一些web应用用到了伪URL例如about:，javascript:，和data:来创建HTML文档。

这种方法是为了不需要再与服务器通信，可以节约时间更快的响应，但是也带进了很多安全隐患。

```
about:blank

```

about协议在现在的浏览器中有很多用途，但是其中大部分不是为了获取正常的页面。

about:blank这个URL可以用来被创建DOM对象，例如：

```
<iframe src="about:blank" name="test"></iframe>
<script> 
frames["test"].document.body.innerHTML = "<h1>Hi!</h1>";
</script>

```

在浏览器中，创建一个about:blank页面，它继承的域为创建它的页面的域。

例如，点击一个链接，提交一个表单，创建一个新窗口，但是当用户手动输入about:或者书签中打开的话，他的域是一个特殊的域，任何其他的页面都不可以访问。

```
data:协议

```

data:协议是设计用来放置小数据的，例如图标之类的，可以减少http请求数量，例如：

```
<img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEBLAEsAAD...">

```

用以下代码研究域的问题：

```
<iframe src="data:text/html;charset=utf-8,<script>alert(document.domain)</script>" >  

```

在Chrome与Safari中，所有的data:都会赋予一个单独的，不可获取的域，而不是从父域中继承的。

Firefox与Opera中，域是继承于当前页面。

IE8之前的版本不支持data:协议。

javascript:和vbscript:

javascript:协议允许后面执行javascript代码，并且继承了调用的当前域。

有些情况会对后面的内容处理两次，如果代码正确的话，会把后面的代码当成html解析，覆盖掉原来的html代码：

```
<iframe src='javascript:"<b>2 + 2 = " + (2+2) + "</b>"'> 
</iframe>

```