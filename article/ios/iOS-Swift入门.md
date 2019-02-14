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

## 字符串和字符
- 连接字符串

```Swift
let string1 = "hello"
let string2 = " there"
var welcome = string1 + string2
// welcome 现在等于 "hello there"
```

- 字符串插值

```Swift
let multiplier = 3
let message = "\(multiplier) times 2.5 is \(Double(multiplier) * 2.5)"
//\(变量名) 自动转换拼接
// message 是 "3 times 2.5 is 7.5"
```

## 集合类型
- 数组(Arrays)

写 Swift 数组应该遵循像 Array<Element> 这样的形式，其中 Element 是这个数组中唯一允许存在的数据类型。

```Swift
var someInts = [Int]()
var array = ["张三", 18, UIView()]//可以放任何类型
array.append("王")//添加一个值
array.removeFirst()//移除第一条
array.removeAll()//清空
array.removeAtIndex(1)//移除第二条

//数组拼接
var array1 = [String]()
var array2 = [String]()
var array3 = array1 + array2
```

- 集合(Sets)

集合(Set)用来存储相同类型并且没有确定顺序的值。当集合元素顺序不重要时或者希望确保每个元素只出现一次时可以使用集合而不是数组。

```Swift
var letters = Set<Character>()
letters.insert("a")
```
使用 intersection(_:) 取交集
使用 symmetricDifference(_:) 取对称差
使用 union(_:) 取并集
使用 subtracting(_:) 取差集

- 字典

Swift 的字典使用 Dictionary<Key, Value> 定义，其中 Key 是字典中键的数据类型，Value 是字典中对应于这些键所存储值的数据类型。

```Swift
var dict = ["name":"zhangsan", "age":18]
dict["height"] = 1.5	//添加，存在 key 覆盖值，不存在新建 key

for (k,v) int dict {
	print("key\(k) value\(v))
}

//字典合并
let dict2 = ["title":"lisi", "age":18]
for (k,v) int dict2 {
	dict[k] = v
}
```
## 控制流
Swift 提供了多种流程控制结构，包括可以多次执行任务的 while 循环，基于特定条件选择执行不同代码分支的 if、guard 和 switch 语句，还有控制流程跳转到其他代码位置的 break 和 continue 语句。

Swift 还提供了for-in 循环，用来更简单地遍历数组（Array），字典（Dictionary），区间（Range），字符串（String）和其他序列类型。

- For-In 循环

```Swift
//遍历数组
let names = ["Anna", "Alex", "Brian", "Jack"]
for name in names {
    print("Hello, \(name)!")
}
// Hello, Anna!
// Hello, Alex!
// Hello, Brian!
// Hello, Jack!

//遍历字典
let numberOfLegs = ["spider": 8, "ant": 6, "cat": 4]
for (animalName, legCount) in numberOfLegs {
    print("\(animalName)s have \(legCount) legs")
}
// ants have 6 legs
// spiders have 8 legs
// cats have 4 legs

//使用范围数字，代替 for(;;)
for index in 1...5 {
    print("\(index) times 5 is \(index * 5)")
}
// 1 times 5 is 5
// 2 times 5 is 10
// 3 times 5 is 15
// 4 times 5 is 20
// 5 times 5 is 25
```

- While 循环

```Swift
while true {  
    //do something ...
}

//do...while
repeat {
    //do something ...
} while true

```

- 条件语句

```Swift
var temperatureInFahrenheit = 90
if temperatureInFahrenheit <= 32 {
    print("It's very cold. Consider wearing a scarf.")
} else if temperatureInFahrenheit >= 86 {
    print("It's really warm. Don't forget to wear sunscreen.")
} else {
    print("It's not that cold. Wear a t-shirt.")
}
// 输出 "It's really warm. Don't forget to wear sunscreen."
```

- Switch 语句

