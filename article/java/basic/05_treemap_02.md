# TreeMap 源码分析（下）

## 引言

通过上一篇[TreeMap 源码分析（上）](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/article/java/basic/04_treemap_01.md)的分析，我们已经了解了红黑树插入数据的操作，本文我们继续来分析红黑树删除数据的操作。

## 红黑树的删除

将红黑树内的某一个节点删除。需要执行的操作依次是：首先，将红黑树当作一颗二叉查找树，将该节点从二叉查找树中删除；然后，通过「旋转和重新着色」等一系列来修正该树，使之重新成为一棵红黑树。详细描述如下：

### 第一步：删除节点

将红黑树当作一颗二叉查找树，将节点删除。这和「删除常规二叉查找树中删除节点的方法是一样的」。分 3 种情况：

1. 被删除节点没有儿子，即为叶节点。那么，直接将该节点删除就行了。
2. 被删除节点只有一个儿子。那么，直接删除该节点，并用该节点的唯一子节点顶替它的位置。
3. 被删除节点有两个儿子。这是最麻烦的情况，因为你删除节点之后，还要保证满足搜索二叉树的结构。

情况 3 其实也比较容易，我们可以选择左儿子中的最大元素或者右儿子中的最小元素放到待删除节点的位置，就可以保证结构的不变。当然，你要记得调整子树，毕竟又出现了节点删除。

习惯上大家选择左儿子中的最大元素，其实选择右儿子的最小元素也一样，没有任何差别，只是人们习惯从左向右。这里咱们也选择左儿子的最大元素，将它放到待删结点的位置。

左儿子的最大元素其实很好找，只要顺着左儿子不断的去搜索右子树就可以了，直到找到一个没有右子树的结点。那就是最大的了。

删除操作的伪代码：

```c
RB-DELETE(T, z)
	// 找到删除节点 y 的子树 x，进行下一步操作。先找左子树，如果没有再找右子树.
	// 注意，这里的 y 有两种可能：
	// 1. 有一棵空子树，则是删除节点 z
	// 2. 有两棵非空子树，则是删除节点 z 的后继节点。
  
  if z.left == T.nil or z.right == T.nil        
		y = z // 只要有一棵空子树，y 则指向 z，不找后继节点
  else // 如果有两棵非空子树，则 y 指向后继节点
  	y = TREE-SUCCESSOR(z)
	
  if y.left ≠ T.nil // 若 “y 的左孩子” 不为空
		x = y.left // 则将 “y 的左孩子” 赋值给 “x”；
	else // 否则，“y 的右孩子” 赋值给 “x”。
    x = y.right

	x.p = y.p // 将 “y 的父节点” 设置为 “x 的父节点”，准备删除 y 节点
	if y.p == T.nil // 情况 1：若 “y 的父节点” 为空       
		T.root = x // 则设置 “x” 为 “根节点”
	else if y == y.p.left // 情况 2：若 “y 是它父节点的左孩子”
		y.p.left = x // 则设置 “x” 为 “y 的父节点的左孩子”
	else // 情况 3：若 “y 是它父节点的右孩子”
		y.p.right = x // 则设置 “x” 为 “y 的父节点的右孩子”
	
	if y ≠ z
  	// 将 “y 的值” 赋值给 “z”。
  	// 注意：这里只拷贝 z 的值给 y，而没有拷贝 z 的颜色！！！        
		x.key = y.key
		copy y's satellite data into z
  if y.color = BLACK // 若 “y 为黑节点”，则调用 RB-DELETE-FIXUP
  	RB-DELETE-FIXUP(T, x) // 到这里，y 已经被 x 取代，所以基于 x 去调整        
	return y
```

### 第二步：修正红黑树

因为「第一步」中删除节点之后，可能会违背红黑树的特性。所以需要通过「旋转和重新着色」来修正该树，使之重新成为一棵红黑树。

