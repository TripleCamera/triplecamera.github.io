---
title: 追本溯源：北航 MOS 操作系统的历史
date: 2025-05-01
updated: 2025-08-27
tags:
---

我们都知道，北航的 MOS 操作系统是从 MIT JOS 移植过来的。（如果你还不知道这一点，说明你既没有认真读过[指导书](https://os.buaa.edu.cn/public/guide-book.pdf)、[宣发页](https://os.buaa.edu.cn/team/)等官方资料，也没有认真看过[知乎](https://www.zhihu.com/question/322261810)等非官方资料；甚至没有认真参与水群，因为水群里会有学长提到这一点。）

但是我们都不知道的是：MOS 到底是衍生自 JOS 哪一年的版本？毕竟指导书里没有写，学长也没有说。我曾问过高阶助教，高阶说他也不知道，具体年份已经不可考了。他还说，要是发现了 MOS 的问题，大家就一起讨论，然后把它改掉。除非涉及到核心问题，不然考证完全没有必要。

那么为什么我要去问高阶，又要费大力气去考证这个呢？原因如下：

## 缘起
为什么我会想到考证 MOS 的历史呢？这还要从我重做课下任务说起。我去年做实验的时候，被代码和指导书的各种问题折磨，吃了不少苦；今年做助教的时候，自然希望能改掉实验课的诸多问题——但要改掉的这些问题已经被我忘光光了。于是我认为，要想发现实验课的不足，就要设身处地，重做一遍课下任务。可惜的是，许多助教并不看重这一点，他们认为，既然去年吃了一遍苦，今年又何必再吃呢？于是他们就没有重做课下，自然也就少了很多发现。

这不，在我重做课下的过程中，由于我对 MOS 理解的加深，越来越多的疑惑逐渐浮出水面。下面我举两个例子：

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

于是我对 MOS 的代码质量产生了担忧。另外，这一届的同学们非常热情，揪出了 MOS 操作系统的许多 bug（这可能是因为我们今年开源了答案）。这加深了我对 MOS 代码质量的怀疑。

除此之外，由于 MOS 代码较为晦涩难懂，加上注释全部由英文写成，同学们在阅读代码的过程中遇到了很大阻力，于是有些同学向代码中补充注释。甚至还有人给每一行都加上注释（我个人感觉这样做无异于阐释经文），还有人将代码中的英文注释翻译成中文。

我不禁感到疑惑：**MOS 的代码质量为何如此之差**？MIT JOS 的代码质量本来也这样差吗？还是说在移植的过程中出现了质量下降的问题？

## 前置知识
我们都知道 MOS 是从 MIT JOS 移植过来的，但这还远远不够。我在去年和今年期间搜集到了一些有关资料，为考证工作带来了便利。下面就让我向你介绍一些前置知识。

### 知乎
众所周知，吐槽你 6 系最好的地方就是知乎。有人在知乎上提问：[如何评价北航计算机学院操作系统课程及其实验？](https://www.zhihu.com/question/322261810)目前已有 16 个回答。

在这些回答中，许多被害惨了同学纷纷吐槽这门课程不足。另外还有同学拿这门课与 6.828 作比较，希望课程能多多吸收 6.828 的优点。

值得庆幸的是，最后一个回答发布于 2022 年——这说明近几年我们这门课并没有什么逆天操作，让同学把课程组挂到知乎上（笑）。

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

好消息是：OCW Archive 里确实保存着 2003 年版的公开课；坏消息是：当我兴高采烈地把装着所有 Lab 代码的 ZIP 文件都下载下来以后，才发现它们都打不开。

我一度以为是 [Ark 压缩文件管理工具](https://zh.wikipedia.org/wiki/Ark)的问题，后来换成 Windows 用 [7-Zip](https://zh.wikipedia.org/wiki/7-Zip) 试了一下，还是不行。

幸好还有时光机！4 月 24 日，我从时光机下载到了 2003 年的存档，结果发现原始文件与 DSpace 上的存档并不一致。——这说明 DSpace 上的存档很有可能损坏了。但具体是哪里的问题呢？我用 `xxd` 将两个版本的 `lab1.zip` 转换为十六进制文本文件，但是由于我的注意力比较涣散（笑），并没能发现其中的不同。直到我将每行显示多个字节拆分为每行一个字节，注意力才变得集中起来——

<figure>
  <img src="/images/mos-ocw2003-kompare.png" alt="使用 Kompare 对比两个版本的 lab1.zip 的十六进制文本文件" style="max-height: 18em">
  <figcaption>使用 Kompare 对比两个版本的 lab1.zip 的十六进制文本文件</figcaption>
</figure>

注意到所有十六进制大于等于 `80` 的字节全部被替换为 `EF BF BD`，也就是 `U+FFFD`。因此推测工作人员在归档过程中可能不小心以 UTF-8 格式保存了这些二进制文件。

没想到 MIT 的员工也会犯这么低级的错误😕。

## 真相大白
进一步对比 OCW 2003 版和 2004 版以后，我几乎可以肯定，MOS 使用的就是 OCW 2003 版。学长们当年很有可能从 MIT OCW 下载了这门课的代码，然后将其移植到 MIPS。当然，最后还剩下一点小小的疑惑，就是为什么他们在 2007 年尝试 JOS 的时候选用的是 OCW 2003 版，而不是 OCW 2006 版。一种可能的解释是，2006 年的课程在 2007 年 3 月上线，在此之前 OCW 上放的是 2003 年课程。

既然现在已经有了 MOS 当年参考的 JOS 源码，我们就能好好解答一下之前提出的那些问题了：

<ol><li>

**为什么 `KADDR` 不会对 `pa` 做类型转换**？我们可以在 `inc/mmu.h` 中找到 `KADDR` 的定义：

```c
// translates from physical address to kernel virtual address
#define KADDR(pa)						\
({								\
	u_long ppn = PPN(pa);					\
	if (ppn >= npage)					\
		panic("KADDR called with invalid pa %08lx", (u_long)pa);\
	(pa) + KERNBASE;					\
})
```

很显然 JOS 也没有做类型转换。但他们在 2004 年版中加上了（此时这一定义移动到了 `kern/pmap.h`）。

```c
// translates from physical address to kernel virtual address
#define KADDR(pa)						\
({								\
	u_long __m_pa = (pa); \
	u_long __m_ppn = PPN(__m_pa);				\
	if (__m_ppn >= npage)					\
		panic("KADDR called with invalid pa %08lx", __m_pa);\
	__m_pa + KERNBASE;					\
})
```

这说明他们很可能是忘记了，后来经过同学提醒加上了。

我觉得这个补丁完全可以 backport（向后移植）给 MOS。

</li><li>

**为什么 `va2pa()` 最后没有加上页偏移**？让我们看看 JOS 的写法（所属文件 `kern/pmap.c`）：

```c
//
// Checks that the kernel part of virtual address space
// has been setup roughly correctly(by i386_vm_init()).
//
// This function doesn't test every corner case,
// in fact it doesn't test the permission bits at all,
// but it is a pretty good sanity check. 
//
static u_long va2pa(Pde *pgdir, u_long va);
```

```c
static u_long
va2pa(Pde *pgdir, u_long va)
{
	Pte *p;

	pgdir = &pgdir[PDX(va)];
	if (!(*pgdir&PTE_P))
		return ~0;
	p = (Pte*)KADDR(PTE_ADDR(*pgdir));
	if (!(p[PTX(va)]&PTE_P))
		return ~0;
	return PTE_ADDR(p[PTX(va)]);
}
```

声明处的注释提到，这个函数是用来检查虚拟地址空间是否设置正确的。实际用例也证明了这一点：

 -  JOS：`kern/pmap.c` 文件下的 `check_boot_pgdir()` 和 `page_check()` 函数。
 -  MOS：`kern/pmap.c` 文件下的 `page_check()` 函数，`kern/env.c` 文件下的 `env_check()` 函数，以及 `lab2_2` 和 `lab2_3` 测试点。

——全部为测试函数。

另外，到了 2005 年，JOS 将这个函数重命名为 `check_va2pa()`，并增加了一些注释。可能是为了强调这个函数只能用于测试吧。

```c
//
// Checks that the kernel part of virtual address space
// has been setup roughly correctly(by i386_vm_init()).
//
// This function doesn't test every corner case,
// in fact it doesn't test the permission bits at all,
// but it is a pretty good sanity check. 
//
static physaddr_t check_va2pa(pde_t *pgdir, uintptr_t va);
```
```c
// This function returns the physical address of the page containing 'va',
// defined by the page directory 'pgdir'.  The hardware normally performs
// this functionality for us!  We define our own version to help check
// the check_boot_pgdir() function; it shouldn't be used elsewhere.

static physaddr_t
check_va2pa(pde_t *pgdir, uintptr_t va)
{
	pte_t *p;

	pgdir = &pgdir[PDX(va)];
	if (!(*pgdir & PTE_P))
		return ~0;
	p = (pte_t*) KADDR(PTE_ADDR(*pgdir));
	if (!(p[PTX(va)] & PTE_P))
		return ~0;
	return PTE_ADDR(p[PTX(va)]);
}
```

我觉得这个补丁 backport 不 backport 都行。

</li></ol>

通过这两个示例可以看出，由于 2003 年是 JOS 被创造出来并用于教学的第二年，2003 年版的 JOS 难免有一些漏洞。

## 展望未来
通过考证历史，我们终于揭开了 MOS 身上的重重的谜团。然后呢？接下来该怎么做？这些工作有什么意义？下面我分享一下我个人的看法。

首先，通过考证，加深了我们对 MOS 历史悠久这一点的认识。在此之前，我们一直以为 MOS 的历史从 2007 年开始；但这些工作将 MOS 的历史上溯到了 2003 年。许多同学都认为 MOS 已经过时了。诚然如此。从 2003 年到 2025 年，MIT 的操作系统课程一直在迭代，到现在已经发生了翻天覆地的变化。但 MOS 从 2009 年移植到 MIPS 架构以来，整体的课程设计并没有发生大的变化。虽然助教们做了许多移植方面的工作，比如将 MOS 从 GXemul 移植到了 QEMU，从 R3000 移植到 R4K，但这些变化始终没有触及到根本。

同学们希望进行课程改革。比如这届就有助教希望推翻 MOS。但是大刀阔斧的改革必然需要消耗大量精力。这些年计院和软院一直拿不出足够的精力来改革，加上今年削减了助教名额和补贴，改革成了一件遥遥无期的事情。在此之前，我们还是得继续用 MOS。

其次，在我“重新发现”JOS 以后，我们需要来一次“重新移植”。虽然大家都知道 MOS 移植自 JOS，但当年的助教们没有保存好关于 JOS 的资料，以至于 JOS 的源代码和资料都没有传下来。后来的助教们只能按照自己的想法，为 MOS 打上各种补丁。考虑到助教们的水平有限（S.T.A.R. 助教全部为本科生），代码质量劣化是在所难免的事。加上 2022 年以前 MOS 的代码没有使用 Git 管理，导致现在连打补丁的历史也几乎不存了。

既然现在已经找到了当年移植所参考的 JOS 源码，那么我们就可以挑选出 JOS 中闪光的地方，“重新移植”到 MOS 已经腐烂的地方上。代码质量不能再劣化下去了，最好能从现在开始有所改观。

最后，考虑到 2003 年版 JOS 漏洞较多，我们可以研究更新版本的 JOS，取其精华 <abbr title="向后移植">backport</abbr> 到 MOS，给 MOS 来一次“升级”。考虑到 2004 和 2005 年版不完整，我们可以将 OCW 2006 年版设置为下一个目标。MIT 的操作系统课用 JOS 一直用到了 2018 年，所以理论上来说可以一直“升级”到 2018 年版。当然实际操作起来大概率是到不了的。

我的助教生涯已经结束了。希望下一届助教可以学习一下 MIT 6.828 2003，然后对 MOS 进行改进。

## 感想
写到这里，回顾我这一学期以来的考证工作，不由得感慨万千。我打算把我的这些感想都留在这里。

操作系统课每年都要培养五百多名学生。这五百多人中，难道没有一人对 MOS 的历史产生过好奇吗？操作系统课每年都要招收约二十名助教。这二十人中，难道没有一人对 MOS 的代码质量产生过疑惑吗？

这使我想起另一件事来了。有学生在讨论区里询问 Thinking 4.9 的第一问是否有问题。我和另几位助教讨论以后，一致认为有问题，但由于出题的助教没有留下答案，我们也无法得知他的意图，只好打算把这一问删掉。

经过考证，这道思考题是 2018 年加入的，距今已有七年时间。没想到这七年间，所有的同学都在想方设法地阐释这道思考题的合理性，却没有人表现出一丝的怀疑。这让我感到非常可悲。指导书不是完美无缺的，MOS 也不是，学长学姐们留下的博客更不是。我们需要的是敢于质疑的人，不是甘于盲从的人。

二十年前的助教们学习 MIT JOS，并把它移植到 MIPS 平台上。十年前的助教们照着 MIT 的指导书编写北航自己的指导书，激昂文字，别管看不看得懂，反正激昂就对了。——那些历史已经离我们远去了。那些历史材料没有保存好，是学长的不对，我们也无法挽回了。

着眼现在。我知道许多同学对 MOS 有所不满，对操作系统这门课程有所不满，乃至对计院、软院的培养方案也有所不满。这并没有什么问题，一方面，上一轮课程改革已是十年以前，经过十年的时间，你 6 系引以为傲的体系结构课已经僵化了。另一方面，考虑到这些年的内卷情况逐渐加重，助教们不得不更加关注自己的保研加分，课程改革缺乏动力。现在体系结构课程正在裁减助教，未来甚至有取消的风险。改革已成为了遥遥无期的事情。

但是我认为，大家作为助教，不应该将眼光局限于完成带领一届学生的任务，拿到保研加分。还应该为下一届、下下一届，为这门课程的未来着想。虽然今年少了两个高阶助教名额，但是我们也注意到了一些变化：今年助教团队中，软院学生人数明显增加。我们推测，这可能是因为 S.T.A.R. 助教取消保研加分的消息传了出去，导致对保研加分更加敏感的计院学生人数下降。只能说，希望这届助教能更有责任吧。

最后，我想借~~《编程》~~《边城》中的最后一句话结束本文：

>	课程改革也许永远不会开始了，也许明年开始！

