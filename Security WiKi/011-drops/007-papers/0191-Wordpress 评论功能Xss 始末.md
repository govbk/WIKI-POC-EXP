# Wordpress 评论功能Xss 始末

近期Wordpress自身程序评论功能的Xss在微博上沸沸扬扬，而其中的修复过程也可谓一波三折，接下来由我为大家一一讲述。

WordPress <4.1.2 xss
====================

* * *

该问题来自于特殊字符截断，mysql官网描述“The character set named utf8 uses a maximum of three bytes per character and contains only BMP characters”，mysql在使用utf8编码时，单个字符大小上限为3字节，当出现超过3个字节的utf8字符时，则会出现由于数据库不识别字符而产生截断效果。示例如下，使用特殊字符：

![enter image description here](http://drops.javaweb.org/uploads/images/da4c18f13bd7d9fee45bcb1596b58af5aea19894.jpg)

```
UPDATE `wp_comments` SET `comment_content` = 'stefanie[特殊字符]555555 ' WHERE `wp_comments`.`comment_ID` =12;

```

在数据库中插入的结果为stefanie，特殊字符及后面的内容并未插入数据库。

UTF-8编码在对于不同的字符区域，编码所占用的字节数各不相同。

![enter image description here](http://drops.javaweb.org/uploads/images/dd79f40c1890c94a81ecf9dcfd03705e4be611e1.jpg)

mysql utf-8编码对于占用四个字节的字符无法识别，使用上图范围内的编码均可达到目的，如

![enter image description here](http://drops.javaweb.org/uploads/images/9f378c953344de905f5b9e02ae05d4621bf9aff5.jpg)![enter image description here](http://drops.javaweb.org/uploads/images/7738d0a420303c34ac3b1b5e9eebb2bd054bfa0f.jpg)![enter image description here](http://drops.javaweb.org/uploads/images/d0a6e20814c3fc77e6c0da98077a5ff9db7f976d.jpg)

当mysql的编码为utf-8mb4或者latin1时，则可以对此类字符进行识别，另外，当mysql开启strict mode时候，会更加严格地处理，确保在数据有效存储之前进行阻止，也就不会产生该问题。

关于漏洞利用，Wordpress只允许评论中出现白名单内的标签和对应的属性，而且要保证标签的完整性，比如尖括号的闭合。Poc如下：

```
<abbr title="123 onmouseover=alert(1) 特殊字符">

```

可以看出，onmouseover是在双引号内作为title属性的值出现的，在插入数据库时由于特殊字符产生截断，右侧的引号不会插入，在输出时，左侧引号会被转义，因而可使得onmouseover成功解析。 相关链接：

(1] http://xteam.baidu.com/?p=177 (2]https://cedricvb.be/post/wordpress-stored-xss-vulnerability-4-1-2/ (3]https://dev.mysql.com/doc/refman/5.5/en/charset-unicode-utf8mb4.html

WordPress <=4.2 xss
===================

* * *

mysql type＝TEXT时，TEXT的最大长度为64kb，当发生数据库的插入操作时，则会将大于64KB的部分抛弃，此时也造成了一种截断，而wordpress保存评论的字段的type正是TEXT。

该漏洞于上一漏洞同理，只是截断的方式有所不同，poc如下：

```
<abbr title="123 onmouseover=alert(1) 此处增加无用字符至64KB ">

```

截断效果如下图：

![enter image description here](http://drops.javaweb.org/uploads/images/8c11f7c902fd4ac8ec012a96917da30570019632.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/7e5da77781b652c842cb2d1b17ec6f73c5b649ce.jpg)

该poc仅限IE使用，而Klikki Oy团队给出了兼容多种浏览器的POC，chrome，IE，firefox测试成功。

```
stefanie<a title='x onmouseover=alert(unescape(/hello%20world/.source))
style=position:absolute;left:0;top:0;width:5000px;height:5000px  此处用特殊字符或者长度截断均可'></a>

```

相关链接： (1] http://xteam.baidu.com/?p=177 (2] https://speakerdeck.com/mathiasbynens/hacking-with-unicode

WordPress <=4.2.1 xss
=====================

* * *

4.2.1版本主要针对长度截断进行了修复，在wp-includes\wp-db.php get_col_length函数中增加了数据库每种类型字段的长度限制，并和传入数据长度做了比较。

```
protected function process_field_lengths( $data, $table ) {
foreach ( $data as $field => $value ) {
    if ( '%d' === $value['format'] || '%f' === $value['format'] ) {
            // We can skip this field if we know it isn't a string.
            // This checks %d/%f versus ! %s because it's sprintf() could take more.
            $value['length'] = false;
        } else {
            $value['length'] = $this->get_col_length( $table, $field );
            if ( is_wp_error( $value['length'] ) ) {
                return false;
            }
        }
        if ( false !== $value['length'] && mb_strlen( $value['value'] ) > $value['length'] ) {
            return false;
        }
        $data[ $field ] = $value;
    }
    return $data;
}

```

$value['length']来自于get_col_length，text类型长度上限为65535字节，mb_strlen( $value['value'] )是mb_strlen函数来统计字符个数的结果，两个值的计量单位不同，一个是字节数，一个是字符的个数。

![enter image description here](http://drops.javaweb.org/uploads/images/a57782554a2d8205c58b09487aebc117a50aa1c2.jpg)

在函数“mb_strlen”中，一个多字节字符统计个数为1。在不同的编码中，一个字符的大小可以为多个字节（多字节字符），所以我们可以构造一个字符串，让字符的个数小于65535而字符串的字节数大于65535字节，从而满足如下条件：

```
if ( false !== $value['length'] && mb_strlen( $value['value'] ) > $value['length'] ) {
                return false;}

```

当php向数据库中插入数据时，由于字节数超过了text类型的长度上线65535字节，所以字符串会被截断，导致了之前的xss可以重新被利用。 相关链接：

(1] http://xteam.baidu.com/?p=198 (2] http://php.net/manual/zh/function.mb-strlen.php

WordPress 4.2.2 中总体修复情况
=======================

* * *

在4.2.2版本中引入了两个变量：

$truncate_by_byte_length ： 是否进行字节长度验证 $needs_validation ： 是否进行多字节字符合规性验证以及长度验证 wp422/wp-includes/wp-db.php 2626行

```
if ( $truncate_by_byte_length ) {
    mbstring_binary_safe_encoding();
    if ( false !== $length && strlen( $value['value'] ) > $length ) {
        $value['value'] = substr( $value['value'], 0, $length );
    }
    reset_mbstring_encoding();
    if ( ! $needs_validation ) {
        continue;
    }
}

```

该处解决了4.2.1中用mb_strlen来测量实际长度和规定长度上线之间的比较造成的问题，改用了strlen来测量长度，并对超长部分进行切割，因而拦截了4.2.1补丁bypass造成的xss。

```
$regex = '/
    (
        (?: [\x00-\x7F]                  # single-byte sequences   0xxxxxxx
        |   [\xC2-\xDF][\x80-\xBF]       # double-byte sequences   110xxxxx 10xxxxxx
        |   \xE0[\xA0-\xBF][\x80-\xBF]   # triple-byte sequences   1110xxxx 10xxxxxx * 2
        |   [\xE1-\xEC][\x80-\xBF]{2}
        |   \xED[\x80-\x9F][\x80-\xBF]
        |   [\xEE-\xEF][\x80-\xBF]{2}';
if ( 'utf8mb4' === $charset ) {
    $regex .= '
        |    \xF0[\x90-\xBF][\x80-\xBF]{2} # four-byte sequences   11110xxx 10xxxxxx * 3
        |    [\xF1-\xF3][\x80-\xBF]{3}
        |    \xF4[\x80-\x8F][\x80-\xBF]{2}
    ';
}
$regex .= '){1,40}                          # ...one or more times
    )
    | .                                  # anything else
    /x';
$value['value'] = preg_replace( $regex, '$1', $value['value'] );
if ( false !== $length && mb_strlen( $value['value'], 'UTF-8' ) > $length ) {
    $value['value'] = mb_substr( $value['value'], 0, $length, 'UTF-8' );
}
continue;
}

```

可以看出，对于utf8编码时，仅仅会取范围内的小于等于3字节UTF8字符，取出之后，会按照当前多字节字符的编码长度再次确认。此处是针对小于4.2版本用四字节utf8字符插入数据库截断以及其他特殊字符截断而修补的。 相关链接：

(1] https://wordpress.org/news/2015/05/wordpress-4-2-2/

致谢：感谢evil_xi4oyu的每一次悉心指点和yaseng的帮助~