# JavaScript 运行原理 & V8 引擎分析

## JavaScript 语言特性

一般例如 C++ 和 Java 等语言是解释性语言，fields* 和 methods* 等的内容是以数组储存的，按一对一对应 fields 和 methods 的名称，个别变量和 methods 等储存的位置，根据类的定义来存储。在 C++ 和 Java 等语言中，事先已知道所存的变量（类）的类型，所以只需要利用数组的位移即可读取 field 和 method。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/js_vs_c.png" alt=""/>

而JavaScript 是动态类型，在 JavaScript 中对象都有自己属性和方法的表格，每次执行方法，都必须检查对象的类型。许多 JavaScript 引擎都使用哈希表（hash table）来存取属性和寻找方法等。每次存取属性或是寻找方法时，就会使用字符串作为寻找对象哈希表的键(key)。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/js_hash.png" alt=""/>

## JavaScript 运行原理

几乎所有人都已经听说过V8引擎的概念，大多数人都知道 JavaScript 是单线程的，或者是使用回调队列。

JavaScript 引擎的一个流行示例是 Google 的 V8 引擎。V8 引擎被 Chrome 和 Node.js 使用。这是一个该引擎非常简化的视图：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/v8_arch.png" alt=""/>

引擎由两个主要组成部分组成：

- 内存堆 - 这是内存分配发生的地方
- 调用堆栈 - 这是你的代码执行时堆栈帧的位置


浏览器中已经有一些几乎被所有 JavaScript 开发人员使用的API（例如“setTimeout”）。然而，引擎不提供这些API。

那么他们从哪里来？ 事实上，这有点复杂。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/v8_runtime.png" alt=""/>

所以，我们有引擎，但实际上还有更多内容。有一些被称为 Web API 的东西，由浏览器提供，如 DOM，AJAX，setTimeout 等等。

然后，还有受欢迎的事件循环和回调队列。

## 调用堆栈

JavaScript是一种单线程编程语言，这意味着它有一个单一的调用堆栈。因此，它一次只可以做一件事。

调用堆栈是一个数据结构，它记录了我们在程序的基本位置。如果我们进入一个函数，我们把它放在堆栈的顶部。如果我们从一个函数返回，我们弹出堆栈的顶部。这就是堆栈做的事情。

我们来看一个例子。看看下面的代码：

```JS
function multiply(x, y) {
    return x * y;
}
function printSquare(x) {
    var s = multiply(x, x);
    console.log(s);
}
printSquare(5);
```

当引擎开始执行此代码时，调用堆栈将为空。之后，步骤如下：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/v8_call_stack.png" alt=""/>

进入调用堆栈中的每个条目称为堆栈帧。

这正是在抛出异常时构造堆栈跟踪的方式 — 当异常发生时，它基本上是调用堆栈的状态。看看下面的代码：

```JS
function foo() {
    throw new Error('SessionStack will help you resolve crashes :)');
}
function bar() {
    foo();
}
function start() {
    bar();
}
start();
```

如果这是在 Chrome 中执行的（假设此代码位于一个名为foo.js的文件中），则会产生以下堆栈跟踪：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/v8_error.png" alt=""/>

Blowing the stack — 当你达到最大调用堆栈尺寸时，会发生这种情况。这可能会非常容易发生，特别是如果你在不经过很大程度测试代码的情况下使用递归。看看这个示例代码：

```JS
function foo() {
    foo();
}
foo();
```

当引擎开始执行这个代码时，它首先调用 “foo” 函数。然而，此函数是递归的，并且开始调用自身而没有任何终止条件。所以在执行的每个步骤中，相同的函数都被一次又一次地添加到调用堆栈中。看起来像这样：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/v8_call_stack2.png" alt=""/>

然后，在调用堆栈中的函数调用次数超过了调用堆栈的实际大小的时候，浏览器决定采取行动，抛出一个错误，看起来像这样：

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/v8_error2.png" alt=""/>

在单线程上运行代码可能非常容易，因为你不必处理在多线程环境中出现的复杂场景，例如死锁。

但在单线程上运行也是非常受限的。由于JavaScript有一个调用堆栈，当事情开始缓慢时会发生什么？

## 并发和事件循环

当你在调用堆栈中进行函数调用需要大量时间才能进行处理时会发生什么？例如，假设你想在浏览器中使用 JavaScript 进行一些复杂的图像转换。

你可能会问 - 为什么这是一个问题？问题在于，当调用堆栈有函数在执行的时候，浏览器实际上不能做任何事情 - 它被阻塞了。这意味着浏览器无法渲染任何内容，它也不能运行任何其他代码，它卡住了。如果你想要的UI流畅，这会产生问题。

这不是唯一的问题。一旦你的浏览器开始处理“调用堆栈”中的许多任务，它可能会停止响应很长时间。大多数浏览器通过提出错误来采取行动，询问你是否要终止网页。

那么，如何不阻塞 UI 并不造成使浏览器不响应的情况下执行繁重的代码呢？解决方案是异步回调。

## JavaScript 引擎

