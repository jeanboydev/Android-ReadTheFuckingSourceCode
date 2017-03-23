# Template Method（模板方法模式） #
## 概述 ##
在模板方法模式（Template Method Pattern）中，一个抽象类公开定义了执行它的方法的方式/模板。 它的子类可以按需要重写方法实现，但调用将以抽象类中定义的方式进行。这种类型的设计模式属于行为型模式。

## 使用 ##

### 实现 ###
1. 抽象模板角色类
```Java
public abstract class AbstractTemplate {
    /**
     * 模板方法
     */
    public void templateMethod(){
        //调用基本方法
        abstractMethod();
        hookMethod();
        concreteMethod();
    }
    /**
     * 基本方法的声明（由子类实现）
     */
    protected abstract void abstractMethod();
    /**
     * 基本方法(空方法)
     */
    protected void hookMethod(){}
    /**
     * 基本方法（已经实现）
     */
    private final void concreteMethod(){
        //业务相关的代码
    }
}
```
2. 具体模板角色类，实现了父类所声明的基本方法
```Java
public class ConcreteTemplate extends AbstractTemplate{

    //基本方法的实现
    @Override
    public void abstractMethod() {
        //业务相关的代码
    }
    //重写父类的方法
    @Override
    public void hookMethod() {
        //业务相关的代码
    }
}
```

## 使用场景 ##
1. 有多个子类共有的方法，且逻辑相同。 
2. 重要的、复杂的方法，可以考虑作为模板方法。

## 主要解决 ##
一些方法通用，却在每一个子类都重新写了这一方法。

## 优点 ##
1. 封装不变部分，扩展可变部分。 
2. 提取公共代码，便于维护。 
3. 行为由父类控制，子类实现。

## 缺点 ##
每一个不同的实现都需要一个子类来实现，导致类的个数增加，使得系统更加庞大。

## 注意事项 ##
为防止恶意操作，一般模板方法都加上 final 关键词。