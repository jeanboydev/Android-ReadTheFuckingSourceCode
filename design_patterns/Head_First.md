# Head First

不管当初软件设计得多好，一段时间之后，总是需要成长与改变，否则软件就会“死亡”。

## 面向对象（OO）

1. 抽象
2. 封装
3. 多态
4. 继承

良好的 OO 设计：可复用，可扩充，可维护。

## 设计原则

- 单一职责原则

一个类有且仅有一个职责，只有一个引起它变化的原因。

> 一个类应该只负责与它相关的操作，不相关的不要放在一起。

- 开闭原则

一个软件实体如类，模块和函数应当对扩展开放，对修改关闭。 即软件实体应尽量在不修改原有代码的情况下进行扩展。

> 封装变化部分，可提高程序可维护性，复用性，稳定性。

- 里氏代换原则

所有引用基类的地方必须能透明地使用其子类的对象。

> 只要父类能出现的地方子类就可以出现，而且替换为子类也不会产生任何错误或异常，使用者根本就不需要知道是父类还是子类，但是反过来不一定成立。可增强程序健壮性，保持兼容性。

- 接口隔离原则

不能强迫用户去依赖那些他们不使用的接口。

> 接口尽量细化，方法尽量少，可提高程序的灵活性，可维护性。

- 依赖倒置原则

高层模块不应该依赖低层模块，两者都应该依赖其抽象；抽象不应该依赖细节；细节应该依赖抽象。

> 面向接口编程，高层不依赖底层，可提高程序的扩展性，可维护性。

- 合成复用原则

尽量使用对象组合，而不是继承来达到复用的目的。

- 迪米特法则

一个软件实体应当尽可能少地与其他实体发生相互作用。

> 最少了解原则，对耦合的类知道的最少，只与直接依赖的类交互。比如：A<-B<-C，A 不能通过 B 操作 C 的方法，只能通过 B 来操作 C。
> 核心观念是解耦，可提供高内聚，低耦合的程序。

## 策略模式

定义了算法组，分别封装起来，让他们之间可以互相替换，此模式让算法的变化独立于使用算法的客户。

## 观察者模式

在对象之间定义一对多的依赖，这样一来，当一个对象改变状态，依赖它的对象都会收到通知。

## 装饰者模式

动态地将责任附加到对象上。想要扩展功能，装饰者提供有别于继承的另一种选择。

## 工厂模式

- 简单工厂

定义了一个创建对象的接口，但由于子类决定要实例化的类是哪一个。工厂方法让类把实例化推迟到子类。

- 抽象工厂

用于创建相关或依赖对象的家族，而不需要明确具体类。

## 单例模式

确保一个类只有一个实例，并提供一个全局的访问点。

1. 懒汉式

```Java
public class Singleton {  
    private static Singleton instance = null;  
    private Singleton() {}

    public static Singleton getInstance() {
        //同时两个线程中获取单例的情况：
        //第一个线程获取时为空，会创建一个实例
        //第二个线程获取时还没有创建完，也会为空，会创建第二个实例
        //这就创建了两个实例
        if (instance == null) {
            instance = new Singleton();  
        }
        return instance;  
    }
}
```

2. 加锁方式

```Java
public class Singleton {  
    private static Singleton instance = null;  
    private Singleton() {}
    
    //加锁
    //每次调用该方法时，如果有线程使用则等待
    //确保只有一个线程进入该方法
    //缺点：性能降低，只有第一次创建实例时才需要同步
    public static synchronized Singleton getInstance() {  
         if (instance == null) {  
             instance = new Singleton();  
         }  
         return instance;  
    }
}
```

3. 饿汉式

```Java
public class Singleton {  
    private static Singleton instance = new Singleton();  
    private Singleton() {}
    
    public static Singleton getInstance(){
        //保证了任何线程访问之前已经创建了实例
        return instance;
    }
}
```

4. 双重检查加锁

```Java
public class Singleton {
    //volatile 关键词确保当 instance 变量被赋值时，多个线程之间数据共享
    private volatile static Singleton instance = null;  
    private Singleton() {}
    
    public static Singleton getInstance(){
        //检查实例，若不存在，进入同步代码块
        //只有第一次调用时实例才不存在
        if(instance == null) {
            synchronized(Singleton.class) {
                //再检查一次，如果仍为空才创建实例
                if(instance == null){
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

> 双重锁不适用于 1.4 及更早版本的 Java，volatile 关键字的实现会导致双重检验加锁的实效，现在可忽略。

5. 匿名内部类

```Java
public class Singleton {  
    private Singleton() {} 
    //延迟加载，减少内存开销  
    private static class SingletonHolder {  
        private static SingletonInner instance = new SingletonInner();  
    }  

    public static Singleton getInstance() {  
        return SingletonHolder.instance;  
    }
}
```

## 命令模式

将请求封装成对象，以便使用不同的请求、队列或者日志来参数化其他对象。命令模式也支持可撤销的操作。

- 使用场景

日程安排，线程池，工作队列，日志记录

## 适配器模式

将一个类的接口，转换成客户期望的另一个接口。适配器让原本接口不兼容的类可以合作无间。

- 使用场景

Iterator，转换两个不兼容的接口

## 外观模式

提供了一个统一的接口，用来访问子系统中的一群接口。外观定义了一个高层接口，让子系统更容易使用。

## 模板方法模式

在一个方法中定义一个算法的骨架，而将一些步骤延迟到子类中，模板方法使得子类可以在不改变的算法结构的情况下，重新定义算法中的某些步骤。

- 使用场景

sort()

## 迭代器模式

提供一种方法顺序访问一个聚合对象中的各个元素，而又不暴露其内部的表示。

- 使用场景

Iterator()

## 组合模式

允许你将对象组合成树形结构来表现“整体/部分”层次结构。组合能让客户以一致的方式处理个别对象以及对象组合。

- 使用场景

树形结构，文件夹

## 状态模式

允许对象在内部状态改变时改变它的行为，对象看起来好像修改了它的类。

## 代理模式

为另一个对象提供一个替身或占位符以访问这个对象。

## 复合模式

模式