JavaScript 引擎是一个执行 JavaScript 代码的程序或解释器。 一个 JavaScript 引擎可以实现为标准解释器，也可以是以某种形式将 JavaScript 编译为字节码的即时编译器。

- V8 ：开源的，由 Google 开发的，用 C++ 编写
- Rhin：由 Mozilla 基金会管理，开放源代码，完全用 Java 开发
- SpiderMonkey ： 第一个 JavaScript 引擎，过去使用在 Netscape Navigator 中，现在工作在 Firefox
- JavaScriptCore ： 开源，由Nitro推出，由苹果公司开发，用在 Safari 中
- KJS ：最初由 Harri Porten 开发，用于 KDE项目的 Konqueror 网络浏览器
- Chakra (JScript9) ： Internet Explorer
- Chakra (JavaScript) ： Microsoft Edge
- Nashorn：开源，作为 OpenJDK 的一部分，由 Oracle Java 语言和工具组编写
- JerryScript ： 是物联网的轻量级引擎

## V8 引擎

由 Google 构建的 V8 引擎是开源的，用 C++ 编写。该引擎在 Google Chrome 内使用。然而，与其他引擎不同的是 V8 也被用于流行的 Node.js 运行时。

V8 最初被设计用于提高 Web 浏览器中 JavaScript 执行的性能。为了获得更快的运行速度，V8 将 JavaScript 代码转换为更有效的机器代码，而不是使用解释器。它通过实现JIT（即时）编译器，就像许多现代 JavaScript 引擎（如SpiderMonkey或Rhino（Mozilla））做的的，将 JavaScript 代码编译成机器代码。与他们相比，最主要的区别在于 V8 不会产生字节码或任何中间代码。

在 V8 5.9 版本发布之前（今年早些时候发布），引擎使用两个编译器：

- full-codegen - 一个简单而非常快速的编译器，可以生成简单而且相对较慢的机器代码。
- Crankshaft - 更复杂（即时）优化编译器，可以生成高度优化的代码。

V8 引擎还内部使用多个线程：

- 主线程执行你所期望的：获取代码，编译然后执行它
- 还有一个单独的线程用于编译，所以主线程在前者正在优化代码时可以继续执行
- Profiler 线程将告诉运行时，我们花费大量时间的方法，以便 Crankshaft 编译器可以优化它们
- 几个处理垃圾收集器扫描的线程

当第一次执行JavaScript代码时，V8利用full-codegen直接将解析后的 JavaScript 转换为机器代码，而无需任何转换。这使得它能够非常快地开始执行机器代码。注意，V8不会使用中间字节码表示，从而无需解释器。

当你的代码运行了一段时间后，Profiler 线程已经收集了足够的数据来判断应该优化哪个方法。

接下来，Crankshaft 从另一个线程开始优化。它将 JavaScript 抽象语法树转换为称为Hydrogen的高级静态单赋值（SSA）表示，并尝试优化Hydrogen图。大多数优化都是在这个级别完成的。

## 内联

第一个优化是提前内联（Inlining）尽可能多的代码。内联是将被调用函数的函数体替换到调用位置（函数所在的代码行）的处理过程。这个简单的步骤让以下优化更有意义。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/code_inlining.png" alt=""/>

## 隐藏类

JavaScript 是一种基于原型的语言：没有使用克隆创建类和对象的过程。 JavaScript 也是一种动态编程语言，这意味着在实例化之后，可以轻松地从对象中添加或删除属性。

大多数 JavaScript 解释器都使用类似字典的结构（基于哈希函数）将对象属性值的位置存储在内存中。这种结构使得检索 JavaScript 中的属性的值比在 Java 或 C# 这样的非动态编程语言中更昂贵。在 Java 中，所有对象属性都是由编译前的固定对象布局确定的，并且不能在运行时动态添加或删除（C# 具有动态类型，这是另一个话题了）。因此，属性值（或指向这些属性的指针）可以作为连续缓冲区存储在存储器中，它们之间具有固定偏移量，偏移量的长度可以根据属性类型容易地确定。而在 JavaScript中，属性类型可能会在运行时间内发生变化，这样做是不可能的。

由于使用字典来查找对象属性在内存中的位置是非常低效的，所以 V8 使用不同的方法替代：隐藏类。隐藏类工作原理类似于 Java 语言中使用的固定对象布局（类），除了它们在运行时被创建。现在，我们来看看它们的实际情况：

```JS
function Point(x, y) {
    this.x = x;
    this.y = y;
}
var p1 = new Point(1, 2);
```

一旦 new Point(1,2) 被调用，V8 将创建一个隐藏的类 C0。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/hide_class.png" alt=""/>

没有为 Point 定义属性，因此C0为空。

一旦执行了第一个语句this.x = x（在Point函数中），V8将创建一个基于C0的第二个隐藏类C1。 C1描述了可以找到属性x的内存中的位置（相对于对象指针）。在这种情况下，在偏移 0 处存储x，这意味着当将存储器中的点对象作为连续缓冲器查看时，第一个偏移将对应于属性x。 V8也会用类转换来更新C0，也就是说，如果将一个属性x添加到点对象，则隐藏类应该从C0切换到C1。下面的点对象的隐藏类现在是C1。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/hide_class1.png" alt=""/>

