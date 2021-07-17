# IORegistryIterator竞争条件漏洞分析与利用

**Author：shrek_wzw@360NirvanTeam**

0x00 简介
=======

* * *

CVE-2015-7084是由于IORegistryIterator没有考虑用户态多线程同时调用的情况，引起Race Condition，可导致任意代码执行。漏洞存在于XNU版本3248.20.55之前的内核上，即Mac OS X 10.11.2、iOS 9.2、watchOS 2.1、tvOS 9.1之前的系统版本上。官方修复公告[https://support.apple.com/en-us/HT205637](https://support.apple.com/en-us/HT205637)。

0x01 漏洞背景
=========

* * *

IORegistryIterator是用于XNU内核中用于遍历访问IO Registry Entry的一个类。在XNU版本3248.20.55之前的内核上，即Mac OS X 10.11.2、iOS 9.2、watchOS 2.1、tvOS 9.1之前的系统版本上，在操作IORegistryIterator时缺少锁机制，用户态进程通过多线程调用引起Race Condition，最终可实现任意代码执行。这个漏洞是由Google Project Zero的Ian Beer报告，CVE编号CVE-2015-7084。

0x02 漏洞分析
=========

* * *

Ian Beer在[https://code.google.com/p/google-security-research/issues/detail?id=598](https://code.google.com/p/google-security-research/issues/detail?id=598)中给出了漏洞的说明，以及一份导致Double Free的PoC代码。

`is_io_registry_iterator_exit_entry`是IORegistryIteratorExitEntry对应的内核接口，会调用IORegistryIterator::exitEntry函数。

```
/* Routine io_registry_iterator_exit */
kern_return_t is_io_registry_iterator_exit_entry(
    io_object_t iterator )
{
    bool    didIt;
    CHECK( IORegistryIterator, iterator, iter );
    didIt = iter->exitEntry();
    return( didIt ? kIOReturnSuccess : kIOReturnNoDevice );
}

```

.

```
bool IORegistryIterator::exitEntry( void )
{
    IORegCursor *   gone;
…

    if( where != &start) {
      gone = where;   // Race Condition
        where = gone->next;
        IOFree( gone, sizeof(IORegCursor));  // gone可能被释放两次
        return( true);
    } else
        return( false);
…
}

```

但是由于缺乏锁的保护，通过多线程调用IORegistryIteratorExitEntry，导致gone指向的内存区域被释放两次，引起崩溃。示意图如下：

![p1](http://drops.javaweb.org/uploads/images/8d917a9cedb3adcbb51fb1989fd2432f8e9c96f5.jpg)

0x03 漏洞利用
=========

* * *

由于Double Free不易利用，Pangu Team在其博客文章[http://blog.pangu.io/race_condition_bug_92/](http://blog.pangu.io/race_condition_bug_92/)中提出了另外一种思路，可以稳定地利用Race Condition实现任意代码执行。下面将对这种思路进行具体的分析，在已知Kernel Slide的情况下，在Mac OS X 10.11上实现提权。

### 1. 攻击流程

通过观察操作IORegistryIterator的函数enterEntry，发现其包含向单向链表插入节点的操作，如下：

```
void IORegistryIterator::enterEntry( const IORegistryPlane * enterPlane )
{
    IORegCursor *   prev;

    prev = where;
    where = (IORegCursor *) IOMalloc( sizeof(IORegCursor));
    assert( where);

    if( where) {
        where->iter = 0;
        where->next = prev; //在链表头部插入新的where节点，where->next指向旧where
        where->current = prev->current;
        plane = enterPlane;
    }
}

```

而IORegistryIterator::exitEntry中，包含移除单向链表头部节点的操作，并且释放移除的节点内存。

```
bool IORegistryIterator::exitEntry( void )
{
    IORegCursor *   gone;
…

    if( where != &start) {
      gone = where;   
      where = gone->next; //从链表头部移除当前where节点
        IOFree( gone, sizeof(IORegCursor)); //释放移除的节点内存区域
        return( true);
    } else
        return( false);
…
}

```

在两个线程中分别调用IORegistryIteratorEnterEntry和IORegistryIteratorExitEntry，在特定的执行序列下，可能导致enterEntry在执行where->next = prev;时，prev指向的where区域已经被exitEntry的IOFree释放，就会导致where->next指向被释放的内存。

那么，当第二次调用exitEntry时，就会使得where指向被释放的内存，这块内存通过Heap Spray可以控制其中的内容。

```
bool IORegistryIterator::exitEntry( void )
{
…
    if( where != &start) {
      gone = where; //where->next已指向被释放的区域
      where = gone->next; //where指向被释放的区域
    }
…
}

```

最后，第三次调用exitEntry时，where->iter可控，通过映射用户空间内存iter对象虚表，可实现任意代码执行。

```
bool IORegistryIterator::exitEntry( void )
{
…
    if( where->iter) {  // where->iter可控
    where->iter->release();  //可通过构造虚表，执行任意代码
    where->iter = 0;
    }
…
}

```

攻击流程示意图如下：

![p2](http://drops.javaweb.org/uploads/images/f68a386d6add92701b47ac053210608aa4ad5066.jpg)

### 2. Heap Spray

关于这个漏洞利用的关键是要控制where指向的被释放的内存区域的内容。where是IORegCursor指针，由IOMalloc申请，位于kalloc.32 zone中。

```
struct IORegCursor {
    IORegCursor          *  next;
    IORegistryEntry      *  current;
    OSIterator       *  iter;
};

```

当第二次exitEntry被调用后，where指向的内存区域在kalloc.32的freelist链表中。我们可以通过heap spray kalloc.32，使得位于freelist中的内存重新被填充为我们控制的数据，实现控制where->iter的目的。heap spray的方法就是通过结合`io_service_open_extended`以及OSData，Pangu Team在其POC 2015的议题《Hacking from iOS8 to iOS9》中提到了这种heap spray的方法。

![p3](http://drops.javaweb.org/uploads/images/0348d0cbf5d4a315b7fe5680f7893d233da1d223.jpg)

通过构造特定的XML数据，包含data标签，那么通过`io_service_open_extended`创建任意UserClient，在OSUnserializeXML中反序列化data数据时，就可以通过OSData占用内存，实现任意zone的heap spray。

```
object_t *
buildData(parser_state_t *state, object_t *o)
{
    OSData *data;

    if (o->size) {
        data = OSData::withBytes(o->data, o->size);
    } else {
        data = OSData::withCapacity(0);
    }
    if (o->idref >= 0) rememberObject(state, o->idref, data);

    if (o->size) free(o->data);
    o->data = 0;
    o->object = data;
    return o;
};

```

### 3. 任意代码执行

在用户空间映射两块内存空间，分别放置构造的iter对象以及构造的虚表。将XML中的data的第三个QWORD字段设置为构造的iter对象指针，并进行heap spray。通过heap spray成功控制where指向的内存区域内容后，where->iter可控，最终调用where->iter->release()时就会调用我们构造的虚表中的函数，实现任意代码执行。在已知Kernel Slide的情况下，在10.10.5以及10.11上都成功实现提权，10.10.5如下：

![p4](http://drops.javaweb.org/uploads/images/235ac4a646369032d5a6c759f28930a752bba08c.jpg)

0x04 官方修复
=========

* * *

在10.11.2的XNU源码中，苹果官方进行了修复。新添加了一个IOUserIterator,用于封装IORegistryIterator，对reset操作等加锁，也在enterEntry和exitEntry时加锁，防止多线程调用引起的Race Condition。

```
/* Routine io_registry_iterator_enter */
kern_return_t is_io_registry_iterator_enter_entry(
    io_object_t iterator )
{
    CHECKLOCKED( IORegistryIterator, iterator, iter );

    IOLockLock(oIter->lock);
    iter->enterEntry();
    IOLockUnlock(oIter->lock);

    return( kIOReturnSuccess );
}

/* Routine io_registry_iterator_exit */
kern_return_t is_io_registry_iterator_exit_entry(
    io_object_t iterator )
{
    bool    didIt;

    CHECKLOCKED( IORegistryIterator, iterator, iter );

    IOLockLock(oIter->lock);
    didIt = iter->exitEntry();
    IOLockUnlock(oIter->lock);

    return( didIt ? kIOReturnSuccess : kIOReturnNoDevice );
}

```

0x05 References
===============

* * *

1.  [https://code.google.com/p/google-security-research/issues/detail?id=598](https://code.google.com/p/google-security-research/issues/detail?id=598)
2.  [http://blog.pangu.io/race_condition_bug_92/](http://blog.pangu.io/race_condition_bug_92/)
3.  [http://blog.pangu.io/wp-content/uploads/2015/11/POC2015_RUXCON2015.pdf](http://blog.pangu.io/wp-content/uploads/2015/11/POC2015_RUXCON2015.pdf)