---
title: 编程随笔（一）
date: 2023-02-25
updated: 2023-06-10
categories:
- 编程随笔
---
昨天（2月24日）晚上，我在写作业之余，去隔壁宿舍逛了逛。

刚一进门，原汁就向我求助。原来他在上学期的 C 语言课上学着写了一段生成全排列的代码，但是始终没有搞清楚代码的工作原理。代码如下：
``` c
#include<stdio.h>

void f( int i ); // i 是正在执行的位数
int num[10];     // 存放每次排列
int a[10];       // 统计该数字有没有被用过

int n;  // n 开成全局变量

int main()
{
	scanf("%d", &n);
	f( 1 );
	return 0;
}


void f( int i )
{
	if( i == n+1 ){
		for( int cnt1=1; cnt1<=n; cnt1++ ){
			printf("%d ", num[cnt1]);
		}
		printf("\n");
		return;
	}
	
	for( int cnt=1; cnt<=n; cnt++ ){
		if( a[cnt] == 1 ){  // 已经使用过这个数字
			continue;
		}
		num[i] = cnt;   // 将这个数字存入答案数组
		a[cnt]++;       // 记录已经使用过这个数字
		f( i+1 );       // 进行下一步递归
		a[cnt] = 0;     // 回溯后将 a 数组归零
	}
	return;
}
```
输入数字 *n*，这个程序就能生成 1&ndash;*n* 的全排列。

原汁不明白，为什么如此简洁的 `f` 函数能够不重不落地生成全排列。我为他画了树状图，演示递归与回溯是如何进行的；可他还是不理解，于是自己亲手模拟了一遍。后来他又用 Dev-C++ 的调试功能监视了一些变量的变化，最后终于明白了。

这时我想到，我的电脑上装有 VSCode，里面的调试功能可能更高级一些，于是我用我的电脑调试了一遍：果不其然，VSCode 支持显示函数调用栈，清晰地向我们展示了递归与回溯的流程：（注：由于 gdb 不支持中文文件名，我将文件名换成了英文。）

![调试界面](/images/programming-1-debug.png)

隔壁宿舍的高子也在用 VSCode，见状直呼牛逼。他也想用 gdb，但是当我帮他启动调试，向控制台中输入 `4` 的时候，却直接卡住了，没有任何反应。我按下 Ctrl+C 中止了调试，之前输入的内容立刻显示了出来。我上网查了许多方法，改了 VSCode 的配置，怎么都没有用。眼看时间已经过去了半个小时，问题还是没有解决，我想要放弃了。

最后，我对比了一下我和他屏幕上输出的调试信息，结果发现了端倪：

我输出的前两行调试信息如下：
```
=thread-group-added,id="i1"
GNU gdb (GDB) 11.2
```

再看高子的，如下：
```
=thread-group-added,id="i1"
GNU gdb (GDB) 7.6.1
```

好老喔，这么老的版本还支持吗？我去查了 [VSCode 的官方教程](https://code.visualstudio.com/docs/cpp/config-mingw)，上面说的是“Get the latest version of Mingw-w64…”，看来最好还是用最新版吧。

高子正在用的是 MinGW，而 MinGW 早已停止了更新。我帮他下载了 [mingw-w64](https://github.com/niXman/mingw-builds-binaries)（注：这是精简包，仅包含必要的功能。），解压出来，并修改了 PATH 环境变量。由于编译器路径写到了他的 VSCode 配置里，我又删掉了配置，这样 VSCode 才会在 PATH 中重新搜索。

至此，VSCode 调试环境的搭建终于成功了。有了 VSCode 强大的调试功能，高子的编程之路更进了一步。