每次将新属性添加到对象中时, 旧的隐藏类都将用转换路径更新为新的隐藏类。隐藏类转换非常重要, 因为它们允许在以相同方式创建的对象之间共享隐藏类。如果两个对象共享一个隐藏类, 并且将相同的属性添加到它们中, 则转换将确保两个对象都收到相同的新隐藏类和随之而来的所有优化代码。

当执行语句this.y = y（在Point函数内部，在this.x = x语句之后）时，会重复此过程。

一个名为C2的新隐藏类被创建，类转换将被添加到C1，表示如果将属性y添加到Point对象（已包含属性x），则隐藏类应更改为C2，点对象的隐藏类也更新为C2。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/hide_class2.png" alt=""/>

隐藏类的转换取决于将属性添加到对象的顺序。看下面的代码片段：

```Js
function Point(x, y) {
    this.x = x;
    this.y = y;
}
var p1 = new Point(1, 2);
p1.a = 5;
p1.b = 6;
var p2 = new Point(3, 4);
p2.b = 7;
p2.a = 8;
```

现在，你可以假设对于p1和p2，将使用相同的隐藏类和转换。实际并不相同。对于p1，首先将添加属性a，然后添加属性b。但是，对于p2，首先分配b，然后再分配a。因此，由于不同的转换路径，p1和p2最终会有不同的隐藏类。在这种情况下，以相同的顺序初始化动态属性要更好，以便隐藏的类可以重用。

## 内联缓存

V8利用另一种称为内联缓存的技术来优化动态类型语言。内联缓存依赖于往往发生在同一类型对象上的对同一方法的重复调用的观察。

那么它是如何工作呢？ V8维护在最近的方法调用中作为参数传递的对象类型的缓存，并使用该信息对将来作为参数传递的对象类型做出假设。如果 V8 能够对未来传递给该方法的对象类型做出一个很好的假设，那么它可以绕过如何访问对象的属性的过程，而是使用来自先前查找的对象的隐藏类存储的信息。

那么隐藏类和内联缓存的概念如何相关？无论何时在特定对象上调用方法，V8引擎必须对该对象的隐藏类执行查找，以确定访问特定属性的偏移量。在同一个隐藏类的两次成功调用相同的方法之后，V8省略了隐藏的类查找，并将属性的偏移量添加到对象指针本身。对于该方法的所有将来的调用，V8引擎假定隐藏类没有改变，并使用先前查找中存储的偏移量直接跳转到特定属性的内存地址。这大大提高了执行速度。

内联缓存也是为什么同一类型的对象共享隐藏类的重要的原因。如果你创建两个相同类型的对象和不同的隐藏类（如前面的示例），V8将无法使用内联缓存，因为即使两个对象的类型相同，它们的相应隐藏类为其属性分配不同的偏移量。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_v8/hide_class_diff.png" alt=""/>

## 编译到机器码

一旦 Hydrogen 图被优化，Crankshaft 将其降低到称为 Lithium 的较低级别表示。大多数 Lithium 的实现都是针对架构的。寄存器分配发生在这个级别。

最后，Lithium 被编译为机器码。然后发生称为 OSR 其他事：堆栈替换。在我们开始编译和优化一个明显长期运行的方法之前，我们可能会运行它。 V8 不会忘记它刚刚缓慢执行的结果，不会再次运行它。相反，它将转换所有的上下文（堆栈，寄存器），以便我们可以在执行过程中切换到优化版本。这是一个非常复杂的任务，请记住，除了其他优化之外，V8在初始化的时候已经内联了代码。 V8不是唯一能够做到这一点的引擎。

有一种称为去优化的保护措施，作出相反的转换，并恢复为非优化代码，以防引擎之前做的的假设不再成立（假设隐藏类没有改变）。

## 垃圾回收

对于垃圾收集，V8采用传统的标记-清除的扫描方法处理 old generation 。标记阶段应该停止执行JavaScript。为了控制 GC 成本并使执行更加稳定，V8使用增量式标记：而不是遍历整个堆，尝试标记每一个可能的对象，相反，只是遍历一部分堆，然后恢复正常执行。下一个 GC 将继续从之前的遍历停止的位置开始。这允许在正常执行期间有非常短的暂停。如前文所述，扫描阶段由单独的线程处理。

## 参考资料

- [为什么V8 JavaScript引擎这么快](http://www.xuanfengge.com/why-v8-so-fast.html)
- [JavaScript 是如何工作的：引擎，运行时和调用堆栈的概述](http://tcatche.site/2017/08/how-javascript-work-part-1-overview/)
- [JavaScript 是如何工作的：V8 引擎内部机制及5个诀窍编写优化代码的技巧](http://tcatche.site/2017/08/how-javascript-work-part-2-v8-engine-and-5-tips-optimized/)


