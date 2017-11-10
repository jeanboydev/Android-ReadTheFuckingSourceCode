# Swift 入门
## 概述
Swift 是一门开发 iOS, macOS, watchOS 和 tvOS 应用的新语言。

Swift 包含了 C 和 Objective-C 上所有基础数据类型，Int表示整型值； Double 和 Float 表示浮点型值； Bool 是布尔型值；String 是文本型数据。 Swift 还提供了三个基本的集合类型，Array ，Set 和 Dictionary。
## 常量与变量
常量和变量必须在使用前声明，用 let 来声明常量，用 var 来声明变量。

```Swift
//let 声明的变量不能再赋值修改
let hello = 10//不指明类型会自动转换
let hello1: String = "hello let"//指明类型时只能是该类型
//var 声明的变量可以再赋值修改
var hello1 = 10
var hello2: String = "hello"
```
Java 方式

```Java
final int hello = 10;
int hello1 = 10;
String hello2 = "hello";
```

- 分号

与其他大部分编程语言不同，Swift 并不强制要求你在每条语句的结尾处使用分号（;），当然，你也可以按照你自己的习惯添加分号。

- 数据类型

Int(整型，在 32 位平台上长度为 32，64 位平台上长度为 64)，UInt(无符号整型)，Float(浮点型 32)，Double(浮点型 64)，String(字符串)，Bool(布尔型)

- nil 与 ? 与 !

nil 表示没有值

```Swift
var a: Int?//? 表示 a 可能没有值，如果 a 没有值默认解析为 nil
var b: Int?
var c: Int?
a = 1
b = 2
c = a! + b!//! 表示开发者确定该变量存在值，如果运行中没有值时程序会崩溃
```
- 类型转换

```Swift
let three = 3
let twoPoint = 2.12345
let count = Double(three) + twoPoint//跟 Java 相似
```

## 基本运算符
- 赋值运算符

```Swift
let a = 10//a 等于 10
let (x, y) = (1, 2)// x 等于 1，y 等于 2
```
- 算术运算符

`+` `-` `*` `/` `%`
`+=` `-=` `*=` `/=` `%=`
- 比较运算符

`==` `!=` `>` `<` `>=` `<=`
- 三目运算符

`? :`
- 空合运算符

`??`

```Swift
a ?? b//表示如果 a 的值为 nil 则默认值为 b，a 与 b 的类型需要一致
```
- 区间运算符

`...`

```Swift
1...5//表示从 1 到 5
1..<5//表示从 1 到 4
```
- 逻辑运算符

逻辑非（!a）
逻辑与（a && b）
逻辑或（a || b）