```Swift
let someCharacter: Character = "z"
switch someCharacter {
case "a":
    print("The first letter of the alphabet")
case "z":
    print("The last letter of the alphabet")
default:
    print("Some other character")
}
// 输出 "The last letter of the alphabet"

//还可以匹配区间
let approximateCount = 62
let countedThings = "moons orbiting Saturn"
let naturalCount: String
switch approximateCount {
case 0:
    naturalCount = "no"
case 1..<5:
    naturalCount = "a few"
case 5..<12:
    naturalCount = "several"
case 12..<100:
    naturalCount = "dozens of"
case 100..<1000:
    naturalCount = "hundreds of"
default:
    naturalCount = "many"
}
print("There are \(naturalCount) \(countedThings).")
// 输出 "There are dozens of moons orbiting Saturn."
```

- 控制转移语句

1. continue：立刻停止本次循环，重新开始下次循环，不会离开循环体
2. break：立刻结束整个控制流的执行
3. fallthrough

    ```Swift
    let integerToDescribe = 5
    var description = "The number \(integerToDescribe) is"
    switch integerToDescribe {
    case 2, 3, 5, 7, 11, 13, 17, 19:
        description += " a prime number, and also"
        fallthrough
    default:
        description += " an integer."
    }
    print(description)
    // 输出 "The number 5 is a prime number, and also an integer."
    ```

4. return

    像 if 语句一样，guard 的执行取决于一个表达式的布尔值。我们可以使用 guard 语句来要求条件必须为真时，以执行 guard 语句后的代码。不同于 if 语句，一个 guard 语句总是有一个 else 从句，如果条件不为真则执行 else 从句中的代码。
    
    ```Swift
    func greet(person: [String: String]) {
        guard let name = person["name"] else {
            return
        }
        print("Hello \(name)")
        guard let location = person["location"] else {
            print("I hope the weather is nice near you.")
            return
        }
        print("I hope the weather is nice in \(location).")
    }
    greet(["name": "John"])
    // 输出 "Hello John!"
    // 输出 "I hope the weather is nice near you."
    greet(["name": "Jane", "location": "Cupertino"])
    // 输出 "Hello Jane!"
    // 输出 "I hope the weather is nice in Cupertino."
    ```

5. throw

    抛出异常
    
## 函数

```Swift
//定义函数
func sum(x: Int, y: Int) -> Int{
	return x + y;
}
//调用函数
sum(10, y: 20)

//外部参数 num1, num2 供外部程序调用参考用，x, y 内部参数
func sum(num1 x: Int, num2 y: Int) -> Int{
	return x + y;
}
sum(num1: 10, num2: 20)
```

没有返回值的写法

```Swift
func demo() {
	print("haha")
}

func demo2 -> Void {
	print("haha")
}

func demo3() -> (){
	print("haha")
}
```

多重返回值函数

```Swift
func minMax(array: [Int]) -> (min: Int, max: Int) {
    var currentMin = array[0]
    var currentMax = array[0]
    for value in array[1..<array.count] {
        if value < currentMin {
            currentMin = value
        } else if value > currentMax {
            currentMax = value
        }
    }
    return (currentMin, currentMax)
}
```
## 闭包
闭包是一组预先准备好的代码，可以当做参数传递，在需要的时候使用。

```Swift
func sum(num1 x: Int, num2 y: Int) -> Int {
	return x + y
}
//sum(10, y: 20)
sum(num1: 10, num2: 20)

let sumFunc = sum//闭包

//sumFunc(5, y: 6)
sumFunc(num1: 5, num2: 6)

//闭包的定义，可以做为参数传递类似于 callback
let demoFunc = {
	print("demo")
}
//执行闭包
demoFunc()
//in 用于区分函数定义和代码实现
let demoFunc2 = { (x: Int, y: Int) -> Int in
	return x + y
}

```
闭包表达式语法
```Swift
{ (parameters) -> returnType in
    //do something ...
}
```
## 枚举
枚举为一组相关的值定义了一个共同的类型，使你可以在你的代码中以类型安全的方式来使用这些值。

```Swift
enum CompassPoint {
    case north
    case south
    case east
    case west
}

directionToHead = .south
switch directionToHead {
    case .north:
        print("Lots of planets have a north")
    case .south:
        print("Watch out for penguins")
    case .east:
        print("Where the sun rises")
    case .west:
        print("Where the skies are blue")
}
// 打印 "Watch out for penguins”
```
## 类与结构体
类和结构体是人们构建代码所用的一种通用且灵活的构造体。我们可以使用完全相同的语法规则来为类和结构体定义属性（常量、变量）和添加方法，从而扩展类和结构体的功能。

