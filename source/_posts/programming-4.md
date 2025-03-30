---
title: 编程随笔（四）
date: 2025-03-19
updated: 2025-03-21
categories:
- 编程随笔
---

不得不说我对 Vue 的理解还是太浅薄了。

## 问题
这学期我担任 OS 开发组助教，任务之一就是制作宣发页。

宣发页使用 Vue 3、Vuetify 3、Vue Router 4 制作。现在有个需求，需要让助教列表支持查看往届助教。另一位助教已经写好了，下面是最小复现示例。

[Vue Playground][1]

很遗憾，Vuetify 不支持选项卡套列表，虽然官方文档里有一个[溢出到菜单](https://vuetifyjs.com/zh-Hans/components/tabs/#section-6ea251fa523083dc5355)示例，但那是用按钮实现的。所以说自己实现是在所难免了。

不得不说，这位助教的实现虽然能用，但是存在一些问题：
 -  目前的实现是鼠标悬停展开菜单，点击查看最新一届助教。用户在没有提示的情况下，很难发现需要悬停才能展开菜单。（可以在文字右侧加一个下三角来提示）
 -  移动端无法做出“悬停”这一动作（长按什么的都不行），因而无法展开菜单。
 -  视觉上有一点不足是，目前被选中的列表项没有显示为选中状态。
 -  最后，代码写得非常不优雅。通过 CSS 让按钮和其他两个选项卡一样宽。`navigateTo` 函数更是不知所云，结尾为什么要调用 `nextTick`，这位助教也说不清——他说他是用 ChatGPT 写的。

我希望能重新实现这个功能，目前有三个策略：
 -  上策：在使用选项卡的前提下实现点击展开菜单，再次点击列表项跳转。查看助教时，“课程助教”选项卡显示为选中状态，菜单项中选中的年份显示为选中状态。
 -  中策：使用按钮伪装为选项卡，并实现点击展开菜单、再次点击列表跳转、选中的菜单项显示为选中状态。
 -  下策：放弃选项卡套列表的布局，改为在 `AssistantPage` 内部做一个下拉菜单。

## 第一版
### 简化
首先我查阅了 `<v-tab>` 的 [API 文档](https://vuetifyjs.com/zh-Hans/api/v-tab/)，在里面找到了 `to` 选项。这个选项对应于 Vue Router 的 to 属性，用这个比自己实现函数方便多了。于是我把 `@click="navigateTo(item)"` 换成了 ``:to="`/assistant?year=${item}`"``。

修改后出现了一个问题，当我查看助教列表时，2025 和 2024 两个列表项都会处于选中状态。幸好，API 文档里提到了 `exact` 属性，加上以后，就只有当前选项卡处于选中状态了。

注：`<v-tab>` 的 `exact` 属性对应旧版 Vue Router 中 `<router-link>` 的 `exact` 属性（现已移除），其要求当前路径与给定路径**完全相同**（包括 `query` 参数）。


### 提问
我用 CodeSandbox 制作了一个最小复现示例，然后扔到了 [StackOverflow](https://stackoverflow.com/q/79420382/20025220) 上。经提醒，附上了完整的代码。

### Vuetify 源码分析
于是我用开发者工具给文档树打了断点，开始调试。但由于调用堆栈过于混乱，无法追踪（这里面还涉及到了事件队列），只好改为阅读 Vuetify 源码。

`/packages/vuetify/src/composables/group.ts`

```ts
  watch(isSelected, value => {
    vm.emit('group:selected', { value })
  }, { flush: 'sync' })
```

`/packages/vuetify/src/components/VTabs/VTab.tsx`

```tsx
        <VBtn
          ...
          onGroup:selected={ updateSlider }
        >
```

`updateSlider` 函数，最后发现是一堆复杂的数学计算，用来实现滑条移动的动画……


可是并没有响应点击事件的代码。`/packages/vuetify/src/components/VBtn/VBtn.tsx`

```tsx
    function onClick (e: MouseEvent) {
      if (
        isDisabled.value ||
        (link.isLink.value && (
          e.metaKey ||
          e.ctrlKey ||
          e.shiftKey ||
          (e.button !== 0) ||
          attrs.target === '_blank'
        ))
      ) return

      link.navigate?.(e)
      group?.toggle()
    }
```

最重要的是最后两行。先看一下 `link` 和 `group` 的定义：
```tsx
    const group = useGroupItem(props, props.symbol, false)
    const link = useLink(props, attrs)
```

先说 `link.navigate?.(e)` 一行，其中 `useLink` 函数是对 Vue Router `RouterLink.useLink()` 的又一次包装。所以这个 `link.navigate?.(e)` 其实是调用了 `RouterLink` 的 `navigate()` 方法。

再说 `group?.toggle()` 一行。在 `useGroupItem()` 中可以找到 `toggle()` 的定义：
```ts
  return {
    ...
    toggle: () => group.select(id, !isSelected.value),
    select: (value: boolean) => group.select(id, value),
    ...
  }
```


[1]: https://play.vuejs.org/#eNqFVttuG0UYfpVhg2RHyu46dpK2xgkuqBIgAVGJ4AIjNF6P7W12Z5aZWTuW5TuEWqpQoaoSJ6kSV3BVARcgJe3T1E25yivwz8wevU6IFHnnPx+/mbkVYp8694TVtvwwYlyiOfI4wZLcjiK0QEPOQlSbxKTWo4kAZ7EkPOE4rjnm7FT/05hIfzgr2lDnXFA5SI3gKHKMkx71GBUSJeJov2yuvqlF0gjr8A8UhJxYkLoJJT8nNgwhZDGV9doGuKptWltW4hIS70gSRgEYPFCCnYkNLP2ZHuw+5shjAeP7PSvifoj5rGclIkUhW/oyIAevHp++fP7LxV9nF2dPXz97cfHbw5dnDy/OTi/P7y+fP14+OH3997Pli68vz3/qeGxADuZz9KaO3RnGQXCI5RgtFh1X8y7PH3TcVQeZ5zRytEFOJKHCZzRj6sAk7osCJaUhySAVF5JYPvp++ceT5XffLB/9qRwB82r5iLMhEYJxUHz15MflP/eXP//67w9P/1cRC+ELial8e0Yw3282mruFAmYKIaExYhGhNqP2mE0IX5EppYw96U+w1F2ZI4gtEmhRMauV+rGUjCJ/AKJZLD0LTey+TxVRa4Ouadfy298hvY5r1KoxuKWJWUkiAOvIC8AN2O2P7BEnMyCOxtAgu7U+PqNl+2AXYhrqlPTBp0hVDEJD7WMyS8jqpCchP3e9wPeO4UzxxB9BaEesrlibwHPXZGA8rrYAyKoH5UZWmptQ8sGqFKQwsvkmKajJVcyy2hOfTLMAtf9UKrEB3yXzcBQe9yOJAkxHkLBUxRFExko0AyHY/7sGqAoAZCdg9VZBkMLmHEHpSmAHAikQJXC3n1usbwLbMHVvgPd5zzIzvYX0107P+iI3kbcERLGYUQ/VJziISRsJyX062kT7B2iukjbenCgW47omIBQBHrRRLd+h2pZhfBUTPmsbPfWngmkjbdiQFupnoaJFCE+xD5EkyeoUEHJdNIX5Z1MnYB6WgB4OJwHDA80H9Y5ram3q/oZto7GUkWi7LkTiHasNHQag7rHQxe6NW7uN7cathttsQDGazQaybdU+IWcatLpJ0WupkZhGxyOtnEB1t+XccLZvugPINKU5IdxQnhCqKRBPYis1i4QHgDEAykZWIFOSqT9QhdtrOs3d6ETnOyZqDdto56YmmAQzg3ApJOVfdx9+SELGZ++BB/jZSohXj5gymFj4jASQIjnEI5JdeAWavvjyiTxMMbYkX6KuaNxO8y5plKipRmmozeBCWQA8kxmrQWIMrFJCoUzFwBd66HLJ7Cooq5SjX1UqjHBRqZyAUiosT7Z/xYqb3RibZrTXdai+qX2bROFzoR8O5ERXbECGOA5S29B3U0nAngh6zyh0XzsAdNUMQJhsz3pW3mVF7llrpzmR6O44LaeRzXNCdYgI7T5nU6GHDWAjtd0FIXdAJpKxQAD8+Ve5qAh295w9Z9sN/L4L1l1Ya3JStp3s0zVBX7mCYFHb0oACxYSSSVg8OvRHKwVTbfUDwj+OFJyUC4cDwIoPNE3ymGSBeWPiHa+h3xMnJthDTqBSE1JIRmI+InCFK/adTz4CXCswQzaIA5C+hnmXCBbEKkYj9k5MBxB2QU5H+77uP0D0kbiTvrCyQHU1tLwu7rvXpJ6H23J2ClVcwYHKa7T4PFu5CEG7ggoV/eIrrapfwYiKfvE9BM9XeKlK2Donea7qG8hR9w48WOGlWvXwJdwQqmZguOXsOtsta/EffGxK/g==
