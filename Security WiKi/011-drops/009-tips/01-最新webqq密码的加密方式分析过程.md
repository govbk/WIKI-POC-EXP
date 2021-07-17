# 最新webqq密码的加密方式分析过程

授人以鱼，不如授人以渔，今天就分享一个 分析qq加密的过程。

工具：谷歌浏览器自带的的调试工具（在浏览器中按F12呼出）

以下是全过程，历时4个的小时。

提交的时候调用 onFormSubmit

```
function onFormSubmit(form)
{
        if (form.remember_uin.checked){
                return ptui_onLoginEx(form, "qq.com")
        }else{                                
                var myDate=new Date();
                myDate.setFullYear(1971,1,1);
                pt.cookie.set("ptui_loginuin",  "", myDate, '/', 'ui.ptlogin2.qq.com');
                return ptui_onLogin(form);
        }
}

```

如果用户没有勾选保存密码调用`ptui_onLogin`

```
function ptui_onLogin(A) {
    try {
        if (parent.ptlogin2_onLogin) {
            if (!parent.ptlogin2_onLogin()) {
                return false
            }
        }
        if (parent.ptlogin2_onLoginEx) {
            var D = A.u.value;
            var B = A.verifycode.value;
            if (str_uintip == D) {
                D = ""
            }
            if (!parent.ptlogin2_onLoginEx(D, B)) {
                return false
            }
        }
    } catch(C) {}
    return ptui_checkValidate(A)
}

```

接下来调用`ptui_checkValidate(A)`

```
function ptui_checkValidate(B) {
    var A = B.u;                                        //此处获取用户名
    var D = B.p;                                        //此处获取密码
    var E = B.verifycode;                        //此处获取验证码
    if (A.value == "" || str_uintip == A.value) {
        pt.show_err(str_no_uin);
        A.focus();
        return false
    }
    A.value = A.value.trim();
    if (!pt.chkUin(A.value)) {
        pt.show_err(str_inv_uin);
        A.focus();
        A.select();
        return false
    }
    if (D.value == "") {
        pt.show_err(str_no_pwd);
        D.focus();
        return false
    }
    if (E.value == "") {
        if (!isLoadVC) {
            loadVC(true);
            g_submitting = true;
            return false
        }
        pt.show_err(str_no_vcode);
        try {
            E.focus()
        } catch(C) {}
        if (!g_loadcheck) {
            ptui_reportAttr(78028)
        } else {
            ptui_reportAttr(78029)
        }
        return false
    }
    if (E.value.length &lt; 4) {
        pt.show_err(str_inv_vcode);
        E.focus();
        E.select();
        return false
    }
    if (isLoadVC &amp;&amp; !(/^[a-zA-Z0-9]+$/.test(E.value))) {
        pt.show_err(str_correct_vcode);
        E.focus();
        E.select();
        return false
    }
    D.setAttribute("maxlength", "32");
    ajax_Submit();
    ptui_reportNum(g_changeNum);
    g_changeNum = 0;
    return true
}

```

然后：

```
function ajax_Submit() {
    if (pt.checkRet == -1 || pt.checkRet == 3) {
        pt.show_err(pt.checkErr[window.g_lang]);
        try {
            $("p").focus()
        } catch(B) {}
        return
    }
    var A = getSubmitUrl("login");
    pt.winName.set("login_param", encodeURIComponent(login_param));
    pt.loadScript(A);
    return
}

```

最后在这个函数中加密组装提交地址：

