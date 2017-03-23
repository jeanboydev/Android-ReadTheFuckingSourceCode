# Interpreter（解释器模式） #
## 概述 ##
解释器模式（Interpreter Pattern）提供了评估语言的语法或表达式的方式，它属于行为型模式。 这种模式实现了一个表达式接口，该接口解释一个特定的上下文。 这种模式被用在 SQL 解析、符号处理引擎等。

## 使用 ##

### 实现 ###
1. 创建一个表达式接口
```Java
public interface Expression {
   public boolean interpret(String context);
}
```
2. 创建实现了上述接口的实体类
```Java
public class TerminalExpression implements Expression {
	
   private String data;

   public TerminalExpression(String data){
      this.data = data; 
   }

   @Override
   public boolean interpret(String context) {
      if(context.contains(data)){
         return true;
      }
      return false;
   }
}
```
```Java
public class OrExpression implements Expression {
	 
   private Expression expr1 = null;
   private Expression expr2 = null;

   public OrExpression(Expression expr1, Expression expr2) { 
      this.expr1 = expr1;
      this.expr2 = expr2;
   }

   @Override
   public boolean interpret(String context) {		
      return expr1.interpret(context) || expr2.interpret(context);
   }
}
```
```Java
public class AndExpression implements Expression {
	 
   private Expression expr1 = null;
   private Expression expr2 = null;

   public AndExpression(Expression expr1, Expression expr2) { 
      this.expr1 = expr1;
      this.expr2 = expr2;
   }

   @Override
   public boolean interpret(String context) {		
      return expr1.interpret(context) && expr2.interpret(context);
   }
}
```
3. InterpreterPatternDemo 使用 Expression 类来创建规则，并解析它们
```Java
public class InterpreterPatternDemo {

   //规则：Robert 和 John 是男性
   public static Expression getMaleExpression(){
      Expression robert = new TerminalExpression("Robert");
      Expression john = new TerminalExpression("John");
      return new OrExpression(robert, john);		
   }

   //规则：Julie 是一个已婚的女性
   public static Expression getMarriedWomanExpression(){
      Expression julie = new TerminalExpression("Julie");
      Expression married = new TerminalExpression("Married");
      return new AndExpression(julie, married);		
   }

   public static void main(String[] args) {
      Expression isMale = getMaleExpression();
      Expression isMarriedWoman = getMarriedWomanExpression();

      System.out.println("John is male? " + isMale.interpret("John"));
      System.out.println("Julie is a married women? " 
      + isMarriedWoman.interpret("Married Julie"));
   }
}
```
4. 输出
```Java
John is male? true
Julie is a married women? true
```

## 使用场景 ##
1. 可以将一个需要解释执行的语言中的句子表示为一个抽象语法树。 
2. 一些重复出现的问题可以用一种简单的语言来进行表达。 
3. 一个简单语法需要解释的场景。

## 主要解决 ##
对于一些固定文法构建一个解释句子的解释器。

## 优点 ##
1. 可扩展性比较好，灵活。 
2. 增加了新的解释表达式的方式。 
3. 易于实现简单文法。

## 缺点 ##
1. 可利用场景比较少。 
2. 对于复杂的文法比较难维护。 
3. 解释器模式会引起类膨胀。 
4. 解释器模式采用递归调用方法。

## 注意事项 ##
可利用场景比较少，JAVA 中如果碰到可以用 expression4J 代替。