# Observer（观察者模式） #
## 概述 ##
当对象间存在一对多关系时，则使用观察者模式（Observer Pattern）。 比如，当一个对象被修改时，则会自动通知它的依赖对象。观察者模式属于行为型模式。

## 使用 ##

### 实现 ###
1. 创建观察者
```Java
public interface Observer {

    void update();
}
```
```Java
public class Observer1 implements Observer {

    @Override
    public void update() {
        System.out.println("Observer1 收到通知！");
    }
}
```
```Java
public class Observer2 implements Observer {

    @Override
    public void update() {
        System.out.println("Observer2 收到通知！");
    }
}
```
2. 创建被观察目标
```Java
public interface Subject {

    /*增加观察者*/
    void add(Observer observer);

    /*删除观察者*/
    void del(Observer observer);

    /*通知所有的观察者*/
    void notifyObservers();

    /*自身的操作*/
    void operation();
}
```
```Java
public abstract class AbstractSubject implements Subject {

    private Vector<Observer> vector = new Vector<Observer>();

    @Override
    public void add(Observer observer) {
        vector.add(observer);
    }

    @Override
    public void del(Observer observer) {
        vector.remove(observer);
    }

    @Override
    public void notifyObservers() {
        Enumeration<Observer> enumo = vector.elements();
        while (enumo.hasMoreElements()) {
            enumo.nextElement().update();
        }
    }
}
```
```Java
public class MySubject extends AbstractSubject {

    @Override
    public void operation() {
        System.out.println("执行更新！");
        notifyObservers();
    }
}
```
3. 测试
```Java
public class ObserverTest {

    @Test
    public void testObserver(){
        Subject sub = new MySubject();
        sub.add(new Observer1());
        sub.add(new Observer2());
        sub.operation();
    }
}
```

4. 输出
```Java
03-23 13:49:11.081 24654-24677/? I/System.out: 执行更新！
03-23 13:49:11.081 24654-24677/? I/System.out: Observer1 收到通知！
03-23 13:49:11.081 24654-24677/? I/System.out: Observer2 收到通知！
```

## 使用场景 ##
1. 有多个子类共有的方法，且逻辑相同。 
2. 重要的、复杂的方法，可以考虑作为模板方法。

## 主要解决 ##
一个对象状态改变给其他对象通知的问题，而且要考虑到易用和低耦合，保证高度的协作。

## 优点 ##
1. 观察者和被观察者是抽象耦合的。 
2. 建立一套触发机制。

## 缺点 ##
1. 如果一个被观察者对象有很多的直接和间接的观察者的话，将所有的观察者都通知到会花费很多时间。
2. 如果在观察者和观察目标之间有循环依赖的话，观察目标会触发它们之间进行循环调用，可能导致系统崩溃。 
3. 观察者模式没有相应的机制让观察者知道所观察的目标对象是怎么发生变化的，而仅仅只是知道观察目标发生了变化。

## 注意事项 ##
1. JAVA 中已经有了对观察者模式的支持类。 
2. 避免循环引用。 
3. 如果顺序执行，某一观察者错误会导致系统卡壳，一般采用异步方式。