# Android Linker学习笔记

0x00 知识预备
=========

* * *

Linker是Android系统动态库so的加载器/链接器，要想轻松地理解Android linker的运行机制，我们需要先熟悉ELF的文件结构，再了解ELF文件的装入/启动，最后学习Linker的加载和启动原理。

鉴于ELF文件结构网上有很多资料，这里就不做累述了。

0x01 so的加载和启动
=============

* * *

我们知道如果一个APP需要使用某一共享库so的话，它会在JAVA层声明代码：

```
Static{
System.loadLibrary(“name”);
}

```

此代码完成library的加载工作。翻看system.loadLibrary的源代码，可以发现：

System.loadLibrary也是一个native方法，它的调用的过程是：

```
Dalvik/vm/native/java_lang_Runtime.cpp: 
Dalvik_java_lang_Runtime_nativeLoad ->Dalvik/vm/Native.cpp:dvmLoadNativeCode
dvmLoadNativeCode

```

打开函数dvmLoadNativeCode,可以找到以下代码：

```
……..
handle = dlopen(pathName, RTLD_LAZY); //获得指定库文件的句柄,这个handle是soinfo*
//这个库文件就是System.loadLibrary(pathName)传递的参数
…..
vonLoad = dlsym(handle, "JNI_OnLoad"); //获取该文件的JNI_OnLoad函数的地址
   if (vonLoad == NULL) { //如果找不到JNI_OnLoad，就说明这是用javah风格的代码了，那么就推迟解析
 LOGD("No JNI_OnLoad found in %s %p, skipping init",pathName, classLoader); //这句话我们在logcat中经常看见！
}else{
….
}

```

从上面的代码可以看出Android系统加载共享库的关键代码为dlopen函数。这个dlopen函数的代码在bionic/linker/dlfcn.c中：

```
void* dlopen(const char* filename, int flags) {
  ScopedPthreadMutexLocker locker(&gDlMutex); 
  soinfo* result = do_dlopen(filename, flags);
  if (result == NULL) {
    __bionic_format_dlerror("dlopen failed", linker_get_error_buffer());
    return NULL;
  }
  return result;
}

```

此函数主要通过调用`do_dlopen`函数来返回一个动态链接库的句柄，该句柄为一个soinfo结构体。Soinfo结构体的具体定义在`bionic/linker/linker.h`中。

继续查看`do_dlopen`函数，代码在linker.cpp中：

```
soinfo* do_dlopen(const char* name, int flags) {
  if ((flags & ~(RTLD_NOW|RTLD_LAZY|RTLD_LOCAL|RTLD_GLOBAL)) != 0) {
    DL_ERR("invalid flags to dlopen: %x", flags);
    return NULL;
  }
  set_soinfo_pool_protection(PROT_READ | PROT_WRITE);
  soinfo* si = find_library(name); //查找动态链接库
  if (si != NULL) {
    si->CallConstructors();
  }
  set_soinfo_pool_protection(PROT_READ);
  return si;
}

```

显然，重点在`find_library`函数。此函数代码如下：

```
static soinfo* find_library(const char* name) {
  soinfo* si = find_library_internal(name); 
  if (si != NULL) {
    si->ref_count++;
  }
  return si;
}

```

继续往下深入：

```
static soinfo* find_library_internal(const char* name) {
  ……..
  soinfo* si = find_loaded_library(name);  //首先查看这个so是否已经加载，如果已经加载，就返回该so的soinfo
  if (si != NULL) {
    if (si->flags & FLAG_LINKED) {
      return si;
    }
    DL_ERR("OOPS: recursive link to \"%s\"", si->name);
    return NULL;
  }

  TRACE("[ '%s' has not been loaded yet.  Locating...]", name);
  si = load_library(name);  //说明该so没有被加载，就调用此函数进行加载
  if (si == NULL) {
    return NULL;
  }

  // At this point we know that whatever is loaded @ base is a valid ELF
  // shared library whose segments are properly mapped in.
  TRACE("[ find_library_internal base=%p size=%zu name='%s' ]",
        reinterpret_cast<void*>(si->base), si->size, si->name);

  if (!soinfo_link_image(si)) {  //加载完so后，根据si的反馈进行链接。会在第3节进行详细分析
    munmap(reinterpret_cast<void*>(si->base), si->size);
    soinfo_free(si);
    return NULL;
  }

  return si;
}

```

先不去关心那些错误处理信息，我们假设各个函数的返回值均在预期范围内，这个函数的执行流程为：

1.  使用find_loaded_library函数在已经加载的动态链接库链表里面查找该动态库。如果找到了，就返回该动态库的soinfo，否则执行第②步；
2.  此时，说明指定的动态链接库还没有被加载，就使用load_library函数来加载该动态库。

`load_library`函数是整个so加载过程的重中之重！它创建了动态链接库的句柄，代码如下：

