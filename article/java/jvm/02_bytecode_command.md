# 字节码指令

虚拟机是一个相对于物理机的概念，这两种机器都有代码执行能力，其区别在于物理机的执行引擎是直接建立在 CPU 处理器、指令集、操作系统和硬件层面上的。

而虚拟机的执行引擎则由自己实现，因此可以制定自己的指令集和执行引擎的结构体系，而且还可以执行一些不被硬件直接支持的指令集格式。这就是虚拟机相对于物理机的优势所在。

但是缺点也比较明显，由于多了一层虚拟指令，执行虚拟机指令后还要转化为本地机器码，所以在执行效率上，虚拟机是不如物理机的。

Java 虚拟机的字节码指令由一个字节长度的操作码（Opcode）以及紧随其后的零至多个操作数（Operands）构成。

如果忽略异常处理，那么 Java 虚拟机的解释器通过下面这个伪代码的循环即可有效工作：

```java
do{
    自动计算pc寄存器以及从pc寄存器的位置取出操作码;
    if(存在操作数){
        取出操作数;
    }
    执行操作码所定义的操作;
} while(处理下一次循环);
```

由于字节码指令集限制了其操作码长度为 1 个字节（0 ~ 255），即意味着整个指令集中包含的指令总数不超过 256 条。

在虚拟机处理超过 1 个字节的数据时，会在运行时重新构建出具体的数据结构。

例如：如果要将一个 16 位无符号的整数使用两个无符号字节存储起来（命名为 byte1 和 byte2），那么这个 16 位无符号数的值应该这样表示：

```java
(byte1 << 8) | byte2
```

这种操作在某种程度上会导致执行字节码时损失一些性能。但这样做的优势也非常明显，放弃了操作数长度对齐，就意味着可以节省很多填充和间隔符号；用一个字节来代表操作码，也是为了尽可能获得短小精干的编译代码。

这种追求尽可能小数据量、高传输效率 的设计是由 Java 语言设计之初面向网络、智能家电的技术背景所决定的并沿用至今。

## 字节码与数据类型

在讲字节码指令之前，我们需要了解下，字节码指令操作的操作数是什么类型的，这些 Java 虚拟机中的数值类型又和 Java 编程语言中的 8 大基本数据类型如何对应的？

Java 语言中的 8 大基本数据类型：

- 整型：byte、short、int、long
- 浮点型：double、float
- 字符型：char
- 布尔型：boolean

Java 程序语言中定义了 8 大基本数据类型，但是在 Java 虚拟机中只分为两大类：

- 原始类型（primitive type）
- 引用类型（reference type）

原始类型对应的数值称为原始值、引用类型的数值称为引用值。

### 原始类型

原始类型包括如下类型。

- 数值类型

数值类型包括：byte、short、int、long、char、float、double。

- boolean 类型

boolean 类型的值有两种：true 和 false，默认为 false，虽然在 Java 虚拟机中定义了 boolean 这种类型，但是却没有指令直接支持其操作。

所以，对 boolean 类型都需要在编译后用虚拟机中的 int 类型来表示 —— 1 表示 true、0 表示 false。

- returnAddress 类型

returnAddress 类型表示一个指向某个操作码 opcode 的指针，此操作码与虚拟机指令相对应。

### 引用类型

引用类型包括如下类型。

- 类类型（class type）
- 数组类型（array type）
- 接口类型（interface type）

这三种引用类型的值分别指向动态创建的类实例、数组实例和实现了某个接口的类/数组实例。

在引用类型中还有一个特殊的值 null，当一个引用不指向任何对象时，它就用 null 表示， null 作为引用类型的初始默认值可以转型成任意的引用类型。

## 加载与存储指令

加载和存储指令用于将数据在栈帧中的局部变量表和操作数栈之间来回传输，这类指令包括如下内容。

- 将一个局部变量加载到操作数栈

`iload`、`iload_<n>`、`lload,load<n>`、`fload,fload_<n>`、`dload,dload_<n>`、`aload,aload_<n>`

- 将一个数值从操作数栈存储到局部变量表

`istore`、`istore_<n>`、`lstore`、`lstore_<n>`、`fstore,fstore_<n>`、`dstore`、`dstore_<n>`、`astore,astore_<n>`

- 将一个常量加载到操作数栈

`bipush`、`sipush`、`ldc`、`ldc_w`、`ldc2_w`、`aconst_null`、`iconst_m1`、`iconst_<i>`、`lconst_<l>`、`fconst_<f>`、`dconst_<d>`

- 扩充局部变量表的访问索引：`wide`

上面所列举的指令助记符中，有一部分是以 `_<n>` 尾的，这些指令助记符实际上是代表了一组指令。

> 如：`iload_<n>` 代表了 iload_0、iload_1、iload_2 和 iload_3这几条指令，此时操作数隐藏于指令之中。

```java
iload_0 表示从当前栈帧局部变量表中 0 号位置取 int 类型的数值加载到操作数栈
iload_1 表示从当前栈帧局部变量表中 1 号位置取 int 类型的数值加载到操作数栈
...
```

## 运算指令

算术指令用于对两个操作数栈上的值进行某种特定运算，并把结构重新压入操作数栈。

大体上算术指令可以分为两种：对整型数据进行运算的指令和对浮点类型数据进行运算的指令。

在每一大类中，都有针对 Java 虚拟机具体数据类型的专用算术指令。但没有直接支持 byte、short、char 和 boolean 类型的算术指令，对于这些数据的运算，都是用 int 类型指令来处理。

所有算术指令包括：

