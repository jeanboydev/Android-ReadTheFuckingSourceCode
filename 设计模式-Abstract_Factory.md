# Abstract Factory（抽象工厂模式） #
## 概述 ##
抽象工厂模式（Abstract Factory Pattern）是围绕一个超级工厂创建其他工厂。 该超级工厂又称为其他工厂的工厂。 这种类型的设计模式属于创建型模式，它提供了一种创建对象的最佳方式。

在抽象工厂模式中，接口是负责创建一个相关对象的工厂，不需要显式指定它们的类。 每个生成的工厂都能按照工厂模式提供对象。


## 使用 ##
### 示例 ###
[Factory（工厂模式）](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/设计模式-Factory.md)

在上一篇中我们成功的采购了辣条，并且卖的特别火爆。 随着生意的火爆我们需要采购更多种类的辣条， 但是每次采购都很痛苦，都得提供种类的名称，比如： kiss，big 等。 于是跟厂家商量你们这的辣条种类太多了，每次采购都很麻烦，有没有简单方式来方便我们采购？ 厂家一听,确实太麻烦了，那就让他们的销售经理 Provider 来帮助我们采购。

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
3. 然后创建销售经理负责提供辣条
```Java
public interface Provider {

     HotStrip produce();
}
```
4. 分别实现销售经理负责种类的辣条生产
```Java
public class BigFactory implements Provider {

    @Override
    public HotStrip produce() {
        return new BigHotStrip();
    }
}
```
```Java
public class KissFactory implements Provider {
    
    @Override
    public HotStrip produce() {
        return new KissHotStrip();
    }
}
```


5. 最后模拟采购流程
```Java
public class FactoryTest {

    @Test
    public void testHotStrip() {
        HotStripFactory factory = new HotStripFactory();
        HotStrip hotStrip = factory.produce("kiss");//需要亲嘴烧时传入kiss
//        hotStrip = factory.produce("big");//需要大面筋时传入big
        hotStrip.info();
    }

 	@Test
    public void testAbstractHotStrip() {//抽象工厂方式
        Provider provider = new BigFactory();//辣条的种类交给Provider提供，调用者不需要关心辣条的种类了
//         provider = new KissFactory();
        HotStrip hotStrip = provider.produce();
        hotStrip.info();
    }
}
```
> 可以看出客户并不知道 Provider 是怎么提供的辣条，也不需要再传入参数了。

## 使用场景 ##
QQ 换皮肤，一整套一起换。

## 优点 ##
1.  抽象工厂模式隔离了具体类的生成，使得客户并不需要知道什么被创建。 由于这种隔离，更换一个具体工厂就变得相对容易，所有的具体工厂都实现了抽象工厂中定义的那些公共接口，因此只需改变具体工厂的实例，就可以在某种程度上改变整个软件系统的行为。
2. 当一个产品工厂中的多个对象被设计成一起工作时，它能够保证客户端始终只使用同一个产品工厂中的对象。
3. 增加新的产品工厂很方便，无须修改已有系统，符合“开闭原则”。
## 缺点 ##
增加新的产品等级结构麻烦（比如：增加方便面种类产品），需要对原有系统进行较大的修改，甚至需要修改抽象层代码，这显然会带来较大的不便，违背了“开闭原则”。