# Mediator（中介者模式） #
## 概述 ##
中介者模式（Mediator Pattern）是用来降低多个对象和类之间的通信复杂性。 这种模式提供了一个中介类，该类通常处理不同类之间的通信，并支持松耦合，使代码易于维护。 中介者模式属于行为型模式。

## 使用 ##
### 示例 ###
我们来模拟一下，通过中介租房的过程。

### 实现 ###
1. 创建一个需要租房的人
```Java
public class Person {

    private String name;

    public Person(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void lease() {
        System.out.println(getName() + ":我想租房！");
    }
}
```
2. 创建房东
```Java
public class Landlord {

    private String name;

    public Landlord(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public void hire() {
        System.out.println(getName() + ":我想把房子租出去！");
    }

}
```
3. 创建中介负责把房东的房子租给租户
```Java
public class Mediator {

    public void handle(Person person, Landlord landlord) {
        person.lease();
        landlord.hire();
        System.out.println("中介将" + landlord.getName() + "的房子租给了" + person.getName());
    }

}
```
4. 测试
```Java
public class MediatorTest {

    @Test
    public void testMediator() {
        Person person = new Person("张三");
        Landlord landlord = new Landlord("李四");

        Mediator mediator = new Mediator();
        mediator.handle(person, landlord);

    }
}
```

5. 输出
```Java
03-23 13:23:39.911 10396-10417/com.jeanboy.app.designpatterns I/System.out: 张三:我想租房！
03-23 13:23:39.911 10396-10417/com.jeanboy.app.designpatterns I/System.out: 李四:我想把房子租出去！
03-23 13:23:39.911 10396-10417/com.jeanboy.app.designpatterns I/System.out: 中介将李四的房子租给了张三
```

> 通过输出信息可以看出，通过中介将房东李四的房子租给了张三。

## 使用场景 ##
1. 系统中对象之间存在比较复杂的引用关系，导致它们之间的依赖关系结构混乱而且难以复用该对象。 
2. 想通过一个中间类来封装多个类中的行为，而又不想生成太多的子类。

## 主要解决 ##
对象与对象之间存在大量的关联关系，这样势必会导致系统的结构变得很复杂，同时若一个对象发生改变，我们也需要跟踪与之相关联的对象，同时做出相应的处理。

## 优点 ##
1. 降低了类的复杂度，将一对多转化成了一对一。 
2. 各个类之间的解耦。 
3. 符合迪米特原则。

## 缺点 ##
中介者会庞大，变得复杂难以维护。

## 注意事项 ##
不应当在职责混乱的时候使用。