```c
RB-DELETE-FIXUP(T, x)
	while x ≠ T.root and x.color = BLACK  
		if x == x.p.left // 若 “x” 是 “它父节点的左孩子”，
			w = x.p.right // 则设置 “w” 为 “x 的叔叔”(即 x 为它父节点的右孩子)                                          
			
			// Case 1 : x 是 “黑 + 黑” 节点，x 的兄弟节点是红色。
			// (此时 x 的父节点和 x 的兄弟节点的子节点都是黑节点)。
			if w.color == RED 
				w.color = BLACK // Case 1 : (01) 将 x 的兄弟节点设为 “黑色”。
				x.p.color = RED // Case 1 : (02) 将 x 的父节点设为 “红色”。
				LEFT-ROTATE(T, x.p) // Case 1 : (03) 对x的父节点进行左旋。
				w = x.p.right // Case 1 : (04) 左旋后，重新设置 x 的兄弟节点。
				
			// Case 2: x 是 “黑 + 黑” 节点，x 的兄弟节点是黑色，
			// x 的兄弟节点的两个孩子都是黑色。
			if w.left.color == BLACK and w.right.color == BLACK       
				w.color = RED // Case 2: (01) 将 x 的兄弟节点设为 “红色”。
				x = x.p // Case 2: (02) 设置 “x 的父节点” 为 “新的 x 节点”。
			
			// Case 3: x 是 “黑 + 黑” 节点，
			// x 的兄弟节点是黑色；x 的兄弟节点的左孩子是红色，右孩子是黑色的。
			else
				if w.right.color == BLACK
					// Case 3: (01) 将x兄弟节点的左孩子设为 “黑色”。
          w.left.color = BLACK
          w.color = RED // Case 3: (02) 将 x 兄弟节点设为 “红色”。
          RIGHT-ROTATE(T, w) // Case 3: (03) 对 x 的兄弟节点进行右旋。
          w = x.p.right // Case 3: (04) 右旋后，重新设置 x 的兄弟节点。
			
				// Case 4: x 是 “黑 + 黑” 节点，x 的兄弟节点是黑色；
				// x 的兄弟节点的右孩子是红色的。
				// Case 4: (01) 将 x 父节点颜色 赋值给 x 的兄弟节点。
				w.color = x.p.color
				x.p.color = BLACK // Case 4: (02) 将 x 父节点设为 “黑色”。
				// Case 4: (03) 将 x 兄弟节点的右子节设为 “黑色”。
				w.right.color = BLACK 
				LEFT-ROTATE(T, x.p) // Case 4: (04) 对 x 的父节点进行左旋。
				x = T.root // Case 4: (05) 设置 “x” 为 “根节点”。
		else
			// 若 “x” 是 “它父节点的右孩子”，
			// 将上面的操作中 “right” 和 “left” 交换位置，然后依次执行。
			(same as then clause with "right" and "left" exchanged)
	x.color = BLACK
```

通过 RB-DELETE 算法，我们知道：删除节点 y 之后，x 占据了原来节点 y 的位置。 既然删除 y（y 是黑色），意味着减少一个黑色节点；那么，再在该位置上增加一个黑色即可。

这样，当我们假设「x 包含一个额外的黑色」，就正好弥补了「删除 y 所丢失的黑色节点」，也就不会违反「特性 5」。 因此，假设「x 包含一个额外的黑色」（x 原本的颜色还存在），这样就不会违反「特性 5」。

现在，我们面临的问题，由解决「违反了特性 2、4、5 三个特性」转换成了「解决违反特性 1、2、4 三个特性」。

RB-DELETE-FIXUP 需要做的就是通过算法恢复红黑树的特性 1、2、4。RB-DELETE-FIXUP 的思想是：将 x 所包含的额外的黑色不断沿树上移「向根方向移动」，直到出现下面的姿态：

- x 指向一个「红 + 黑」节点。此时，将 x 设为一个「黑」节点即可。
- x 指向根。此时，将 x 设为一个「黑」节点即可。
- 非前面两种姿态。

将上面的姿态，可以概括为 3 种情况：

- 情况一：x是「红 + 黑」节点。

处理方法：直接把 x 设为黑色，结束。此时红黑树性质全部恢复。

- 情况二：x 是「黑 + 黑」节点，且 x 是根。

处理方法：什么都不做，结束。此时红黑树性质全部恢复。

