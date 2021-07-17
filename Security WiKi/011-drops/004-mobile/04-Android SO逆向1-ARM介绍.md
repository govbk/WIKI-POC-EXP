# Android SO逆向1-ARM介绍

0x00 概述
=======

* * *

把之前学习SO逆向的笔记分享出来，内容比较简单，大牛就可以略过了。

0x01 ARM寄存器
===========

* * *

1.1.通用寄存器
---------

```
1.未分组寄存器:R0~R7
2.分组寄存器:R8~812
R13:SP，常用作堆栈指针，始终指向堆栈的顶部，当一个数据(32位)推入堆栈时，SP(R13的值减4)向下浮动指向下一个地址，即新的栈顶，当数据从堆栈中弹出时，SP(R13的值加4)向上浮动指向新的栈顶。
R14:连接寄存器(LR),当执行BL子程序调用指令时，R14中得到R15(程序计数器PC)的备份，其他情况下，R14用作通用寄存器。
R15:程序计数器(PC):用于控制程序中指令的执行顺序。正常运行时，PC指向CPU运行的下一条指令。每次取值后PC的值会自动修改以指向下一条指令，从而保证了指令按一定的顺序执行。当程序的执行顺序发生改变(如转移)时，需要修改PC的值。

```

1.2.状态寄存器
---------

```
CPSR(R16):当前程序状态寄存器，用来保存ALU中的当前操作信息，控制允许和禁止中断、设置处理器的工作模式等。
SPSRs:五个备份的程序状态寄存器，用来进行异常处理。当异常发生时，SPSR用于保存CPSR的当前值，从异常退出时可由SPSR来恢复CPSR。

```

