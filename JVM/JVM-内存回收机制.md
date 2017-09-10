# Java 虚拟机垃圾回收机制

## 概述

垃圾回收是一种自动的存储管理机制。 当一些被占用的内存不再需要时，就应该予以释放，以让出空间，这种存储资源管理，称为垃圾回收（Garbage Collection）。 垃圾回收器可以让程序员减轻许多负担，也减少程序员犯错的机会。

## 哪些对象需要回收？

自动垃圾回收机制就是寻找Java堆中的对象，并对对象进行分类判别，寻找出正在使用的对象和已经不会使用的对象，然后把那些不会使用的对象从堆上清除。

- 引用计数法

引用计数算法是垃圾收集器中的早期策略。 在这种方法中，堆中的每个对象实例都有一个引用计数。 当一个对象被创建时，且将该对象实例分配给一个引用变量，该对象实例的引用计数设置为 1。 当任何其它变量被赋值为这个对象的引用时，对象实例的引用计数加 1（a = b，则b引用的对象实例的计数器加 1），但当一个对象实例的某个引用超过了生命周期或者被设置为一个新值时，对象实例的引用计数减 1。 特别地，当一个对象实例被垃圾收集时，它引用的任何对象实例的引用计数器均减 1。 任何引用计数为0的对象实例可以被当作垃圾收集。

引用计数收集器可以很快的执行，并且交织在程序运行中，对程序需要不被长时间打断的实时环境比较有利，但其很难解决对象之间相互循环引用的问题

- 可达性分析

可达性分析算法是从离散数学中的图论引入的，程序把所有的引用关系看作一张图，通过一系列的名为 “GC Roots” 的对象作为起始点，从这些节点开始向下搜索，搜索所走过的路径称为引用链（Reference Chain）。 当一个对象到 GC Roots 没有任何引用链相连（用图论的话来说就是从 GC Roots 到这个对象不可达）时，则证明此对象是不可用的。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_reference_chain.jpg" alt="可达性分析"/>

## 如何回收

- 标记-清除算法

1. 标记，也就是垃圾收集器会找出那些需要回收的对象所在的内存和不需要回收的对象所在的内存，并把它们标记出来，简单的说，也就是先找出垃圾在哪儿？

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_marking.jpg" alt="标记"/>

所有堆中的对象都会被扫描一遍，以此来确定回收的对象，所以这通常会是一个相对比较耗时的过程。

2. 清除，垃圾收集器会清除掉上一步标记出来的那些需要回收的对象区域。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_clean.jpg" alt="清除"/>

存在的问题就是碎片问题，标记清除之后会产生大量不连续的内存碎片，空间碎片太多可能会导致以后在程序运行过程中需要分配较大对象时，无法找到足够的连续内存而不得不提前触发另一次垃圾收集动作。

- 复制算法

标记清除算法每次执行都需要对堆中全部对象扫面一遍效率不高，为解决效率问题，复制算法将内存按容量划分为大小相等的两块，每次只是用其中的一块。 当这一块使用完了，就将还存活的对象复制到另一块上面，然后再把已使用过的内存空间一次清理掉。 这样使得每次都对半区进行内存回收，内存分配时也就不用考虑内存碎片等复杂情况，只要移动堆顶指针，按顺序分配内存即可，实现简单，运行高效。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_copy.jpg" alt="复制算法"/>

- 标记-整理算法

由于简单的标记清除可能会存在碎片的问题，所以又出现了压缩清除的方法，也就是先清除需要回收的对象，然后再对内存进行压缩操作，将内存分成可用和不可用两大部分。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_compacting.jpg" alt="压缩"/>

## 内存分代

当前商业虚拟机的垃圾收集都采用“分代收集”（Generation Collection）算法，这种算法并没有什么新的思想，只是根据对象存活周期的不同将内存划分为几块。 一般是把 Java 堆分为新生代和老年代，这样就可以根据各个年代的特点采用最适当的收集算法。 在新生代中，每次垃圾收集时都发现有大批对象死去，只有少量存活，那就选用复制算法，只需要付出少量存活对象的复制成本就可以完成收集。 而老年代中因为对象存活率较高、没有额外的空间对它进行分配担保，就必须使用“标记-清除”或者“标记-整理”算法来回收。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_heap_structure.jpg" alt="内存分代"/>

- 新生代

所有新 new 出来的对象都会最先出现在新生代中，当新生代这部分内存满了之后，就会发起一次垃圾收集事件，这种发生在新生代的垃圾收集称为 Minor collections。 这种收集通常比较快，因为新生代的大部分对象都是需要回收的，那些暂时无法回收的就会被移动到老年代。

全局暂停事件（Stop the World）：所有小收集（minor garbage collections）都是全局暂停事件，也就是意味着所有的应用线程都需要停止，直到垃圾回收的操作全部完成。类似于“你妈妈在给你打扫房间的时候，肯定也会让你老老实实地在椅子上或者房间外待着，如果她一边打扫，你一边乱扔纸屑，这房间还能打扫完？”

- 老年代