- 情况三：x 是「黑 + 黑」节点，且 x 不是根。

 处理方法：这种情况又可以划分为 4 种子情况。

#### Case 1：「黑 + 黑」，兄弟红

如下图，x 是「黑 + 黑」节点，x 的兄弟节点是红色，此时 x 的父节点和 x 的兄弟节点的子节点都是黑节点。

![img](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/treemap/08.jpg)

处理策略：

1. 将 x 的兄弟节点设为「黑色」。
2. 将 x 的父节点设为「红色」。
3. 对 x 的父节点进行左旋。
4. 左旋后，重新设置 x 的兄弟节点。

下面说明谈谈为什么这么处理？

这样做的目的是将「Case 1」转换为「Case 2」、「Case 3」或「Case 4」，从而进行进一步的处理。

对 x 的父节点进行左旋；左旋后，为了保持红黑树特性，就需要在左旋前「将 x 的兄弟节点设为黑色」，同时「将 x 的父节点设为红色」；左旋后，由于 x 的兄弟节点发生了变化，需要更新 x 的兄弟节点，从而进行后续处理。

#### Case 2：x「黑 + 黑」，兄弟黑色，兄弟孩子黑

如下图，x 是「黑 + 黑」节点，x 的兄弟节点是黑色，x 的兄弟节点的两个孩子都是黑色。

![img](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/treemap/09.jpg)

处理策略：

1. 将 x 的兄弟节点设为「红色」。
2. 设置「x 的父节点」为「新的 x 节点」。

下面说明谈谈为什么这么处理？

这个情况的处理思想是将「x 中多余的一个黑色属性上移（往根方向移动）」。 

x 是「黑 + 黑」节点，我们将 x 由「黑 + 黑」节点 变成 「黑」节点，多余的一个「黑」属性移到 x 的父节点中，即 x 的父节点多出了一个「黑」属性（若 x 的父节点原先是「黑」，则此时变成了「黑 + 黑」；若 x 的父节点原先时「红」，则此时变成了「红 + 黑」）。

此时，需要注意的是：所有经过 x 的分支中黑节点个数没变化；但是，所有经过 x 的兄弟节点的分支中黑色节点的个数增加了1（因为 x 的父节点多了一个黑色属性）！

为了解决这个问题，我们需要将「所有经过 x 的兄弟节点的分支中黑色节点的个数减1」即可，那么就可以通过「将 x 的兄弟节点由黑色变成红色」来实现。

经过上面的步骤「将 x 的兄弟节点设为红色」，多余的一个颜色属性「黑色」已经跑到 x 的父节点中。我们需要将 x 的父节点设为「新的 x 节点」进行处理。若「新的 x 节点」是「黑 + 红」，直接将「新的 x 节点」设为黑色，即可完全解决该问题；若「新的 x 节点」是「黑 + 黑」，则需要对「新的 x 节点」进行进一步处理。

#### Case 3：「黑 + 黑」，兄弟黑，兄弟孩子左红，右黑

如下图，x 是「黑 + 黑」节点，x 的兄弟节点是黑色；x 的兄弟节点的左孩子是红色，右孩子是黑色的。

![img](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/treemap/10.jpg)

处理策略：

1. 将 x 兄弟节点的左孩子设为「黑色」。
2. 将 x 兄弟节点设为「红色」。
3. 对 x 的兄弟节点进行右旋。
4. 右旋后，重新设置 x 的兄弟节点。

下面说明谈谈为什么这么处理？

我们处理「Case 3」的目的是为了将「Case 3」进行转换，转换成「Case 4」，从而进行进一步的处理。

转换的方式是对 x 的兄弟节点进行右旋；为了保证右旋后，它仍然是红黑树，就需要在右旋前「将 x 的兄弟节点的左孩子设为黑色」，同时「将 x 的兄弟节点设为红色」；右旋后，由于 x 的兄弟节点发生了变化，需要更新 x 的兄弟节点，从而进行后续处理。

#### Case 4：「黑 + 黑」，兄弟黑，兄弟孩子右红，左任意

