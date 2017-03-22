# Proxy（代理模式） #
## 概述 ##
在代理模式（Proxy Pattern）中，一个类代表另一个类的功能。 这种类型的设计模式属于结构型模式。

在代理模式中，我们创建具有现有对象的对象，以便向外界提供功能接口。

## 使用 ##

### 实现 ###
1. 直接看代码
```Java
public interface Sourceable {  
    public void method();  
}  
```
```Java
public class Source implements Sourceable {  
  
    @Override  
    public void method() {  
        System.out.println("the original method!");  
    }  
}  
```
```Java
public class Proxy implements Sourceable {  
  
    private Source source;  
    public Proxy(){  
        super();  
        this.source = new Source();  
    }  
    @Override  
    public void method() {  
        before();  
        source.method();  
        atfer();  
    }  
    private void atfer() {  
        System.out.println("after proxy!");  
    }  
    private void before() {  
        System.out.println("before proxy!");  
    }  
}  
```
2. 测试
```Java
public class ProxyTest {

    @Test
    public void testFacade() {

        Sourceable source = new Proxy();  
        source.method();  
    }
}
```

## 使用场景 ##
按职责来划分，通常有以下使用场景： 
1. 远程代理。
2. 虚拟代理。 
3. Copy-on-Write 代理。 
4. 保护（Protect or Access）代理。 
5. Cache代理。 
6. 防火墙（Firewall）代理。 
7. 同步化（Synchronization）代理。 
8. 智能引用（Smart Reference）代理。

## 主要解决 ##
在直接访问对象时带来的问题，比如说：要访问的对象在远程的机器上。 在面向对象系统中，有些对象由于某些原因（比如对象创建开销很大，或者某些操作需要安全控制，或者需要进程外的访问），直接访问会给使用者或者系统结构带来很多麻烦，我们可以在访问此对象时加上一个对此对象的访问层。

## 优点 ##
1. 职责清晰。
2. 高扩展性。
3. 智能化。

## 缺点 ##
1. 由于在客户端和真实主题之间增加了代理对象，因此有些类型的代理模式可能会造成请求的处理速度变慢。
2. 实现代理模式需要额外的工作，有些代理模式的实现非常复杂。

## 注意事项 ##
1. 和适配器模式的区别：适配器模式主要改变所考虑对象的接口，而代理模式不能改变所代理类的接口。
2. 和装饰器模式的区别：装饰器模式为了增强功能，而代理模式是为了加以控制。