```
function getSubmitUrl(K) {
    var E = true;
    var C = document.forms[0];
    var A = (pt.isHttps ? "https://ssl.": "http://") + "ptlogin2." + g_domain + "/" + K + "?";
    var B = document.getElementById("login2qq");
    if (pt.regmaster == 2) {
        A = "http://ptlogin2.function.qq.com/" + K + "?regmaster=2&amp;"
    } else {
        if (pt.regmaster == 3) {
            A = "http://ptlogin2.crm2.qq.com/" + K + "?regmaster=3&amp;"
        }
    }
    for (var J = 0; J &lt; C.length; J++) {
        if (K == "ptqrlogin" &amp;&amp; (C[J].name == "u" || C[J].name 
== "p" || C[J].name == "verifycode" || C[J].name == "h")) {
            continue
        }
        if (C[J].name == "ipFlag" &amp;&amp; !C[J].checked) {
            A += C[J].name + "=-1&amp;";
            continue
        }
        if (C[J].name == "fp" || C[J].type == "submit") {
            continue
        }
        if (C[J].name == "ptredirect") {
            g_ptredirect = C[J].value
        }
        if (C[J].name == "low_login_enable" &amp;&amp; (!C[J].checked)) {
            E = false;
            continue
        }
        if (C[J].name == "low_login_hour" &amp;&amp; (!E)) {
            continue
        }
        if (C[J].name == "webqq_type" &amp;&amp; !B &amp;&amp; (!C[J].checked)) {
            continue
        }
        A += C[J].name;
        A += "=";
        if (C[J].name == "u" &amp;&amp; pt.needAt) {
            A += pt.needAt + "&amp;";
            continue
        }
        if (C[J].name == "p") {
            var M = C.p.value;
            var I = hexchar2bin(md5(M));
            var H = md5(I + pt.uin);
            var G = md5(H + C.verifycode.value.toUpperCase());
            A += G
        } else {
            if (C[J].name == "u1" || C[J].name == "ep") {
                var D = C[J].value;
                var L = "";
                if (g_appid == "1003903" &amp;&amp; B) {
                    L = /\?/g.test(D) ? "&amp;": "?";
                    var F = document.getElementById("webqq_type").value;
                    L += "login2qq=" + B.value + "&amp;webqq_type=" + F
                }
                A += encodeURIComponent(D + L)
            } else {
                A += C[J].value
            }
        }
        A += "&amp;"
    }
    A += "fp=loginerroralert&amp;action=" + pt.action.join("-") + "-" + 
(new Date() - g_begTime) + "&amp;mibao_css=" + pt.mibao_css + "&amp;t=" +
 pt.submitN[pt.uin] + "&amp;g=1";
    A += "&amp;js_type=" + pt.js_type + "&amp;js_ver=" + window.g_pt_version + "&amp;login_sig=" + window.g_login_sig;
    return A
}

```

核心的加密代码如下：

```
if (C[J].name == "p") {
            var M = C.p.value;
            var I = hexchar2bin(md5(M));
            var H = md5(I + pt.uin);        //pt.uin  估计是用户qq号的16进制表示 
            var G = md5(H + C.verifycode.value.toUpperCase());
            A += G

var M = "××××××";var ver="!";var I = hexchar2bin(md5(M));var H = md5(I + pt.uin);var G = md5(H + ver.toUpperCase());

```

hexchar2bin算法如下：

```
function hexchar2bin(str) {
    var arr = [];
    for (var i = 0; i &lt; str.length; i = i + 2) {
        arr.push("\\x" + str.substr(i, 2))
    }
    arr = arr.join("");
    eval("var temp = '" + arr + "'");
    return temp
}

```

最终加密过程如下：

```
md5(md5(hexchar2bin(md5(pwd))+uin)+verifycode.toUpperCase())





#!js
md5(md5(hexchar2bin(md5("××××××××"))+'\x00\x00\x00\x00\x01\xd3\xff\xf3')+"!EHZ")
"918AAFDF8C9481F7AC2FC1C89A4DED7B"

```

此处改变了 pt.uin:

```
function ptui_checkVC(A, C, B) {
    clearTimeout(checkClock);
    pt.checkRet = A;
    pt.uin = B;
    if (A == "2") {
        g_uin = "0";
        pt.show_err(str_inv_uin)
    }
    if (!pt.submitN[B]) {
        pt.submitN[B] = 1
    }
    var E = new Date();
    g_time.time7 = E;
    var D = {
        "12": g_time.time7 - g_time.time6
    };
    if (!curXui) {
        ptui_speedReport(D)
    }
    g_loadcheck = false;
    switch (A + "") {
    case "0":
    case "2":
    case "3":
        $("verifycode").value = C || "abcd";
        loadVC(false);
        break;
    case "1":
        $("verifycode").value = pt.needCodeTip ? str_codetip: "";
        loadVC(true);
        break;
    default:
        break
    }
}

```

其实找出这个算法花的时间很少，只是一直找不到 ptui_checkVC 调用的地方，后来恍然大悟，在验证qq是否需要图片验证码的时候返回的就是给js调用的，地址是：

```
https://ssl.ptlogin2.qq.com/chec ... 5Q4YxDJ8Rza4-1ubGMR*aruR6Byct1dQ&u1=http%3A%2F%2Fweb2.qq.com%2Floginproxy.html&r=0.5011255156714469

```

返回内容如下：

```
ptui_checkVC('0','!BGC','\x00\x00\x00\x00\x01\xd3\xff\xf3');  

```

第三个参数就是 16进制表示的qq号码

至此全搞定，剩下的就是编程实现。https方式访问。可以试试 libcurl   或者自己 用openssl+socket也可以