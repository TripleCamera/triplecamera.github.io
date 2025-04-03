---
title: 编程随笔（四）
date: 2025-03-19
updated: 2025-04-03
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

## 第二版
看上去非常好！可惜还有一点美中不足：如果先进入助教列表页面，然后刷新，那么 slider 会回到“发展历史”下方，而不是继续停在“课程助教”下方。

>   在 Vue Playground 中，我们使用的是 [Memory 模式](https://router.vuejs.org/zh/guide/essentials/history-mode.html#Memory-%E6%A8%A1%E5%BC%8F)，因此当前路由不会记录在 URL 中。当你刷新页面时，你会回到初始路由 `/`。若要改变初始路由，请在 `router.ts` 中创建 `router` 后加入如下代码：
>   ```ts
>   router.push('/assistant?year=2025');
>   ```

在着手修复这个小 bug 之前，不妨让我们先回头看一下第一版的改动。我们可以使用 `v-model` 来将 `<v-tabs>` 的状态双向绑定到 `selectedTab` 上。`v-model` 会被展开为 `v-bind:model-value` 和 `v-on:update:model-value`，前者将 `selectedTab` 的值传入 `<v-tabs>`，后者在 `<v-tabs>` 更新状态时将新值同步到 `selectedTab`。即前者读取 `selectedTab`，后者写入 `selectedTab`。我们所作的修改是：
 -  拦截正常写入逻辑。当 `<v-tabs>` 欲写入的新值为 2 时，不写入。
 -  额外新增写入逻辑。当点击菜单中的菜单项时，写入 2。

目前的问题是缺乏初始的写入逻辑。那么最简单的解法就是在初始化时根据当前路由设定初始值。

### 次优解
只需要在 `app.vue` 的 `<script setup>` 中添加如下代码：
```ts
import { useRoute } from 'vue-router';
const route = useRoute();
switch (route.path) {
  case '/':
    selectedTab.value = 0;
    break;
  case '/professor':
    selectedTab.value = 1;
    break;
  case '/assistant':
    selectedTab.value = 2;
    break;
  default:
    selectedTab.value = -1;
    break;
}
```

即可正确初始化 `selectedTab`。注意在 `<script setup>` 中不能使用 `$route`，需要通过 `useRoute()` 来获取 route 对象。

### 最优解……？
虽然问题解决了，但是我还想介绍一种更简单的方法。

我在 StackOverflow 上搜索如何获取当前路由的时候，看到[这个问题](https://stackoverflow.com/q/53126710)以及其下的许多回答都提到了 [计算属性（`computed`）](https://cn.vuejs.org/guide/essentials/computed)。于是我去了解了一下计算属性，然后发现之前的逻辑完全可以使用计算属性重写。

我们将 `selectedTab` 改为计算属性实现，让其在路由改变时自动变化。这样就不需要再去手动更新它了，`<v-tabs>` 的 `@update:model-value` 和 `<v-list-item>` 的 `@click`，都可以删掉了。

以下是重写后的 `<script setup>`：
```ts
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const years = ["2025", "2024"]
const selectedTab = computed(() => {
  switch (route.path) {
    case '/':
      return 0;
    case '/professor':
      return 1;
    case '/assistant':
      return 2;
    default:
      return -1;
  }
});
```

总揽全局，我们发现：点击按钮时路由更新，路由更新触发 `<v-tabs>` 组件状态更新，组件状态更新触发 slider 更新。现在我们所做的，就是重写“路由更新触发组件状态更新”这一步骤。

最后我们修复两个小 bug：
 -  点击“课程助教”时菜单栏的位置和选项卡略有重叠，这是 `<v-tab>` 嵌套 `<button>` 搞的鬼，把 `<button>` 去掉即可。
 -  给“课程助教”右侧加个下三角图标。

结果没想到，修了这两个 bug 又引入了新的 bug？！

现在点击“课程助教”时，slider 会直接滑动到“课程助教”下方。这使我百思不得其解。我用 Vue DevTools 看了一下，发现在教师团队页面点击“课程助教”选项卡时，虽然 `<VTabs>` 的 `modelValue` 属性仍然为 `1`，但 `<VSlideGroup>` 的 `modelValue` 属性却已经变成了 `2`。这是为什么？？

我不由得对之前没有弄懂的 `useProxiedModel()` 产生了怀疑。但是由于逻辑实在是太复杂了，我让 Copliot 解释这个函数的内容。

<details><summary>Copilot 的回答：（点击展开）</summary>

>   这段代码定义了一个名为 `useProxiedModel` 的 TypeScript 函数，主要用于在 Vue 3 的组合式 API 中处理受控和非受控的双向绑定模型。它通过代理模式简化了组件属性的管理，尤其是在需要支持 `v-model` 或类似功能的场景中。
>   
>   ### 函数签名
>   `useProxiedModel` 是一个泛型函数，接受以下参数：
>   1. **`props`**: 一个对象，包含组件的属性。
>   2. **`prop`**: 一个字符串，表示需要代理的属性名。
>   3. **`defaultValue`**: 可选参数，表示属性的默认值。
>   4. **`transformIn`** 和 **`transformOut`**: 两个函数，用于在内部值和外部值之间进行转换，默认是直接返回值。
>   
>   ### 内部变量
>   - **`vm`**: 通过 `getCurrentInstance` 获取当前组件实例，用于访问组件的虚拟节点和事件。
>   - **`internal`**: 一个 `ref`，存储内部状态。如果 `props[prop]` 有值，则使用它，否则使用 `defaultValue`。
>   - **`kebabProp`** 和 **`checkKebab`**: 用于处理属性名的驼峰式和短横线式写法的兼容性。
>   - **`isControlled`**: 一个 `computed` 计算属性，用于判断当前属性是否受控。受控属性意味着它由父组件通过 `v-model` 或 `onUpdate` 事件进行管理。
>   
>   ### 核心逻辑
>   1. **受控属性检测**:
>      - 如果属性是受控的（即父组件通过 `v-model` 或 `onUpdate` 事件管理），`isControlled` 会返回 `true`。
>      - 受控属性的值直接来源于 `props[prop]`，而非内部状态。
>   
>   2. **非受控属性的同步**:
>      - 使用 `useToggleScope` 和 `watch`，当属性是非受控时，监听 `props[prop]` 的变化，并将其同步到 `internal`。
>   
>   3. **`model` 的定义**:
>      - `model` 是一个 `computed` 对象，提供 `get` 和 `set` 方法。
>      - `get` 方法根据 `isControlled` 决定返回外部值（`props[prop]`）还是内部值（`internal`），并通过 `transformIn` 转换。
>      - `set` 方法用于更新值。它会通过 `transformOut` 转换后，更新内部状态或触发 `update` 事件通知父组件。
>   
>   4. **`externalValue` 的定义**:
>      - 使用 `Object.defineProperty` 为 `model` 添加一个只读属性 `externalValue`，直接返回当前的外部值或内部值。
>   
>   ### 返回值
>   函数最终返回 `model`，它是一个响应式对象，既可以作为受控属性的代理，也可以作为非受控属性的内部状态管理工具。
>   
>   ### 应用场景
>   `useProxiedModel` 适用于需要支持双向绑定的 Vue 组件开发。它通过统一的接口处理受控和非受控属性，简化了组件逻辑，同时提供了灵活的值转换功能（`transformIn` 和 `transformOut`），适合复杂的场景。

</details>

豁然开朗了。由于我们删掉了 `<v-tabs>` 的 `@update:model-value`，导致 `useProxiedModel()` 认为 `<v-tabs>`“不受控”，于是只会将外部 `modelValue` 的更新单向同步到内部，而内部 `modelValue` 的更新则不会同步到外部。这就导致内外 `modelValue`“脱节”。

那么该如何解决呢？我们可以向 `<v-tabs>` 传入一个空的 `@update:model-value`，但那样只会让代码变得更乱。如果我们能将读写逻辑封装在一块儿就好了。——之前研究计算属性时瞥到过的[可写计算属性](https://cn.vuejs.org/guide/essentials/computed.html#writable-computed)就派上用场了。

### 成功！

以下是最终版的 `selectedTab`：
```ts
const selectedTab = computed({
  get() {
    switch (route.path) {
      case '/':
        return 0;
      case '/professor':
        return 1;
      case '/assistant':
        return 2;
      default:
        return -1;
    }
  },
  set() {
    // Do nothing.
  }
});
```

以下是最终版的代码：

[Vue Playground][3]

## 后记
这次探索真的非常不容易！虽然最后的代码实现看上去并不复杂，但是为了写出它们，我阅读了 Vuetify 源码，并学习了 Vue 的各种机制。由于我对 Vue 的理解尚浅，缺乏实践经验，导致研究的过程更加的冗长。

但是，这次探索也非常有意义。它让我对 Vue 和 Vuetify 有了更深入的理解。在此之前，我只会“搭积木”似的将各种组件“缝”在一起，这是我第一次对组件进行深入的自定义。

在探索初期，我曾让 Copilot 帮我实现需求，但它没能实现出来。那时 DeepSeek 刚刚火起来，可惜我后来并没有尝试让 DeepSeek 实现，之后可以考验一下它。

另外如果你对我的研究过程或实现方式有任何的建议，欢迎在讨论区提出。谢谢！


[1]: https://play.vuejs.org/#eNqFVttuG0UYfpVhg2RHyu46dpK2xgkuqBIgAVGJ4AIjNF6P7W12Z5aZWTuW5TuEWqpQoaoSJ6kSV3BVARcgJe3T1E25yivwz8wevU6IFHnnPx+/mbkVYp8694TVtvwwYlyiOfI4wZLcjiK0QEPOQlSbxKTWo4kAZ7EkPOE4rjnm7FT/05hIfzgr2lDnXFA5SI3gKHKMkx71GBUSJeJov2yuvqlF0gjr8A8UhJxYkLoJJT8nNgwhZDGV9doGuKptWltW4hIS70gSRgEYPFCCnYkNLP2ZHuw+5shjAeP7PSvifoj5rGclIkUhW/oyIAevHp++fP7LxV9nF2dPXz97cfHbw5dnDy/OTi/P7y+fP14+OH3997Pli68vz3/qeGxADuZz9KaO3RnGQXCI5RgtFh1X8y7PH3TcVQeZ5zRytEFOJKHCZzRj6sAk7osCJaUhySAVF5JYPvp++ceT5XffLB/9qRwB82r5iLMhEYJxUHz15MflP/eXP//67w9P/1cRC+ELial8e0Yw3282mruFAmYKIaExYhGhNqP2mE0IX5EppYw96U+w1F2ZI4gtEmhRMauV+rGUjCJ/AKJZLD0LTey+TxVRa4Ouadfy298hvY5r1KoxuKWJWUkiAOvIC8AN2O2P7BEnMyCOxtAgu7U+PqNl+2AXYhrqlPTBp0hVDEJD7WMyS8jqpCchP3e9wPeO4UzxxB9BaEesrlibwHPXZGA8rrYAyKoH5UZWmptQ8sGqFKQwsvkmKajJVcyy2hOfTLMAtf9UKrEB3yXzcBQe9yOJAkxHkLBUxRFExko0AyHY/7sGqAoAZCdg9VZBkMLmHEHpSmAHAikQJXC3n1usbwLbMHVvgPd5zzIzvYX0107P+iI3kbcERLGYUQ/VJziISRsJyX062kT7B2iukjbenCgW47omIBQBHrRRLd+h2pZhfBUTPmsbPfWngmkjbdiQFupnoaJFCE+xD5EkyeoUEHJdNIX5Z1MnYB6WgB4OJwHDA80H9Y5ram3q/oZto7GUkWi7LkTiHasNHQag7rHQxe6NW7uN7cathttsQDGazQaybdU+IWcatLpJ0WupkZhGxyOtnEB1t+XccLZvugPINKU5IdxQnhCqKRBPYis1i4QHgDEAykZWIFOSqT9QhdtrOs3d6ETnOyZqDdto56YmmAQzg3ApJOVfdx9+SELGZ++BB/jZSohXj5gymFj4jASQIjnEI5JdeAWavvjyiTxMMbYkX6KuaNxO8y5plKipRmmozeBCWQA8kxmrQWIMrFJCoUzFwBd66HLJ7Cooq5SjX1UqjHBRqZyAUiosT7Z/xYqb3RibZrTXdai+qX2bROFzoR8O5ERXbECGOA5S29B3U0nAngh6zyh0XzsAdNUMQJhsz3pW3mVF7llrpzmR6O44LaeRzXNCdYgI7T5nU6GHDWAjtd0FIXdAJpKxQAD8+Ve5qAh295w9Z9sN/L4L1l1Ya3JStp3s0zVBX7mCYFHb0oACxYSSSVg8OvRHKwVTbfUDwj+OFJyUC4cDwIoPNE3ymGSBeWPiHa+h3xMnJthDTqBSE1JIRmI+InCFK/adTz4CXCswQzaIA5C+hnmXCBbEKkYj9k5MBxB2QU5H+77uP0D0kbiTvrCyQHU1tLwu7rvXpJ6H23J2ClVcwYHKa7T4PFu5CEG7ggoV/eIrrapfwYiKfvE9BM9XeKlK2Donea7qG8hR9w48WOGlWvXwJdwQqmZguOXsOtsta/EffGxK/g==
[2]: https://play.vuejs.org/#eNqFVl9vG0UQ/yrbayQ7Uu7OsZOWGjt1QZUACYhKBQ8Y0fN57Vxzd3vs7jmxLL+iQlUqhCqBQKrEEzwh4AUphU9TN/SpX6G/2/vj2zsnfYjim/3NzG9nZmdmYQSOF1r3hdE1vCBiXJIFcTl1JL0VRWRJJpwFpDGLaWMYZgDOYkl5dmLZ6ef6ONf/NKbSm8zLNpLvNTBxkBtxoshKnQxDl4VCkgxO+rq55raC5Ayb+IOEECsWtJlSWX9nNlJBwOJQNhtX4aqxbewYmUtcvCdpEPkweJAAezMTR+pn/mGOHE5c5jPeHxoR9wKHz4dGBimDTOlJnx68+OHR839/Of/77Pzs6f9//Hf+28PnZw/Pzx69evag57IxPVgsyJYia01i3z905BFZLnu2Onv17JsCJ6hPXUnHd51Rl0Cp9K0p9OwqhYJbfjdylZ5KGgqPhcWhoi6dkVgLCOkGMOqbM8ePKa5bcjk0yrhBHI1htwLfojMaStI/INmvK/0+aZObGvV+fugIEsbBCNXUJXE4phMvpOOymxLVnCyRDH5sxH/1+PvVn09W3329evxXEgEcXoyPOJtQIRiH4osnP63+ebD6+deXPz69WFETKWFAw7gi1SLsuNKbOVKVyYLAYyTIslQoJaVRLCULiTcG1BHCE9IJ5dAgM3PkhYlQaUM3rZ/Vt7+DdM9O1eocbK2EK7R9WCeuDzewO5qaU07nEE6PUA9mZzO/VMv0YLd+SkBzom6ZnBMvJHPqcLDdBO0e03mGvACgKvYNkCSH9+wiUjcTh/2tRaKyvLdZiZ4iH5sOBq7vucd6baMm25vM2BtincamWh4Q1+qjXlyZRKwfaDV1pbe8bkJJl16rpH3OnHn0pCCo/OeozAZ+a+bxKVzuRZL4TjhFACRyhpcp4wRa9G9OJ1rnf3vdlVWeEavPh0a71d4fGjtE/dobGl/kGD2qMNZsbcNEz059pzyumCY5kjISXdtGRt1jNqN84rMTy2WB7djXb+y3dls3Wna7BT/tdouYZnIdIeequw0yto3cSBxGx1OlnHX9Qce6bu2+ZY+Rq1xmBRh2rhDJlcAns4VhkEZ04xz8kAaMz9+DFfzbyYR30hlYipJZzMEikp9RH3zooTOlxaArydTAA5EMfZg3KA2vSSsat/LXoGlo0lwjz40imSYQZYIehdHTJQ27gYsxWA3Rlbsa8eWOjiz6qK6is68qFe9WV9IvkCihiDSqvJj/acSbi8TwUZqM7qYMNbeV7/Si+LlUCwM9VRHDhHFiP7eNvKeRxMOJkHsWIvvKAXqROsDzwNxNH9jQWGc5EQ+NjaWXIQZ7VsdqFcWXSS0qAnPE2YlQxYbnk9seAGSP6Uwy5gu8Xe8iFzXg4Jp1zdq1fW9kw7qN6UFPddtZ8V9C+sL3AovKVmJqiWAiZFIgPxNvWglYklbPp/zjSGLF0APn+HjYHyiZ5DEtiLlH1D3eIL8vTlOyh5wiUjNauox0+JRiUibHtz/5CEtN6RC7SOwDfcnhHSqYHyccU9g72DtAu4RTbN9X+ffC6V1xO9+bCqIqGgqvgvvuJVdf0+1Ye6UoVvpAbQst7zaVLg7tWleo6ZdXnLp+rUfU9MtrB9ZR7J4Sr87KttavYsrnVjIMsIZi/6x7+BLtPIkZDHesfWu3YyxfA7rhJo0=
[3]: https://play.vuejs.org/#eNp9Vt1uG0UUfpVhW8mOlN114qShxgkuUAmQgKhUcIERXa/H9ja7M8vMrBPL8i0qVKVCqBIIpEpcwRUCbpBSeJq6gau+Qr+Z/bedXCTeOec7Z77zM2dmbkVewJz70upYQRRzocic+IJ6it6KY7IgI8Ej0pgmtNFnGUDwRFGRaRw3XZbq3P6ThKpgNKv60OsSqDfInXhx7KSb9JnPmVQkg5PDurvmloHkDJv4g4QQJ5G0mVIp15mPVBDxhKlm4xq2amxZ21a2JQLvKhrFIRweaWB3akNlPvOFPfAE8XnIxWHfikUQeWLWtzJIFWSrQIX06MX3j57/8/PFX+cX50//+/3fi18fPj9/eHH+6OWzB12fD+nRfE6uG7LOKAnDY09NyGLRdY3u5bOvC5ykIfUVHd71Bh0Co8o637xq13VXmRQU8xDJNXqmKJMBZ4XSRKC8gSRTO4KrEFFWdyojLbFEcaBc6JaPv1v+8WT57VfLx39qAlBejo8FH1EpuYDhiyc/Lv9+sPzpl/9/eHqJYURZUpPVIvF8FUw9ZaoyJ3AdS7JYYVthMLUHARuaCgLZtwhSRdnQDtBwkEbDwOxnD/kpg5e0cMtvfgPPTfTg1601Tm3DMEAP+6EnJVwPxvZY0BmE4wmSb7c3k9Q2dgCfoDoyUZlFwMiMekIz7pzQWSbWK1Pj6lrn+J6LTeHJY+pNbXd4fa71i3tA0DPkjLhrcaR717MP4Ur6syzIsqtWE1BpwPIA6QlTmqRn1J4G9LQgYvbKUZkPfNfcYyl9EcSKhB4bI06lEyKpSjS0nD08irHBsDa63qgAMBfuaApVgJ3NMODy8WMkGD45vLkFZaoyxYDqs76129rd71vbxHzt9a3Pc0zl+OgJlpFqznWAY6qaW8R8EiJPA+VPSDq6nBiToFAR4nuSkobb6JQ1EAhYMNICmxqmOFgbwDur4KJBNoB3C/CQjrwkVOsQO3e40D+Lbf0fhSiDcl3yDieMq0nAxo4B9dlCZ7DrpkVMC/qabZOJUrHsuC74+Cd8SsUo5KcOMuZ67sHN/dZO62bL3W0h0bu7LWLbui+kmpnZ1suq2sidJCw+GRvjbPT32s6Bs/O6O0S8ucyJcOP5UupyX+Ghh4HgjjhTvQNnz9k7cGHiRmhGEXjhkMpgzPTkkMaViSxjhbsl7aeN1+oHNOJi9i744Gc7E5oWE5taUucp8/ApDcGLHntjWtybFZm5P8tOP84booavSVcsbuVdUbOoSXOL2ilJzwKKjBmM/u3ojkVg6HnOKFOdGvG0W0pk2bc1kzr7VaOyf2tG9QC0Ec5jjaoonhNpxtMDOUmL0dlUoeaW2TsNFJ8L8/5Ag2cljhM5aVYYpSNXz4WG7vc+o2cmudlhyszQImnSMfZitAlnaBTDBcPcKDDccOOnx6lvlQ2hxX1rY79niN6e03ZaRcdnUofKyB4IfipNX2Jo5b57ALlDOlWchxKTN7hsizVg74Zzw9lxw2DgwruLy5We1X1nJ+4K0pceUng0vvLpgZQpiVKOgvFKwnQHBCEVH8UKr5p64rwQ0+R9I1MioQUxf0L9kw3y+/IsJXssKDI1pZVglCcwulP17Y8/xDuqosS7KQmBvkJ5h0oeJppjCnsrYUPQruAM2/dM/TE478rb+VOtIFoOXJPct68IvaTbdvYqWVwZGWvv3+p7buUOhvXaAFmzrz7r1u3XxsmaffXdhYcwXr24RqSTvZe/TKiYOfqQ4eWLJ+/6Dl/gDtE5g+O2s+/stK3FK+rbaxs=