如下图，x 是「黑 + 黑」节点，x 的兄弟节点是黑色；x 的兄弟节点的右孩子是红色的，x 的兄弟节点的左孩子任意颜色。

![img](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/java/basic/treemap/11.jpg)

处理策略：

1. 将 x 父节点颜色赋值给  x 的兄弟节点。
2. 将 x 父节点设为「黑色」。
3. 将 x 兄弟节点的右子节点设为「黑色」。
4. 对 x 的父节点进行左旋。
5. 设置 x 为「根节点」。

下面说明谈谈为什么这么处理？

我们处理「Case 4」的目的是：去掉 x 中额外的黑色，将 x 变成单独的黑色。

处理的方式是：进行颜色修改，然后对 x 的父节点进行左旋。

下面，我们来分析是如何实现的：

为了便于说明，我们设置「当前节点」为 S（Original Son），「兄弟节点」为 B（Brother），「兄弟节点的左孩子」为 BLS（Brother's Left Son），「兄弟节点的右孩子」为 BRS（Brother's Right Son），「父节点」为 F（Father）。

我们要对 F 进行左旋。但在左旋前，我们需要调换 F 和 B 的颜色，并设置 BRS 为黑色。

为什么需要这里处理呢？因为左旋后，F 和 BLS 是父子关系，而我们已知 BL 是红色，如果 F 是红色，则违背了「特性 4」；为了解决这一问题，我们将「F 设置为黑色」。 但是，F 设置为黑色之后，为了保证满足「特性 5」，即为了保证左旋之后：

- 第一，同时经过根节点和 S 的分支的黑色节点个数不变。

若满足「第一」，只需要 S 丢弃它多余的颜色即可。因为 S 的颜色是「黑+黑」，而左旋后「同时经过根节点和 S 的分支的黑色节点个数」增加了1；现在，只需将 S 由「黑+黑」变成单独的「黑」节点，即可满足「第一」。

- 第二，同时经过根节点和 BLS 的分支的黑色节点数不变。

若满足「第二」，只需要将「F 的原始颜色」赋值给 B 即可。之前，我们已经将「F 设置为黑色」（即，将 B 的颜色「黑色」，赋值给了 F）。至此，我们算是调换了 F 和 B 的颜色。

- 第三，同时经过根节点和 BRS 的分支的黑色节点数不变。

在「第二」已经满足的情况下，若要满足「第三」，只需要将 BRS 设置为「黑色」即可。

经过，上面的处理之后。红黑树的特性全部得到的满足！接着，我们将 x 设为根节点，就可以跳出 while 循环（参考伪代码）；即完成了全部处理。

至此，我们就完成了 Case 4 的处理。理解 Case 4 的核心，是了解如何「去掉当前节点额外的黑色」。

至此，红黑树的理论知识差不多讲完了，我们来看下 TreeMap 里的实现。

## 插入

```java
public V put(K key, V value) {
  Entry<K,V> t = root;
  // 1.如果根节点为 null，将新节点设为根节点
  if (t == null) {
    compare(key, key); // type (and possibly null) check

    root = new Entry<>(key, value, null);
    size = 1;
    modCount++;
    return null;
  }
  int cmp;
  Entry<K,V> parent;
  // split comparator and comparable paths
  Comparator<? super K> cpr = comparator;
  if (cpr != null) {
    do { // 2.为 key 在红黑树找到合适的位置
      parent = t;
      cmp = cpr.compare(key, t.key);
      if (cmp < 0)
        t = t.left;
      else if (cmp > 0)
        t = t.right;
      else
        return t.setValue(value);
    } while (t != null);
  }
  else { // 与上面代码逻辑类似
    if (key == null)
      throw new NullPointerException();
    @SuppressWarnings("unchecked")
    Comparable<? super K> k = (Comparable<? super K>) key;
    do {
      parent = t;
      cmp = k.compareTo(t.key);
      if (cmp < 0)
        t = t.left;
      else if (cmp > 0)
        t = t.right;
      else
        return t.setValue(value);
    } while (t != null);
  }
  Entry<K,V> e = new Entry<>(key, value, parent);
  // 3.将新节点链入红黑树中
  if (cmp < 0)
    parent.left = e;
  else
    parent.right = e;
  // 4.插入新节点可能会破坏红黑树性质，这里修正一下
  fixAfterInsertion(e);
  size++;
  modCount++;
  return null;
}
```

