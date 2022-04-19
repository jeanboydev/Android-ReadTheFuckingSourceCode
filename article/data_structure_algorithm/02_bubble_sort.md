# 冒泡排序

## 排序过程

1. 外循环从右向左遍历
2. 内循环从左向右遍历，排除最后一位数
3. 如果当前的数比后一位数大，则交换

## 代码实现

```java
private static void bubbleSort(int[] arr) {
  if (arr == null || arr.length < 2) return;
  int n = arr.length;
  boolean isSwap = false; // 是否发生了交换
  // 从右向左遍历
  for (int i = n - 1; i > 0; i--) {
    isSwap = false; // 重置标识
    for (int j = 0; j < i; j++) { // 每一轮冒泡，最后一位肯定是最大的数，所以排除最后一位
      if (arr[j] > arr[j + 1]) { // 右边的数比左边大，交换数据
        int temp = arr[j];
        arr[j] = arr[j + 1];
        arr[j + 1] = temp;
        isSwap = true; // 发生了数据交换
      }
    }
    if (!isSwap) { // 没有发生交换，说明已经是正序的数组了
      break;
    }
  }
}
```