```
static soinfo* load_library(const char* name) {
    // Open the file.
    int fd = open_library(name);
    if (fd == -1) {
        DL_ERR("library \"%s\" not found", name);
        return NULL;
    }

    // Read the ELF header and load the segments.
    ElfReader elf_reader(name, fd);
    if (!elf_reader.Load()) {
        return NULL;
    }

    const char* bname = strrchr(name, '/');
    soinfo* si = soinfo_alloc(bname ? bname + 1 : name);
    if (si == NULL) {
        return NULL;
    }
    si->base = elf_reader.load_start();
    si->size = elf_reader.load_size();
    si->load_bias = elf_reader.load_bias();
    si->flags = 0;
    si->entry = 0; //入口函数设为null
    si->dynamic = NULL;
    si->phnum = elf_reader.phdr_count();
    si->phdr = elf_reader.loaded_phdr();
    return si;
}

```

`load_library`函数的执行过程可以概括如下：

1.  使用open_library函数打开指定so文件；
2.  创建ElfReader类对象，并通过该对象的load方法，读取Elf文件头，然后通过分析Elf文件来加载各个segments；
3.  使用soinfo_alloc函数分配一个soinfo结构体，并为这个结构体中的各个成员赋值。

下面对`步骤二`加以详细介绍。

### 1.1 SO文件的读取与加载工作

Linker使用ElfRead类的load函数完成so文件的分析工作。该类的源代码在`linker_phdr.cpp`中。Load函数代码如下：

```
bool ElfReader::Load() {
  return ReadElfHeader() &&
         VerifyElfHeader() &&
         ReadProgramHeader() &&
         ReserveAddressSpace() &&
         LoadSegments() &&
         FindPhdr();
}

```

显然此函数依次调用ReadElfHeader、ReadProgramHeader等函数。

首先，我们需要知道Android系统加载segments的机制：

一个ELF文件的程序头表包含一个或多个`PT_LOAD segments`，这些segments标志ELF文件中需要被映射到进程空间的区域。每一个可以加载的segment都含有如下重要属性：

*   `p_offset`: 段在文件的偏移地址
*   `p_filesz`：段的大小
*   `p_memsz`：段在内存中占据的大小(通常大于p_filesz)。
*   `p_vaddr`： 段的虚拟地址
*   `p_flags`：段的标记(可读，可写，可执行)

当前，我们忽略`p_paddr`和`p_align`成员。

可以加载的segments能在虚拟地址范围`[p_vaddr…p_vaddr+p_memsz)`以列表的形式展现。其中有如下几个规则：

1.  各个segments的虚拟地址范围不可重叠；
2.  如果一个segment的`p_filesz`小于`p_memsz`，那么两者之间的额外数据将被初始化为0；
3.  segment的虚拟地址范围的起、始地址不是必须在某一页的边界。两个不同的segments的起、始地址可以在同一页，在这种情况，该页继承后一segment的映射标记(mapping flags)
4.  每一个segment实际加载的地址并非p`_vaddr`。而是由加载器决定将第一个segment加载到内存中的哪个位置，然后剩下的segments就以第一个segment为参照物，进行加载。比如：

下面是两个loadable segments的信息：

```
[ offset:0,      filesz:0x4000, memsz:0x4000, vaddr:0x30000 ],
[ offset:0x4000, filesz:0x2000, memsz:0x8000, vaddr:0x40000 ],

```

相当于这两个segments的虚拟地址范围分别为:

```
0x30000...0x34000
0x40000...0x48000

```

如果加载器决定将第一个segment加载到0xa0000000的话(通过后面的分析会知道，这个加载地址是在加载程序头部表的时候由系统确定的)，那么它们的实际虚拟地址范围就是：

```
0xa0030000...0xa0034000
0xa0040000...0xa0048000

```

换句话说，所有的segments的实际加载开始地址与其vaddr的偏差值是固定的(0xa0030000 – 0x30000 = 0xa0040000 – 0x40000)。

但是，在实际情况下，segments的地址并不是在每一页的边界出开始的。考虑到我们只能在页面边界进行内存映射，因此，这就意味着加载地址的偏差bias应当按照如下方法进行计算：

```
load_bias = phdr0_load_address - PAGE_START(phdr0->p_vaddr)
(#define PAGE_START(x)  ((x) & PAGE_MASK)  
PAGE_MASK的值一般为0xfffff000。）

```

所以第一个segment的`load_bias`= 0xa0030000 – 0x30000&0xfffff000 = 0xa00000000。

这里`phdr0_load_address`必须以某一页的边界为起始地址，所以该segments的真正内容的开始地址为：

```
phdr0_load_address + PAGE_OFFSET(phdr0->p_vaddr)
(#define  PAGE_OFFSET(x)  ((x) & ~PAGE_MASK)   就是x & 0xfff)

```

注意：ELF要求如下条件，以满足mmap正常工作：

```
PAGE_OFFSET(phdr0->p_vaddr) == PAGE_OFFSET(phdr0->p_offset)

```

每一个loadable segments的`p_vaddr`都必须加上`load_bias`，其和就是该segments在内存中的实际开始地址。

**1.1.1 ReadProgramHeader**

理清了Android加载segments的机制，我们就来看linker中的实际代码，先看ReadProgramHeader:

```
bool ElfReader::ReadProgramHeader() {
phdr_num_ = header_.e_phnum;
  ……..
  ElfW(Addr) page_min = PAGE_START(header_.e_phoff);
  ElfW(Addr) page_max = PAGE_END(header_.e_phoff + (phdr_num_ * sizeof(ElfW(Phdr))));
  ElfW(Addr) page_offset = PAGE_OFFSET(header_.e_phoff);

  phdr_size_ = page_max - page_min;

  void* mmap_result = mmap(NULL, phdr_size_, PROT_READ, MAP_PRIVATE, fd_, page_min);
  ……..
  phdr_mmap_ = mmap_result;
  phdr_table_ = reinterpret_cast<ElfW(Phdr)*>(reinterpret_cast<char*>(mmap_result) + page_offset);
  return true;
}

```

1.  首先读取elf文件的程序头部表项数目`phdr_num`;
2.  然后分别获取程序头部表在页边界对齐后的起始地址`page_min`、结束地址`page_max`和偏移地址`page_offset`。并根据`page_max`与`page_start`计算出程序头部表占据的页面大小`phdr_size`；
3.  再以只读模式建立一个私有映射，该映射将elf文件中偏移值为`page_min`，大小为`phdr_size`的区域映射到内存中。将映射后的内存地址赋给`phdr_mmap_`，简单一句话：将程序头部表映射到内存中，并将内存地址赋值；
4.  `reinterpret_cast<new_type>(expression)`，这是c++中的强制类型转换符，类似于`(new_type*)(expression)`。这里我们对上面红色部分代码加以解释：

(_注:红色代码为倒数第三句_)

首先`reinterpret_cast<char*>(mmap_result)`：经`void*`型指针`mmap_result`强制转换成`char*`型；

然后`reinterpret_cast<char*>(mmap_result) + page_offset`：`char*`型指针+`page_offset`，表示指向程序头部表真正开始的地方；

最后再将其转换成`ElfW(Phdr)*`型指针，显然`phdr_table_`指向程序头部表开始地址。

**1.1.2 ReserveAddressSpace**

再来看ReserveAddressSpace：

```
/*预备一块足够大的虚拟地址范围，用来加载所有可加载的segments.我们可以通过mmap创建一个带有PROT_NONE属性的私有匿名内存映射。PROT_NONE表示页不可访问，匿名映射表示映射区不与任何文件关联(要求fd为-1)，私有映射表示对该映射区域的写入操作会产生一个映射文件的复制，对此区域做的任何修改够不会写会原来的文件*/
bool ElfReader::ReserveAddressSpace() {
  ElfW(Addr) min_vaddr;
  load_size_ = phdr_table_get_load_size(phdr_table_, phdr_num_, &min_vaddr);
  ……..
  uint8_t* addr = reinterpret_cast<uint8_t*>(min_vaddr);
  int mmap_flags = MAP_PRIVATE | MAP_ANONYMOUS;
  void* start = mmap(addr, load_size_, PROT_NONE, mmap_flags, -1, 0);
  ……..
  load_start_ = start;
  load_bias_ = reinterpret_cast<uint8_t*>(start) - addr;
  return true;
}

```

这里有一个关键函数`phdr_table_get_load_siz`：

```
/*返回ELF文件程序头部表中所指定的所有可加载segments(这些segments可能是非连续的)的区间大小，如果没有可加载的segments，就返回0
如果out_min_vaddr 或 out_max_vadd是非空的，它们就会被设置成将被存储的页的最小/大地址(如果没有可加载segments的话，就设为0) */
size_t phdr_table_get_load_size(const ElfW(Phdr)* phdr_table, size_t phdr_count,
                                ElfW(Addr)* out_min_vaddr,
                                ElfW(Addr)* out_max_vaddr) {
  ElfW(Addr) min_vaddr = UINTPTR_MAX;
  ElfW(Addr) max_vaddr = 0;

  bool found_pt_load = false;
  for (size_t i = 0; i < phdr_count; ++i) {
    const ElfW(Phdr)* phdr = &phdr_table[i];
    if (phdr->p_type != PT_LOAD) {
      continue;
    }
    found_pt_load = true;
    if (phdr->p_vaddr < min_vaddr) {
      min_vaddr = phdr->p_vaddr;
    }
    if (phdr->p_vaddr + phdr->p_memsz > max_vaddr) {
      max_vaddr = phdr->p_vaddr + phdr->p_memsz;
    }
  }
  if (!found_pt_load) {
    min_vaddr = 0;
  }

  min_vaddr = PAGE_START(min_vaddr);
  max_vaddr = PAGE_END(max_vaddr);

  if (out_min_vaddr != NULL) {
    *out_min_vaddr = min_vaddr;
  }
  if (out_max_vaddr != NULL) {
    *out_max_vaddr = max_vaddr;
  }
  return max_vaddr - min_vaddr;
}

```