```Swift
class SomeClass {
    // 在这里定义类
}
struct SomeStructure {
    // 在这里定义结构体
}
```

- 类和结构体对比
Swift 中类和结构体有很多共同点。共同处在于：

1. 定义属性用于存储值
2. 定义方法用于提供功能
3. 定义下标操作使得可以通过下标语法来访问实例所包含的值
4. 定义构造器用于生成初始化值
5. 通过扩展以增加默认实现的功能
6. 实现协议以提供某种标准功能

与结构体相比，类还有如下的附加功能：

1. 继承允许一个类继承另一个类的特征
2. 类型转换允许在运行时检查和解释一个类实例的类型
3. 析构器允许一个类实例释放任何其所被分配的资源
4. 引用计数允许对一个类的多次引用

> 结构体总是通过被复制的方式在代码中传递，不使用引用计数。

- 类与结构体的选择
按照通用的准则，当符合一条或多条以下条件时，请考虑构建结构体：

1. 该数据结构的主要目的是用来封装少量相关简单数据值。
2. 有理由预计该数据结构的实例在被赋值或传递时，封装的数据将会被拷贝而不是被引用。
3. 该数据结构中储存的值类型属性，也应该被拷贝，而不是被引用。
4. 该数据结构不需要去继承另一个既有类型的属性或者行为。

## 继承
一个类可以继承另一个类的方法，属性和其它特性。当一个类继承其它类时，继承类叫子类，被继承类叫超类（或父类）。在 Swift 中，继承是区分「类」与其它类型的一个基本特征。

```Swift
class SomeClass: SomeSuperclass, SomeSuperclass2 {
    // 这里是子类的定义
}
```

- 重写(override)

子类可以为继承来的实例方法，类方法，实例属性，或下标提供自己定制的实现。我们把这种行为叫重写。

- 防止重写

你可以通过把方法，属性或下标标记为 final 来防止它们被重写，只需要在声明关键字前加上 final 修饰符即可（例如：final var，final func，final class func，以及 final subscript）。

## 构造过程
构造过程是使用类、结构体或枚举类型的实例之前的准备过程。在新实例可用前必须执行这个过程，具体操作包括设置实例中每个存储型属性的初始值和执行其他必须的设置或初始化工作。

- 构造器

构造器在创建某个特定类型的新实例时被调用。它的最简形式类似于一个不带任何参数的实例方法，以关键字 init 命名：

```Swift
init() {
    // 在此处执行构造过程
}
```
## 析构过程
析构器只适用于类类型，当一个类的实例被释放之前，析构器会被立即调用。析构器用关键字deinit来标示，类似于构造器要用 init 来标示。

- 析构器

Swift 会自动释放不再需要的实例以释放资源。Swift 通过自动引用计数（ARC）处理实例的内存管理。通常当你的实例被释放时不需要手动地去清理。但是，当使用自己的资源时，你可能需要进行一些额外的清理。例如，如果创建了一个自定义的类来打开一个文件，并写入一些数据，你可能需要在类实例被释放之前手动去关闭该文件。

```Swift
deinit {
    // 执行析构过程
}
```

析构器是在实例释放发生前被自动调用。你不能主动调用析构器。子类继承了父类的析构器，并且在子类析构器实现的最后，父类的析构器会被自动调用。即使子类没有提供自己的析构器，父类的析构器也同样会被调用。

## 错误处理
在 Swift 中，错误用符合 Error 协议的类型的值来表示。这个空协议表明该类型可以用于错误处理。

Swift 的枚举类型尤为适合构建一组相关的错误状态，枚举的关联值还可以提供错误状态的额外信息。例如，你可以这样表示在一个游戏中操作自动贩卖机时可能会出现的错误状态：

```Swift
enum VendingMachineError: Error {
    case invalidSelection                    //选择无效
    case insufficientFunds(coinsNeeded: Int) //金额不足
    case outOfStock                          //缺货
}
```