![img](http://drops.javaweb.org/uploads/images/192fc06fce1ad9cbef7e028fcd4e542898cc6965.jpg)

N、Z、C、V均为条件码标志位，他们的内容可被运算的结果所改变。

```
N:正负标志，N=1表示运算的结果为负，N=0表示运算的结果为正或0
Z:零标志，Z=1表示运算的结果为0，Z=0表示运算的结果为非0
C:进位标志，加法运算产生了进位时则C=1，否则C=0
  借位标志，减肥运算产生了借位则C=0，否则C=1
V:溢出标志，V=1表示有溢出，V=0表示无溢出

```

1.3.地址空间
--------

```
程序正常执行时，每执行一条ARM指令，当前指令计数器增加4个字节。

```

0x02 汇编语言
=========

* * *

2.1.汇编指令格式
----------

```
<opcode>{<cond>}{S}<Rd>,<Rn>{,<OP2>}
格式中<>的内容必不可少，{}中的内容可省略
<opcode>:表示操作码，如ADD表示算术加法
{<cond>}:表示指令执行的条件域，如EQ、NE等。
{S}:决定指令的执行结果是否影响CPSR的值，使用该后缀则指令执行的结果影响CPSR的值，否则不影响
<Rd>:表示目的寄存器
<Rn>:表示第一个操作数，为寄存器
<op2>:表示第二个操作数，可以是立即数、寄存器或寄存器移位操作数





例子：ADDEQS R0,R1,#8;其中操作码为ADD,条件域cond为EQ,S表示该指令的执行影响CPSR寄存器的值，目的寄存器Rd为R0,第一个操作数寄存器Rd为R1，第二个操作数OP2为立即数#8

```

2.2.指令的可选后缀
-----------

```
S：指令执行后程序状态寄存器的条件标志位将被刷新
    ADDS R1,R0,#2
!:指令中的地址表达式中含有!后缀时，指令执行后，基址寄存器中的地址值将发生变化，变化的结果是：基址寄存器中的值(指令执行后)=指令执行前的值 + 地址偏移量
    LDR R3,[R0,#2]!    指令执行后，R0 = R0 + 2

```

2.3.指令的条件执行
-----------

```
指令的条件后缀只是影响指令是否执行，不影响指令的内容

```

| 条件码 | 助记符后缀 | 标志 | 含义 |
| --- | --- | --- | --- |
| 0000 | EQ | Z置位 | 相等 |
| 0001 | NE | Z清零 | 不相等 |
| 0010 | CS | C指令 | 无符号数大于或等于 |
| 0011 | CC | C清零 | 无符号数小于 |
| 0100 | MI | N置位 | 负数 |
| 0101 | PL | N清零 | 正数或零 |
| 0110 | VS | V置位 | 溢出 |
| 0111 | VC | V清零 | 未溢出 |
| 1000 | HI | C置位Z清零 | 无符号数大于 |
| 1001 | LS | C清零Z置位 | 无符号数小于或等于 |
| 1010 | GE | N等于V | 带符号数大于或等于 |
| 1011 | LT | N不等于V | 带符号数小于 |
| 1100 | GT | Z清零且(N等于V) | 带符号数大于 |
| 1101 | LE | Z置位或(N不等于V) | 带符号数小于或等于 |
| 1110 | AL | 忽略 | 无条件执行 |

例子：ADDEQ R4,R3,#1 相等则相加，即CPSR中Z置位时该指令执行，否则不执行。

2.4.ARM指令分类
-----------

| 助记符 | 指令功能描述 | 助记符 | 指令功能描述 |
| --- | --- | --- | --- |
| ADC | 带进位加法指令 | MRC | 从协处理器寄存器到ARM寄存器的数据传输指令 |
| ADD | 加法指令 | MRS | 传送CPSR或SPSR的内容到通用寄存器指令 |
| AND | 逻辑与指令 | MSR | 传送通用寄存器到CPSR或SPSR的指令 |
| B | 分支指令 | MUL | 32位乘法指令 |
| BIC | 位清零指令 | MLA | 32位乘加指令 |
| BL | 带返回的分支指令 | MVN | 数据取反传送指令 |
| BLX | 带返回和状态切换的分支指令 | ORR | 逻辑或指令 |
| BX | 带状态切换的分支指令 | RSB | 逆向减法指令 |
| CDP | 协处理器数据操作指令 | RSC | 带错位的逆向减法指令 |
| CMN | 比较反值指令 | SBC | 带错位减法指令 |
| CMP | 比较指令 | STC | 协处理器寄存器写入存储器指令 |
| EOR | 异或指令 | STM | 批量内存字写入指令 |
| LDC | 存储器到协处理器的数据传输指令 | STR | 寄存器到存储器的数据存储指令 |
| LDM | 加载多个寄存器指令 | SUB | 减法指令 |
| LDR | 存储器到寄存器的数据加载指令 | SWI | 软件中断指令 |
| MCR | 从ARM寄存器到协处理器寄存器的数据传输指令 | TEQ | 相等测试指令 |
| MOV | 数据传送指令 | TST | 位测试指令 |

2.5.ARM寻址方式
-----------

```
寻址方式就是根据指令中操作数的信息来寻找操作数实际物理地址的方式

```

### 2.5.1立即数寻址

```
MOV R0,#15       #15就是立即数

```

### 2.5.2寄存器寻址

```
ADD R0, R1, R2    将R1和R2的内容相加，其结果存放在寄存器R0中

```

### 2.5.3寄存器间接寻址

```
LDR R0, [R4]      以寄存器R4的值作为操作数的地址，在存储器中取得一个操作数存入寄存器R0中

```

### 2.5.4寄存器移位寻址

```
ADD R0,R1,R2,LSL #1    将R2的值左移一位，所得值与R1相加，存放到R0中
MOV R0,R1,LSL R3    将R1的值左移R3位，然后将结果存放到R0中

```

### 2.5.5基址变址寻址

```
LDR R0,[R1,#4]    将R1的值加4作为操作数的地址，在存储器中取得操作数放入R0中
LDR R0,[R1,#4]!   将R1的值加4作为操作数的地址，在存储器中取得操作数放入R0中,然后R1 = R1+4
LDR R0,[R1],#4    R0 = [R1],R1 = R1 +4
LDR R0,[R1,R2]   R0 = [R1+R2]

```

### 2.5.6.多寄存器寻址

```
一条指令可以完成多个寄存器值的传送(最多可传送16个通用寄存器)，连续的寄存器用“-”，否则用“，”
LDMIA R0!,{R1 - R4}   R1 = [R0],R2=[R0+4],R3=[R0+8],R4=[R0+12]
后缀IA表示在每次执行玩加载/存储操作后，R0按自长度增加。

```

### 2.5.7.相对寻址

```
以程序计数器PC的当前值为基地址，指令中的地址标号作为偏移量，将两者相加之后得到操作数的有效地址，如下图的BL分支跳转
     BL proc        跳转到子程序proc处执行
     ...
proc MOV R0,#1
     ...

```

### 2.5.8.堆栈寻址

```
按先进先出的方式工作，堆栈指针用R13表示，总是指向栈顶，LDMFD和STMFD分别表示POP出栈和PUSH进栈
STMFD R13!,{R0 - R4};
LDMFD R13!,{R0 - R4};

```

2.6.数据处理指令
----------

### 2.6.1. MOV指令

```
MOV {<cond>}{S} Rd,op2          将op2传给Rd
MOV R1, R0          将寄存器R0的值传到寄存器R1
MOV PC,R14          将寄存器R14的值传到PC，常用于子程序返回
MOV R1,R0,LSL #3    将寄存器R0的值左移3位后传给R1
MOV R0,#5           将立即数5传给R0

```

### 2.6.2. MVN指令

```
MVN {<cond>}{S}Rd, op2          将op2取反传给Rd
MVN R0,#0           将0取反后传给R0，R0 = -1
MVN R1,R2           将R2取反，结果保存到R1

```

### 2.6.3. 移位指令

```
LSL 逻辑左移
LSR 逻辑右移
ASR 算术右移
ROR 循环右移
RRX 带扩展的循环右移

```

### 2.6.4. ADD加法指令

```
ADD{<cond>}{S}Rd, Rn, op2
ADD R0,R1,R2            R0 = R1 + R2
ADD R0,R1,#5            R0 = R1 + 5
ADD R0,R1,R2,LSL #2     R0 = R1 + (R2左移2位)

```

### 2.6.5. ADC带进位加法指令

```
ADC{<cond>}{S} Rd,Rn,op2    将Rn的值和操作数op2相加，再加上CPSR中C条件标志位的值，并将结果保存到Rd中
例：用ADC完成64位加法，设第一个64位操作数保存在R2,R3中，第二个64位操作数放在R4,R5中，结果保存在R0,R1中
ADDS R0,R2,R4       低32位相加，产生进位
ADC R1,R3,R5        高32位相加，加上进位

```

### 2.6.6. SUB减法指令

```
SUB{<cond>}{S} Rd,Rn,op2    Rd = Rn - op2
SUB R0,R1,R2            R0 = R1 - R2
SUB R0,R1,#6            R0 = R1 -6
SUB R0,R2,R3,LSL #1     R0 = R2 - (R3左移1位)

```

### 2.6.7. SBC带借位减法指令

```
SBC{<cond>}{S} Rd,Rn,op2    把Rn的值减去操作数op2，再减去CPSR中的C标志位的反码，并将结果保存到Rd中，Rd = Rn - op2 - !C
例:用SBC完成64位减法，设第一个64位操作数保存在R2,R3中，第二个64位操作数放在R4,R5中，结果保存在R0,R1中
SUBS R0,R2,R4       低32位相减，S影响CPSR
SBC R1,R3,R5        高32位相减，去除C的反码

```

### 2.6.8. RSC带借位的逆向减法指令

```
RSC{<cond>}{S} Rd,Rn,op2    把操作数op2减去Rn，再减去CPSR中的C标志位的反码，并将结果保存到Rd中，Rd = op2 - Rn - !C

```

### 2.6.9. 逻辑运算指令

```
AND{<cond>}{S} Rd,Rn,op2    按位与，Rd = Rn AND op2
ORR{<cond>}{S} Rd,Rn,op2    按位或，Rd = Rn OR op2
EOR{<cond>}{S} Rd,Rn,op2    按位异或，Rd = Rn EOR op2

```

### 2.6.10. CMP比较指令

```
CMP{<cond>}{S} Rd,Rn,op2    将Rn的值和op2进行比较，同时更新CPSR中条件标志位的值(实际上是执行一次减法，但不存储结果)，当操作数Rn大于op2时，则此后带有GT后缀的指令将可以执行(根据相应的指令判断是否执行，如GT,LT等)。
CMP R1,#10                  比较R1和10，并设置CPSR的标志位
ADDGT R0,R0,#5              如果R1>10,则执行ADDGT指令，将R0加5

```

### 2.6.11. CMN反值比较指令

```
CMN{<cond>}{S} Rd,Rn,op2    将Rn的值和op2取反后进行比较，同时更新CPSR中条件标志位的值(实际上将Rn和op2相加)，后面的指令就可以根据条件标志位决定是否执行。  
CMN R0,R1       将R0和R1相加，并设置CPSR的值

```

### 2.6.12. MUL/MLA/SMULL/SMLAL/UMULL/UMLAL乘法指令

```
MUL     32位乘法指令
MLA     32位乘加指令
SMULL   64位有符号数乘法指令
SMLAL   64位有符号数乘加指令
UMULL   64位无符号数乘法指令
UMLAL   64位无符号数乘加指令
MUL{<cond>}{S} Rd,Rm,Rs         Rd = Rm * Rs
MULS R0,R1,R2
MLA{<cond>}{S} Rd,Rm,Rs,Rn      Rd = (Rm * Rs) + Rn
MLAS R0,R1,R2,R3

```

2.7.数据加载与存储指令
-------------

| 助记符 | 说明 | 操作 |
| --- | --- | --- |
| LDR{}Rd，addr | 加载字数据 | Rd = [addr] |
| LDRB{}Rd，addr | 加载无符号字节数据 | Rd = [addr] |
| LDRT{}Rd，addr | 以用户模式加载字数据 | Rd = [addr] |
| LDRBT{}Rd，addr | 以用户模式加载无符号字节数据 | Rd = [addr] |
| LDRH{}Rd，addr | 加载无符号半字数据 | Rd = [addr] |
| LDRSB{}Rd，addr | 加载有符号字节数据 | Rd = [addr] |
| LDRSH{}Rd，addr | 加载有符号半字数据 | Rd = [addr] |
| STR{}Rd，addr | 存储字数据 | [addr] = Rd |
| STRB{}Rd，addr | 存储字节数据 | [addr] = Rd |
| STRT{}Rd，addr | 以用户模式存储字数据 | [addr] = Rd |
| STRBT{}Rd，addr | 以用户模式存储字节数据 | [addr] = Rd |
| STRH{}Rd，addr | 存储半字数据 | [addr] = Rd |
| LDM{}{type}Rn{!}，regs | 多寄存器加载 | reglist = [Rn...] |
| STM{}{type}Rn{!}，regs | 多寄存器存储 | [Rn...] = reglist |
| SWP{}Rd,Rm,[Rn] | 寄存器和存储器字数据交换 | Rd=[Rn],[Rn]=Rm(Rn!=Rd或Rm) |
| SWP{}B Rd,Rm,[Rn] | 寄存器和存储器字节数据交换 | Rd = [Rn],[Rn] = Rm(Rn!=Rd或Rm) |

### 2.7.1. LDR/STR字数据加载/存储指令

```
LDR/STR{<cond>}{T}Rd,addr       LDR指令用于从存储器中将一个32位的字数据加载到目的寄存器Rd中，当程序计数器PC作为目的寄存器时，指令从存储器中读取的字数据被当做目的地址，从而可以实现程序流程的跳转。
STR指令用于从源寄存器中将一个32位的字数据存储到存储器中，和LDR相反。后缀T可选。
LDR R4,START            将存储地址为START的字数据读入R4
STR R5,DATA1            将R5存入存储地址为DATA1中
LDR R0,[R1]             将存储器地址为R1的字数据读入存储器R0
LDR R0,[R1,R2]          将存储器地址为R1+R2的字数据读入存储器R0
LDR R0,[R1,#8]          将存储器地址为R1+8的字数据读入存储器R0
LDR R0,[R1,R2,LSL #2]   将存储器地址为R1+R2*4的字数据读入存储区R0
STR R0,[R1,R2]!         将R0字数据存入存储器地址R1+R2的存储单元中，并将新地址R2+R2写入R2
STR R0,[R1,#8]!         将R0字数据存入存储器地址R1+8的存储单元中，并将新地址R2+8写入R2
STR R0,[R1,R2,LSL #2]   将R0字数据存入存储器地址R1+R2*4的存储单元中，并将新地址R2+R2*4写入R1
LDR R0,[R1],#8          将存储器地址为R1的字数据读入寄存器R0，并将新地址R1+8写入R1  
LDR R0,[R1],R2          将存储器地址为R1的字数据读入寄存器R0，并将新地址R1+R2写入R1
LDR R0,[R1],R2,LSL #2   将存储器地址为R1的字数据读入寄存器R0，并将新地址R1+R2*4写入R1

```

### 2.7.2. LDRB/STRB字节数据加载/存储指令

```
LDRB/STRB{<cond>}{T}Rd,addr         LDRB指令用于从存储器中将一个8位的字节数据加载到目的寄存器中，同时将寄存器的高24位清零，当程序计数器PC作为目的寄存器时，指令从存储器中读取的字数据被当做目的地址，从而可以实现程序流程的跳转。
STRB指令用于从源寄存器中将一个8位的字节数据存储到存储器中，和LDRB相反。后缀T可选。

```

### 2.7.3. LDRH/STRH半字数据加载/存储指令

```
LDRH/STRH{<cond>}{T}Rd,addr         LDRH指令用于从存储器中将一个16位的半字数据加载到目的寄存器中，同时将寄存器的高16位清零，当程序计数器PC作为目的寄存器时，指令从存储器中读取的字数据被当做目的地址，从而可以实现程序流程的跳转。
STRH指令用于从源寄存器中将一个16位的半字数据存储到存储器中，和LDRH相反。后缀T可选。

```

### 2.7.4. LDM/STM批量数据加载/存储指令

```
LDM/STM{<cond>}{<type>}Rn{!},<regs>{^}      LDM用于从基址寄存器所指示的一片连续存储器中读取数据到寄存器列表所指向的多个寄存器中，内存单元的起始地址为基址寄存器Rn的值，各个寄存器由寄存器列表regs表示，该指令一般用于多个寄存器数据的出栈操作
STM用于将寄存器列表所指向的多个寄存器中的值存入由基址寄存器所指向的一片连续存储器中，内存单元的起始地址为基址寄存器Rn的值，各个寄存器又寄存器列表regs表示。该指令一般用于多个寄存器数据的进栈操作。
type表示类型，用于数据的存储与读取有以下几种情况：
IA：每次传送后地址值加。
IB：每次传送前地址值加。
DA:每次传送后地址值减。
DB:每次传送前地址值减。
用于堆栈操作时有如下几种情况：
FD:满递减堆栈
ED:空递减堆栈
FA:满递增堆栈
EA:空递增堆栈

```

### 2.7.5. SWP字数据交换指令

```
SWP{<cond>}<Rd>,<Rm>,[<Rn>]         Rd = [Rn],[Rn] = Rm,当寄存器Rm和目的寄存器Rd为同一个寄存器时，指令交换该急促亲和存储器的内容
SWP R0,R1,[R2]          R0 = [R2],[R2] = R1
SWP R0,R0,[R1]          R0 = [R1],[R1] = R0
SWPB指令用于将寄存器Rn指向的存储器中的字节数据加载到目的寄存器Rd中，目的寄存器的高24位清零，同时将Rm中的字数据存储到Rn指向的存储器中。

```

2.8.分支语句
--------

| 助记符 | 说明 | 操作 |
| --- | --- | --- |
| B{cond}label | 分支指令 | PC<-label |
| BL{cond}label | 带返回的分支指令 | PC<-label，LR=BL后面的第一条指令地址 |
| BX{cond}Rm | 带状态切换的分支指令 | PC = Rm & 0xffffffe，T=Rm[0] & 1 |
| BLX{cond}label | Rm | 带返回和状态切换的分支指令 | PC=label，T=1 PC； PC = Rm & 0xffffffe，T=Rm[0] & 1；LR = BLX后面的第一条指令地址 |

### 2.8.1. 分支指令B

```
B{<cond>}label          跳转到label处执行，PC=label

例子：
backword    SUB R1,R1,#1
            CMP R1,#0           比较R1和0
            BEQ forward         如果R1=0，跳转到forware处执行
            SUB R1,R2,#3
            SUB R1,R1,#1
forward     ADD R1,R2,#4
            ADD R2,R3,#2
            B backword          无条件跳转到backword处执行

```

### 2.8.2. 带返回的分支指令BL

```
BL{<cond>}label         在跳转之前，将PC的当前内容保存在R14(LR)中保存，因此，可以通过将R14的内容重新加载到PC中，返回到跳转指令之后的指令处执行。该指令用于实现子程序的调用，程序的返回可通过把LR寄存器的值复制到PC寄存器中来实现。
例子：
BL func             跳转到子程序
ADD R1,R2,#2        子程序调用完返回后执行的语句，返回地址
....
func                子程序
...
MOV R15,R14         复制返回地址到PC，实现子程序的返回

```

### 2.8.3. 带状态切换的分支指令BX

```
BX{<cond>} Rm       当执行BX指令时，如果条件cond满足，则处理器会判断Rm的位[0]是否为1，如果为1则跳转时自动将CPSR寄存器的标志T置位，并将目标地址的代码解释为Thumb代码来执行，则处理器会切换到Thumb状态，反之，若Rm的位[0]为0，则跳转时自动将CPSR寄存器的标志T复位，并将目标地址处的代码解释为ARM代码来执行，即处理器会切换到ARM状态。

```

注意：bx lr的作用等同于mov pc,lr。即跳转到lr中存放的地址处。 非零值存储在R0中返回。

那么lr存放的是什么地址呢？lr就是连接寄存器(Link Register, LR)，在ARM体系结构中LR的特殊用途有两种：一是用来保存子程序返回地址；二是当异常发生时，LR中保存的值等于异常发生时PC的值减4（或者减2），因此在各种异常模式下可以根据LR的值返回到异常发生前的相应位置继续执行。　　

当通过BL或BLX指令调用子程序时，硬件自动将子程序返回地址保存在R14寄存器中。在子程序返回时，把LR的值复制到程序计数器PC即可实现子程序返回。

2.9堆栈
-----

### 2.9.1. 进栈出栈

```
出栈使用LDM指令，进栈使用STM指令。LDM和STM指令往往结合下面一些参数实现堆栈的操作。
FD:满递减堆栈。
ED:空递减堆栈。
FA:满递增堆栈。
EA:空递增堆栈。
满堆栈是指SP(R13)指向堆栈的最后一个已使用地址或满位置(也就是SP指向堆栈的最后一个数据项的位置)；相反，空堆栈是指SP指向堆栈的第一个没有使用的地址或空位置。
LDMFD和STMFD分别指POP出栈和PUSH入栈

```

### 2.9.2. PUSH指令

```
PUSH{cond} reglist      PUSH将寄存器推入满递减堆栈
PUSH {r0,r4-r7}         将R0,R4-R7寄存器内容压入堆栈

```

### 2.9.3. POP指令

```
POP{cond} reglist       POP从满递减堆栈中弹出数据到寄存器
POP {r0,r4-r7}          将R0,R4-R7寄存器从堆栈中弹出

```

0x03 创建Android NDK程序
====================

* * *

3.1. NDK程序创建过程
--------------

```
1.创建一个android程序。
2.在程序右键-->Android Tools-->Add Native Support(需要ADT配置好NDK的路径，新版的ADT没有配置NDK的地方，需要安装NDK的jar包)-->命名so文件(比如叫HelloJNI)。然后就会在程序中创建jni目录，包含了我们要写的NDK程序文件。
3.在src的包中(比如叫com.example.hellojni)中创建java文件，后面会演示几个实例。
4.在程序根目录下创建文件build_headers.xml，使用ANT editor打开(ADT需要安装ANT)，使用alt+/键调出自动提示，选择Bulidfile template创建模板文件。后面会给出代码实例。
5.打开ANT工具，选择第一个"增加"按钮(一个小的加号)，然后将build_headers.xml添加进来，ANT中就会增加HelloJNI，每次修改源码后，双击HelloJNI，就会自动修改/jni目录下的文件。

```

3.2. 编写程序
---------

3.2.1. CLASS文件
--------------

在com.example.hellojni包中创建class文件，本文一次创建多个实例，共参考。

GetInt.java代码为

```
package com.example.hellojni;
public class GetInt {
    public static native int getInt();
}

```

GetString.java代码为

```
package com.example.hellojni;    

public class GetString {

    public static native String getStr();

    public native String getString();

    public native int add(int a, int b);    

}

```

GetFor.java代码为

```
package com.example.hellojni;    

public class GetFor {
    public static native int getFor1(int n);
    public static native int getFor2(int n);
}

```

GetIfElse.java代码为

```
package com.example.hellojni;    

public class GetIfElse {
    public static native String getIfElse(int n);
}    

```

GetWhile.java代码为

```
package com.example.hellojni;    

public class GetWhile {
    public static native int getWhile(int n);
}

```

GetSwitch.java代码为

```
package com.example.hellojni;    

public class GetSwitch {
    public static native int getSwitch(int a,int b,int i);
}

```

MainActivity.java代码为

```
package com.example.hellojni;    

import android.support.v7.app.ActionBarActivity;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.TextView;    


public class MainActivity extends ActionBarActivity {

    private TextView tv;    

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        tv = (TextView) findViewById(R.id.tv);
        //tv.setText(String.valueOf(GetInt.getInt()));
        //tv.setText(GetString.getStr());
        //tv.setText(String.valueOf(GetFor.getFor1(4)));
        //tv.setText(String.valueOf(GetFor.getFor2(4)));
        //tv.setText(String.valueOf(GetWhile.getWhile(5)));
        //tv.setText(GetIfElse.getIfElse(20));
        tv.setText(String.valueOf(GetSwitch.getSwitch(4,2,2)));

    }

    static{
        System.loadLibrary("HelloJNI");
    }
}

```

build_headers.xml代码为

```
<?xml version="1.0" encoding="UTF-8"?>
    <!-- ====================================================================== 
     2014-10-28 上午8:05:50                                                            

     HelloJNI    
     description

     0xExploit                                                                
     ======================================================================     -->
<project name="HelloJNI" default="BuildAllHeaders">
    <description>
            description
    </description>    

    <!-- ================================= 
          target: BuildAllHeaders              
         ================================= -->
    <target name="BuildAllHeaders">
        <antcall target="BuildGetStringHeader"></antcall>
        <antcall target="BuildGetIntHeader"></antcall>
        <antcall target="BuildGetForHeader"></antcall>
        <antcall target="BuildGetWhileHeader"></antcall>
        <antcall target="BuildGetIfElseHeader"></antcall>
        <antcall target="BuildGetStringHeader"></antcall>
    </target>    

    <!-- - - - - - - - - - - - - - - - - - 
          target: depends                      
         - - - - - - - - - - - - - - - - - -->
    <target name="BuildGetStringHeader">
        <javah destdir="./jni" classpath="./bin/classes/" class="com.example.hellojni.GetString"></javah>
    </target>    

    <target name="BuildGetIntHeader">
        <javah destdir="./jni" classpath="./bin/classes/" class="com.example.hellojni.GetInt"></javah>
    </target>

    <target name="BuildGetForHeader">
            <javah destdir="./jni" classpath="./bin/classes/" class="com.example.hellojni.GetFor"></javah>
    </target>

    <target name="BuildGetWhileHeader">
            <javah destdir="./jni" classpath="./bin/classes/" class="com.example.hellojni.GetWhile"></javah>
    </target>

    <target name="BuildGetIfElseHeader">
            <javah destdir="./jni" classpath="./bin/classes/" class="com.example.hellojni.GetIfElse"></javah>
    </target>

    <target name="BuildGetSwitchHeader">
            <javah destdir="./jni" classpath="./bin/classes/" class="com.example.hellojni.GetSwitch"></javah>
    </target>    

</project>

```

然后双击ANT中的HelloJNI,然后F5刷新工程项目，可以看到jni目录下，多出6个文件，com_example_hellojni_GetFor.h等，此文件里面就是函数.h接口文件，是没有具体代码的,需要把里面的函数复制到jni目录下的HelloJNI.cpp文件中，然后去实现函数的具体部分。

HelloJNI.cpp的代码为

```
#include <jni.h>
#include <com_example_hellojni_GetInt.h>
#include <com_example_hellojni_GetString.h>
#include <com_example_hellojni_GetFor.h>
#include <com_example_hellojni_GetIfElse.h>
#include <com_example_hellojni_GetWhile.h>
#include <com_example_hellojni_GetSwitch.h>    

int nums[5] = {1, 2, 3, 4, 5};    

JNIEXPORT jstring JNICALL Java_com_example_hellojni_GetString_getStr
  (JNIEnv *env, jclass){
    return env->NewStringUTF("static method call");
}    

/*
 * Class:     com_example_hellojni_GetString
 * Method:    getString
 * Signature: ()Ljava/lang/String;
 */
JNIEXPORT jstring JNICALL Java_com_example_hellojni_GetString_getString
  (JNIEnv *env, jobject){
    return env->NewStringUTF("method call");
}    

/*
 * Class:     com_example_hellojni_GetString
 * Method:    add
 * Signature: (II)I
 */
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetString_add
  (JNIEnv *, jobject, jint a, jint b){
    return a+b;
}    


JNIEXPORT jint JNICALL Java_com_example_hellojni_GetInt_getInt
  (JNIEnv *, jclass){
    return 8;
}    

JNIEXPORT jint JNICALL Java_com_example_hellojni_GetFor_getFor1
  (JNIEnv *, jclass, jint n){
    int i = 0;
    int s = 0;
        for (i = 0; i < n; i++){
            s += i * 2;
        }
        return s;
}    

JNIEXPORT jint JNICALL Java_com_example_hellojni_GetFor_getFor2
  (JNIEnv *, jclass, jint n){
    int i = 0;
        int s = 0;
        for (i = 0; i < n; i++){
            s += i * i + nums[n-1];
        }
        return s;
}
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetWhile_getWhile
  (JNIEnv *, jclass, jint n){
        int i = 1;
        int s = 0;
        while(i <= n){
            s += i++;
        }
        return s;
}
JNIEXPORT jstring JNICALL Java_com_example_hellojni_GetIfElse_getIfElse
  (JNIEnv *env, jclass, jint n){
        if(n < 16){
            return env->NewStringUTF("he is a boy");
        } else if(n < 30){
            return env->NewStringUTF("he is a young man");
        } else if(n < 45){
            return env->NewStringUTF("he is a strong man");
        } else{
            return env->NewStringUTF("he is an old man");
        }
}
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetSwitch_getSwitch
  (JNIEnv *, jclass, jint a, jint b, jint i){
    switch (i){
        case 1:
            return a + b;
            break;
        case 2:
            return a - b;
            break;
        case 3:
            return a * b;
            break;
        case 4:
            return a / b;
            break;
        default:
            return a + b;
            break;
        }
}

```

以上就是一些实例的代码，下面就来分析逆向后的ARM代码。以下反汇编代码都是通过IDA得到的，至于IDA的使用方法，大家可以看看书。

### 3.2.2. getInt()方法

getInt()的方法代码如下：

```
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetInt_getInt
  (JNIEnv *, jclass){
    return 8;
}

```

反编译后的代码为:

```
EXPORT Java_com_example_hellojni_GetInt_getInt
Java_com_example_hellojni_GetInt_getInt
MOVS    R0, #8      ;R0 = 8
BX      LR          ;子程序返回R0

```

### 3.2.3. getStr()方法

getStr()的方法代码如下：

```
JNIEXPORT jstring JNICALL Java_com_example_hellojni_GetString_getStr
  (JNIEnv *env, jclass){
    return env->NewStringUTF("static method call");
}

```

反编译后的代码为：

```
EXPORT Java_com_example_hellojni_GetString_getStr
Java_com_example_hellojni_GetString_getStr
PUSH    {R3,LR}                                 ;将R3和LR入栈
LDR     R2, [R0]                                ;[R0]是JNIEnv，R2=*env，RO一般是放返回值的,调用函数后会被覆盖的,所以要复制出去
LDR     R1, =(aStaticMethodCa - 0xF7A)          
MOVS    R3, #0x29C                              ;R3=0x29C
ADD     R1, PC          ; "static method call"  ;R1="static method call"
LDR     R3, [R2,R3]     ;R2偏移R3，是NewStringUTF，可以查看JNI API(Android软件安全与逆向分析7.6节也有介绍),如下图所示，所有的函数在附件中。
BLX     R3              ;调用NewStringUTF函数，第一个参数R0，是JNIEnv,子程序返回,第二个参数是R1

```

![img](http://drops.javaweb.org/uploads/images/2a00e3bf9ad055c1d08829b86590367e04b8d963.jpg)

### 3.2.3. getFor1()方法

getFor1()的方法代码如下：

```
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetFor_getFor1
  (JNIEnv *, jclass, jint n){
    int i = 0;
    int s = 0;
        for (i = 0; i < n; i++){
            s += i * 2;
        }
        return s;
}

```

反编译后的代码为：

![img](http://drops.javaweb.org/uploads/images/adca738e89e7449b5a608c08ca3ef5749be690e5.jpg)

代码解释如下：

```
EXPORT Java_com_example_hellojni_GetFor_getFor1
Java_com_example_hellojni_GetFor_getFor1
               MOVS    R0, #0       ;R0 = 0
               MOVS    R3, R0       ;R3 = 0
               B       loc_FB0      ;跳转到loc_FB0
; ---------------------------------------------------------------------------
loc_FAA                                 ; CODE XREF: Java_com_example_hellojni_GetFor_getFor1+Ej
               LSLS    R1, R3, #1       ;R1=R3左移一位(即R1=R3*2)
               ADDS    R0, R0, R1       ;R0=R0+R1
               ADDS    R3, #1           ;R3=R3+1
loc_FB0                                 ; CODE XREF: Java_com_example_hellojni_GetFor_getFor1+4j
                CMP     R3, R2      ;比较R3和R2，R2是第一个参数，即n
                BLT     loc_FAA     ;如果R3<R2，跳到loc_FAA
                BX      LR          ;否则，子程序返回R0
;End of function Java_com_example_hellojni_GetFor_getFor1

```

### 3.2.4. getWhile()方法

getWhile()的函数代码如下：

```
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetWhile_getWhile
  (JNIEnv *, jclass, jint n){
        int i = 1;
        int s = 0;
        while(i <= n){
            s += i++;
        }
        return s;
}

```

反编译后的结果为：

![img](http://drops.javaweb.org/uploads/images/13b2609a0948f6c810102b31295635fb63297df1.jpg)

代码解释如下：

```
                 EXPORT Java_com_example_hellojni_GetWhile_getWhile
 Java_com_example_hellojni_GetWhile_getWhile
                 MOVS    R0, #0         ;R0 = 0
                 MOVS    R3, #1         ;R3 = 1
                 B       loc_FEA        ;跳转到loc_FEA
 ; 
-------------------------------------------------------------
 loc_FE6                                 ; CODE XREF: 
le_hellojni_GetWhile_getWhile+Cj
                 ADDS    R0, R0, R3   ;R0=R0+R3
                 ADDS    R3, #1           ;R3=R3+1
 loc_FEA                                 ; CODE XREF: 
le_hellojni_GetWhile_getWhile+4j
                 CMP     R3, R2         ;比较R3和R2，R2为第一个参数，即n
                 BLE     loc_FE6        ;如果R3<R2,跳转到loc_FE6
                 BX      LR             ;否则返回结果R0
 ; End of function Java_com_example_hellojni_GetWhile_getWhile

```

### 3.2.5. getIfElse()方法

getIfElse()的代码如下

```
JNIEXPORT jstring JNICALL Java_com_example_hellojni_GetIfElse_getIfElse
  (JNIEnv *env, jclass, jint n){
        if(n < 16){
            return env->NewStringUTF("he is a boy");
        } else if(n < 30){
            return env->NewStringUTF("he is a young man");
        } else if(n < 45){
            return env->NewStringUTF("he is a strong man");
        } else{
            return env->NewStringUTF("he is an old man");
        }
}

```

反编译后的结果为：

![img](http://drops.javaweb.org/uploads/images/7799078aee45410cff5db8abfc8aa02c4e620e70.jpg)

代码解释如下：

```
                 EXPORT Java_com_example_hellojni_GetIfElse_getIfEls
 Java_com_example_hellojni_GetIfElse_getIfElse
                 PUSH    {R4,LR}            ;R4,LR入栈。
                 MOVS    R3, #0xA7          ;R3=167
                 LDR     R4, [R0]           ;[R0]是JNIEnv，此处是R4=*env
                 LSLS    R3, R3, #2     ;R3=R3左移2位
                 CMP     R2, #0xF           ;比较R2(即n)和16
                 BGT     loc_1002           ;如果R2>16，跳转到loc_1002
                 LDR     R1, =(aHeIsABoy - 0x1002)  ;和下一条指令一起，将R1="he is a boy"
                 ADD     R1, PC          ; "he is a boy"
                 B       loc_101A           ;跳转到loc_101A
 ; 
-------------------------------------------------------------
 loc_1002                                ; CODE XREF: 
le_hellojni_GetIfElse_getIfElse+Aj
                 CMP     R2, #0x1D
                 BGT     loc_100C
                 LDR     R1, =(aHeIsAYoungMan - 0x100C)
                 ADD     R1, PC          ; "he is a young man"
                 B       loc_101A
 ; 
-------------------------------------------------------------
 loc_100C                                ; CODE XREF: 
le_hellojni_GetIfElse_getIfElse+14j
                 CMP     R2, #0x2C
                 BGT     loc_1016
                 LDR     R1, =(aHeIsAStrongMan - 0x1016)
                 ADD     R1, PC          ; "he is a strong man"
                 B       loc_101A
 ; 
-------------------------------------------------------------
 loc_1016                                ; CODE XREF: 
le_hellojni_GetIfElse_getIfElse+1Ej
                 LDR     R1, =(aHeIsAnOldMan - 0x101C)
                 ADD     R1, PC          ; "he is an old man"
 loc_101A                                ; CODE XREF: 
le_hellojni_GetIfElse_getIfElse+10j
                                         ; 
le_hellojni_GetIfElse_getIfElse+1Aj ...
                 LDR     R3, [R4,R3]        ;R4的偏移R3*4，是NewStringUTF
                 BLX     R3                 ;子程序返回，第一个参数是R0，第二个参数是R1
                 POP     {R4,PC}            ;一般是和第一行执行相反的出栈动作.将LR放入到PC,PC是下一条命令的地址,改变它的值也就相当跳转.
 ; End of function Java_com_example_hellojni_GetIfElse_getIfElse

```

### 3.2.6. getSwitch()方法

getSwitch()的代码如下：

```
JNIEXPORT jint JNICALL Java_com_example_hellojni_GetSwitch_getSwitch
  (JNIEnv *, jclass, jint a, jint b, jint i){
    switch (i){
        case 1:
            return a + b;
            break;
        case 2:
            return a - b;
            break;
        case 3:
            return a * b;
            break;
        case 4:
            return a / b;
            break;
        default:
            return a + b;
            break;
        }
}

```

反编译后的结果为：

![img](http://drops.javaweb.org/uploads/images/a1e00baa51abf0c3176a0a686a7644c99e71cda5.jpg)

代码解释如下：

```
                 EXPORT Java_com_example_hellojni_GetSwitch_getSwitch
 Java_com_example_hellojni_GetSwitch_getSwitch
 arg_0           =  0
                 PUSH    {R3,LR}
                 LDR     R1, [SP,#8+arg_0]
                 ADDS    R0, R2, R3
                 SUBS    R1, #1
                 CMP     R1, #3          ; switch 4 cases
                 BHI     locret_105C     ; jumptable 0000103E default case，跳转到default,此时返回R0，R0=R2+R3
                 MOVS    R0, R1
                 BL      __gnu_thumb1_case_uqi ; switch jump
 ; 
-------------------------------------------------------------
 jpt_103E        DCB 2                   ; jump table for switch statement
                 DCB 4
                 DCB 6
                 DCB 9
 ; 
-------------------------------------------------------------
 loc_1046                                ; CODE XREF: 
le_hellojni_GetSwitch_getSwitch+Ej
                 ADDS    R0, R2, R3      ; jumptable 0000103E case 0
                 B       locret_105C     ; jumptable 0000103E default case
 ; 
-------------------------------------------------------------
 loc_104A                                ; CODE XREF: 
le_hellojni_GetSwitch_getSwitch+Ej
                 SUBS    R0, R2, R3      ; jumptable 0000103E case 1
                 B       locret_105C     ; jumptable 0000103E default case
 ; 
-------------------------------------------------------------
 loc_104E                                ; CODE XREF: 
le_hellojni_GetSwitch_getSwitch+Ej
                 MOVS    R0, R3          ; jumptable 0000103E case 2
                 MULS    R0, R2
                 B       locret_105C     ; jumptable 0000103E default case
 ; 
-------------------------------------------------------------
 loc_1054                                ; CODE XREF: 
le_hellojni_GetSwitch_getSwitch+Ej
                 MOVS    R0, R2          ; jumptable 0000103E case 3
                 MOVS    R1, R3
                 BLX     __divsi3
 locret_105C                             ; CODE XREF: 
le_hellojni_GetSwitch_getSwitch+Aj
                                         ; 
le_hellojni_GetSwitch_getSwitch+18j ...
                 POP     {R3,PC}         ; jumptable 0000103E default case
 ; End of function Java_com_example_hellojni_GetSwitch_getSwitch

```