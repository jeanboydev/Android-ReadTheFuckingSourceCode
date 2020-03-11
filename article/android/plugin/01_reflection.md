# Java 反射

反射 (Reflection) 是 Java 的特征之一，它允许运行中的 Java 程序获取自身的信息，并且可以操作类或对象的内部属性。

Oracle 官方对反射的解释是：

> Reflection enables Java code to discover information about the fields, methods and constructors of loaded classes, and to use reflected fields, methods, and constructors to operate on their underlying counterparts, within security restrictions.
> The API accommodates applications that need access to either the public members of a target object (based on its runtime class) or the members declared by a given class. It also allows programs to suppress default reflective access control.

简而言之，通过反射，我们可以在运行时获得程序或程序集中每一个类型的成员和成员的信息。程序中一般的对象的类型都是在编译期就确定下来的，而 Java 反射机制可以动态地创建对象并调用其属性，这样的对象的类型在编译期是未知的。所以我们可以通过反射机制直接创建对象，即使这个对象的类型在编译期是未知的。

反射的核心是 JVM 在运行时才动态加载类或调用方法/访问属性，它不需要事先（写代码的时候或编译期）知道运行对象是谁。

Java 反射主要提供以下功能：

- 在运行时判断任意一个对象所属的类；
- 在运行时构造任意一个类的对象；
- 在运行时判断任意一个类所具有的成员变量和方法（通过反射甚至可以调用private方法）；
- 在运行时调用任意一个对象的方法

## Class 对象

Class对象是Java反射的基础，它包含了与类相关的信息，事实上，Class对象就是用来创建类的所有对象的。

Class 对象是 java.lang.Class<T> 这个类生成的对象，其中类型参数T表示由此 Class 对象建模的类的类型。例如，String.class 的类型是 Class<String>；如果将被建模的类未知，则使用 Class<?>。

以下是Java API的描述：

> Class 类的实例表示正在运行的 Java 应用程序中的类和接口。枚举是一种类，注释是一种接口。每个数组属于被映射为 Class 对象的一个类，所有具有相同元素类型和维数的数组都共享该 Class 对象。基本的Java类型（boolean、byte、char、short、int、long、float 和 double）和关键字 void 也表示为 Class 对象。

Class 没有公共构造方法。Class 对象是在加载类时由 Java 虚拟机以及通过调用类加载器中的 defineClass 方法自动构造的。

实际上，每个类都有一个 Class 对象。换言之，每当编写并且编译了一个新类，就会产生一个 Class 对象（更恰当的说，是被保存在一个同名的 .class 文件中）。

如果我们想生成这个类的对象，运行这个程序的 Java 虚拟机将使用类加载器子系统，类加载器首先检查这个类的 Class 对象是否已经加载。如果尚未加载，默认的类加载器就会根据类名查找 .class 文件，并将其载入，一旦某个类的 Class 对象被载入内存，它就被用来创建这个类的所有对象。

获取 Class 对象有三种方式：

- 通过实例变量的 getClass() 方法

```java
Class clazz = new String("abc").getClass();
```

- 通过 Class 类的静态方法 forName() 方法

```java
Class clazz = Class.forName("xxx");
```

注意：当使用 Class.forName() 方法时，必须提供完全限定类名，即类名要包括所有包。

- 使用类字面常量或 TYPE 字段

```java
Class<Integer> intClass = int.class;
Class<Integer> integerType = Integer.TYPE;
```

类字面常量不仅可以应用于普通的类，也可以应用于接口、数组以及基本数据类型，这种方式不仅更简单，而且更安全，因为它在编译时就会受到检查，并且根除了对 forName 方法的调用，所以也更高效，建议使用 .class 的形式。

TYPE 是基本数据类型的包装类型的一个标准字段，它是一个引用，指向对应的基本数据类型的 Class 对象，附表如下，两边等价：

| class         | TYPE           |
| :------------ | :------------- |
| boolean.class | Boolean.TYPE   |
| char.class    | Character.TYPE |
| byte.class    | Byte.TYPE      |
| short.class   | Short.TYPE     |
| int.class     | Integer.TYPE   |
| long.class    | Long.TYPE      |
| float.class   | Float.TYPE     |
| double.class  | Double.TYPE    |
| void.class    | Void.TYPE      |

## 类名

从 Class 对象中可以获取两个不同的类名。完全限定类名（包括包名）可以使用 getName() 或 getCanonicalName() 方法获取，例如：

