---
title: 追本溯源：北航 MOS 操作系统的历史
date: 2025-05-01
updated: 2025-08-20
tags:
---

我们都知道，北航的 MOS 操作系统是从 MIT JOS 移植过来的。（如果你还不知道这一点，说明你既没有认真读过[指导书](https://os.buaa.edu.cn/public/guide-book.pdf)、[宣发页](https://os.buaa.edu.cn/team/)等官方资料，也没有认真看过[知乎](https://www.zhihu.com/question/322261810)等非官方资料。）

但是我们都不知道一件事：MOS 到底是衍生自 JOS 哪一年的版本？毕竟指导书里没有写，学长也没有说。我曾问过高阶助教，高阶说他也不知道，还说他现在并没有兴趣去考证这个，只想维护好现在的 MOS。

那么为什么我要去问高阶，又要费大力气去考证这个呢？原因如下：

## 缘起
为什么我会想到考证 MOS 的历史呢？这是因为，在我时隔一年重新完成课下任务的过程中，由于我对 MOS 理解的加深，越来越多的疑惑逐渐浮出水面。下面我举两个例子：

第一个例子是 `KADDR` 宏，这个宏的作用是将物理地址转换为 kseg0 虚拟地址，便于在内核态直接访问：
```c
// translates from physical address to kernel virtual address
#define KADDR(pa)                                                                                  \
	({                                                                                         \
		u_long _ppn = PPN(pa);                                                             \
		if (_ppn >= npage) {                                                               \
			panic("KADDR called with invalid pa %08lx", (u_long)pa);                   \
		}                                                                                  \
		(pa) + ULIM;                                                                       \
	})
```

不过这个宏有一些问题：它没有对传入的 `pa` 参数作类型转换。我在写 Lab2 的时候，就曾经往里面传了个 `Pte *` 类型的值，结果 `KADDR` 就直接对指针做了加法，导致计算结果发生了溢出。在我翻看我去年的代码时，才发现我去年在同样的地方被坑过一次，甚至还发了篇帖子求助助教。

于是我和助教们讨论了一下。如果 `KADDR` 是一个函数，那它必定会对传入的参数进行类型转换；但 `KADDR` 是个宏——于是这就成为了一个暗雷。

第二个例子是 `va2pa` 函数，这个函数的作用是查询页表，将虚拟地址转换为物理地址：
```c
static inline u_long va2pa(Pde *pgdir, u_long va) {
	Pte *p;

	pgdir = &pgdir[PDX(va)];
	if (!(*pgdir & PTE_V)) {
		return ~0;
	}
	p = (Pte *)KADDR(PTE_ADDR(*pgdir));
	if (!(p[PTX(va)] & PTE_V)) {
		return ~0;
	}
	return PTE_ADDR(p[PTX(va)]);
}
```

但是这个函数有个问题：它最后没有加上页偏移。于是有同学在讨论区里发帖询问这样设计的用意。高阶助教也开了个 issue，希望把这个函数移动到测试程序中。

于是我对 MOS 的代码质量产生了担忧。另外，这一届的同学们非常热情，揪出了 MOS 操作系统的许多 bug。这加深了我对 MOS 代码质量的怀疑。

除此之外，由于 MOS 代码较为晦涩难懂，加上注释全部由英文写成，同学们在阅读代码的过程中遇到了很大阻力，于是有些同学向代码中补充注释。甚至还有人给每一行都加上注释（我个人感觉这样做无异于阐释经文），还有人将代码中的英文注释翻译成中文。

我不禁感到疑惑：**MOS 的代码质量为何如此之差**？MIT JOS 的代码质量本来也这样差吗？还是说在移植的过程中出现了质量下降的问题？

## 前置知识
我们都知道 MOS 是从 MIT JOS 移植过来的，但这还远远不够。我在去年和今年期间搜集到了一些有关资料，为考证工作带来了便利。下面就让我向你介绍一些前置知识。

### 知乎

### 旧版指导书
每年都会发布新的指导书，课程组也提醒我们不要用旧版指导书。在去年做实验的过程中，我就四处搜寻往届指导书。我从往届的 GitHub 仓库里翻到了学长顺手传上去的指导书，有 2023 年、2021 年、2019 年的版本。但紧接着，我找到了[旧版指导书的源代码](https://github.com/SivilTaram/BUAAOS-guide-book)！

根据 README 的介绍，他们于 2015 年 7 月决定要编写指导书，2016 年 3 月开始编写，直到 2018 年 3 月改为自建 GitLab 托管。Releases 中有编译出来的 PDF，最后一版 v2.1.4 发布于 2017 年 10 月 10 日。

这版指导书与我们现在使用的指导书有很大不同：书名叫《小操作系统实验指导书》；没有“引言”部分，取而代之的是“编者序”~~（非常中二）~~、“教师寄语”，以及一张大事表，上面记载着操作系统实验课程自 1999 年以来的发展。

<figure>
  <img src="/images/mos-guide-book.png" alt="旧版指导书中的“MIPS 操作系统实验大事表”" style="max-height: 12em">
  <figcaption>旧版指导书中的“MIPS 操作系统实验大事表”</figcaption>
</figure>

现在版本指导书的“引言”部分，以及去年新增的宣发页，都包含了旧指导书的部分内容，但略去了一部分细节。

<figure>
  <img src="/images/mos-course-team.png" alt="操作系统实验课程宣发页（截取于 2025 年 5 月 1 日）" style="max-height: 18em">
  <figcaption>操作系统实验课程宣发页（截取于 2025 年 5 月 1 日）</figcaption>
</figure>

### 旧版代码
对于操作系统实验这门课来说，GitHub 上最有价值的并不是指导书，而是学长们的代码！大多数同学在完成实验的时候，或多或少都参考过学长的代码。值得一提的是，考虑到大家课下大量借鉴学长的代码，课下题目约等于送分，加上部分学长代码有 bug，会在课上考试时爆雷，因此课程组在今年开源了 MOS 操作系统代码（含答案），大家终于可以参考 100% 正确的官方代码了！

大家在参考学长代码的时候，肯定是越新越好。因为 MOS 每年都有一些小改动，太旧的代码可能没有办法使用。但我为了考古，肯定是越久越好。就这样，在花费了一些时间翻找后，我居然找到了一份 2015 年的 MOS 源码！源码仓库的作者也是旧版指导书仓库的作者，他叫 [SivilTaram](https://github.com/SivilTaram)，根据仓库中遗留的线索推断，应该就是大事表中所说的刘乾学长。下面让我们来好好研究一下这个仓库：

 -  首先，仓库的名字叫做 Jos-mips，说明当时还没有 MOS 这个名字。
 -  仓库的结构和现在的 MOS 很像，但也有一些不同：比如说，当时并没有 `kern` 目录，那内核代码应该放在哪里呢？
 -  多个 Makefile 中都有 Zhu Like 的版权声明，时间为 2007 年，根据大事表推断，应该是参与 MIPS 移植工作的朱沥可学长。
 -  `mips_init` 函数已经成形了。
 -  现在的 `vprintfmt` 函数，当时叫做 `lp_Print`，意义不明。

这一天是 2025 年 4 月 8 日，找到这个仓库为我的考证工作打下了坚实的基础。

### 【内部资料】指导书与代码提交记录
由于我有幸担任了 2025 年操作系统实验助教，因此可以接触到内部资料：指导书和 MOS 两个仓库的提交记录。这些内部资料为考证工作带来了方便，但没有它们也能得出下文的结论。

 -	指导书在 v2.1.4（2017 年 10 月 10 日）及以前提交记录与 GitHub 上的提交记录完全重合。
 -	MOS 提交记录始于 2022 年 9 月 4 日。尚不清楚在此之前是使用何种方式分发代码的。

## MIT 操作系统课程
首先，建议阅读一下 [CS 自学指南（csdiy.wiki）](https://csdiy.wiki/%E6%93%8D%E4%BD%9C%E7%B3%BB%E7%BB%9F/MIT6.S081/) 对 MIT 6.S081（原名 6.828）这门课程的介绍。

由于我并不是 MIT 的学生（笑），所以只能通过翻阅官网的方式了解这门课程的历史。幸好官网对校外是完全开放的，我不仅能查阅课程资料，还可以下载各个 Lab 的代码。

在春季学期到暑假的这段时间，我将之前下载的各种资料整理了一下，准备上传到 Internet Archive。由于资料还没有整理完成，所以分了几批上传。但是 <abbr title="Internet Archive">IA</abbr> 的网页上传工具实在是太难用了，上传时不能新建文件夹，只能上传后再移动，在此过程中系统自动生成的文件也删不掉，于是我只好新建了一个 GitHub 仓库来暂存各种资料，并不定期同步到 <abbr title="Internet Archive">IA</abbr>。你可以前往 [Internet Archive](https://archive.org/details/mit-6.828-lab-files) 或 [GitHub](https://github.com/TripleCamera/mit-6.828-lab-files) 来查阅我整理的资料。我还请求第三方为它们做了备份，所以有了双重保险，不用怕它们丢失了。

---

最开始 MIT 并没有操作系统课。2002 年，MIT 开设了 [6.097: OPERATING SYSTEM ENGINEERING](https://pdos.csail.mit.edu/archive/6.097/) 课程。这门课程的任务是学习 V6 操作系统（后来换成了 xv6 操作系统），并自己编写一个操作系统（后来被命名为 JOS）。

注意从 2003 到 2002 的链接有点隐蔽，你需要仔细观察才能找到它。

### 2003 - 2018
### 2019 - 现在

## MOS 断代工程
我们已经准备好了 MIT 6.828 的历届代码，以及一份 2015 年的 Jos-mips 代码。接下来，我们就可以开始为 MOS 做一次“断代”了。

根据指导书中的大事表，课程组在 2007 年发现、完成并开始移植 JOS，到 2009 年完成移植。那么移植的到底是 2007 年还是 2009 年的版本呢？我决定把 MIT 每一年的代码都拿出来比较。

由于 Makefile 中有 `Copyright (C) 2007` 字样，于是我从 2007 年开始比较。我从 MIT 6.828 官网下载了 2006 年和 2007 年的代码。（注：按理来说应该下载 2007 年和 2008 年的代码，但我脑抽了。）非常可惜的是，这两年的 Lab5 和 Lab6 代码都缺失了。我只好用 Lab4 的代码进行对比。

首先，运行如下命令：

```console
$ diff -ru 2006/lab4 2007/lab4 > 2006-2007-lab4.diff
```

得到一份 2006 年和 2007 年的 Lab4 差异。接下来，我们将这些差异与 Jos-mips 逐一比较：
 -	对于 2007 年新增的内容：
	 -	如果 Jos-mips 中也有，说明 Jos-mips 使用的<u>很可能</u>是 2007 年或更晚的版本。
	 -	如果 Jos-mips 中没有，不能说明什么，因为可能本来就没有，也可能是移植的过程中删掉的。
 -	对于 2007 年删除的内容：
	 -	如果 Jos-mips 中还存在，说明 Jos-mips 使用的<u>很可能</u>是 2006 年或更早的版本。
	 -	如果 Jos-mips 中也没有，不能说明什么，理由同上。
 -	对于 2007 年修改的内容：
	 -	如果 Jos-mips 中与 2006 年版一致，说明 Jos-mips 使用的<u>很可能</u>是 2006 年或更早的版本。
	 -	如果 Jos-mips 中与 2007 年版一致，说明 Jos-mips 使用的<u>很可能</u>是 2007 年或更晚的版本。
	 -	当然，大多数情况下，Jos-mips 中也没有相关内容。

在这里我举几个例子：

<ol><li>

我是占位符。

```diff
diff -ru 2006/lab4/inc/trap.h 2007/lab4/inc/trap.h
--- 2006/lab4/inc/trap.h	2006-10-12 03:56:25.000000000 +0800
+++ 2007/lab4/inc/trap.h	2007-10-09 23:32:52.000000000 +0800
@@ -16,7 +16,7 @@
#define T_TSS       10		// invalid task switch segment
#define T_SEGNP     11		// segment not present
#define T_STACK     12		// stack exception
-#define T_GPFLT     13		// genernal protection fault
+#define T_GPFLT     13		// general protection fault
#define T_PGFLT     14		// page fault
/* #define T_RES    15 */	// reserved
#define T_FPERR     16		// floating point error
[...]
```

这里修复了一处 typo。Jos-mips 在 `include/trap.h` 中也有这段代码，其中的 typo 并没有修复，说明很可能是 2006 或以前。

</li><li>

我是占位符。

```diff
diff -ru 2006/lab4/kern/init.c 2007/lab4/kern/init.c
--- 2006/lab4/kern/init.c	2006-10-12 03:56:25.000000000 +0800
+++ 2007/lab4/kern/init.c	2007-10-09 23:32:52.000000000 +0800
@@ -33,8 +33,6 @@
 	// Lab 2 memory management initialization functions
 	i386_detect_memory();
 	i386_vm_init();
-	page_init();
-	page_check();
 
 	// Lab 3 user environment initialization functions
 	env_init();
```

这里删掉了 `page_init()` 和 `page_check()` 这两个函数的调用。Jos-mips 的 `mips_init()` 中也有这两个函数调用（但 `page_check()` 被注释掉了），说明很有可能是 2006 或以前。

</li><li>

我是占位符。

```diff
diff -ru 2006/lab4/kern/kclock.c 2007/lab4/kern/kclock.c
--- 2006/lab4/kern/kclock.c	2006-10-12 03:56:25.000000000 +0800
+++ 2007/lab4/kern/kclock.c	2007-10-09 23:32:52.000000000 +0800
@@ -1,7 +1,9 @@
 /* See COPYRIGHT for copyright information. */
 
-/* The Run Time Clock and other NVRAM access functions that go with it. */
-/* The run time clock is hard-wired to IRQ8. */
+/* Support for two time-related hardware gadgets: 1) the run time
+ * clock with its NVRAM access functions; 2) the 8253 timer, which
+ * generates interrupts on IRQ 0.
+ */
 
 #include <inc/x86.h>
 #include <inc/stdio.h>
```

Jos-mips 的 `lib/kclock.c` 中也有这段注释，而且和 2006 版一样，说明很可能是 2006 或以前。

</li></ol>

证据有很多，这里就不一一列举了。总之，经过耐心比对，可以认为 Jos-mips 使用的是 2006 年或更早的版本。

随后我又比较了 2005 和 2006、2004 和 2005。最后认定 Jos-mips 使用的是 2004 年或更早的版本。我还想继续比下去，可惜 2003 年的文件已经全部丢失了（其实是路径变化，我没有找着而已），2002 年的文件全部禁止访问。

### MIT OpenCourseWare
（4 月 17 日）我在网上搜索 [MIT 6.828 2003](https://www.google.com/search?q=MIT+6.828+2003)，结果发现 DSpace（MIT 数字图书馆）

首先介绍一下 [MIT OpenCourseWare](https://ocw.mit.edu/)。这是 MIT 的公开课平台，里面有各类课程的公开资料。更多信息可以去看[英文维基百科](https://en.wikipedia.org/wiki/MIT_OpenCourseWare)，我这里就不过多介绍了。

——说起来，北航似乎也曾经有过一个公开课平台。我们知道，智学北航的网址是 [spoc.buaa.edu.cn](https://spoc.buaa.edu.cn/)。我曾经查过 SPOC 这个缩写，它的意思是“小型私人在线课程”（Small Private Online Course），与 MOOC（Massive Open Online Course，大规模开放在线课程）互为反义词。于是我尝试了一下 [mooc.buaa.edu.cn](http://mooc.buaa.edu.cn/) 这个网址，没想到这个网站确实存在，但是已经罢工了。翻阅存档可知，这里曾经是北航的公开课平台。哈哈。