抛出一个错误可以让你表明有意外情况发生，导致正常的执行流程无法继续执行。抛出错误使用 throw 关键字。例如，下面的代码抛出一个错误，提示贩卖机还需要 5 个硬币：

```Swift
throw VendingMachineError. insufficientFunds(coinsNeeded: 5)
```
- 用 Do-Catch 处理错误

可以使用一个 do-catch 语句运行一段闭包代码来处理错误。如果在 do 子句中的代码抛出了一个错误，这个错误会与 catch 子句做匹配，从而决定哪条子句能处理它。
```Swift
do {
    try expression
    statements
} catch pattern 1 {
    statements
} catch pattern 2 where condition {
    statements
}
```
- 将错误转换成可选值

可以使用 try? 通过将错误转换成一个可选值来处理错误。如果在评估 try? 表达式时一个错误被抛出，那么表达式的值就是 nil。例如，在下面的代码中，x 和 y 有着相同的数值和等价的含义：

```Swift
func someThrowingFunction() throws -> Int {
    // ...
}

let x = try? someThrowingFunction()

let y: Int?
do {
    y = try someThrowingFunction()
} catch {
    y = nil
}
```

如果你想对所有的错误都采用同样的方式来处理，用 try? 就可以让你写出简洁的错误处理代码。例如，下面的代码用几种方式来获取数据，如果所有方式都失败了则返回 nil。

```Swift
func fetchData() -> Data? {
    if let data = try? fetchDataFromDisk() { return data }
    if let data = try? fetchDataFromServer() { return data }
    return nil
}
```

- 指定清理操作

可以使用 defer 语句在即将离开当前代码块时执行一系列语句。该语句让你能执行一些必要的清理工作，不管是以何种方式离开当前代码块的——无论是由于抛出错误而离开，或是由于诸如 return、break 的语句。例如，你可以用 defer 语句来确保文件描述符得以关闭，以及手动分配的内存得以释放。

```Swift
func processFile(filename: String) throws {
    if exists(filename) {
        let file = open(filename)
        defer {
            close(file)
        }
        while let line = try file.readline() {
            // 处理文件。
        }
        // close(file) 会在这里被调用，即作用域的最后。
    }
}
```
## 类型转换
类型转换 可以判断实例的类型，也可以将实例看做是其父类或者子类的实例。

类型转换在 Swift 中使用 is 和 as 操作符实现。这两个操作符提供了一种简单达意的方式去检查值的类型或者转换它的类型。

- 检查类型

用类型检查操作符（is）来检查一个实例是否属于特定子类型。若实例属于那个子类型，类型检查操作符返回 true，否则返回 false。

```Swift
var movieCount = 0
var songCount = 0

for item in library {
    if item is Movie {
        movieCount += 1
    } else if item is Song {
        songCount += 1
    }
}

print("Media library contains \(movieCount) movies and \(songCount) songs")
// 打印 “Media library contains 2 movies and 3 songs”
```
- 向下转型

某类型的一个常量或变量可能在幕后实际上属于一个子类。当确定是这种情况时，你可以尝试向下转到它的子类型，用类型转换操作符（as? 或 as!）。

因为向下转型可能会失败，类型转型操作符带有两种不同形式。条件形式as? 返回一个你试图向下转成的类型的可选值。强制形式 as! 把试图向下转型和强制解包转换结果结合为一个操作。

当你不确定向下转型可以成功时，用类型转换的条件形式（as?）。条件形式的类型转换总是返回一个可选值，并且若下转是不可能的，可选值将是 nil。这使你能够检查向下转型是否成功。

只有你可以确定向下转型一定会成功时，才使用强制形式（as!）。当你试图向下转型为一个不正确的类型时，强制形式的类型转换会触发一个运行时错误。

```Swift
for item in library {
    if let movie = item as? Movie {
        print("Movie: '\(movie.name)', dir. \(movie.director)")
    } else if let song = item as? Song {
        print("Song: '\(song.name)', by \(song.artist)")
    }
}

// Movie: 'Casablanca', dir. Michael Curtiz
// Song: 'Blue Suede Shoes', by Elvis Presley
// Movie: 'Citizen Kane', dir. Orson Welles
// Song: 'The One And Only', by Chesney Hawkes
// Song: 'Never Gonna Give You Up', by Rick Astley
```
## 扩展
扩展 就是为一个已有的类、结构体、枚举类型或者协议类型添加新功能。

