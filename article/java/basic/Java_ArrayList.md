# ArrayList 源码分析

## 简介

ArrayList 是一种变长的基于数组实现的集合类，ArrayList 允许空值和重复元素，当往 ArrayList 中添加的元素数量大于其底层数组容量时，它会自动扩容至一个更大的数组。

另外，由于 ArrayList 底层基于数组实现，所以其可以保证在 `O(1)` 复杂度下完成随机查找操作。其他方面，ArrayList 是非线程安全类，并发环境下，多个线程同时操作 ArrayList，会引发不可预知的错误。

ArrayList 是大家最为常用的集合类，我们先来看下常用的方法：

```java
List<String> dataList = new ArrayList<>();//创建 ArrayList
dataList.add("test");//添加数据
dataList.add(1,"test1");//指定位置，添加数据
dataList.get(0);//获取指定位置的数据
dataList.remove(0);//移除指定位置的数据
dataList.clear();//清空数据
```

## 构造方法

ArrayList 有两个构造方法，一个是无参，另一个需传入初始容量值。大家平时最常用的是无参构造方法，相关代码如下：

```java
private static final int DEFAULT_CAPACITY = 10; // 初始容量为 10
private static final Object[] EMPTY_ELEMENTDATA = {};// 一个空对象
// 一个空对象，如果使用默认构造函数创建，则默认对象内容默认是该值
private static final Object[] DEFAULTCAPACITY_EMPTY_ELEMENTDATA = {};
transient Object[] elementData; //当前数据对象存放地方，当前对象不参与序列化
private int size; // 当前数组长度

public ArrayList(int initialCapacity) {
    if (initialCapacity > 0) {
        this.elementData = new Object[initialCapacity];
    } else if (initialCapacity == 0) {
        this.elementData = EMPTY_ELEMENTDATA;
    } else {
        throw new IllegalArgumentException("Illegal Capacity: "+
                                           initialCapacity);
    }
}

public ArrayList() {
    this.elementData = DEFAULTCAPACITY_EMPTY_ELEMENTDATA;
}
```

上面的代码比较简单，两个构造方法做的事情并不复杂，目的都是初始化底层数组 elementData。区别在于无参构造方法会将 elementData 初始化一个空数组，插入元素时，扩容将会按默认值重新初始化数组。而有参的构造方法则会将 elementData 初始化为参数值大小（>= 0）的数组。

## add()

对于数组（线性表）结构，插入操作分为两种情况。一种是在元素序列尾部插入，另一种是在元素序列其他位置插入。

- 尾部插入元素

```java
/** 在元素序列尾部插入 */
public boolean add(E e) {
    // 1. 检测是否需要扩容
    ensureCapacityInternal(size + 1);  // Increments modCount!!
    // 2. 将新元素插入序列尾部
    elementData[size++] = e;
    return true;
}
```

对于在元素序列尾部插入，这种情况比较简单，只需两个步骤即可：

1. 检测数组是否有足够的空间插入
2. 将新元素插入至序列尾部

如下图：

![尾部插入](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/java_arraylist/arraylist_add.png)

- 指定位置插入元素

```java
/** 在元素序列 index 位置处插入 */
public void add(int index, E element) {
    if (index > size || index < 0)
            throw new IndexOutOfBoundsException(outOfBoundsMsg(index));

    // 1. 检测是否需要扩容
    ensureCapacityInternal(size + 1);  // Increments modCount!!
    // 2. 将 index 及其之后的所有元素都向后移一位
    // arraycopy(被复制的数组, 从第几个元素开始, 复制到哪里, 从第几个元素开始粘贴, 复制的元素个数)
    System.arraycopy(elementData, index, elementData, index + 1, size - index);
    // 3. 将新元素插入至 index 处
    elementData[index] = element;
    size++;
}
```

如果是在元素序列指定位置（假设该位置合理）插入，则情况稍微复杂一点，需要三个步骤：

1. 检测数组是否有足够的空间
2. 将 index 及其之后的所有元素向后移一位
3. 将新元素插入至 index 处

如下图：

![指定位置插入](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/java_arraylist/arraylist_add2.png)

从上图可以看出，将新元素插入至序列指定位置，需要先将该位置及其之后的元素都向后移动一位，为新元素腾出位置。这个操作的时间复杂度为`O(N)`，频繁移动元素可能会导致效率问题，特别是集合中元素数量较多时。在日常开发中，若非所需，我们应当尽量避免在大集合中调用第二个插入方法。

## 扩容机制

下面就来简单分析一下 ArrayList 的扩容机制，对于变长数据结构，当结构中没有空余空间可供使用时，就需要进行扩容。在 ArrayList 中，当空间用完，其会按照原数组空间的 1.5 倍进行扩容。相关源码如下：

