# Factory（工厂模式） #
## 概述 ##
工厂模式（Factory Pattern）是 Java 中最常用的设计模式之一。 这种类型的设计模式属于创建型模式，它提供了一种创建对象的最佳方式。

在工厂模式中，我们在创建对象时不会对客户端暴露创建逻辑，并且是通过使用一个共同的接口来指向新创建的对象。

## 使用 ##
### 示例 ###
比如说我开了一家超市，需要采购辣条，于是我找到了辣条工厂来采购辣条。 我并不需要知道辣条是怎么生产出来的，只需要提供所需要的种类，他们生产出来就行了。

### 实现 ###
1. 首先创建一个辣条类
```Java
public interface HotStrip {
    void info();//用于输出辣条信息
}
```
2. 然后实现不同种类的辣条
- 实现大面筋辣条
```Java
public class BigHotStrip implements HotStrip {

    @Override
    public void info() {
        System.out.println("这是大面筋！");
    }
}
```
- 实现亲嘴烧辣条
```Java
public class KissHotStrip implements HotStrip{

    @Override
    public void info() {
        System.out.println("这是亲嘴烧！");
    }
}
```
3. 然后创建一个工厂类用于生产辣条
```Java
public class HotStripFactory {

    public HotStrip produce(String type) {
        if ("kiss".equals(type)) {
            return new KissHotStrip();
        } else if ("big".equals(type)) {
            return new BigHotStrip();
        }
        return null;
    }
}
```
4. 最后模拟采购流程
```Java
public class FactoryTest {

    @Test
    public void testHotStrip() {
        HotStripFactory factory = new HotStripFactory();
        HotStrip hotStrip = factory.produce("kiss");//需要亲嘴烧时传入kiss
//        hotStrip = factory.produce("big");//需要大面筋时传入big
        hotStrip.info();
    }
}
```
> 可以看到客户并不知道工厂内部是怎么生产的辣条，只需要传入类型即可得到所需要的辣条。

## 使用场景 ##
1. 日志记录器：记录可能记录到本地硬盘、系统事件、远程服务器等，用户可以选择记录日志到什么地方。 
2. 数据库访问，当用户不知道最后系统采用哪一类数据库，以及数据库可能有变化时。 
3. 设计一个连接服务器的框架，需要三个协议，"POP3"、"IMAP"、"HTTP"，可以把这三个作为产品类，共同实现一个接口。

## 优点 ##
1. 一个调用者想创建一个对象，只要知道其名称就可以了。
2. 扩展性高，如果想增加一个产品，只要扩展一个工厂类就可以。
3. 屏蔽产品的具体实现，调用者只关心产品的接口。
## 缺点 ##
每次增加一个产品时，都需要增加一个具体类和对象实现工厂，使得系统中类的个数成倍增加，在一定程度上增加了系统的复杂度，同时也增加了系统具体类的依赖。这并不是什么好事。

## 注意事项 ##
作为一种创建类模式，在任何需要生成复杂对象的地方，都可以使用工厂方法模式。有一点需要注意的地方就是复杂对象适合使用工厂模式，而简单对象，特别是只需要通过 new 就可以完成创建的对象，无需使用工厂模式。如果使用工厂模式，就需要引入一个工厂类，会增加系统的复杂度。