- 扩展语法

使用关键字 extension 来声明扩展：

```Swift
extension SomeType {
    // 为 SomeType 添加的新功能写到这里
}
```
## 协议
协议 定义了一个蓝图，规定了用来实现某一特定任务或者功能的方法、属性，以及其他需要的东西。类、结构体或枚举都可以遵循协议，并为协议定义的这些要求提供具体实现。某个类型能够满足某个协议的要求，就可以说该类型遵循这个协议。

除了遵循协议的类型必须实现的要求外，还可以对协议进行扩展，通过扩展来实现一部分要求或者实现一些附加功能，这样遵循协议的类型就能够使用这些功能。

- 协议语法

协议的定义方式与类、结构体和枚举的定义非常相似：

```Swift
protocol SomeProtocol {
    // 这里是协议的定义部分
}
```

要让自定义类型遵循某个协议，在定义类型时，需要在类型名称后加上协议名称，中间以冒号（:）分隔。遵循多个协议时，各协议之间用逗号（,）分隔：

```Swift
struct SomeStructure: FirstProtocol, AnotherProtocol {
    // 这里是结构体的定义部分
}
```

拥有父类的类在遵循协议时，应该将父类名放在协议名之前，以逗号分隔：

```Swift
class SomeClass: SomeSuperClass, FirstProtocol, AnotherProtocol {
    // 这里是类的定义部分
}
```

- 委托（代理）模式

委托是一种设计模式，它允许类或结构体将一些需要它们负责的功能委托给其他类型的实例。委托模式的实现很简单：定义协议来封装那些需要被委托的功能，这样就能确保遵循协议的类型能提供这些功能。委托模式可以用来响应特定的动作，或者接收外部数据源提供的数据，而无需关心外部数据源的类型。

## 泛型
泛型代码让你能够根据自定义的需求，编写出适用于任意类型、灵活可重用的函数及类型。它能让你避免代码的重复，用一种清晰和抽象的方式来表达代码的意图。

- 泛型函数

```Swift
func swapTwoValues<T>(_ a: inout T, _ b: inout T) {
    let temporaryA = a
    a = b
    b = temporaryA
}
```

- 泛型类型

除了泛型函数，Swift 还允许你定义泛型类型。这些自定义类、结构体和枚举可以适用于任何类型，类似于 Array 和 Dictionary。

```Swift
struct Stack<Element> {
    var items = [Element]()
    mutating func push(_ item: Element) {
        items.append(item)
    }
    mutating func pop() -> Element {
        return items.removeLast()
    }
}
```
## 访问控制
在 Swift 语言中，访问修饰符有五种，分别为 fileprivate，private，internal，public 和 open。

> 其中 fileprivate 和 open 是 Swift 3 新添加的。由于过去 Swift 对于访问权限的控制，不是基于类的，而是基于文件的。这样会有问题，所以 Swift 3 新增了两个修饰符对原来的 private、public 进行细分。

- private

private 访问级别所修饰的属性或者方法只能在当前类里访问。
（注意：Swift4 中，extension 里也可以访问 private 的属性。）

- fileprivate

fileprivate 访问级别所修饰的属性或者方法在当前的 Swift 源文件里可以访问。（比如上面样例把 private 改成 fileprivate 就不会报错了）

- internal（默认访问级别，internal修饰符可写可不写）

1. internal 访问级别所修饰的属性或方法在源代码所在的整个模块都可以访问。
2. 如果是框架或者库代码，则在整个框架内部都可以访问，框架由外部代码所引用时，则不可以访问。
3. 如果是 App 代码，也是在整个 App 代码，也是在整个 App 内部可以访问。

- public

可以被任何人访问。但其他 module 中不可以被 override 和继承，而在 module 内可以被 override 和继承。

- open

可以被任何人使用，包括 override 和继承。

- 5种修饰符访问权限排序

从高到低排序如下：

open > public > interal > fileprivate > private


