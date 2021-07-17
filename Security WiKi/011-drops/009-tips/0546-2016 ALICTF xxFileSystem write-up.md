# 2016 ALICTF xxFileSystem write-up

0x00 介绍
=======

* * *

这是关于文件系统的一个题，给了程序和数据，比赛时是分成了两部分，第一部分是需要我们恢复删除的文件，第二部分是需要解密加了密的文件。比赛完时有挺多队把第一部分解出，但第二部分只有PPP解出，我赛后在队友wxy前期的分析和出题人的帮助下才解了出来，这里仅做一个分享，各位大大忽喷。

0x01 恢复文件
=========

* * *

第一部分的题是恢复删除的文件，删除文件的函数为0x4018FC

```
__int64 __fastcall rm_func(MemStruct *system, char *arg)
{
  char dir_flag; // [sp+13h] [bp-1Dh]@1
  signed int mask; // [sp+14h] [bp-1Ch]@9
  char *filename; // [sp+18h] [bp-18h]@4
  inodeSt *filenode; // [sp+20h] [bp-10h]@9
  __int64 v7; // [sp+28h] [bp-8h]@1

  v7 = *MK_FP(__FS__, 40LL);
  dir_flag = 0;
  if ( *(arg + 1) && !strcmp(**(arg + 1), "-r") )
    dir_flag = 1;
  filename = *arg;
  if ( arg_filter(filename, off_6082C0) ^ 1 )
  {
    puts(" error");
  }
  else if ( !strcmp(filename, ".") || !strcmp(filename, "..") )
  {
    puts(" error");
  }
  else
  {
    filenode = find_filenode(system, *&system->pwd_node, filename, &mask);
    if ( filenode )
    {
      if ( filenode->is_dir && dir_flag != 1 )
      {
        puts(" error (add -r please)");
      }
      else if ( rm_filenode(system, filenode) )
      {
        *(*&system->pwd_node + 0x60LL) &= ~(1 << mask);
        --*(*&system->pwd_node + 0x64LL);
      }
    }
    else
    {
      puts(" error");
    }
  }
  return *MK_FP(__FS__, 40LL) ^ v7;
}

```

这个函数主要的操作是根据文件名找到对应的文件节点，然后调用真正的删除函数0x40168F

```
signed __int64 __fastcall rm_filenode(MemStruct *system, inodeSt *filenode)
{
  signed int i; // [sp+10h] [bp-20h]@4
  signed int dir_mask; // [sp+14h] [bp-1Ch]@4
  signed int j; // [sp+18h] [bp-18h]@12
  signed int file_mask; // [sp+1Ch] [bp-14h]@12

  if ( check_password(system, filenode) ^ 1 )
    return 0LL;
  if ( filenode->is_dir )
  {
    dir_mask = *&filenode->mask >> 2;
    for ( i = 2; i <= 23; ++i )
    {
      if ( dir_mask & 1 )
      {
        if ( rm_filenode(system, (system->disk + (*(&filenode->id + i) << 9))) ^ 1 )
          return 0LL;
        *&filenode->mask &= ~(1 << i);
        --*&filenode->size;
      }
      dir_mask >>= 1;
    }
    used_table[*&filenode->id] = 0;
    adjust_used_table(system, *&filenode->id);
  }
  else
  {
    file_mask = *&filenode->mask >> 2;
    for ( j = 2; j <= 23; ++j )
    {
      if ( file_mask & 1 )
      {
        used_table[*(&filenode->id + j)] = 0;
        *&filenode->mask &= ~(1 << j);
        *&filenode->size -= 0x200LL;
        used_table[*(&filenode->id + j)] = 0;
        adjust_used_table(system, *(&filenode->id + j));
        if ( *&filenode->size < 0 )
          *&filenode->size = 0LL;
        if ( !*&filenode->size )
          break;
      }
      file_mask >>= 1;
    }
    if ( *&filenode->size > 0LL && rm_filenode(system, (system->disk + (*&filenode->parent_filenode_id << 9))) ^ 1 )
      return 0LL;
    used_table[*&filenode->id] = 0;
    adjust_used_table(system, *&filenode->id);
  }
  return 1LL;
}

```

这个函数首先会判断这个文件节点是否为目录，如果是目录就循环删除目录中的文件，如果是文件则循环删除文件块，通过分析可以知道文件头的格式