通俗点讲，此函数就是返回ELF文件中包含的可加载segments总共需要占用的空间大小，并设置其最小虚拟地址的值(是页对齐的)。值得注意的是，原函数有4个参数，但是在ReserveAddressSpace中调用该函数时却只传递了3个参数，忽略了`out_max_vaddr`。在我个人看来是因为已知了`out_min_vaddr`及两者的差值`load_size`，所以可以通过`out_min_vaddr + load_size`来求得`out_max_vaddr`。

现在回到ReserveAddressSpace函数。求得`load_size`之后，就需要为这些segments分配足够的内存空间。这里需要注意的是mmap的第一个参数并非为Null，而是addr。这就表示将映射区间的开始地址放在进程的addr地址处(一般不会成功，而是由系统自动分配，所以可以看作是Null)，mmap返回实际映射后的内存开始地址start。显然`load_bias_ = start – addr`就是实际映射内存地址同linker期望的映射地址的误差值。后面的操作中，linker就可以通过`p_vaddr + load_bias_`来获取某一segments在内存中的开始地址了。

**1.1.3 LoadSegments**

现在就开始加载ELF文件中的可加载segments了：

```
bool ElfReader::LoadSegments() {
  for (size_t i = 0; i < phdr_num_; ++i) {
    const ElfW(Phdr)* phdr = &phdr_table_[i];

    if (phdr->p_type != PT_LOAD) {
      continue;
    }

    // Segment addresses in memory.
    ElfW(Addr) seg_start = phdr->p_vaddr + load_bias_;
    ElfW(Addr) seg_end   = seg_start + phdr->p_memsz;

    ElfW(Addr) seg_page_start = PAGE_START(seg_start);
    ElfW(Addr) seg_page_end   = PAGE_END(seg_end);

    ElfW(Addr) seg_file_end   = seg_start + phdr->p_filesz;
    // File offsets.
    ElfW(Addr) file_start = phdr->p_offset;
    ElfW(Addr) file_end   = file_start + phdr->p_filesz;

    ElfW(Addr) file_page_start = PAGE_START(file_start);
    ElfW(Addr) file_length = file_end - file_page_start;

    if (file_length != 0) {
      void* seg_addr = mmap(reinterpret_cast<void*>(seg_page_start),
                            file_length, //是以文件大小为参照，而非内存大小
                            PFLAGS_TO_PROT(phdr->p_flags),
                            MAP_FIXED|MAP_PRIVATE,
                            fd_,
                            file_page_start);
      if (seg_addr == MAP_FAILED) {
        DL_ERR("couldn't map \"%s\" segment %zd: %s", name_, i, strerror(errno));
        return false;
      }
    }

    /*如果segments可写，并且该segments的实际结束地址不在某一页的边界的话，就将该segments实际结束地址到此页的边界之间的内存全置为0*/
    if ((phdr->p_flags & PF_W) != 0 && PAGE_OFFSET(seg_file_end) > 0) {
      memset(reinterpret_cast<void*>(seg_file_end), 0, PAGE_SIZE - PAGE_OFFSET(seg_file_end));
    }

    seg_file_end = PAGE_END(seg_file_end);

    // seg_file_end is now the first page address after the file
    // content. If seg_end is larger, we need to zero anything
    // between them. This is done by using a private anonymous
    // map for all extra pages.
    if (seg_page_end > seg_file_end) {
      void* zeromap = mmap(reinterpret_cast<void*>(seg_file_end),
                           seg_page_end - seg_file_end,
                           PFLAGS_TO_PROT(phdr->p_flags),
                           MAP_FIXED|MAP_ANONYMOUS|MAP_PRIVATE,
                           -1,
                           0);
      if (zeromap == MAP_FAILED) {
        DL_ERR("couldn't zero fill \"%s\" gap: %s", name_, strerror(errno));
        return false;
      }
    }
  }
  return true;
}

```

此部分功能很简单：就是将ELF中的可加载segments依次映射到内存中，并进行一些辅助扫尾工作。

**1.1.4 FindPhdr**

返回程序头部表在内存中地址。这与`phdr_table_`是不同的，后者是一个临时的、在so被重定位之前会为释放的变量：

```
bool ElfReader::FindPhdr() {
  const ElfW(Phdr)* phdr_limit = phdr_table_ + phdr_num_;

  //如果段类型是 PT_PHDR, 那么我们就直接使用该段的地址.
  for (const ElfW(Phdr)* phdr = phdr_table_; phdr < phdr_limit; ++phdr) {
    if (phdr->p_type == PT_PHDR) {
      return CheckPhdr(load_bias_ + phdr->p_vaddr);
    }
  }

  //否则，我们就检查第一个可加载段。如果该段的文件偏移值为0，那么就表示它是以ELF头开始的，我们就可以通过它来找到程序头表加载到内存的地址(虽然过程有点繁琐)。
  for (const ElfW(Phdr)* phdr = phdr_table_; phdr < phdr_limit; ++phdr) {
    if (phdr->p_type == PT_LOAD) {
      if (phdr->p_offset == 0) {
        ElfW(Addr)  elf_addr = load_bias_ + phdr->p_vaddr;
        const ElfW(Ehdr)* ehdr = reinterpret_cast<const ElfW(Ehdr)*>(elf_addr);
        ElfW(Addr)  offset = ehdr->e_phoff;
        return CheckPhdr((ElfW(Addr))ehdr + offset);
      }
      break;
    }
  }

  DL_ERR("can't find loaded phdr for \"%s\"", name_);
  return false;
}

```

