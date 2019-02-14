# Groovy Language

- [Groovy - 官方文档](http://www.groovy-lang.org/documentation.html)

Gradle 依赖于 Groovy，Groovy 同时本身是一种 DSL。所以学习 Gradle 之前我们先熟悉一下 Groovy 语言。

> DSL 的全称是 Domain Specific Language，即领域特定语言，或者直接翻译成”特定领域的语言”，算了，再直接点，其实就是这个语言不通用，只能用于特定的某个领域，俗称“小语言”。因此 DSL 也是语言。

Groovy 程序运行时，首先被编译成 Java 字节码，然后通过 JVM 来执行。  Java, Groovy 和 JVM 之间的关系类似于下图： 

![img](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/gradle/01.png)

实际上，由于 Groovy Code 在真正执行的时候，已经变成了 Java 字节码， 因此 JVM 根本不知道自己运行的是 Groovy 代码。

## 环境搭建

- 配置 Java JDK

  Groovy 是依赖于 Java 的，所以首先要配置好 JDK。

- 下载安装 Groovy

  http://groovy-lang.org/download.html

  下载完解压放在固定目录下。

- 配置环境变量 

  > // 配置 Groovy 环境变量
  >
  > $ vim ~/.bash_profile

  ```js
  export PATH=$PATH:/Users/<username>/Develop/groovy-2.4.15/bin 
  ```

  > // 重新加载配置文件，使配置生效
  >
  > $ source ~/.base_profile
  >
  > // 打印版本号
  >
  > $ groovy -v

  显示结果为：

  ```json
  Groovy Version: 2.4.15 JVM: 9.0.1 Vendor: Oracle Corporation OS: Mac OS X
  ```

- Hello World

  创建一个 `hello.groovy` 文件。

  > $ vim hello.groovy 

  输入代码：

  ```groovy
  println "Hello Groovy!"
  ```

  保存并执行

  > $ groovy hello.groovy

  输出结果为：

  ```json
  Hello Groovy!
  ```

## 基本语法

默认情况下，Groovy 在代码中包括以下库，因此您不需要显式导入它们。

```groovy
import java.lang.* 
import java.util.* 
import java.io.* 
import java.net.* 

import groovy.lang.* 
import groovy.util.* 

import java.math.BigInteger 
import java.math.BigDecimal
```

- 变量

  ```groovy
  def variable = 1//不需要指定类型，不需要分号结尾
  def int x = 1//也可以指定类型
  ```

- 函数

  ```groovy
  //无需指定参数类型
  String test(arg1, arg2) {
      return "hello"
  }
  
  //返回值也可以无类型
  def test2(arg1, arg2) {
      return 1
  }
  
  def getResult() {
      "First Blood, Double Kill" // 如果这是最后一行代码，则返回类型为String
      1000 //如果这是最后一行代码，则返回类型为Integer
  }
  
  //函数调用，可以不加()
  test a,b
  test2 a,b
  getResult()
  ```

  调用函数要不要带括号，我个人意见是如果这个函数是 Groovy API 或者 Gradle API 中比较常用的，比如 println，就可以不带括号，否则还是带括号。

- 字符串

  ```groovy
  //单引号包裹的内容严格对应Java中的String，不对$符号进行转义
  def singleQuote='I am $ dolloar' //打印singleQuote时，输出I am $ dollar
  
  def x = 1
  def test = "I am $x" //打印test时，将输出I am 1
  ```

- 容器类

  Groovy中的容器类主要有三种：  List(链表)、Map(键-值表)及Range(范围)。

  ```groovy
  //List
  // 元素默认为Object，因此可以存储任何类型
  def aList = [5, 'test', true]
  println aList.size  //结果为3
  println aList[2]  //输出true
  aList[10] = 8
  println aList.size // 在index=10的位置插入元素后，输出11，即自动增加了长度
  println aList[9] //输出null， 自动增加长度时，未赋值的索引存储null
  
  //添加as关键字，并指定类型
  def aList = [5, 'test', true] as int[]
  
  //Map
  def aMap = ['key1':1, "key2":'test', key3:true]
  
  //读取元素
  println aMap.key1    //结果为1
  println aMap.key2    //结果为test
               //注意这种使用方式，key不用加引号
  
  println aMap['key2'] //结果为test
  
  //插入元素
  aMap['key3'] = false
  println aMap         //结果为[key1:1, key2:test, key3:false] 
                       //注意用[]持有key时，必须加引号
  
  aMap.key4 = 'fun'    //Map也支持自动扩充
  println aMap         //结果为[key1:1, key2:test, key3:false, key4:fun]
  
  //Range
  def aRange = 1..5
  println aRange       // [1, 2, 3, 4, 5]
  
  aRange = 1..<6       
  println aRange       // [1, 2, 3, 4, 5]
  
  println aRange.from  // 1
  println aRange.to    // 5
  
  println aRange[0]    //输出1
  aRange[0] = 2        //抛出java.lang.UnsupportedOperationException
  ```

- 闭包

  ```groovy
  //同样用def定义一个闭包
  def aClosure = {
      //代码为具体执行时的代码
      println 'this is closure'
  }
  
  //像函数一样调用，无参数
  aClosure() //将执行闭包中的代码，即输出'this is closure'
  
  //下面这种写法也可以
  //aClosure.call()
  ```

- 类

  Groovy 可以像 Java 那样定义类，例如：

  ```groovy
  package com.jeanboy.groovy
  
  class Test {
      String mName
      String mTitle
  
      Test(name, title) {
          mName = name
          mTitle = title
      }
  
      def print() {
          println mName + ' ' + mTitle
      }
  }
  ```

  与 Java 不同的是，如果不声明 public/private 等访问权限，  Groovy 中定义类的方法及成员变量均默认是 public 的。

  与 Java 一样，其它文件如果需要使用这个类时， 需要使用 import 关键字导入。

  例如，在 Test 类的根目录下创建一个测试文件 test.groovy 时， 可以这么使用 Test.groovy：

  ```groovy
  import com.jeanboy.groovy.Test
  
  def test = new Test('superman', 'hero')
  test.print()
  ```

- 文件

  ```groovy
  def targetFile = new File("/home/jeanboy/Desktop/file.txt")
  //读文件的每一行
  targetFile.eachLine { String oneLine ->
      println oneLine
  }
  def bytes = targetFile.getBytes()//返回文件对应的 byte()
  ```

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！