修正插入节点后的红黑树：

```java
private void fixAfterInsertion(Entry<K,V> x) {
  x.color = RED;

  while (x != null && x != root && x.parent.color == RED) {
    if (parentOf(x) == leftOf(parentOf(parentOf(x)))) {
      Entry<K,V> y = rightOf(parentOf(parentOf(x)));
      if (colorOf(y) == RED) { // Case 1
        setColor(parentOf(x), BLACK);
        setColor(y, BLACK);
        setColor(parentOf(parentOf(x)), RED);
        x = parentOf(parentOf(x));
      } else {
        if (x == rightOf(parentOf(x))) { // Case 2
          x = parentOf(x);
          rotateLeft(x);
        }
        // Case 3
        setColor(parentOf(x), BLACK);
        setColor(parentOf(parentOf(x)), RED);
        rotateRight(parentOf(parentOf(x)));
      }
    } else {
      Entry<K,V> y = leftOf(parentOf(parentOf(x)));
      if (colorOf(y) == RED) {
        setColor(parentOf(x), BLACK);
        setColor(y, BLACK);
        setColor(parentOf(parentOf(x)), RED);
        x = parentOf(parentOf(x));
      } else {
        if (x == leftOf(parentOf(x))) {
          x = parentOf(x);
          rotateRight(x);
        }
        setColor(parentOf(x), BLACK);
        setColor(parentOf(parentOf(x)), RED);
        rotateLeft(parentOf(parentOf(x)));
      }
    }
  }
  root.color = BLACK;
}
```

可以看到插入与前面介绍的的伪代码是一致的，这里不再赘述。

## 删除

```java
public V remove(Object key) {
  Entry<K,V> p = getEntry(key);
  if (p == null)
    return null;

  V oldValue = p.value;
  deleteEntry(p);
  return oldValue;
}
```

删除节点：

```java
private void deleteEntry(Entry<K,V> p) {
  modCount++;
  size--;

  // 1. 如果 p 有两个孩子节点，则找到后继节点，
  // 并把后继节点的值复制到节点 P 中，并让 p 指向其后继节点
  if (p.left != null && p.right != null) {
    Entry<K,V> s = successor(p);
    p.key = s.key;
    p.value = s.value;
    p = s;
  } // p has 2 children

  // Start fixup at replacement node, if it exists.
  Entry<K,V> replacement = (p.left != null ? p.left : p.right);

  if (replacement != null) {
    // 2. 将 replacement parent 引用指向新的父节点，
    // 同时让新的父节点指向 replacement。
    replacement.parent = p.parent;
    if (p.parent == null) // 情况 1
      root = replacement;
    else if (p == p.parent.left) // 情况 2
      p.parent.left  = replacement;
    else // 情况 3
      p.parent.right = replacement;

    // Null out links so they are OK to use by fixAfterDeletion.
    p.left = p.right = p.parent = null;

    // 3. 如果删除的节点 p 是黑色节点，则需要进行调整
    if (p.color == BLACK)
      fixAfterDeletion(replacement);
  } else if (p.parent == null) { // 删除的是根节点，且树中当前只有一个节点
    root = null;
  } else { // 删除的节点没有孩子节点
    if (p.color == BLACK)
      fixAfterDeletion(p);

    if (p.parent != null) {
      if (p == p.parent.left)
        p.parent.left = null;
      else if (p == p.parent.right)
        p.parent.right = null;
      p.parent = null;
    }
  }
}
```

修正删除节点后的红黑树：

