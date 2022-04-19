# 快速排序

## 排序过程

1. 首先定义左右两个指针
2. 以左边第一个数为基数 base
3. while(i<j) 时遍历
   - 先从右向左遍历，找到第一个比 base 小的数，放到最左边
   - 然后从左向右遍历，找到死一个比 base 大的数，放到最右边
4. 然后将 i 的位置放入 base
5. 继续遍历左边部分
6. 继续遍历右半部分

## 代码实现

```java
private static void quickSort(int[] arr) {
  if (arr == null || arr.length < 2) return;
  quickSort(arr, 0, arr.length - 1);
}

private static void quickSort(int[] arr, int l, int r) {
  int i = l; // 左边哨兵
  int j = r; // 右边哨兵
  int base = arr[i]; // 基准数
  while (i < j) {
    while (i < j && arr[j] >= base) { // 从右向左遍历，找到第一个比 base 小的数
      j--;
    }
    arr[i] = arr[j];  // 找到比 base 小的数，放入到最左边
    while (i < j && arr[i] < base) { // 从左向右遍历，找到第一个比 base 大的数
      i++;
    }
    arr[j] = arr[i]; // 找到比 base 大的数，放入到右边
  }
  arr[i] = base;  // 遍历完说明两个哨兵相遇，最后交换哨兵与与基准数
  if (i > l) { // 左边部分排序
    quickSort(arr, l, i - 1);
  }
  if (j < r) { // 右边部分排序
    quickSort(arr, j + 1, r);
  }
}
```

