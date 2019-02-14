# Strategy（策略模式） #
## 概述 ##
在策略模式（Strategy Pattern）中，一个类的行为或其算法可以在运行时更改。 这种类型的设计模式属于行为型模式。

## 使用 ##

### 实现 ###
1. 创建一个接口
```Java
public interface Strategy {

    int doOperation(int num1, int num2);
}
```
2. 创建实现接口的实体类
```Java
public class OperationAdd implements Strategy {

    @Override
    public int doOperation(int num1, int num2) {
        return num1 + num2;
    }
}
```
```Java
public class OperationSubstract implements Strategy {

    @Override
    public int doOperation(int num1, int num2) {
        return num1 - num2;
    }
}
```
```Java
public class OperationMultiply implements Strategy {

    @Override
    public int doOperation(int num1, int num2) {
        return num1 * num2;
    }
}
```
3. 创建 Target 类
```Java
public class Target {

    private Strategy strategy;

    public Target(Strategy strategy) {
        this.strategy = strategy;
    }

    public int executeStrategy(int num1, int num2) {
        return strategy.doOperation(num1, num2);
    }
}
```
4. 测试
```Java
public class StrategyTest {

    @Test
    public void testStrategy(){
        Target target = new Target(new OperationAdd());
        System.out.println("10 + 5 = " + target.executeStrategy(10, 5));

        target = new Target(new OperationSubstract());
        System.out.println("10 - 5 = " + target.executeStrategy(10, 5));

        target = new Target(new OperationMultiply());
        System.out.println("10 * 5 = " + target.executeStrategy(10, 5));
    }
}
```

5. 输出
```Java
03-23 14:22:07.791 26691-26715/? I/System.out: 10 + 5 = 15
03-23 14:22:07.791 26691-26715/? I/System.out: 10 - 5 = 5
03-23 14:22:07.791 26691-26715/? I/System.out: 10 * 5 = 50
```

## 使用场景 ##
1. 如果在一个系统里面有许多类，它们之间的区别仅在于它们的行为，那么使用策略模式可以动态地让一个对象在许多行为中选择一种行为。 
2. 一个系统需要动态地在几种算法中选择一种。 
3. 如果一个对象有很多的行为，如果不用恰当的模式，这些行为就只好使用多重的条件选择语句来实现。

## 主要解决 ##
在有多种算法相似的情况下，使用 if...else 所带来的复杂和难以维护。

## 优点 ##
1. 算法可以自由切换。 
2. 避免使用多重条件判断。 
3. 扩展性良好。

## 缺点 ##
1. 策略类会增多。 
2. 所有策略类都需要对外暴露。

## 注意事项 ##
如果一个系统的策略多于4个，就需要考虑使用混合模式，解决策略类膨胀的问题。