# Adapter（适配器模式） #
## 概述 ##
适配器模式（Adapter Pattern）是作为两个不兼容的接口之间的桥梁。 这种类型的设计模式属于结构型模式，它结合了两个独立接口的功能。

主要解决在软件系统中，常常要将一些"现存的对象"放到新的环境中，而新环境要求的接口是现对象不能满足的。

## 使用 ##
### 示例 ###
比如说我们使用读卡器通过电脑读取SD卡。 读卡器可以看做是适配器。

### 实现 ###
1. 首先创建一个SD卡
```Java
public class SDCard {

    private String data;

    public void setData(String data) {
        this.data = data;
    }

    public String getData() {
        return data;
    }
}
```
2. 然后我们需要一台电脑读取数据
```Java
public interface USBInterface {

    String readData();
}
```
```Java
public class Computer {

    public void showData(USBInterface usb) {
        System.out.println(usb.readData());
    }
}
```
3. 创建读卡器
```Java
public class SDCardAdapter implements USBInterface {

    private SDCard card;

    public SDCardAdapter(SDCard card) {
        this.card = card;
    }

    @Override
    public String readData() {
        return card.getData();
    }
}
```
4. 使用读卡器读取并显示数据
```Java
public class AdapterTest {

    @Test
    public void testAdapter() {
        SDCard card = new SDCard();
        card.setData("SD Card 保存的数据！");

        USBInterface usb = new SDCardAdapter(card);

        Computer computer = new Computer();
        computer.showData(usb);
    }
}
```

> 可以看出，电脑使用USB接口读取数据，读卡器可以插卡共提供USB接口，这样就可以使用电脑读取我们的SD卡了。

## 使用场景 ##
1. JAVA 中的 jdbc。
2. 在 LINUX 上运行 WINDOWS 程序。
3. JAVA JDK 1.1 提供了 Enumeration 接口，而在 1.2 中提供了 Iterator 接口，想要使用 1.2 的 JDK，则要将以前系统的 Enumeration 接口转化为 Iterator 接口，这时就需要适配器模式。

## 优点 ##
1. 可以让任何两个没有关联的类一起运行。
2. 提高了类的复用。
3. 增加了类的透明度。
4. 灵活性好。
## 缺点 ##
1. 过多地使用适配器，会让系统非常零乱，不易整体进行把握。
2. 由于 JAVA 至多继承一个类，所以至多只能适配一个适配者类，而且目标类必须是抽象类。

## 注意事项 ##
适配器不是在详细设计时添加的，而是解决正在服役的项目的问题。