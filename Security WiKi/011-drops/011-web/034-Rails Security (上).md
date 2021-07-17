# Rails Security (上)

**Author: Lobsiinvok**

0x00 前言
=======

* * *

Rails是Ruby广泛应用方式之一，在Rails平台上设计出一套独特的MVC开发架构，采取模型（Model）、外观（View）、控制器（Controller）分离的开发方式，不但减少了开发中的问题，更简化了许多繁复的动作。

此篇讲稿分为上下部份，因为最近在开发Rails，需要针对安全问题做把关，便借此机会针对历史上Rails发生过的安全问题进行归纳与整理。

这篇讲稿承蒙安全领域研究上的先进，在自行吸收转​​换后，如有笔误或理解错误的地方还望各位见谅并纠正我，感谢 :D

* * *

**快速跳转**

*   [Mass assignment](http://drops.com:8000/#mass_assignment)
*   [Unsafe Query Generation](http://drops.com:8000/#unsafe_query_gen)
*   [Content_tag](http://drops.com:8000/#content_tag)
*   [YAML.load](http://drops.com:8000/#yaml_load)
*   [Dynamic Render Path](http://drops.com:8000/#dynamic_render_path)
*   [Reference](http://drops.com:8000/#refs)

0x01 Mass assignment
====================

* * *

*   让Rails developers爱上的毒药(toxic)
*   ActiveRecord在新增物件时可传入Hash直接设定多项属性
*   若没有限制可传入的参数会造成物件属性可被任意修改
    
    ![p1](http://drops.javaweb.org/uploads/images/ab39b7f431d1da92e7e4de9b1192870a33ceb139.jpg)
    
*   透过新增/修改送出的属性，可以变更任意物件属性
    
*   [Case](https://github.com/blog/1068-public-key-security-vulnerability-and-mitigation)
    
*   Rails 3.2.3后，config.active_record.whitelist_attributes = true
    
    ![p2](http://drops.javaweb.org/uploads/images/27660286ab4aa8e7a406f89f539d36302f8b368f.jpg)
    
*   Rails 4后，Rails Core内建strong_parameters
    
*   更适当地将处理的过程锁定在Controller layer
    
*   更有弹性地针对属性作过滤
    

0x02 Unsafe Query Generation
============================

* * *

*   Rake在处理params时，有时候会产生Unsafe的query
    
    ![p3](http://drops.javaweb.org/uploads/images/dc3bf5bce8c5211c863f4e1894936c8609ad4929.jpg)
    
*   透过伪造params[:token]成[], [nil], [nil, nil, ...]或['foo', nil]，都能够通过.nil?的检查，使得SQL语句被安插IS NULL or IN ('foo', NULL)造成非预期的结果
    
*   在Rails 3.2.8增加deep_munge方法来消除掉Hash里的nil
    
*   commit中可看到类似的检查
    
    ![p4](http://drops.javaweb.org/uploads/images/e898ffecdfbf61e17b140660475629f1e3d14866.jpg)
    

### Code for Testing

![p5](http://drops.javaweb.org/uploads/images/70afa689649502b0b743d80b3bc48d1348823404.jpg)

**Rails 3.1.0: 成功绕过nil?的检查**

![p6](http://drops.javaweb.org/uploads/images/2dbd22dadc1d20b307ecb664a02166b0574f3531.jpg)

**Rails 4.2.5: 被拦截，直接替换成nil**

![p7](http://drops.javaweb.org/uploads/images/faa4799d8758d5b3cee51a78de7a0629c066eb68.jpg)

0x03 Content_tag
================

* * *

**Rails提供content_tag方便产生HTML**

*   尽管方便，产生出的HTML是safe的吗？很显然的并不是！
*   Ref:[brakeman](https://github.com/presidentbeef/brakeman/blob/master/lib/brakeman/checks/check_content_tag.rb)
    
    ![p8](http://drops.javaweb.org/uploads/images/c4e1fa48681c19e968b2d1e3b5c21ac9bd95533f.jpg)
    
*   In latest rails 4.2.5, attr still can be injected with any html data.
    
    ![p9](http://drops.javaweb.org/uploads/images/93301b5ef18b14e45fef71d8db480b4dc7b666c3.jpg)
    
*   尽管attr values​​有escape，但跟button_to一起作用时却……
    
    ![p10](http://drops.javaweb.org/uploads/images/4c27445f3515c3f3b8b02ed62347217c074892de.jpg)
    

### Why？

*   Content_tag回传`html_safe`的字串，代表此字串在后续输出时不再做escape
*   建立在attacker无法构建`html_safe`型的字串(等价于raw)
*   丢给button_to时因为不再做escape导致XSS问题

0x04 YAML.load
==============

* * *

### 难得一见的RCE漏洞(CVE-2013-0156)

*   主因出在YAML
*   CVE-2013-0156发生在可透过YAML解析时指定tag的方式覆盖已经载入的instance
*   在rails3后已从`DEFAULT_PARSERS`移除
    
    ![p11](http://drops.javaweb.org/uploads/images/93c926d3345f7e2d2715b06b7a97201f3b9f22d3.jpg)
    
*   此次问题发生在XML解析
    
*   在解析时会经过Hash.from_xml(request.raw_post)，底处是到typecast_xml_value进行xml的处理，[这篇](http://drops.wooyun.org/papers/61)前辈的文章解释得很清楚，因为typecast_xml_value里针对xml node type可以进行YAML的解析调用(允许的type定义在`ActiveSupport::XmlMini::PARSING`)，因此造成RCE问题
    
*   透过patch可以更明显看到修补后的不同
    

![p12](http://drops.javaweb.org/uploads/images/70a5e621b7c89476f306b939695e5ac3650f53c5.jpg)

![p13](http://drops.javaweb.org/uploads/images/21626c4c5dd5d18fb253d3b3f82ef222d7a54108.jpg)

Ref:[Rails 3.2](https://github.com/rails/rails/commit/43109ecb986470ef023a7e91beb9812718f000fe)

### Proof

**Rails 3.1: 成功执行指令**

![p14](http://drops.javaweb.org/uploads/images/a24eab2a174bfeae6b052216cba84c41de90cffd.jpg)

### 难得一见的RCE漏洞(CVE-2013-0333)

*   CVE-2013-0333问题一样发生在`YAML.load`
*   在rails 3.0.19(含)前，rails3.0.x的JSON Parser竟然是使用YAML作为Backend
*   问题发生在YAML backend中的`convert_json_to_yaml`
*   [这篇](http://ronin-ruby.github.io/blog/2013/01/28/new-rails-poc.html)讲得很详细
*   Patch for CVE-2013-0333

![p15](http://drops.javaweb.org/uploads/images/29317581c80371b0d6bae725691ddacdb34af158.jpg)

[Rails 3.0.20](https://github.com/rails/rails/commit/5375dce1ac29141821a48fdc683e6b797f61f113)

0x05 Dynamic Render Path
========================

* * *

**Render是处理request的一连串过程**

*   除了Insecure Direct Object Reference的安全问题，[DEVCORE](http://devco.re/blog/2015/07/24/the-vulnerability-of-dynamic-render-paths-in-rails/)也在进行渗透测试时发现潜在的RCE问题
*   rails目前最新版本4.2.5预设也是用ERB去做样板处理，但在rails5开发过程中已经加入此次[commit](https://github.com/rails/rails/commit/4be859f0fdf7b3059a28d03c279f03f5938efc80)
*   动态样板间接变成LFI问题，搭配上面所述的`default_template_handler`为ERB，只要找到有调用ruby code的样板或是可自行写入的档案，就能够造成RCE
    
    ![p16](http://drops.javaweb.org/uploads/images/ae0add5752a181d5dfd0bbe5e438c4b638179608.jpg)
    
    ![p17](http://drops.javaweb.org/uploads/images/86547f8901c4d750c3e94143f0e4ab0cdf371054.jpg)
    
*   真实环境下发生的问题可以前往[DEVCORE](http://devco.re/blog/2015/07/24/the-vulnerability-of-dynamic-render-paths-in-rails/)查看
    
*   如果有类似开发环境应立即处理，`default_template_handler`要到rails5才转换成RAW
    
*   改以白名单的方式限制template名称或是根据commit的内容手动Patch
    

0x06 Reference
==============

* * *

*   [The Ruby/GitHub hack: translated](http://blog.erratasec.com/2012/03/rubygithub-hack-translated.html#.VnfEIxV97IU)
*   [How Does Rack Parse Query Params? With Parse_nested_query](http://codefol.io/posts/How-Does-Rack-Parse-Query-Params-With-parse-nested-query)
*   [Cross Site Scripting (Content Tag)](http://brakemanscanner.org/docs/warning_types/content_tag/)
*   [Bad coding style can lead to XSS in Ruby on Rails](https://en.internetwache.org/bad-coding-style-can-lead-to-xss-in-ruby-on-rails-14-10-2014/)
*   [分析下难得一见的ROR的RCE（CVE－2013－0156）](http://drops.wooyun.org/papers/61)
*   [Rails PoC exploit for CVE-2013-0333](http://ronin-ruby.github.io/blog/2013/01/28/new-rails-poc.html)
*   [Dynamic Render Path](http://brakemanscanner.org/docs/warning_types/dynamic_render_paths/)
*   [Rails 动态样板路径的风险](http://devco.re/blog/2015/07/24/the-vulnerability-of-dynamic-render-paths-in-rails/)