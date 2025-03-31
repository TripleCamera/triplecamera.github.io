---
title: 编程随笔（四）
date: 2025-03-19
updated: 2025-03-30
categories:
- 编程随笔
---

不得不说我对 Vue 的理解还是太浅薄了。

## 问题
这学期我担任 OS 开发组助教，任务之一就是制作宣发页。

宣发页使用 Vue 3、Vuetify 3、Vue Router 4 制作。现在有个需求，需要让助教列表支持查看往届助教。由于我那段时间没空，这项任务就交给了另一位助教。经过几次修改后，这项功能合并到了主分支。下面是最小复现示例：

[Vue Playground][1]

值得注意的是，最初的版本不长这个样子。在最初的版本中，“课程助教”选项卡是用 `<v-btn>` 实现的，点击展开菜单，再次点击菜单项即可跳转——和官方文档里的[溢出到菜单](https://vuetifyjs.com/zh-Hans/components/tabs/#section-6ea251fa523083dc5355)示例几乎一模一样。但是每个 `<v-tab>` 下方都有一个横条（文档中叫 slider），用来指示当前选中的选项卡。而 `<v-btn>` 下方没有 slider，这就导致路由切换到“课程助教”页面时，slider 并不会自动更新，还位于其他选项卡下方：

![路由切换到“课程助教”页面时，slider 还位于“教师团队”选项卡下方](/images/programming-4.png)

于是他改成了用 `<v-tab>` 套 `<v-btn>` 实现，并把交互逻辑改成了悬浮展开菜单、点击跳转。一位高阶助教又在此基础上进行小修，将 `<v-btn>` 改为 `<button>`，修复了样式问题。

不得不说，这位助教的实现虽然能用，但是存在一些问题：
 -  用户在没有外部提示的情况下，往往会直接点击选项卡，很难发现需要悬停才能展开菜单。（文字右侧本来有一个下三角图标的，可惜去掉了，再加回来就好）
 -  移动端无法做出“悬停”这一动作（长按什么的都不行），因而无法展开菜单。
 -  视觉上有一点不足是，目前被选中的菜单项（2024/2025）不会显示为选中状态。
 -  最后，代码写得非常不优雅。通过 CSS 让按钮和其他两个选项卡一样宽。`navigateTo` 函数更是不知所云，结尾为什么要调用 `nextTick`，这位助教也说不清——他说他是用 ChatGPT 写的。

我希望能重新实现这个功能，目前有三个策略：
 -  上策：既使用 `<v-tab>` ，又支持点击展开菜单。另外“课程助教”选项卡和其下的菜单项能够正确显示为选中状态。
 -  中策：为了支持点击展开菜单而放弃 `<v-tab>` 的 slider，改回之前的 `<v-btn>`。在此基础上，菜单项要能够显示为选中状态。
 -  下策：彻底放弃选项卡套列表的布局，改为在 `AssistantPage` 内部做一个下拉菜单。

## 第一版
### 简化
首先我查阅了 `<v-tab>` 的 [API 文档](https://vuetifyjs.com/zh-Hans/api/v-tab/)，在里面找到了 `to` 选项。这个选项对应 Vue Router 的 to 属性，用这个比自己实现函数方便多了。于是我把 `@click="navigateTo(item)"` 换成了 ``:to="`/assistant?year=${item}`"``。

修改后出现了一个问题，当我查看助教列表时，2025 和 2024 两个列表项都会处于选中状态。幸好，API 文档里提到了 `exact` 属性，加上以后，就只有当前选项卡处于选中状态了。

注：`<v-tab>` 的 `exact` 属性对应旧版 Vue Router 中 `<router-link>` 的 `exact` 属性（现已移除），其要求当前路径与给定路径**完全相同**（包括 `query` 参数）。


### 提问
接下来我不知道该怎么做了。于是我想去 StackOverflow 提问。考虑到光贴代码不好测试，我用 CodeSandbox 制作了一个最小复现示例，然后附到了我的[问题](https://stackoverflow.com/q/79420382/20025220)上。随后有人提醒我，如果链接失效，我的问题将变得一文不值，于是我又附上了完整的代码。

### Vuetify 源码分析
问题提完后，我又回到了研究中。我用开发者工具给选项卡标签（`<a>`）打上了“属性修改时”断点，开始调试。但由于调用堆栈过于混乱，无法追踪（这里面还涉及到了事件队列），只好改为阅读 Vuetify 源码。值得一提的是，用 GitHub Codespace 看源码真的非常方便。

根据堆栈信息，我们找到了以下文件：

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
我花了很久的时间来研究 `updateSlider` 函数，最后发现是一堆复杂的数学计算，用来实现滑条移动的动画……

可惜的是，以上这些代码中并没有响应点击事件的逻辑。下面这个才是重点：

`/packages/vuetify/src/components/VBtn/VBtn.tsx`
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

先说 `link.navigate?.(e)` 一行，其中 `useLink` 函数是对 Vue Router `RouterLink.useLink()` 的封装。所以这个 `link.navigate?.(e)` 其实是调用了 `RouterLink` 的 `navigate()` 方法。

再说 `group?.toggle()` 一行。在 `useGroupItem()` 中可以找到 `toggle()` 的定义：
```ts
  return {
    ...
    toggle: () => group.select(id, !isSelected.value),
    select: (value: boolean) => group.select(id, value),
    ...
  }
```
看来是在更新选项卡所在组（也就是 `<v-tabs>` 选项卡组）的数据。

很遗憾，这次源码分析并没有找到多少实用信息。但就在这时，有人回答了我的问题——但只有一个人。他的解决方法是监听选项卡的状态更新，然后判断这次更新是否是通过点击“课程助教”选项卡造成的——如果是的话就把状态改回去，然后弹出菜单。可惜的是，他并没有用 Vue Router，因此对我的价值也不大。

不过，他这种方法给了我一些启发……

### 更多 Vuetify 源码和一些 Vue 特性

他的回答中提到了 `update:model-value`，这是文档中记录的一个事件（文档中称之为 `update:modelValue`）。`VTabs.tsx` 中确实定义了这个事件，但并没有触发，我通过研究发现触发逻辑写在 `useProxiedModel()` 里。

```tsx
  emits: {
    'update:modelValue': (v: unknown) => true,
  },

  setup (props, { attrs, slots }) {
    const model = useProxiedModel(props, 'modelValue')
    ...
    useRender(() => {
      ...
      return (
        <>
          <VSlideGroup
            ...
            v-model={ model.value }
            ...
          >
            ...
          </VSlideGroup>

          ...
        </>
      )
    })
    ...
  },
```

至于 `v-model` 这个属性，文档中也有多个示例使用，是用来绑定选项卡组状态的，其值为当前选中的选项卡。你可以为 `<v-tab>` 设置 `value` 属性，如果不设置的话，默认就是 0、1、2……

接下来，我通过查阅 Vue 文档了解了 [`v-model` 的底层原理](https://cn.vuejs.org/guide/components/v-model.html#under-the-hood)：原来 `v-model` 会展开为 `v-bind` 和 `v-on`！那么，如果我不用 `v-model` 这个简写，而是手动指定 `v-bind` 和 `v-on`，那我岂不是可以控制数据的更新了？

于是我给 `<v-tabs>` 加上了 `v-bind:model-value` 和 `v-on:update:model-value`，并对数据更新进行了拦截：如果新值为 2 就不更新，其他情况下正常更新。这可比等它更新完再改回去要方便多了。
```vue
        <v-tabs
          :model-value="selectedTab"
          @update:model-value="$event => $event !== 2 ? selectedTab = $event as number : undefined"
        >
```

以及在 `<v-menu>` 被点击时手动更新选项卡状态：
```vue
                <v-list-item
                  ...
                  @click="selectedTab = 2"
                />
```

最后要清理旧逻辑。“课程助教”选项卡不需要点击跳转了，也就不需要 `to` 属性了；`<v-menu>` 从也可以悬停弹出改为点击弹出了。`navigateTo()` 和那堆 CSS 都用不到了，可以删掉了。以下是第一版的代码：

[Vue Playground][2]


[1]: https://play.vuejs.org/#eNqFVttuG0UYfpVhg2RHyu46dpK2xgkuqBIgAVGJ4AIjNF6P7W12Z5aZWTuW5TuEWqpQoaoSJ6kSV3BVARcgJe3T1E25yivwz8wevU6IFHnnPx+/mbkVYp8694TVtvwwYlyiOfI4wZLcjiK0QEPOQlSbxKTWo4kAZ7EkPOE4rjnm7FT/05hIfzgr2lDnXFA5SI3gKHKMkx71GBUSJeJov2yuvqlF0gjr8A8UhJxYkLoJJT8nNgwhZDGV9doGuKptWltW4hIS70gSRgEYPFCCnYkNLP2ZHuw+5shjAeP7PSvifoj5rGclIkUhW/oyIAevHp++fP7LxV9nF2dPXz97cfHbw5dnDy/OTi/P7y+fP14+OH3997Pli68vz3/qeGxADuZz9KaO3RnGQXCI5RgtFh1X8y7PH3TcVQeZ5zRytEFOJKHCZzRj6sAk7osCJaUhySAVF5JYPvp++ceT5XffLB/9qRwB82r5iLMhEYJxUHz15MflP/eXP//67w9P/1cRC+ELial8e0Yw3282mruFAmYKIaExYhGhNqP2mE0IX5EppYw96U+w1F2ZI4gtEmhRMauV+rGUjCJ/AKJZLD0LTey+TxVRa4Ouadfy298hvY5r1KoxuKWJWUkiAOvIC8AN2O2P7BEnMyCOxtAgu7U+PqNl+2AXYhrqlPTBp0hVDEJD7WMyS8jqpCchP3e9wPeO4UzxxB9BaEesrlibwHPXZGA8rrYAyKoH5UZWmptQ8sGqFKQwsvkmKajJVcyy2hOfTLMAtf9UKrEB3yXzcBQe9yOJAkxHkLBUxRFExko0AyHY/7sGqAoAZCdg9VZBkMLmHEHpSmAHAikQJXC3n1usbwLbMHVvgPd5zzIzvYX0107P+iI3kbcERLGYUQ/VJziISRsJyX062kT7B2iukjbenCgW47omIBQBHrRRLd+h2pZhfBUTPmsbPfWngmkjbdiQFupnoaJFCE+xD5EkyeoUEHJdNIX5Z1MnYB6WgB4OJwHDA80H9Y5ram3q/oZto7GUkWi7LkTiHasNHQag7rHQxe6NW7uN7cathttsQDGazQaybdU+IWcatLpJ0WupkZhGxyOtnEB1t+XccLZvugPINKU5IdxQnhCqKRBPYis1i4QHgDEAykZWIFOSqT9QhdtrOs3d6ETnOyZqDdto56YmmAQzg3ApJOVfdx9+SELGZ++BB/jZSohXj5gymFj4jASQIjnEI5JdeAWavvjyiTxMMbYkX6KuaNxO8y5plKipRmmozeBCWQA8kxmrQWIMrFJCoUzFwBd66HLJ7Cooq5SjX1UqjHBRqZyAUiosT7Z/xYqb3RibZrTXdai+qX2bROFzoR8O5ERXbECGOA5S29B3U0nAngh6zyh0XzsAdNUMQJhsz3pW3mVF7llrpzmR6O44LaeRzXNCdYgI7T5nU6GHDWAjtd0FIXdAJpKxQAD8+Ve5qAh295w9Z9sN/L4L1l1Ya3JStp3s0zVBX7mCYFHb0oACxYSSSVg8OvRHKwVTbfUDwj+OFJyUC4cDwIoPNE3ymGSBeWPiHa+h3xMnJthDTqBSE1JIRmI+InCFK/adTz4CXCswQzaIA5C+hnmXCBbEKkYj9k5MBxB2QU5H+77uP0D0kbiTvrCyQHU1tLwu7rvXpJ6H23J2ClVcwYHKa7T4PFu5CEG7ggoV/eIrrapfwYiKfvE9BM9XeKlK2Donea7qG8hR9w48WOGlWvXwJdwQqmZguOXsOtsta/EffGxK/g==
[2]: https://play.vuejs.org/#eNqFVt1uG0UUfpXpNpIdKbvrOElLjZ26oEqABESlgguM6Ho9drbZ3VlmZp1Ylu8QaqlChapK/EmVuIKrCrgAKWmfpm7KVV6Bb2Z/vOt1wkUU7/n5zjfnnDlzpkbgeKF1XxgtwwsixiWZEpdTR9JbUURmZMhZQGrjmNZ6YWrAWSwpTzWWnXwu1Jn/pzGV3nBSxFDfC0MVIANxoshKgvRCl4VCktScdMpw9XVtkjGs4w8SQqxY0HpCZfGdYiSCgMWhrNeuIlRt3dgw0pA4eFvSIPIBuKsM22MTKv0z+zD7Dicu8xnv9IyIe4HDJz0jNSkamdKTPt19/eT41Ytfzv46OTt59ub5y7PfHr06eXR2cnx++mD+4sn84fGbv5/PX359fvpT22UDujudkjXN3RrGvr/nyH0ym7VtrTs/fdi2lwPkkTPm5Co9kjQUHgtzpSYmnb5YCAhpBQD1zbHjxxSHEdSnrqSDu06/ZxTtunE0AO6S+Rod01CSzi5Jf13pdEiT3CQFHFQsVTqChHHQR6+0SBwO6NAL6aAYpkA1I0skQxwb2Z0//n7+x9P5d9/MH/+pMgDlxfYRZ0MqBONwfP30x/k/D+Y///rvD88udiyJtDCgYbwkLWXYcaU3dqRugilBxEiQWaENCk79WEoWEm8AU0cIT0gnlD2DjM2+Fyqh9oZv0h3zb38H6baduFU52KUGXaLtA524PsIAtz8yR5xOIBztox/MrdX8Ei/TA25VS0BzqE+p9MQLyYQ6HGxXmbYO6CS1vMBAd+z/mKga3rPzTN1UATtrU+Uyu7faiR6hHqsUXdf33INyb6Mnm6tg7BW5TnKz3B4QV/qj2lypRCwu6HLpCnd5MWLUDF64JFPMHHv0MCeo42dWKQZ+l+DxKVzuRZL4TjhCAiRqhpspY2WaT2dOh6W5/vZi5uo6I1ef94xmo7nTMzaI/rXdM77IbMpZBVi9sQ6Itp3ETnhcMU2yL2UkWraNiroHbEz50GeHlssC27Gv39hpbDZuNOxmA3GazQYxTXUcISd6unVTtrUMJA6jg5F2Tmd6d8u6bm2+ZQ9Qq0xmBXjKXCHUkcAnxcKoTzK68pX7kAaMT94DCv5tpMI7yQtXyJKZv3J5Jj+jPvjQPWdE82esINPPGYik1nvZgCrZl6RLHrey21DyKEkzj6w2mmRSQLQJZhRekhap2TUcjAE1xFRulYjPNsqW+Rwtu5TZLzvl97bsVD6AckITlajy/HVPMl6fKuD9pBitVRWqr+vYyUHxc6bXAXqkM4YXxon9DBt1TzKJixOh9ixE9XUAzCKtwPVoES1RskWVlbhnrGy91KK7bW1Zjbz5UqlFRWD2OTsUutlwfTLsLozsAR1LxnyBu+tdFKJi2L1mXbM2bd/r20C38XrQozJ22vyXkL7wvgBRYymoGZKJlEmB+gy90VLCVFk9n/KPI4kVo5w4x8fF/kDLJI9pTszdp+7BCvl9cZSQ3eMUmRrTwmGkw0cUL6VS3/7kIyw1BSV2kdiH9SXKO1QwP1YcE7N3sHeAdsFOs31f198LR3fF7WxvyonqbGh7ndx3Lzn6gu6WtV3I4tIcqOyYxd1maYrDuzIVKv7FFafqX5kRFf/i2oGlFPunxK2z0iX0q5jyiaUeA6yh2D+rEb7EOFc5A/CWtWNtbhmz/wBoFR1t
