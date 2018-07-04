# Facede - 外观模式

## 引入

最近在开发微信小程序和支付宝小程序，它们都有自己的架构。

![Facade-01](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/design_patterns/Facade-01.png)

一般开发流程是，开发两套不同的小程序，也就是写两套代码。费时费力，效率很低。

考虑到，微信和支付宝整体架构很基本一致，在代码与API上有很多相似性。能不能写一套代码运行在两个平台呢？

![Facade-03](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/design_patterns/Facade-03.png)

答案是可以的，通过封装两个平台API的差异，抽象出一个统一的API。

## 示例代码

- 微信

  ```js
  wx.showToast({
      title: 'content',
      icon: 'type',
      duration: 1500,
      success: function () {},
      fail: function (res) {},
      complete: function (res) {}
  });
  ```

- 支付宝

  ```js
  my.showToast({
      type: 'type',
      content: 'content',
      duration: 1500,
      success: function () {},
      fail: function (res) {},
      complete: function (res) {}
  });
  ```

- Arch

  ```js
  arch.ui.showToast({
      type: 'type',
      content: 'content',
      duration: 1500,
      onSuccess: function () {},
      onError: function (res) {},
      onComplete: function (res) {}
  });
  ```

## Facede

> 牛津词典：
>
> 1. the front of a building.（建筑物的）正面，立面 
> 2. the way that sb/sth appears to be, which is different from the way sb/sth really is.（虚假的）表面，外表 

外观：

> 1. 物体外表的样子。
> 2. 哲学名词。指掩盖事物本质的现象，即假象。

## 简介

> Facade Pattern: Provide a unified interface to a set of interfaces in a subsystem. Facade defines a higher-level interface that makes the subsystem easier to use. 

为子系统中的一组接口提供一个统一的入口。外观模式定义 了一个高层接口，这个接口使得这一子系统更加容易使用。 

外观模式又称为门面模式，它是一种对象结构型模式。外观模式是迪米特法则的一种具体实现，通过引入一个新的外观角色可以降低原有系统的复杂度，同时降低客户端与子系统的耦合度。

## 解决问题

将一个系统划分成若干个子系统有利于降低系统的复杂性。一个常见的设计目标是使子系统间的通信和相互依赖关系达到最小。达到该目标的途径之一就是引入一个外观对象，它使子系统中较一般的设施提提供了一个单一而简单的界面。

![Facade-04](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/design_patterns/Facade-04.png)

## 结构

![Facade-05](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/design_patterns/Facade-05.png)

外观模式的主要目的在于降低系统的复杂程度，在面向对象软件系统中，类与类之间的关系越多，不能表示系统设计得越好，反而表示系统中类之间的耦合度太大，这样的系统在维护和修改时都缺乏灵活性，因为一个类的改动会导致多个类发生变化，而外观模式的引入在很大程度上降低了类与类之间的耦合关系。

引入外观模式之后，增加新的子系统或者移除子系统都非常方便，客户类无须进行修改(或者极少的修改)，只需要在外观类中增加或移除对子系统的引用即可。从这一点来说，外观模式在一定程度上并不符合开闭原则，增加新的子系统需要对原有系统进行一定的修改，虽然这个修改工作量不大。

外观模式中所指的子系统是一个广义的概念，它可以是一个类、一个功能模块、系统的一个组成部分或者一个完整的系统。子系统类通常是一些业务类，实现了一些具体的、独立的业务功能。

## 示例代码

```java
class SubSystemA {
    public void MethodA() {
    	//业务实现代码
    } 
}
class SubSystemB {
    public void MethodB() {
    	//业务实现代码
    }
}
class SubSystemC {
    public void MethodC() {
    	//业务实现代码
    }
}
```

```java
//引入外观模式
class Facade {
    private SubSystemA obj1 = new SubSystemA();
    private SubSystemB obj2 = new SubSystemB();
    private SubSystemC obj3 = new SubSystemC();
    
    public void Method() {
        obj1.MethodA();
        obj2.MethodB();
        obj3.MethodC();
	}
}
//客户端调用
class Program {
    static void Main(string[] args) {
        Facade facade = new Facade();
        facade.Method();
    }
}
```



## 抽象外观类

![Facade-06](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/design_patterns/Facade-06.png)

在标准的外观模式结构图中，如果需要增加、删除或更换与外观类交互的子系统类，必须修改外观类或客户端的源代码，这将违背开闭原则，因此可以通过引入抽象外观类来对系统进行改进，在一定程度上可以解决该问题。

![Facade-07](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/design_patterns/Facade-07.png)

在引入抽象外观类之后，客户端可以针对抽象外观类进行编程，对于新的业务需求，不需要修改原有外观类，而对应增加一个新的具体外观类，由新的具体外观类来关联新的子系统对象，同时通过修改配置文件来达到不修改任何源代码并更换外观类的目的。

## 示例代码

```java
class SubSystemA {
    public void MethodA() {
    	//业务实现代码
    } 
}
class SubSystemB {
    public void MethodB() {
    	//业务实现代码
    }
}
```

```java
//引入抽象外观类
abstract class AbstractFacade {
    public abstract void Method();
}
```

```java
//引入外观模式
class Facade extend AbstractFacade {
    private SubSystemA obj1 = new SubSystemA();
    private SubSystemB obj2 = new SubSystemB();
    
    public void Method() {
        obj1.MethodA();
        obj2.MethodB();
	}
}
//客户端调用
class Program {
    static void Main(string[] args) {
        AbstractFacade facade = new Facade();
        facade.Method();
    }
}
```

## 总结

- 优点
  1. 它对客户端屏蔽了子系统组件，减少了客户端所需处理的对象数目，并使得子系统使用起来更加容易。通过引入外观模式，客户端代码将变得很简单，与之关联的对象也很少。
  2. 它实现了子系统与客户端之间的松耦合关系，这使得子系统的变化不会影响到调用它的客户端，只需要调整外观类即可。
  3. 一个子系统的修改对其他子系统没有任何影响，而且子系统内部变化也不会影响到外观对象。
- 缺点
  1. 不能很好地限制客户端直接使用子系统类，如果对客户端访问子系统类做太多的限制则减少了可变性和灵活性。
  2. 如果设计不当，增加新的子系统可能需要修改外观类的源代码，违背了开闭原则。
- 使用场景
  1. 当要为访问一系列复杂的子系统提供一个简单入口时可以使用外观模式。
  2. 客户端程序与多个子系统之间存在很大的依赖性。引入外观类可以将子系解耦，从而提高子系统的独立性和可移植性。
  3. 在层次化结构中，可以使用外观模式定义系统中每一层的入口，层与层之间不直接产生联系，而通过外观类建立联系，降低层之间的耦合度。

## 应用实例

- IDE 操作
- 工具类
- SDK