要理解这段代码，我们需要知道段类型PT_PHDR所表示的意义：指定程序头表在文件及程序内存映像中的位置和大小。此段类型不能在一个文件中多次出现。此外，仅当程序头表是程序内存映像的一部分时，才可以出现此段。此类型（如果存在）必须位于任何可装入段的各项的前面。有关详细信息，请参见[程序的解释程序](http://docs.oracle.com/cd/E19253-01/819-7050/6n918j8nq/index.html#chapter6-71736)。

至此so文件的读取、加载工作就分析完毕了。我们可以发现，Android对so的**加载操作**只是以段为单位，跟section完全没有关系。另外，通过查看VerifyElfHeader的代码，我们还可以发现，Android系统仅仅对ELF文件头的`e_ident`、`e_type`、`e_version`、`e_machine`进行验证(当然，`e_phnum`也是不能错的)，所以，这就解释了为什么有些加壳so文件头的section相关字段可以任意修改，系统也不会报错了。

### 1.2 so的链接机制

在1.1我们详细分析了Android so的加载机制，现在就开始分析so的链接机制。在分析linker的关于链接的源代码之前，我们需要学习ELF文件关于动态链接方面的知识。

**1.2.1 动态节区**

如果一个目标文件参与动态链接，它的程序头部表将包含类型为`PT_DYNAMIC`的元素。此“段”包含`.dynamic`节区(这个节区是一个数组)。该节区采用一个特殊符号`_DYNAMIC`来标记，其中包含如下结构的数组：

```
typedef struct { 
Elf32_Sword d_tag; 
union { 
Elf32_Word d_val; 
Elf32_Addr d_ptr; 
} d_un; 
} Elf32_Dyn; 
extern Elf32_Dyn _DYNAMIC[]; //注意这里是一个数组
/*注意:
对每个这种类型的对象，d_tag控制d_un的解释含义： 
d_val 此 Elf32_Word 对象表示一个整数值，可以有多种解释。
d_ptr 此 Elf32_Addr 对象代表程序的虚拟地址。
关于d_tag的值、该值的意义，及其与d_un的关系，可查看ELF.PDF  p24。 */

```

该`Elf32_Dyn`数组就是soinfo结构体中的dynamic成员，我们在第2节介绍的`load_library`函数中发现，`si->dynamic`被赋值为null，这就说明，在加载阶段是不需要此值的，只有在链接阶段才需要。Android的动态库的链接工作还是由linker完成，主要代码就是在linker.cpp的`soinfo_link_image`(`find_library_internal`方法中调用)中，此函数的代码相当多，我们来分块分析：

首先，我们需要从程序头部表中获取dynamic节区信息：

```
/*in function soinfo_link_image */    
    /*抽取动态节区*/
    size_t dynamic_count;
    ElfW(Word) dynamic_flags;
    /*这里的si->dynamic 为ElfW(Dyn)指针，就是上面提到的Elf32_Dyn _DYNAMIC[]*/
    phdr_table_get_dynamic_section(phdr, phnum, base, &si->dynamic,
                                   &dynamic_count, &dynamic_flags);

```

此函数很简单：

```
/*返回ELF文件中的dynamic节区在内存中的地址和大小，如果没有该节区就返回null
 * Input:
 *   phdr_table  -> program header table
 *   phdr_count  -> number of entries in tables
 *   load_bias   -> load bias
 * Output:
 *   dynamic       -> address of table in memory (NULL on failure).
 *   dynamic_count -> number of items in table (0 on failure).
 *   dynamic_flags -> protection flags for section (unset on failure)
*/
void phdr_table_get_dynamic_section(const ElfW(Phdr)* phdr_table, size_t phdr_count,
                                    ElfW(Addr) load_bias,
                                    ElfW(Dyn)** dynamic, size_t* dynamic_count, ElfW(Word)* dynamic_flags) {
  const ElfW(Phdr)* phdr = phdr_table;
  const ElfW(Phdr)* phdr_limit = phdr + phdr_count;

  for (phdr = phdr_table; phdr < phdr_limit; phdr++) {
    if (phdr->p_type != PT_DYNAMIC) {
      continue;
    }

    *dynamic = reinterpret_cast<ElfW(Dyn)*>(load_bias + phdr->p_vaddr);
    if (dynamic_count) {
      *dynamic_count = (unsigned)(phdr->p_memsz / 8);
      //这里需要解释下，在2.2.1中我们介绍了Elf32_Dyn的结构，它占8字节。而PT_DYNAMIC段就是存放着Elf32_Dyn数组，所以dynamic_count的值就是该段的memsz/8。
    }
    if (dynamic_flags) {
      *dynamic_flags = phdr->p_flags; 
    }
    return;
  }
  *dynamic = NULL;
  if (dynamic_count) {
    *dynamic_count = 0;
  }
}

```

成功获取了dynamic节区信息，我们就可以根据该节区中的`Elf32_Dyn`数组来进行so链接操作了。我们需要从dynamic节区中抽取有用的信息，linker采用遍历dynamic数组的方式，根据每个元素的flags()进行相应的处理:

```
/*in function soinfo_link_image */ 
    // 从动态dynamic节区中抽取有用信息
    uint32_t needed_count = 0;

    //开始从头遍历dyn数组，根据数组中个元素的标记进行相应的处理
    for (ElfW(Dyn)* d = si->dynamic; d->d_tag != DT_NULL; ++d) { //标记为 DT_NULL 的项目标注了整个 _DYNAMIC 数组的末端，因此以它为结尾标志。 
        ........
        switch (d->d_tag) {
        case DT_HASH:
            ........
            break;
        case DT_STRTAB:
            si->strtab = reinterpret_cast<const char*>(base + d->d_un.d_ptr);
            break;
        case DT_SYMTAB:
            si->symtab = reinterpret_cast<ElfW(Sym)*>(base + d->d_un.d_ptr);
            break;
        case DT_JMPREL:
#if defined(USE_RELA)
            si->plt_rela = reinterpret_cast<ElfW(Rela)*>(base + d->d_un.d_ptr);
#else
            si->plt_rel = reinterpret_cast<ElfW(Rel)*>(base + d->d_un.d_ptr);
#endif
            break;
        case DT_PLTRELSZ:
#if defined(USE_RELA)
            si->plt_rela_count = d->d_un.d_val / sizeof(ElfW(Rela));
#else
            si->plt_rel_count = d->d_un.d_val / sizeof(ElfW(Rel));
#endif
            break;
#if defined(__mips__)
        case DT_PLTGOT:
            // Used by mips and mips64.
            si->plt_got = reinterpret_cast<ElfW(Addr)**>(base + d->d_un.d_ptr);
            break;
#endif
         ........
#if defined(USE_RELA)
         case DT_RELA:
            si->rela = reinterpret_cast<ElfW(Rela)*>(base + d->d_un.d_ptr);
            break;
         case DT_RELASZ:
            si->rela_count = d->d_un.d_val / sizeof(ElfW(Rela));
            break;
        case DT_REL:
            DL_ERR("unsupported DT_REL in \"%s\"", si->name);
            return false;
        case DT_RELSZ:
            DL_ERR("unsupported DT_RELSZ in \"%s\"", si->name);
            return false;
#else
        case DT_REL:
            si->rel = reinterpret_cast<ElfW(Rel)*>(base + d->d_un.d_ptr);
            break;
        case DT_RELSZ:
            si->rel_count = d->d_un.d_val / sizeof(ElfW(Rel));
            break;
         case DT_RELA:
            DL_ERR("unsupported DT_RELA in \"%s\"", si->name);
            return false;
#endif
        case DT_INIT: //只有可执行文件才有此节区
            si->init_func = reinterpret_cast<linker_function_t>(base + d->d_un.d_ptr);
            DEBUG("%s constructors (DT_INIT) found at %p", si->name, si->init_func);
            break;
        case DT_FINI:
            si->fini_func = reinterpret_cast<linker_function_t>(base + d->d_un.d_ptr);
            DEBUG("%s destructors (DT_FINI) found at %p", si->name, si->fini_func);
            break;
        case DT_INIT_ARRAY:
            si->init_array = reinterpret_cast<linker_function_t*>(base + d->d_un.d_ptr);
            DEBUG("%s constructors (DT_INIT_ARRAY) found at %p", si->name, si->init_array);
            break;
        case DT_INIT_ARRAYSZ:
            si->init_array_count = ((unsigned)d->d_un.d_val) / sizeof(ElfW(Addr));
            break;
        case DT_FINI_ARRAY:
            si->fini_array = reinterpret_cast<linker_function_t*>(base + d->d_un.d_ptr);
            DEBUG("%s destructors (DT_FINI_ARRAY) found at %p", si->name, si->fini_array);
            break;
        case DT_FINI_ARRAYSZ: 
            si->fini_array_count = ((unsigned)d->d_un.d_val) / sizeof(ElfW(Addr));
            break;
        case DT_PREINIT_ARRAY:
            si->preinit_array = reinterpret_cast<linker_function_t*>(base + d->d_un.d_ptr);
            DEBUG("%s constructors (DT_PREINIT_ARRAY) found at %p", si->name, si->preinit_array);
            break;
        case DT_PREINIT_ARRAYSZ:
            si->preinit_array_count = ((unsigned)d->d_un.d_val) / sizeof(ElfW(Addr));
            break;
        case DT_TEXTREL:
#if defined(__LP64__)
            DL_ERR("text relocations (DT_TEXTREL) found in 64-bit ELF file \"%s\"", si->name);
            return false;
#else
            si->has_text_relocations = true;
            break;
#endif
        case DT_SYMBOLIC:
            si->has_DT_SYMBOLIC = true;
            break;
        case DT_NEEDED:
            ++needed_count;
            break;
        case DT_FLAGS:
            if (d->d_un.d_val & DF_TEXTREL) {
                ........
                si->has_text_relocations = true;
            }
            if (d->d_un.d_val & DF_SYMBOLIC) {
                si->has_DT_SYMBOLIC = true;
            }
            break;
#if defined(__mips__)
        case DT_STRSZ:
        case DT_SYMENT:
        case DT_RELENT:
             break;
        case DT_MIPS_RLD_MAP:
            // Set the DT_MIPS_RLD_MAP entry to the address of _r_debug for GDB.
            {
              r_debug** dp = reinterpret_cast<r_debug**>(base + d->d_un.d_ptr);
              *dp = &_r_debug;
            }
            break;
        case DT_MIPS_RLD_VERSION:
        case DT_MIPS_FLAGS:
        case DT_MIPS_BASE_ADDRESS:
        case DT_MIPS_UNREFEXTNO:
            break;

        case DT_MIPS_SYMTABNO:
            si->mips_symtabno = d->d_un.d_val;
            break;

        case DT_MIPS_LOCAL_GOTNO:
            si->mips_local_gotno = d->d_un.d_val;
            break;

        case DT_MIPS_GOTSYM:
            si->mips_gotsym = d->d_un.d_val;
            break;
#endif

        default:
            DEBUG("Unused DT entry: type %p arg %p",
                  reinterpret_cast<void*>(d->d_tag), reinterpret_cast<void*>(d->d_un.d_val));
            break;
        }
    }

```

完成dynamic数组的遍历后，就说明我们已经获取了其中的有用信息了，那么现在就需要根据这些信息进行处理：

```
/*in function soinfo_link_image */ 

    //再检测一遍，这种做法总是明智的
    if (relocating_linker && needed_count != 0) {
        DL_ERR("linker cannot have DT_NEEDED dependencies on other libraries");
        return false;
    }
    if (si->nbucket == 0) {
        DL_ERR("empty/missing DT_HASH in \"%s\" (built with --hash-style=gnu?)", si->name);
        return false;
    }
    if (si->strtab == 0) {
        DL_ERR("empty/missing DT_STRTAB in \"%s\"", si->name);
        return false;
    }
    if (si->symtab == 0) {
        DL_ERR("empty/missing DT_SYMTAB in \"%s\"", si->name);
        return false;
    }

    // If this is the main executable, then load all of the libraries from LD_PRELOAD now.
    //如果是main可执行文件，那么就根据LD_PRELOAD信息来加载所有相关的库
    //这里面涉及到的gLdPreloadNames变量，我们知道在前面的整个分析过程中均没有涉及，这是因为，对于可执行文件而言，它的起始函数并不是dlopen，而是系统内核的execv函数，通过层层调用之后才会执行到linker的linker_init_post_ralocation函数，在这个函数中调用parse_LD_PRELOAD函数完成 gLdPreloadNames变量的赋值
    if (si->flags & FLAG_EXE) {
        memset(gLdPreloads, 0, sizeof(gLdPreloads));
        size_t preload_count = 0;
        for (size_t i = 0; gLdPreloadNames[i] != NULL; i++) {
            soinfo* lsi = find_library(gLdPreloadNames[i]);
            if (lsi != NULL) {
                gLdPreloads[preload_count++] = lsi;
            } else {
                ........
            }
        }
    }

    //分配一个soinfo*[]指针数组，用于存放本so库需要的外部so库的soinfo指针
    soinfo** needed = reinterpret_cast<soinfo**>(alloca((1 + needed_count) * sizeof(soinfo*)));
    soinfo** pneeded = needed;
    //依次获取dynamic数组中定义的每一个外部so库soinfo
    for (ElfW(Dyn)* d = si->dynamic; d->d_tag != DT_NULL; ++d) {
        if (d->d_tag == DT_NEEDED) {
            const char* library_name = si->strtab + d->d_un.d_val; //根据index值获取所需库的名字
            DEBUG("%s needs %s", si->name, library_name);
            soinfo* lsi = find_library(library_name);  //获取该库的soinfo
            if (lsi == NULL) {
                ........
            }
            *pneeded++ = lsi;
        }
    }
    *pneeded = NULL; 

#if !defined(__LP64__)
    if (si->has_text_relocations) {
        // Make segments writable to allow text relocations to work properly. We will later call
        // phdr_table_protect_segments() after all of them are applied and all constructors are run.
        DL_WARN("%s has text relocations. This is wasting memory and prevents "
                "security hardening. Please fix.", si->name);
        if (phdr_table_unprotect_segments(si->phdr, si->phnum, si->load_bias) < 0) {
            DL_ERR("can't unprotect loadable segments for \"%s\": %s",
                   si->name, strerror(errno));
            return false;
        }
    }
#endif

#if defined(USE_RELA)
    if (si->plt_rela != NULL) {
        DEBUG("[ relocating %s plt ]\n", si->name);
        if (soinfo_relocate(si, si->plt_rela, si->plt_rela_count, needed)) {
            return false;
        }
    }
    if (si->rela != NULL) {
        DEBUG("[ relocating %s ]\n", si->name);
        if (soinfo_relocate(si, si->rela, si->rela_count, needed)) {
            return false;
        }
    }
#else
    if (si->plt_rel != NULL) {
        DEBUG("[ relocating %s plt ]", si->name);
        if (soinfo_relocate(si, si->plt_rel, si->plt_rel_count, needed)) {
            return false;
        }
    }
    if (si->rel != NULL) {
        DEBUG("[ relocating %s ]", si->name);
        if (soinfo_relocate(si, si->rel, si->rel_count, needed)) {
            return false;
        }
    }
#endif

#if defined(__mips__)
    if (!mips_relocate_got(si, needed)) {
        return false;
    }
#endif

    si->flags |= FLAG_LINKED;
    DEBUG("[ finished linking %s ]", si->name);

#if !defined(__LP64__)
    if (si->has_text_relocations) {
        // All relocations are done, we can protect our segments back to read-only.
        if (phdr_table_protect_segments(si->phdr, si->phnum, si->load_bias) < 0) {
            DL_ERR("can't protect segments for \"%s\": %s",
                   si->name, strerror(errno));
            return false;
        }
    }
#endif

    /* We can also turn on GNU RELRO protection */
    if (phdr_table_protect_gnu_relro(si->phdr, si->phnum, si->load_bias) < 0) {
        DL_ERR("can't enable GNU RELRO protection for \"%s\": %s",
               si->name, strerror(errno));
        return false;
    }

    notify_gdb_of_load(si);
    return true;
}

```

0x02 开始执行so文件
=============

* * *

上面的`find_library_internal`函数中的`soinfo_link_image`函数执行完后就返回到上层函数`find_library`中，然后进一步返回到`do_dlopen`函数：

```
soinfo* do_dlopen(const char* name, int flags) {
  if ((flags & ~(RTLD_NOW|RTLD_LAZY|RTLD_LOCAL|RTLD_GLOBAL)) != 0) {
    DL_ERR("invalid flags to dlopen: %x", flags);
    return NULL;
  }
  set_soinfo_pool_protection(PROT_READ | PROT_WRITE);
  soinfo* si = find_library(name);
  if (si != NULL) {
    si->CallConstructors();
  }
  set_soinfo_pool_protection(PROT_READ);
  return si;
}

```

如果获取的si不为空，就说明so的加载和链接操作正确完成，那么就可以执行so的初始化构造函数了：

```
void soinfo::CallConstructors() {
  ........
  // DT_INIT should be called before DT_INIT_ARRAY if both are present.
  //如果文件含有.init和.init_array节区的话，就先执行.init节区的代码再执行.init_array节区的代码
  CallFunction("DT_INIT", init_func);  
  CallArray("DT_INIT_ARRAY", init_array, init_array_count, false);
}

```

由于我们只分析so库，所以只需要关心`CallArray("DT_INIT_ARRAY", init_array, init_array_count, false)`函数即可：

```
void soinfo::CallArray(const char* array_name UNUSED, linker_function_t* functions, size_t count, bool reverse) {
  ........
  //这里的recerse变量用于指定.init_array中的函数是由前到后执行还是由后到前执行。默认是由前到后
  int begin = reverse ? (count - 1) : 0;
  int end = reverse ? -1 : count;
  int step = reverse ? -1 : 1;

  for (int i = begin; i != end; i += step) {
    TRACE("[ %s[%d] == %p ]", array_name, i, functions[i]);
    CallFunction("function", functions[i]); //依次调用init_array中的函数。
  }
 ........
}

```

这里需要对`init_array`节区的结构和作用加以说明。

首先是`init_array`节区的数据结构。该节中包含指针，这些指针指向了一些初始化代码。这些初始化代码一般是在main函数之前执行的。在C++程序中，这些代码用来运行静态构造函数。另外一个用途就是有时候用来初始化C库中的一些IO系统。使用IDA查看具有`init_array`节区的so库文件就可以找到如下数据：

![p1](http://drops.javaweb.org/uploads/images/3187836bcb11b17441221a8a54b444be301ff174.jpg)

这里共三个函数指针，每个指针指向一个函数地址。值得注意的是，上图中每个函数指针的值都加了1，这是因为地址的最后1位置1表明需要使得处理器由ARM转为Thumb状态来处理Thumb指令。将目标地址处的代码解释为Thumb代码来执行。

然后再来看CallFunction的具体实现：

```
void soinfo::CallFunction(const char* function_name UNUSED, linker_function_t function) {
  //如果函数地址为空或者为-1就直接退出。
  if (function == NULL || reinterpret_cast<uintptr_t>(function) == static_cast<uintptr_t>(-1)) {
    return;
  }
  ........
  function(); //执行该指针所指定的函数
  // The function may have called dlopen(3) or dlclose(3), so we need to ensure our data structures
  // are still writable. This happens with our debug malloc (see http://b/7941716).
  set_soinfo_pool_protection(PROT_READ | PROT_WRITE);
}

```

至此，整个Android so的linker机制就分析完毕了！