# Visitor（访问者模式） #
## 概述 ##
在访问者模式（Visitor Pattern）中，我们使用了一个访问者类，它改变了元素类的执行算法。 通过这种方式，元素的执行算法可以随着访问者改变而改变。 这种类型的设计模式属于行为型模式。 

## 使用 ##

### 实现 ###
1. 创建一个Visitor类，存放要访问的对象
```Java
public interface Visitor {

    public void visit(Subject sub);
}  
```
```Java
public class MyVisitor implements Visitor {
  
    @Override  
    public void visit(Subject sub) {
        System.out.println("visit the subject："+sub.getSubject());
    }  
}  
```
2. Subject类，accept方法，接受将要访问它的对象，getSubject()获取将要被访问的属性
```Java
public interface Subject {

    public void accept(Visitor visitor);
  
    public String getSubject();
}  
```
```Java
public class MySubject implements Subject {
  
    @Override  
    public void accept(Visitor visitor) {
        visitor.visit(this);  
    }  
  
    @Override  
    public String getSubject() {
        return "love";  
    }  
}  
```
3. 测试
```Java
public class VisitorTest {
  
	@Test
    public void testVisitor() {
          
        Visitor visitor = new MyVisitor();  
        Subject sub = new MySubject();  
        sub.accept(visitor);      
    }  
}  
```

## 使用场景 ##
1. 对象结构中对象对应的类很少改变，但经常需要在此对象结构上定义新的操作。 
2. 需要对一个对象结构中的对象进行很多不同的并且不相关的操作，而需要避免让这些操作"污染"这些对象的类，也不希望在增加新操作时修改这些类。

## 主要解决 ##
稳定的数据结构和易变的操作耦合问题。

## 优点 ##
1. 符合单一职责原则。 
2. 优秀的扩展性。 
3. 灵活性。

## 缺点 ##
1. 具体元素对访问者公布细节，违反了迪米特原则。 
2. 具体元素变更比较困难。 
3. 违反了依赖倒置原则，依赖了具体类，没有依赖抽象。

## 注意事项 ##
访问者可以对功能进行统一，可以做报表、UI、拦截器与过滤器。