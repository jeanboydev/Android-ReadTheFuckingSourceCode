# Composite（组合模式） #
## 概述 ##
组合模式（Composite Pattern），又叫部分整体模式，是用于把一组相似的对象当作一个单一的对象。 

组合模式依据树形结构来组合对象，用来表示部分以及整体层次。 这种类型的设计模式属于结构型模式，它创建了对象组的树形结构。
这种模式创建了一个包含自己对象组的类。 该类提供了修改相同对象组的方式。

## 使用 ##
### 示例 ###
我们来模拟一个树。

### 实现 ###
1. 首先创建一个节点
```Java
public class TreeNode {

    private String name;

    private TreeNode parent;

    private Vector<TreeNode> children = new Vector<>();

    public TreeNode(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public TreeNode getParent() {
        return parent;
    }

    public void setParent(TreeNode parent) {
        this.parent = parent;
    }

    public void addChildren(TreeNode node){
        children.add(node);
    }

    public void removeChildren(TreeNode node){
        children.remove(node);
    }

    public Vector<TreeNode> getChildren() {
        return children;
    }
}
```
2. 测试
```Java
public class CompositeTest {

    @Test
    public void testComposite() {

        TreeNode root=new TreeNode("root");

        TreeNode nodeA=new TreeNode("A");
        TreeNode nodeB=new TreeNode("B");

        nodeA.addChildren(nodeB);
        root.addChildren(nodeA);
    }
}
```

## 使用场景 ##
将多个对象组合在一起进行操作，常用于表示树形结构中，例如二叉树，树形菜单，文件、文件夹的管理。。

## 优点 ##
1. 高层模块调用简单。
2. 节点自由增加。
## 缺点 ##
在使用组合模式时，其叶子和树枝的声明都是实现类，而不是接口，违反了依赖倒置原则。

## 注意事项 ##
定义时为具体类。