```java
Class aClass = MyObject.class;
String className = aClass.getName();
String className1 = aClass.getCanonicalName();
```

如果想要获取不含包名的类名可以使用 `getSimpleName()` 方法，如下:

```java
String simpleClassName = aClass.getSimpleName();
```

## 修饰符

使用 Class 对象可以获取一个类的修饰符。类的修饰符即关键字 public、private、static 等。如下：

```java
Class aClass = MyObject.class;
int modifiers = aClass.getModifiers();
```

修饰符被包装进一个 int 内，每一个修饰符都是一个标志位（置位或清零）。可以使用java.lang.reflect.Modifier 类中的以下方法来检验修饰符：

```java
Modifier.isAbstract(int modifiers)
Modifier.isFinal(int modifiers)
Modifier.isInterface(int modifiers)
Modifier.isNative(int modifiers)
Modifier.isPrivate(int modifiers)
Modifier.isProtected(int modifiers)
Modifier.isPublic(int modifiers)
Modifier.isStatic(int modifiers)
Modifier.isStrict(int modifiers)
Modifier.isSynchronized(int modifiers)
Modifier.isTransient(int modifiers)
Modifier.isVolatile(int modifiers)
```

## 包信息

使用 Class 对象可以获取包信息，如下:

```java
Class aClass = MyObject.class;
Package package = aClass.getPackage();
String packageName = package.getName();
```

## 父类

通过 Class 对象可以获取类的父类，如下：

```java
Class  aClass = MyObject.class;
Class superclass = aClass.getSuperclass();
```

父类的 Class 对象和其它 Class 对象一样是一个 Class 对象，可以继续使用反射。

## 实现的接口

通过给定的类可以获取这个类所实现的接口列表，如下：

```java
Class aClass = MyObject.class;
Class[] interfaces = aClass.getInterfaces();
```

一个类可以实现多个接口，因此返回一个 Class 数组。在 Java 反射机制中，接口也由 Class 对象表示。

> 注意：只有给定类声明实现的接口才会返回。例如，如果类 A 的父类 B 实现了一个接口 C，但类 A并没有声明它也实现了 C，那么 C 不会被返回到数组中。即使类 A 实际上实现了接口 C，因为它的父类 B 实现了 C。

为了得到一个给定的类实现接口的完整列表，需要递归访问类和其超类。

## 构造函数

使用 Class 对象可以获取类的构造函数，如下：

```java
Class aClass = MyObject.class;
Constructor[] constructors = aClass.getConstructors();
```

Constructor 数组为每一个在类中声明的 public 构造函数保存一个 Constructor 实例。

如果知道要访问的构造函数确切的参数类型，可以不获取构造函数数组。

```java
Constructor constructor = aClass.getConstructor(new Class[]{String.class});
```

如果没有匹配给定的构造函数参数，在这个例子当中是 `String.class`，会抛出  `NoSuchMethodException` 异常。

### 参数

可以知道给定的构造函数接受什么参数，如下：

```java
Class[] parameterTypes = constructor.getParameterTypes();
```

### 实例化对象

```java
MyObject myObject = (MyObject)constructor.newInstance("constructor-arg1");
```

## 字段

使用 Class 对象可以获取类的字段（成员变量），如下:

```java
Class aClass = MyObject.class;
// 返回类中所有公有（public）成员变量，包括其父类的公有成员变量
Field[] fields = aClass.getFields();
// 返回类或接口声明的所有成员变量，包括公共、保护、默认（包）访问和私有成员变量，但不包括继承的成员变量
Field[] fields = aClass.getDeclaredFields();
// 返回一个特定的成员变量，其中第一个参数为成员变量名称
Field field = aClass.getField("xxx");
Field field = aClass.getDeclaredField("xxx");
```

### 类型

可以使用 Field.getType() 方法确定一个字段的类型（String、int等）：

```java
Object fieldType = field.getType();
```

### 获取和设置字段值

可以使用 Field.get() 和 Field.set() 方法获取和设置它的值，如下：

```java
Class aClass = MyObject.class
Field field = aClass.getField("someField");
MyObject objectInstance = new MyObject();
Object value = field.get(objectInstance);
field.set(objetInstance, value);
```

## 方法

使用 Class 对象可以获取类的方法，如下:

```java
Class aClass = MyObject.class;
// 返回类中所有公用（public）方法，包括其继承类的公用方法
Method[] methods = aClass.getMethods();
// 返回类或接口声明的所有方法，包括公共、保护、默认（包）访问和私有方法，但不包括继承的方法
Method[] methods = aClass.getDeclaredMethods();
// 返回一个特定的方法，其中第一个参数为方法名称，后面的参数为方法的参数对应 Class 的对象
Method method = aClass.getMethod("xxx", String.class);
Method method = aClass.getDeclaredMethod("xxx", String.class);
```

### 参数和返回值

使用 Method 对象可以获取方法的参数，如下：

```java
Class[] parameterTypes = method.getParameterTypes();
```

也可以获取方法的返回值类型，如下：

```java
Class returnType = method.getReturnType();
```

### 调用方法

```java
Method method = MyObject.class.getMethod("doSomething", String.class);
MyObject objectInstance = new MyObject();
Object returnValue = method.invoke(objectInstance, "parameter-value1");
```

## 私有字段和方法

要想访问私有字段你需要调用 Class.getDeclaredField(Stringname) 或 Class.getDeclaredFields() 方法。Class.getField(String name) 和 Class.getFields() 方法仅返回 public 字段。

```java
PrivateObject privateObject = new PrivateObject("The Private Value");
Field privateStringField = PrivateObject.class.getDeclaredField("privateString");
privateStringField.setAccessible(true);
```

通过调用 Field.setAcessible(true) 方法关闭了特定 Field 实例的访问检查，现在通过反射可以访问它，即使它是私有的，保护的或包范围，甚至调用者不属于这些范围。

想要访问私有方法需要调用 Class.getDeclaredMethod(String name,Class[] parameterTypes) 或 Class.getDeclaredMethods() 方法。Class.getMethod(String name, Class[]parameterTypes) 和 Class.getMethods() 方法仅返回 public 方法。

```java
PrivateObject privateObject = new PrivateObject("The Private Value");
Method privateStringMethod = PrivateObject.class.getDeclaredMethod("getPrivateString", null);
privateStringMethod.setAccessible(true);
```

通过调用 Method.setAcessible(true) 方法关闭了特定Method实例的访问检查。

## 注解

使用 Class 对象可以获取类的注解，如下：

```java
Class aClass = MyObject.class;
// 获取类注解
Annotation[] annotations = aClass.getAnnotations();
for(Annotation annotation : annotations){
  if(annotation instanceof MyAnnotation){
    MyAnnotation myAnnotation = (MyAnnotation) annotation;
    System.out.println("name: " + myAnnotation.name());
    System.out.println("value: " + myAnnotation.value());
  }
}
```

也可以获取指定的类注解，如下：

```java
Class aClass = TheClass.class;
Annotation annotation = aClass.getAnnotation(MyAnnotation.class);
if(annotation instanceof MyAnnotation){
         MyAnnotation myAnnotation = (MyAnnotation) annotation;
         System.out.println("name: " + myAnnotation.name());
         System.out.println("value: " + myAnnotation.value());
}
```

### 方法注解

下面是方法注解的示例：

```java
public class TheClass {
  @MyAnnotation(name="someName",  value = "Hello World")
  public void doSomething(){}
}
```

获取方法的所有注解，如下：

```java
Method method = ... // 反射获取到方法
  // 获取方法的特定注解
  Annotation annotation = method.getAnnotation(MyAnnotation.class);
Annotation[] annotations = method.getDeclaredAnnotations();
for(Annotation annotation : annotations){
  if(annotation instanceof MyAnnotation){
    MyAnnotation myAnnotation = (MyAnnotation) annotation;
    System.out.println("name: " + myAnnotation.name());
    System.out.println("value: " + myAnnotation.value());
  }
}
```

### 参数注解

也可以给方法声明的参数添加注解，如下：

```java
public class TheClass {
  public static void doSomethingElse(
    @MyAnnotation(name="aName", value="aValue") String parameter){
  }
}
```

从 Method 对象获取参数注解：

```java
Method method = ... // 反射获取到方法
Annotation[][] parameterAnnotations = method.getParameterAnnotations();
Class[] parameterTypes = method.getParameterTypes();
int i = 0;
for(Annotation[] annotations : parameterAnnotations){
  Class parameterType = parameterTypes[i++];
  for(Annotation annotation : annotations){
    if(annotation instanceof MyAnnotation){
      MyAnnotation myAnnotation = (MyAnnotation)annotation;
      System.out.println("param: " + parameterType.getName());
      System.out.println("name : " + myAnnotation.name());
      System.out.println("value: " + myAnnotation.value());
    }
  }
}
```