- 加法指令：iadd、ladd、fadd、dadd
- 减法指令：isub、lsub、fsub、dsub
- 乘法指令：imul、lmul、fmul、dmul
- 除法指令：idiv、ldiv、fdiv、ddiv
- 求余指令：irem、lrem、frem、drem
- 求负值指令：ineg、lneg、fneg、dneg
- 移位指令：ishl、ishr、iushr、lshl、lshr、lushr
- 按位或指令：ior、lor
- 按位与指令：iand、land
- 按位异或指令：ixor、lxor
- 局部变量自增指令：iinc
- 比较指令：dcmpg、dcmpl、fcmpg、fcmpl、lcmp

## 类型转换指令

类型转换指令可以在两种 Java 虚拟机数值类型之间相互转换。这些转换操作一般用于实现用户代码中的显式类型转换操作，或者用来解决 Java 虚拟机字节码指令的不完备问题。

Java 虚拟机直接支持以下数值的宽化类型转换（widening numeric conversion，小范围类型向大范围类型的安全转换）：

- 从 int 类型到 long、float 或者 double 类型
- 从 long 类型到 float、double 类型
- 从 float 类型到 double 类型

宽化类型转换指令包括：i2l、i2f、i2d、l2f、l2d 和 f2d。

Java 虚拟机也支持以下窄化类型转换：

- 从 int 类型到 byte、short 或者 char 类型
- 从 long 类型到 int 类型
- 从 float 类型到 int 或者 long 类型
- 从 double 类型到 int、long 或者 float 类型

窄化类型转换（narrowing numeric conversion）指令包括：i2b、i2c、i2s、l2i、f2i、f2l、d2i、d2l、d2f。

## 对象创建与访问指令

在 Java 中类实例和数组都是对象，但是 Java 虚拟机对类 class 对象和数组对象的创建使用了不同的字节码指令。

- 创建类实例的指令：*new*

- 创建数组的指令：newarray、anewarray、multianewarray

- 访问类变量（static 字段）的指令：getstatic、putstatic

- 访问实例变量的指令：getfield、putfield

- 将一个数组元素加载到操作数栈的指令：baload、caload、saload、iaload、laload、faload、daload、aaload

- 将一个操作数栈的值存到数组元素中的指令：bastore、castore、sastore、iastor、fastore、dastore、aastore

- 取数组长度的指令：*arraylength*

- 检查类实例类型的指令：instanceof、checkcast

## 操作数栈管理指令

Java 虚拟机提供了一些用于直接操控操作数栈的指令，包括：pop、pop2、dup、dup2、dup_x1、dup_x2、dup2_x1、dup_x2、dup2_x2 和 swap。

## 控制转移指令

控制转移指令可以让 Java 虚拟机有条件或无条件地从指定指令而不是控制转移指令的下一条指令继续执行程序。

控制指令包括：

- 条件分支

ifeq、iflt、ifle、ifne、ifgt、ifge、jfnull、ifnonnull、ificmpeq、ificmpne、ificmplt、ificmpgt、if_icmple、if_icmpge、if_acmpeq、if_acmpne

- 符合条件分支

tableswitch、lookupswitch

- 无条件分支

goto、goto_w、jsr、jsr_w、ret

## 方法调用与返回指令

以下 5 条指令用于方法调用：

- invokevirtual

用于调用对象的实例方法，根据对象的实际类型进行分派（虚方法分派），这也是 Java 语言中最常见的方法分派方式。

- invokeinterface

用于调用接口方法，它会在运行时搜索一个实现了此接口的对象，找出合适的方法进行调用。

- invokestatic

用于调用类方法（static 方法）。

- invokedynamic

指令用于在运行时动态解析出调用点限定符所引用的方法，并执行该方法，前面的 4 条调用指令的分派逻辑都固话在 Java 虚拟机内部，而 invokedynamic 指令的分派逻辑则是由用户所设定的引导方法所决定的。

## 异常处理指令

在 Java 程序中显示抛出异常的操作（throw 语句）都由 athrow 指令来实现，除了用 throw 语句显示抛出的异常以外，Java 虚拟机规范还规定了许多会在 Java 虚拟机检查到异常状况时自动抛出的运行时异常。

> 如：在整数运算中，当除数为 0 时，虚拟机会在 idiv 或 ldiv 指令中抛出 ArithmeticException 异常。

此处需要注意的是，在 Java 虚拟机中处理异常（catch 语句）不是由字节码指令实现的，而是采用异常处理器（异常表）来完成的。

## 同步指令

Java 虚拟机可以支持方法级的同步和方法内部一段指令序列的同步，两种同步都是使用管程（Monitor）来支持的。

- 方法级的同步

方法级的同步时隐式的，即无需通过字节码指令控制，它实现在方法调用和返回操作之中。虚拟机可以从方法常量池的方法表中 ACC_SYNCHRONIZED 访问标志得知此方法是否声明为同步方法。

当方法调用时，如果此方法为同步方法，则执行线程就要去先成功持有管程，然后才能执行方法，方法（无论是否正常完成）完成后释放管程。

如果这个同步方法执行期间抛出异常，并且方法内部无法处理，那么此方法持有的管程将在异常抛出去后自动释放。

- 指令序列级的同步

同步一段指令序列通常是由 Java 中的 synchronized 语句块来表示的，Java 虚拟机指令集中有 monitorenter 和 monitorexit 两条指令来支持 synchronized 关键字。

## 附录

- [虚拟机字节码指令表](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/java/jvm/00_command_list.md)

## 参考资料

- 《深入理解 Java 虚拟机》
- 《Java 虚拟机规范 SE 8 版》