# Flyweight（享元模式） #
## 概述 ##
享元模式（Flyweight Pattern）主要用于减少创建对象的数量，以减少内存占用和提高性能。 这种类型的设计模式属于结构型模式，它提供了减少对象数量从而改善应用所需的对象结构的方式。

享元模式的主要目的是实现对象的共享，即共享池，当系统中对象多的时候可以减少内存的开销，通常与工厂模式一起使用。

## 使用 ##
### 实现 ###
1. 创建享元目标类
```Java
public class Target {

    private String name;

    public Target(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    @Override
    public String toString() {
        return "Target{" +
                "name='" + name + '\'' +
                '}';
    }
}
```
2. 创建工厂类
```Java
public class TargetFactory {

    private static final HashMap<String, Target> map = new HashMap();

    public static Target getTarget(String name) {
        Target target = map.get(name);
        if (target == null) {
            target = new Target(name);
            map.put(name, target);
            System.out.println("创建新对象: " + name);
        }
        return target;
    }
}
```
3. 测试
```Java
public class FlyweightTest {

    private String[] nameArr = new String[]{"1", "2", "3", "4", "5"};

    @Test
    public void testFlyweight() {
        for (int i = 0; i < 20; ++i) {
            Target target = TargetFactory.getTarget(getRandomName());
            System.out.println("获取到对象: " + target.toString());
        }
    }

    private String getRandomName() {
        return nameArr[(int) (Math.random() * nameArr.length)];
    }
}
```
4. 输入结果
```Java
03-22 16:59:57.831 27045-27075/? I/System.out: 创建新对象: 1
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='1'}
03-22 16:59:57.831 27045-27075/? I/System.out: 创建新对象: 5
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='5'}
03-22 16:59:57.831 27045-27075/? I/System.out: 创建新对象: 2
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='2'}
03-22 16:59:57.831 27045-27075/? I/System.out: 创建新对象: 4
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='4'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='5'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='2'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='4'}
03-22 16:59:57.831 27045-27075/? I/System.out: 创建新对象: 3
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='3'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='1'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='1'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='3'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='3'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='4'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='4'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='1'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='4'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='3'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='1'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='5'}
03-22 16:59:57.831 27045-27075/? I/System.out: 获取到对象: Target{name='4'}
```

> 通过输出结果可以看出，已创建过的类不会再重新创建。

## 使用场景 ##
1. 系统有大量相似对象。
2. 需要缓冲池的场景。

## 优点 ##
大大减少对象的创建，降低系统的内存，使效率提高。

## 缺点 ##
提高了系统的复杂度，需要分离出外部状态和内部状态，而且外部状态具有固有化的性质，不应该随着内部状态的变化而变化，否则会造成系统的混乱。

## 注意事项 ##
1. 注意划分外部状态和内部状态，否则可能会引起线程安全问题。
2. 这些类必须有一个工厂对象加以控制。