| 偏移 | 目录 | 文件 |
| :-: | :-: | :-: |
| 0x0-0x3 | 当前节点的id | 同目录 |
| 0x4-0x7 | 上级目录的id | 0xFFFFFFFF |
| 0x8-0x5F | 包含文件的id(每4个字节) | 包含文件块的id(每4个字节) |
| 0x60-0x63(mask) | 之前每4个字节的id是否有效(0x8开始) | 同目录 |
| 0x64-0x67(size) | 包含文件的个数 | 文件大小(每个块512字节) |
| 0x68-0x6B | 00000000 | 同目录 |
| 0x6C-～ | 目录名 | 文件名 |
| 0x16C | 0x01 | 0x00 |
| 0x16D-0x170(type) | 第0位置1表示隐藏，第3位置1表示加密 | 同目录 |
| 0x171-0x172 | password的md5值的前2个字节 | 同目录 |

从删除文件可以看出，它只是把used_table中id对应的值置0，并把size和mask中的有效位清0，通过这些分析可以得出被删除文件的一些特征：

*   当前节点的id在used_table中的值为0
*   mask为0x03
*   size为0

由于文件的0x4-0x7为0xFFFFFFFF，再加上之前的一些特征就可以搜索出被删除文件的文件名，代码如下

```
from pwn import *

file = open('xxdisk.bin', 'rb')
data = file.read()
used_table = data[0:0x4e20]
str_data = ''.join(data[0x5024:])
index = 0
filenames = []
while True:
    if index != -1:
        index = str_data.find('\xff\xff\xff\xff', index + 1)
        used_table_index = u32(str_data[index-4:index])
        if used_table_index < 0x4e20 and used_table[used_table_index] == '\x00':
            filename = ''
            filename_index = index - 4 + 0x6c
            while str_data[filename_index] != '\x00':
                filename += str_data[filename_index]
                filename_index += 1
            filenames.append(filename)
    else:
        break

print filenames

```

搜索出的结果如下图

