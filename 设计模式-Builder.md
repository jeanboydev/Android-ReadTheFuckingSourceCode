# Builder（建造者模式） #
## 概述 ##
建造者模式（Builder Pattern）使用多个简单的对象一步一步构建成一个复杂的对象。 这种类型的设计模式属于创建型模式，它提供了一种创建对象的最佳方式。

一个 Builder 类会一步一步构造最终的对象。 该 Builder 类是独立于其他对象的。

主要解决在软件系统中，有时候面临着"一个复杂对象"的创建工作，其通常由各个部分的子对象用一定的算法构成； 由于需求的变化，这个复杂对象的各个部分经常面临着剧烈的变化，但是将它们组合在一起的算法却相对稳定。

## 使用 ##
### 示例 ###
我们的辣条销售异常火爆，但是辣条厂由于经营不善濒临倒闭，我们不能让辣条厂倒闭啊，没有了辣条以后就没有生意做了，影响我们以后上市啊。 索性就把辣条厂收购了，我们自己来管理。 收购了辣条厂发现之前的辣条种类很多，但是口味单一，现在需要拓展不同口味的辣条来满足更多的人群。

### 实现 ###
1. 首先调整下之前的辣条类
```Java
public interface HotStrip {
    String getType();//保存辣条的种类信息
}
```
2. 现有的辣条种类
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
3. 创建不同味道的辣条
```Java
public interface Taste {

    String getTaste();
}
```
```Java
public class SaltyHotStrip implements Taste {

    @Override
    public String getTaste() {
        return "咸味儿的";
    }
}
```
```Java
public class SweetHotStrip implements Taste {

    @Override
    public String getTaste() {
        return "甜味儿的";
    }
}
```
4. 创建一个有分类带味道的辣条
```Java
public class TasteHotStrip {

    private HotStrip type;
    private Taste taste;//味道

    public HotStrip getType() {
        return type;
    }

    public void setType(HotStrip type) {
        this.type = type;
    }

    public Taste getTaste() {
        return taste;
    }

    public void setTaste(Taste taste) {
        this.taste = taste;
    }
}
```
5. 创建一台可以生产不同味道辣条的机器
```Java
public interface Builder {

    void buildType(HotStrip type);

    void buildTaste(Taste taste);

    TasteHotStrip create();
}
```
```Java
public class TasteHotStripBuilder implements Builder {

    private TasteHotStrip tasteHotStrip = new TasteHotStrip();

    @Override
    public void buildType(HotStrip type) {
        tasteHotStrip.setType(type);
    }

    @Override
    public void buildTaste(Taste taste) {
        tasteHotStrip.setTaste(taste);
    }

    @Override
    public TasteHotStrip create() {
        return tasteHotStrip;
    }
}
```
6. 开一条生产线生产不同味道的辣条
```Java
public class Director {

    private Builder builder = null;

    public Director(Builder builder) {
        this.builder = builder;
    }

    public void construct(HotStrip type, Taste taste) {
        builder.buildType(type);
        builder.buildTaste(taste);
    }
}
```
7. 试运行下生产线看看效果
```Java
public class BuilderTest {

    @Test
    public void testTasteHotStrip() {
        Builder builder = new TasteHotStripBuilder();
        Director director = new Director(builder);

        HotStrip hotStrip = new BigHotStrip();
//        hotStrip = new KissHotStrip();
        Taste taste = new SweetHotStrip();
//        taste = new SaltyHotStrip();

        director.construct(hotStrip, taste);//可传入任何类型，味道
        TasteHotStrip tasteHotStrip = builder.create();

        System.out.println(tasteHotStrip.toString());
    }
}
```
> 可以看出，虽然我们生产的辣条种类和口味都不相同，但是它们都有相似的特征，都有种类和口味。 我们提取这些相似的特征，再组装到一起就可以满足我们的需求了。

## 使用场景 ##
JAVA 中的 StringBuilder。

## 优点 ##
1. 建造者独立，易扩展。
2. 便于控制细节风险。
## 缺点 ##
1. 产品必须有共同点，范围有限制。
2. 如内部变化复杂，会有很多的建造类。

## 注意事项 ##
与工厂模式的区别是： 建造者模式更加关注与零件装配的顺序。