老年代用来存储那些存活时间较长的对象。 一般来说，我们会给新生代的对象限定一个存活的时间，当达到这个时间还没有被收集的时候就会被移动到老年代中。随着时间的推移，老年代也会被填满，最终导致老年代也要进行垃圾回收。这个事件叫做大收集(major garbage collection)。

大收集也是全局暂停事件。通常大收集比较慢，因为它涉及到所有的存活对象。所以，对于对相应时间要求高的应用，应该将大收集最小化。此外，对于大收集，全局暂停事件的暂停时长会受到用于老年代的垃圾回收器的影响。

- 永久代

永久代存储了描述应用程序类和方法的元数据，JVM 运行应用程序的时候需要这些元数据。 永久代由 JVM 在运行时基于应用程序所使用的类产生。 此外，Java SE 类库的类和方法可能也存储在这里。

如果 JVM 发现有些类不在被其他类所需要，同时其他类需要更多的空间，这时候这些类可能就会被垃圾回收。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_heap_structure_desc.jpg" alt="内存分代详细"/>

## 分代垃圾回收过程

我们已经知道垃圾回收所需要的方法和堆内存的分代，那么接下来我们就来具体看一下垃圾回收的具体过程。

1. 第一步 所有 new 出来的对象都会最先分配到新生代区域中，两个 survivor 区域初始化是为空的。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection1.jpg" alt="内存分代收集1"/>

2. 第二步，当 eden 区域满了之后，就引发一次小收集（minor garbage collections）。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection2.jpg" alt="内存分代收集2"/>

3. 第三步，当在小收集（minor garbage collections）存活下来的对象就会被移动到 S0 survivor 区域。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection3.jpg" alt="内存分代收集3"/>

4. 第四步，然后当 eden 区域又填满的时候，又会发生下一次的垃圾回收，存活的对象会被移动到 survivor 区域而未存活对象会被直接删除。 但是，不同的是，在这次的垃圾回收中，存活对象和之前的 survivor 中的对象都会被移动到 s1 中。 一旦所有对象都被移动到 s1 中，那么 s2 中的对象就会被清除，仔细观察图中的对象，数字表示经历的垃圾收集的次数。 目前我们已经有不同的年龄对象了。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection4.jpg" alt="内存分代收集4"/>

5. 第五步，下一次垃圾回收的时候，又会重复上次的步骤，清除需要回收的对象，并且又切换一次 survivor 区域，所有存活的对象都被移动至 s0。 eden 和 s1 区域被清除。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection5.jpg" alt="内存分代收集5"/>

6. 第六步，重复以上步骤，并记录对象的年龄，当有对象的年龄到达一定的阈值的时候，就将新生代中的对象移动到老年代中。在本例中，这个阈值为8。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection6.jpg" alt="内存分代收集6"/>

7. 第七步，接下来垃圾收集器就会重复以上步骤，不断的进行对象的清除和年代的移动。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection7.jpg" alt="内存分代收集7"/>

8. 最后，我们观察上述过程可以发现，大部分的垃圾收集过程都是在新生代进行的，直到老年代中的内存不够用了才会发起一次 大收集(major garbage collection)，会进行标记和整理压缩。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/jvm/gc_collection8.jpg" alt="内存分代收集8"/>

## 垃圾回收器的类型

Java 提供多种类型的垃圾回收器。 JVM 中的垃圾收集一般都采用“分代收集”，不同的堆内存区域采用不同的收集算法，主要目的就是为了增加吞吐量或降低停顿时间。

- Serial 收集器：新生代收集器，使用复制算法，使用一个线程进行 GC，串行，其它工作线程暂停。
- ParNew 收集器：新生代收集器，使用复制算法，Serial 收集器的多线程版，用多个线程进行 GC，并行，其它工作线程暂停。 使用 -XX:+UseParNewGC 开关来控制使用 ParNew+Serial Old 收集器组合收集内存；使用 -XX:ParallelGCThreads 来设置执行内存回收的线程数。
- Parallel Scavenge 收集器：吞吐量优先的垃圾回收器，作用在新生代，使用复制算法，关注 CPU 吞吐量，即运行用户代码的时间/总时间。 使用 -XX:+UseParallelGC 开关控制使用 Parallel Scavenge+Serial Old 收集器组合回收垃圾。
- Serial Old 收集器：老年代收集器，单线程收集器，串行，使用标记整理算法，使用单线程进行GC，其它工作线程暂停。
- Parallel Old 收集器：吞吐量优先的垃圾回收器，作用在老年代，多线程，并行，多线程机制与 Parallel Scavenge 差不错，使用标记整理算法，在 Parallel Old 执行时，仍然需要暂停其它线程。
- CMS（Concurrent Mark Sweep）收集器：老年代收集器，致力于获取最短回收停顿时间（即缩短垃圾回收的时间），使用标记清除算法，多线程，优点是并发收集（用户线程可以和GC线程同时工作），停顿小。 使用 -XX:+UseConcMarkSweepGC 进行 ParNew+CMS+Serial Old 进行内存回收，优先使用 ParNew+CMS，当用户线程内存不足时，采用备用方案 Serial Old 收集。