![search_result](http://drops.javaweb.org/uploads/images/58e73df19ee2023c61a63e214fb766d4fe8e34c9.jpg)

发现了一个奇怪的名为555的文件，根据它的文件块id提取出这个文件

```
file = open('xxdisk.bin', 'rb')
data = file.read()
out = open('extract', 'wb')
ids = [0x333, 0x32c, 0x32d, 0x324, 0x326, 0x325]

for file_id in ids:
    out.write(data[0x5024+(file_id<<9):0x5024+(file_id<<9)+512])

out.close()

```

提取出来是一个tar包，解压后得到一个名为555的文件，cat一下在最后得到flag

![get_flag1](http://drops.javaweb.org/uploads/images/f970b0548d449d0538ea48b0dfca738d166ffbf0.jpg)

0x02 解密文件
=========

* * *

第二部分的题是解密加了密的文件，首先搜索xxdisk.bin可以发现有一个flag.file的加密文件，通过查看type可以知道是一个加密的文件，因此需要分析加密函数0x402B04

```
__int64 __fastcall crypt_func(MemStruct *system, const char **filename_arg)
{
  unsigned int pass_len; // eax@10
  const char *filename; // [sp+10h] [bp-130h]@1
  inodeSt *filenode; // [sp+18h] [bp-128h]@4
  char input_password_md5; // [sp+20h] [bp-120h]@10
  char password; // [sp+30h] [bp-110h]@8
  __int64 v8; // [sp+138h] [bp-8h]@1

  v8 = *MK_FP(__FS__, 40LL);
  filename = *filename_arg;
  if ( !strcmp(*filename_arg, ".") || !strcmp(filename, "..") )
  {
    puts(" error");
  }
  else
  {
    filenode = find_file(system, *&system->pwd_node, filename);
    if ( filenode )
    {
      if ( *&filenode->filetype & 8 )
      {
        puts(" error");
      }
      else
      {
        printf("password:", filename_arg);
        fflush(0LL);
        readln(&password, 256, '\n');
        if ( strlen(&password) > 5 )
        {
          pass_len = strlen(&password);
          md5(&password, pass_len, &input_password_md5);
          *&filenode->pass_md5 = *&input_password_md5;// 前两个字节
          *&filenode->filetype |= 8u;
          do_crypt(system, filenode, &password, *(*&system->pwd_node + 4LL));
        }
        else
        {
          puts(" error");
        }
      }
    }
    else
    {
      puts(" error");
    }
  }
  return *MK_FP(__FS__, 40LL) ^ v8;
}

```

它会计算password的md5值，然后把前两个字节存储到0x171-0x172，在把0x16D-0x170的值或8，然后进行加密操作0x4027AF

```
__int64 __fastcall do_crypt(MemStruct *system, inodeSt *filenode, char *pass_arg, unsigned __int16 parent_filenode_id_arg)
{
  char *password; // ST18_8@1
  unsigned __int16 parent_filenode_id; // ST14_2@1
  char key; // [sp+20h] [bp-20h]@1
  __int64 v8; // [sp+38h] [bp-8h]@1

  password = pass_arg;
  parent_filenode_id = parent_filenode_id_arg;
  v8 = *MK_FP(__FS__, 40LL);
  memset(&key, 0, 10uLL);
  sprintf(
    &key,
    "%c%c%c%c%04x",
    *password,
    password[1],
    password[2],
    password[3],
    *&filenode->pass_md5 + parent_filenode_id);
  des_key_init(&key);
  if ( filenode->is_dir )
    crypt_head(filenode);
  else
    crypt_all(system, filenode);
  return *MK_FP(__FS__, 40LL) ^ v8;
}

```

这个函数先是初始化key，`key=password[0:4]+(int(md5(password)[0:2])+parent_node_id)`，然后如果是文件夹就仅仅加密文件头0x00-0x68，如果是文件就加密文件内容和头部。

完整的加密步骤是：

1.  filenode[0x171-0x172] = md5(password)[0:2]
2.  filenode[0x16D-0x170] |= 8
3.  key = password[0:4] + (int(md5(password)[0:2]) + parent_node_id)
4.  des_key_init(key)
5.  如果是文件夹则加密filenode[0x00-0x68]，如果是文件则加密文件块内容和filenode[0x00-0x68]
6.  每组8字节进行des加密

> 注意：这里的DES是非标准的

因此我们要做的就是爆破password[0:4]和parent_node_id，我先尝试解开了flag-door，然后发现里面是三个加了密的文件夹，又解密了其中一个文件夹，发现里面又是三个加了密的文件夹，于是猜测flag.file是位于这些加了密的文件夹里的，所以parent_node_id就是这些加了密的文件夹的id，后来又发现有些加了密的文件夹是空的（很容易判断。。。），可以剔除掉这些，下面进行搜索

```
file = open('xxdisk.bin', 'rb')
data = file.read()
indexes = []

for i in xrange(len(data)):
    if data[i] == '\x01' and data[i+1] == '\x08':
        start = i - 0x16c
        offset1 = start + 8
        offset2 = offset1 + 0x10
        offset7 = offset2 + 0x50
        if data[offset1] != data[offset2] and data[offset7] == '\x00':
            indexes.append((start - 0x5024) / 512)

print indexes

```

搜索结果如下图

![search_ids](http://drops.javaweb.org/uploads/images/b71ace1eb58aa7c8c8fda0a7ea224a5a3451803e.jpg)

接下来就是爆破出加密flag.file的key，由于不是标准的DES，我抽取的代码也有问题，所以我直接patch程序，把main函数改为了下面这样

![patched_main](http://drops.javaweb.org/uploads/images/e700ac5b3364eefcb7718f48caf0120bddacf932.jpg)

print_char_table是数字+字母+下划线，indexes是上面搜索出的id，这里可以把第一个for循环分块处理，这样可以比较快地跑出key

```
./xxFileSystem_patch_1 `echo -n '\x82\xA7\x1D\xDE\x4D\xB6\x74\xB6'` `echo -n '\xd4\x02\x00\x00\xff\xff\xff\xff'`
Wh4tfab0
Wh4vfab0
Wh4Tfab0
Wh4Vfab0

```

这样就知道了flag.file的parent_node_id为0x210，接下来就是解密这个文件，有4个key，随便取一个就行，解密时可以把flag.file挂载到根目录，就是把根目录的parent_node_id改为0x210，把0x2d4(flag.file的id)加到目录的文件id中，并把mask的有效位和size都设置正确，然后动态调试下断点解密，你们懂的，解密出来之后cat，在最后得到下一部分的文件名

![cat_flag.file](http://drops.javaweb.org/uploads/images/3e544674f01258f67572a1b8f17c393e97f5eada.jpg)

查看xx_0.0_xx的type发现它是一个隐藏了的加密文件，用之前的方法爆破出key为`B4d_a8bc`，然后把type改为0x8，挂载到根目录，相同的方法解密出xx_0.0_xx是一个tar包，解压得到一个aes.cc的文件，cat一下得到flag

![get_flag2](http://drops.javaweb.org/uploads/images/97a0d3cc5188b7814717c923f42299741871a62d.jpg)

0x03 总结
=======

* * *

收获挺多的，增强了我patch的能力，但是还有很长的路要走。。。