```java
private void fixAfterDeletion(Entry<K,V> x) {
  while (x != root && colorOf(x) == BLACK) {
    if (x == leftOf(parentOf(x))) {
      Entry<K,V> sib = rightOf(parentOf(x));

      if (colorOf(sib) == RED) { // Case 1
        setColor(sib, BLACK);
        setColor(parentOf(x), RED);
        rotateLeft(parentOf(x));
        sib = rightOf(parentOf(x));
      }

      if (colorOf(leftOf(sib))  == BLACK &&
          colorOf(rightOf(sib)) == BLACK) { // Case 2
        setColor(sib, RED);
        x = parentOf(x);
      } else {
        if (colorOf(rightOf(sib)) == BLACK) { // Case 3
          setColor(leftOf(sib), BLACK);
          setColor(sib, RED);
          rotateRight(sib);
          sib = rightOf(parentOf(x));
        }
        // Case 4
        setColor(sib, colorOf(parentOf(x)));
        setColor(parentOf(x), BLACK);
        setColor(rightOf(sib), BLACK);
        rotateLeft(parentOf(x));
        x = root;
      }
    } else { // symmetric
      Entry<K,V> sib = leftOf(parentOf(x));

      if (colorOf(sib) == RED) {
        setColor(sib, BLACK);
        setColor(parentOf(x), RED);
        rotateRight(parentOf(x));
        sib = leftOf(parentOf(x));
      }

      if (colorOf(rightOf(sib)) == BLACK &&
          colorOf(leftOf(sib)) == BLACK) {
        setColor(sib, RED);
        x = parentOf(x);
      } else {
        if (colorOf(leftOf(sib)) == BLACK) {
          setColor(rightOf(sib), BLACK);
          setColor(sib, RED);
          rotateLeft(sib);
          sib = leftOf(parentOf(x));
        }
        setColor(sib, colorOf(parentOf(x)));
        setColor(parentOf(x), BLACK);
        setColor(leftOf(sib), BLACK);
        rotateRight(parentOf(x));
        x = root;
      }
    }
  }

  setColor(x, BLACK);
}
```

与前面介绍的伪代码一致，不再赘述。

## 查找

```java
public V get(Object key) {
  Entry<K,V> p = getEntry(key);
  return (p==null ? null : p.value);
}

final Entry<K,V> getEntry(Object key) {
  // Offload comparator-based version for sake of performance
  if (comparator != null)
    return getEntryUsingComparator(key);
  if (key == null)
    throw new NullPointerException();
  @SuppressWarnings("unchecked")
  Comparable<? super K> k = (Comparable<? super K>) key;
  Entry<K,V> p = root;
  while (p != null) {
    int cmp = k.compareTo(p.key);
    if (cmp < 0)
      p = p.left;
    else if (cmp > 0)
      p = p.right;
    else
      return p;
  }
  return null;
}
```

TreeMap 基于红黑树实现，而红黑树是一种自平衡二叉查找树，所以 TreeMap 的查找操作流程和二叉查找树一致。

二叉树的查找流程是这样的：先将目标值和根节点的值进行比较，如果目标值小于根节点的值，则再和根节点的左孩子进行比较。如果目标值大于根节点的值，则继续和根节点的右孩子比较。在查找过程中，如果目标值和二叉树中的某个节点值相等，则返回 true，否则返回 false。

TreeMap 查找和此类似，只不过在 TreeMap 中，节点（Entry）存储的是键值对 `<k,v>`。在查找过程中，比较的是键的大小，返回的是值，如果没找到，则返回 `null`。

## 总结

TreeMap 与 HashMap 相比，TreeMap 保存的记录是有序的，且存取的时间复杂度都是O(log(n))；由于 HashMap 实现方式是 `数组` + `链表` + `红黑树`，所以 HashMap 在随机访问数据时会有一些优势，但是 HashMap 保存的记录是无序的，记录达到阈值后会自动扩容。

## 参考资料

- [维基百科 - 红黑树](https://zh.wikipedia.org/wiki/红黑树)
- [TreeMap源码分析](http://www.tianxiaobo.com/2018/01/11/TreeMap源码分析)
- [教你初步了解红黑树](https://blog.csdn.net/v_JULY_v/article/details/6105630)
- [红黑树(一)之 原理和算法详细介绍](https://www.cnblogs.com/skywang12345/p/3245399.html)
- [红黑树可视化网站](https://www.cs.usfca.edu/~galles/visualization/RedBlack.html)