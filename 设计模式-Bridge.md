# Bridge（桥接模式） #
## 概述 ##
桥接（Bridge）是用于把抽象化与实现化解耦，使得二者可以独立变化。 这种类型的设计模式属于结构型模式，它通过提供抽象化和实现化之间的桥接结构，来实现二者的解耦。

桥接模式是软件设计模式中最复杂的模式之一，它把事物对象和其具体行为、具体特征分离开来，使它们可以各自独立的变化。

## 使用 ##
### 示例 ###
回到我们的辣条工厂，之前的辣条生产线和包装线都是一条线完成的，现在需要将辣条的生产和包装分开，使分工更加明确。

### 实现 ###
1. 之前的辣条
```Java
public interface HotStrip {
    String getType();//保存辣条的种类信息
}
```
```Java
public class KissHotStrip implements HotStrip {

    @Override
    public String getType() {
        return "这是亲嘴烧！";
    }
}
```
```Java
public class BigHotStrip implements HotStrip {

    @Override
    public String getType() {
        return "这是大面筋！";
    }

}
```
2. 将辣条生产和包装分离
```Java
public abstract class Bridge {

    private HotStrip hotStrip;

    public HotStrip getHotStrip() {
        return hotStrip;
    }

    public void setHotStrip(HotStrip hotStrip) {
        this.hotStrip = hotStrip;
    }

    public abstract void pack();

}
```
3. 创建辣条包装生产线
```Java
public class PackageBridge extends Bridge {
    
    @Override
    public void pack() {
        System.out.println("包装辣条：" + getHotStrip().getType());
    }
}
```
4. 测试生产线
```Java
public class BridgeTest {

    @Test
    public void testBridge() {

        Bridge bridge = new PackageBridge();

        HotStrip hotStrip1 = new KissHotStrip();
        bridge.setHotStrip(hotStrip1);
        bridge.pack();

        HotStrip hotStrip2 = new BigHotStrip();
        bridge.setHotStrip(hotStrip2);
        bridge.pack();
    }
}
```

> 可以看出，不管是生产任何种类的辣条都不会影响包装的生产线。

## 使用场景 ##
1. 如果一个系统需要在构件的抽象化角色和具体化角色之间增加更多的灵活性，避免在两个层次之间建立静态的继承联系，通过桥接模式可以使它们在抽象层建立一个关联关系。 
2. 对于那些不希望使用继承或因为多层次继承导致系统类的个数急剧增加的系统，桥接模式尤为适用。
3. 一个类存在两个独立变化的维度，且这两个维度都需要进行扩展。

## 主要解决 ##
在有多种可能会变化的情况下，用继承会造成类爆炸问题，扩展起来不灵活。

## 优点 ##
1. 抽象和实现的分离。
2. 优秀的扩展能力。
3. 增加了类的透明度。
4. 灵活性好。
## 缺点 ##
桥接模式的引入会增加系统的理解与设计难度，由于聚合关联关系建立在抽象层，要求开发者针对抽象进行设计与编程。

## 注意事项 ##
对于两个独立变化的维度，使用桥接模式再适合不过了。