注意 Method.getParameterAnnotations() 方法返回的是二维的Annotation数组，每个方法参数都有一个一维的 Annotation 数组。

### 字段注解

下面是字段注解示例：

```java
public class TheClass {
  @MyAnnotation(name="someName",  value = "Hello World")
  public String myField = null;
}
```

获取字段的所有注解，如下：

```java
Field field = ... // 反射获取到字段
// 获取指定字段的注解
Annotation annotation = field.getAnnotation(MyAnnotation.class);
Annotation[] annotations = field.getDeclaredAnnotations();
for(Annotation annotation : annotations){
  if(annotation instanceof MyAnnotation){
    MyAnnotation myAnnotation = (MyAnnotation) annotation;
    System.out.println("name: " + myAnnotation.name());
    System.out.println("value: " + myAnnotation.value());
  }
}
```

## 泛型

经常在文章中看到说所有 Java 泛型信息在编译的时候被擦除了，所以在运行时访问不到任何泛型信息。这并不完全正确，在极少数的情况下，在运行时是可以访问泛型信息的。这些情况实际上涵盖一些我们需要的 Java 泛型信息。

使用 Java 的泛型通常分为两种不同的情况：

- 声明一个可参数化的类/接口。
- 使用参数化的类。

### 方法返回类型

如果你获取到一个 java.lang.reflect.Method 对象，可以获取它的返回值类型信息。

```java
public class MyClass {
  protected List<String> stringList = ...;
  public List<String> getStringList(){
    return this.stringList;
  }
}
```

在这个类中可以获取 getStringList() 方法的泛型返回值类型。换句话说，可以探测到 getStringList() 返回的是 List<String> 而不仅是一个 List。如下：

```java
Method method = MyClass.class.getMethod("getStringList", null);
Type returnType = method.getGenericReturnType();
if(returnType instanceof ParameterizedType){
  ParameterizedType type = (ParameterizedType) returnType;
  Type[] typeArguments = type.getActualTypeArguments();
  for(Type typeArgument : typeArguments){
    Class typeArgClass = (Class) typeArgument;
    System.out.println("typeArgClass = " + typeArgClass);
  }
}
```

代码输出 `typeArgClass = class java.lang.String`。

### 方法参数类型

通过 Java 反射可以在运行时访问参数类型的泛型类型。下面的示例中，类有一个使用参数化的 List 作为参数的方法：

```java
public class MyClass {
  protected List<String> stringList = ...;
  public void setStringList(List<String> list){
    this.stringList = list;
  }
}
```

可以访问方法参数的泛型参数类型，如下：

```java
Method method = Myclass.class.getMethod("setStringList", List.class);
Type[] genericParameterTypes = method.getGenericParameterTypes();
for(Type genericParameterType : genericParameterTypes){
  if(genericParameterType instanceof ParameterizedType){
    ParameterizedType aType = (ParameterizedType) genericParameterType;
    Type[] parameterArgTypes = aType.getActualTypeArguments();
    for(Type parameterArgType : parameterArgTypes){
      Class parameterArgClass = (Class) parameterArgType;
      System.out.println("parameterArgClass = " + parameterArgClass);
    }
  }
}
```

代码输出 `parameterArgType= class java.lang.String`。

### 字段类型

可以访问 public 字段的泛型类型。字段即类的成员变量-静态的或实例变量。下面是一个例子，类有一个实例变量 stringList：

```java
public class MyClass {
  public List<String> stringList = ...;
}
Field field = MyClass.class.getField("stringList");
Type genericFieldType = field.getGenericType();  
if(genericFieldType instanceof ParameterizedType){
  ParameterizedType aType = (ParameterizedType) genericFieldType;
  Type[] fieldArgTypes = aType.getActualTypeArguments();
  for(Type fieldArgType : fieldArgTypes){
    Class fieldArgClass = (Class) fieldArgType;
    System.out.println("fieldArgClass = " + fieldArgClass);
  }
}
```

代码将输出 `fieldArgClass = class java.lang.String`。

## 参考资料

- [深入解析Java反射（1） - 基础](https://www.sczyh30.com/posts/Java/java-reflection-1/)
- [Java Reflection Tutorial](http://tutorials.jenkov.com/java-reflection/index.html)