```java
/** 计算最小容量 */
private void ensureCapacityInternal(int minCapacity) {
    if (elementData == DEFAULTCAPACITY_EMPTY_ELEMENTDATA) {
        minCapacity = Math.max(DEFAULT_CAPACITY, minCapacity);
    }

    ensureExplicitCapacity(minCapacity);
}

private void ensureExplicitCapacity(int minCapacity) {
    modCount++;

    // overflow-conscious code
    if (minCapacity - elementData.length > 0)
        grow(minCapacity);
}

/** 扩容的核心方法 */
private void grow(int minCapacity) {
    // overflow-conscious code
    int oldCapacity = elementData.length;
    // newCapacity = oldCapacity + oldCapacity / 2 = oldCapacity * 1.5
    int newCapacity = oldCapacity + (oldCapacity >> 1);
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    // 进行扩容
    elementData = Arrays.copyOf(elementData, newCapacity);
}

private static int hugeCapacity(int minCapacity) {
    if (minCapacity < 0) // overflow
        throw new OutOfMemoryError();
    // 如果最小容量超过 MAX_ARRAY_SIZE，则将数组容量扩容至 Integer.MAX_VALUE
    return (minCapacity > MAX_ARRAY_SIZE) ? Integer.MAX_VALUE : MAX_ARRAY_SIZE;
}

```

上面就是扩容的逻辑，逻辑很简单，这里就不赘述了。

## get()

```java
public E get(int index) {
    if (index >= size)
        throw new IndexOutOfBoundsException(outOfBoundsMsg(index));

    return (E) elementData[index];
}
```

get 的逻辑很简单，就是检查是否越界，根据 index 获取元素。

## remove()

```java
public E remove(int index) {
    if (index >= size)
        throw new IndexOutOfBoundsException(outOfBoundsMsg(index));

    modCount++;
    // 返回被删除的元素值
    E oldValue = (E) elementData[index];

    int numMoved = size - index - 1;
    if (numMoved > 0)
        // 将 index + 1 及之后的元素向前移动一位，覆盖被删除值
        System.arraycopy(elementData, index+1, elementData, index,
                         numMoved);
    // 将最后一个元素置空，并将 size 值减 1     
    elementData[--size] = null; // clear to let GC do its work

    return oldValue;
}

E elementData(int index) {
    return (E) elementData[index];
}

/** 删除指定元素，若元素重复，则只删除下标最小的元素 */
public boolean remove(Object o) {
    if (o == null) {
        for (int index = 0; index < size; index++)
            if (elementData[index] == null) {
                fastRemove(index);
                return true;
            }
    } else {
        // 遍历数组，查找要删除元素的位置
        for (int index = 0; index < size; index++)
            if (o.equals(elementData[index])) {
                fastRemove(index);
                return true;
            }
    }
    return false;
}

/** 快速删除，不做边界检查，也不返回删除的元素值 */
private void fastRemove(int index) {
    modCount++;
    int numMoved = size - index - 1;
    if (numMoved > 0)
        System.arraycopy(elementData, index+1, elementData, index,
                         numMoved);
    elementData[--size] = null; // clear to let GC do its work
}
```

上面的删除方法并不复杂，这里以第一个删除方法为例，删除一个元素步骤如下：

1. 获取指定位置 index 处的元素值
2. 将 index + 1 及之后的元素向前移动一位
3. 将最后一个元素置空，并将 size 值减 1
4. 返回被删除值，完成删除操作

如下图：

![删除元素](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/java_arraylist/arraylist_remove.png)

上面就是删除指定位置元素的分析，并不是很复杂。

现在，考虑这样一种情况。我们往 ArrayList 插入大量元素后，又删除很多元素，此时底层数组会空闲处大量的空间。因为 ArrayList 没有自动缩容机制，导致底层数组大量的空闲空间不能被释放，造成浪费。对于这种情况，ArrayList 也提供了相应的处理方法，如下：

```java
/** 将数组容量缩小至元素数量 */
public void trimToSize() {
    modCount++;
    if (size < elementData.length) {
        elementData = (size == 0)
          ? EMPTY_ELEMENTDATA
          : Arrays.copyOf(elementData, size);
    }
}
```

通过上面的方法，我们可以手动触发 ArrayList 的缩容机制。这样就可以释放多余的空间，提高空间利用率。

![缩容机制](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/java_arraylist/arraylist_trim.png)

## clear()

```java
public void clear() {
    modCount++;

    // clear to let GC do its work
    for (int i = 0; i < size; i++)
        elementData[i] = null;

    size = 0;
}
```

clear 的逻辑很简单，就是遍历一下将所有的元素设置为空。

## 参考资料

- [ArrayList 源码分析](http://www.tianxiaobo.com/2018/01/28/ArrayList%E6%BA%90%E7%A0%81%E5%88%86%E6%9E%90/)