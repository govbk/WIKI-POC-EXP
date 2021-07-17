# WordPress更新至 3.8.2 修复多个漏洞

![enter image description here](http://drops.javaweb.org/uploads/images/959bc13deaa384c1cb5e2bb5d832f11b0c3a95dd.jpg)

在被OpenSSL刷屏的时候，WordPress更新。

WordPress 3.8.2现在已经提供下载，最新的版本更新了几个重要的安全问题，所以推荐更新。

WordPress 3.8.2修复的一个重要漏洞是cookie伪造漏洞（[CVE -2014- 0166](http://web.nvd.nist.gov/view/vuln/detail?vulnId=CVE-2014-0166)）。该漏洞可以被攻击者利用通过伪造身份验证Cookie，登陆网站。该漏洞是由WordPress的安全团队成员[Jon Cave](http://joncave.co.uk/)发现。

第二个漏洞是权限提升（CVE -2014- 0165）漏洞，可以使投稿人角色发布文章。

还有[后台注入漏洞](https://security.dxw.com/advisories/sqli-in-wordpress-3-6-1/)，以及在上传文件处使用第三方库导致的xss漏洞。

注入漏洞修改代码：[https://core.trac.wordpress.org/changeset/27917](https://core.trac.wordpress.org/changeset/27917)

是一个二次注入。

cookie伪造修复wp-includes/pluggable.php文件中：

[https://github.com/WordPress/WordPress/commit/7f001bfe242580eb18f98e2889aad4ab1b33301b](https://github.com/WordPress/WordPress/commit/7f001bfe242580eb18f98e2889aad4ab1b33301b)

```
    $key = wp_hash($username . $pass_frag . '|' . $expiration, $scheme);
    $hash = hash_hmac('md5', $username . '|' . $expiration, $key);

 -  if ( $hmac != $hash ) {
 +  if ( hash_hmac( 'md5', $hmac, $key ) !== hash_hmac( 'md5', $hash, $key ) ) {
```