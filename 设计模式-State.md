# State（状态模式） #
## 概述 ##
在状态模式（State Pattern）中，类的行为是基于它的状态改变的。这种类型的设计模式属于行为型模式。

在状态模式中，我们创建表示各种状态的对象和一个行为随着状态对象改变而改变的 context 对象。

## 使用 ##

### 实现 ###
1. 创建一个接口
```Java
public interface State {

    void doAction(Target target);
}
```
2. 创建实现接口的实体类
```Java
public class StartState implements State {


    @Override
    public void doAction(Target target) {
        System.out.println("设置状态为start");
        target.setState(this);
    }

    @Override
    public String toString() {
        return "StartState";
    }
}
```
```Java
public class StopState implements State {


    @Override
    public void doAction(Target target) {
        System.out.println("设置状态为stop");
        target.setState(this);
    }

    @Override
    public String toString() {
        return "StopState";
    }
}
```
3. 创建 Target 类
```Java
public class Target {

    private State state;

    public Target() {
        state = null;
    }

    public State getState() {
        return state;
    }

    public void setState(State state) {
        this.state = state;
    }
}
```
4. 使用 Target 来查看当状态 State 改变时的行为变化
```Java
public class StateTest {

    @Test
    public void testObserver(){
        Target target=new Target();

        StartState startState=new StartState();
        startState.doAction(target);

        StopState stopState=new StopState();
        stopState.doAction(target);

        System.out.println(target.getState().toString());
    }
}
```

5. 输出
```Java
03-23 14:04:02.751 25649-25676/? I/System.out: 设置状态为start
03-23 14:04:02.751 25649-25676/? I/System.out: 设置状态为stop
03-23 14:04:02.751 25649-25676/? I/System.out: StopState
```

## 使用场景 ##
1. 行为随状态改变而改变的场景。 
2. 条件、分支语句的代替者。

## 主要解决 ##
对象的行为依赖于它的状态（属性），并且可以根据它的状态改变而改变它的相关行为。

## 优点 ##
1. 封装了转换规则。 
2. 枚举可能的状态，在枚举状态之前需要确定状态种类。 
3. 将所有与某个状态有关的行为放到一个类中，并且可以方便地增加新的状态，只需要改变对象状态即可改变对象的行为。 
4. 允许状态转换逻辑与状态对象合成一体，而不是某一个巨大的条件语句块。 
5. 可以让多个环境对象共享一个状态对象，从而减少系统中对象的个数。

## 缺点 ##
1. 状态模式的使用必然会增加系统类和对象的个数。 
2. 状态模式的结构与实现都较为复杂，如果使用不当将导致程序结构和代码的混乱。 
3. 状态模式对"开闭原则"的支持并不太好，对于可以切换状态的状态模式，增加新的状态类需要修改那些负责状态转换的源代码，否则无法切换到新增状态，而且修改某个状态类的行为也需修改对应类的源代码。

## 注意事项 ##
在行为受状态约束的时候使用状态模式，而且状态不超过 5 个。