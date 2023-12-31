![image-20230306172540972](https://s2.loli.net/2023/03/06/XZdTvEa5YuN3sWG.png)

# NIO基础

**注意：**推荐完成JavaSE篇、JavaWeb篇的学习再开启这一部分的学习，如果在这之前完成了JVM篇，那么看起来就会比较轻松了。

在JavaSE的学习中，我们了解了如何使用IO进行数据传输，Java IO是阻塞的，如果在一次读写数据调用时数据还没有准备好，或者目前不可写，那么读写操作就会被阻塞直到数据准备好或目标可写为止。Java NIO则是非阻塞的，每一次数据读写调用都会立即返回，并将目前可读（或可写）的内容写入缓冲区或者从缓冲区中输出，即使当前没有可用数据，调用仍然会立即返回并且不对缓冲区做任何操作。

NIO框架是在JDK1.4推出的，它的出现就是为了解决传统IO的不足，这一期视频，我们就将围绕着NIO开始讲解。

**NIO的三大组件：Buffer、Channel、Selector**

## 缓冲区

一切的一切还要从缓冲区开始讲起，包括源码在内，其实这个不是很难，只是需要理清思路。

### Buffer类及其实现

Buffer类是缓冲区的实现，类似于Java中的数组，也是用于存放和获取数据的。但是Buffer相比Java中的数组，功能就非常强大了，它包含一系列对于数组的快捷操作。

Buffer是一个抽象类，它的核心内容：

```java
public abstract class Buffer {
    // 这四个变量的关系: mark <= position <= limit <= capacity
  	// 这些变量就是Buffer操作的核心了，之后我们学习的过程中可以看源码是如何操作这些变量的
    private int mark = -1;
    private int position = 0;
    private int limit;
    private int capacity;

    // 直接缓冲区实现子类的数据内存地址（之后会讲解）
    long address;
```

我们来看看Buffer类的子类，包括我们认识到的所有基本类型（除了`boolean`类型之外）：

* IntBuffer   -   int类型的缓冲区。
* ShortBuffer   -   short类型的缓冲区。
* LongBuffer   -   long类型的缓冲区。
* FloatBuffer   -   float类型的缓冲区。
* DoubleBuffer   -   double类型的缓冲区。
* ByteBuffer   -   byte类型的缓冲区。
* CharBuffer   -   char类型的缓冲区。

（注意我们之前在JavaSE中学习过的StringBuffer虽然也是这种命名方式，但是不属于Buffer体系，这里不会进行介绍）

这里我们以IntBuffer为例，我们来看看如何创建一个Buffer类：

```java
public static void main(String[] args) {
  	//创建一个缓冲区不能直接new，而是需要使用静态方法去生成，有两种方式：
    //1. 申请一个容量为10的int缓冲区
    IntBuffer buffer = IntBuffer.allocate(10);
    //2. 可以将现有的数组直接转换为缓冲区（包括数组中的数据）
    int[] arr = new int[]{1, 2, 3, 4, 5, 6};
    IntBuffer buffer = IntBuffer.wrap(arr);
}
```

那么它的内部是本质上如何进行操作的呢？我们来看看它的源码：

```java
public static IntBuffer allocate(int capacity) {
    if (capacity < 0)   //如果申请的容量小于0，那还有啥意思
        throw new IllegalArgumentException();
    return new HeapIntBuffer(capacity, capacity);   //可以看到这里会直接创建一个新的IntBuffer实现类
  	//HeapIntBuffer是在堆内存中存放数据，本质上就数组，一会我们可以在深入看一下
}
```

```java
public static IntBuffer wrap(int[] array, int offset, int length) {
    try {
      	//可以看到这个也是创建了一个新的HeapIntBuffer对象，并且给了初始数组以及截取的起始位置和长度
        return new HeapIntBuffer(array, offset, length);
    } catch (IllegalArgumentException x) {
        throw new IndexOutOfBoundsException();
    }
}

public static IntBuffer wrap(int[] array) {
    return wrap(array, 0, array.length);   //调用的是上面的wrap方法
}
```

那么这个HeapIntBuffer又是如何实现的呢，我们接着来看：

```java
HeapIntBuffer(int[] buf, int off, int len) { // 注意这个构造方法不是public，是默认的访问权限
    super(-1, off, off + len, buf.length, buf, 0);   //你会发现这怎么又去调父类的构造方法了，绕来绕去
  	//mark是标记，off是当前起始下标位置，off+len是最大下标位置，buf.length是底层维护的数组真正长度，buf就是数组，最后一个0是起始偏移位置
}
```

我们又来看看IntBuffer中的构造方法是如何定义的：

```java
final int[] hb;                  // 只有在堆缓冲区实现时才会使用
final int offset;
boolean isReadOnly;                 // 只有在堆缓冲区实现时才会使用

IntBuffer(int mark, int pos, int lim, int cap,   // 注意这个构造方法不是public，是默认的访问权限
             int[] hb, int offset)
{
    super(mark, pos, lim, cap);  //调用Buffer类的构造方法
    this.hb = hb;    //hb就是真正我们要存放数据的数组，堆缓冲区底层其实就是这么一个数组
    this.offset = offset;   //起始偏移位置
}
```

最后我们来看看Buffer中的构造方法：

```java
Buffer(int mark, int pos, int lim, int cap) {       // 注意这个构造方法不是public，是默认的访问权限
    if (cap < 0)  //容量不能小于0，小于0还玩个锤子
        throw new IllegalArgumentException("Negative capacity: " + cap);
    this.capacity = cap;   //设定缓冲区容量
    limit(lim);    //设定最大position位置
    position(pos);   //设定起始位置
    if (mark >= 0) {  //如果起始标记大于等于0
        if (mark > pos)  //并且标记位置大于起始位置，那么就抛异常（至于为啥不能大于我们后面再说）
            throw new IllegalArgumentException("mark > position: ("
                                               + mark + " > " + pos + ")");
        this.mark = mark;   //否则设定mark位置（mark默认为-1）
    }
}
```

通过对源码的观察，我们大致可以得到以下结构了：

![image-20230306172558001](https://s2.loli.net/2023/03/06/tAihmNPUVbHBJZI.png)

现在我们来总结一下上面这些结构的各自职责划分：

* Buffer：缓冲区的一些基本变量定义，比如当前的位置（position）、容量 (capacity)、最大限制 (limit)、标记 (mark)等，你肯定会疑惑这些变量有啥用，别着急，这些变量会在后面的操作中用到，我们逐步讲解。
* IntBuffer等子类：定义了存放数据的数组（只有堆缓冲区实现子类才会用到）、是否只读等，也就是说数据的存放位置、以及对于底层数组的相关操作都在这里已经定义好了，并且已经实现了Comparable接口。
* HeapIntBuffer堆缓冲区实现子类：数据存放在堆中，实际上就是用的父类的数组在保存数据，并且将父类定义的所有底层操作全部实现了。

这样，我们对于Buffer类的基本结构就有了一个大致的认识。

### 缓冲区写操作

前面我们了解了Buffer类的基本操作，现在我们来看一下如何向缓冲区中存放数据以及获取数据，数据的存放包括以下五个方法：

* public abstract IntBuffer put(int i);   -   在当前position位置插入数据，由具体子类实现
* public abstract IntBuffer put(int index, int i);   -   在指定位置存放数据，也是由具体子类实现
* public final IntBuffer put(int[] src);   -   直接存放所有数组中的内容（数组长度不能超出缓冲区大小）
* public IntBuffer put(int[] src, int offset, int length);   -   直接存放数组中的内容，同上，但是可以指定存放一段范围
* public IntBuffer put(IntBuffer src);   -   直接存放另一个缓冲区中的内容

我们从最简的开始看，是在当前位置插入一个数据，那么这个当前位置是怎么定义的呢，我们来看看源码：

```java
public IntBuffer put(int x) {
    hb[ix(nextPutIndex())] = x;   //这个ix和nextPutIndex()很灵性，我们来看看具体实现
    return this;
}

protected int ix(int i) {
    return i + offset;   //将i的值加上我们之前设定的offset偏移量值，但是默认是0（非0的情况后面会介绍）
}

final int nextPutIndex() {
    int p = position;    //获取Buffer类中的position位置（一开始也是0）
    if (p >= limit)    //位置肯定不能超过底层数组最大长度，否则越界
        throw new BufferOverflowException();
    position = p + 1;   //获取之后会使得Buffer类中的position+1
    return p;   //返回当前的位置
}
```

所以put操作实际上是将底层数组`hb`在position位置上的数据进行设定。

![image-20230306172609624](https://s2.loli.net/2023/03/06/krusLfxyGnDHWFw.png)

设定完成后，position自动后移：

![image-20230306172619452](https://s2.loli.net/2023/03/06/6hrs4Spq1bnvXWa.png)

我们可以编写代码来看看：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.allocate(10);
    buffer
            .put(1)
            .put(2)
            .put(3);   //我们依次存放三个数据试试看
    System.out.println(buffer);
}
```

通过断点调试，我们来看看实际的操作情况：

![image-20230306172631282](https://s2.loli.net/2023/03/06/2VU34QjRFLiagkq.png)

可以看到我们不断地put操作，position会一直向后移动，当然如果超出最大长度，那么会直接抛出异常：

![image-20230306172641642](https://s2.loli.net/2023/03/06/kMGuPHyn2JQqCV8.png)

接着我们来看看第二个put操作是如何进行，它能够在指定位置插入数据：

```java
public IntBuffer put(int i, int x) {
    hb[ix(checkIndex(i))] = x;  //这里依然会使用ix，但是会检查位置是否合法
    return this;
}

final int checkIndex(int i) {                       // package-private
    if ((i < 0) || (i >= limit))    //插入的位置不能小于0并且不能大于等于底层数组最大长度
        throw new IndexOutOfBoundsException();
    return i;   //没有问题就把i返回
}
```

实际上这个比我们之前的要好理解一些，注意全程不会操作position的值，这里需要注意一下。

我们接着来看第三个put操作，它是直接在IntBuffer中实现的，是基于前两个put方法的子类实现来完成的：

```java
public IntBuffer put(int[] src, int offset, int length) {
    checkBounds(offset, length, src.length);   //检查截取范围是否合法，给offset、调用者指定长度、数组实际长度
    if (length > remaining())   //接着判断要插入的数据量在缓冲区是否容得下，装不下也不行
        throw new BufferOverflowException();
    int end = offset + length;   //计算出最终读取位置，下面开始for
    for (int i = offset; i < end; i++)
        this.put(src[i]);   //注意是直接从postion位置开始插入，直到指定范围结束
    return this;   //ojbk
}

public final IntBuffer put(int[] src) {
    return put(src, 0, src.length);   //因为不需要指定范围，所以直接0和length，然后调上面的，多捞哦
}

public final int remaining() {  //计算并获取当前缓冲区的剩余空间
    int rem = limit - position;   //最大容量减去当前位置，就是剩余空间
    return rem > 0 ? rem : 0;  //没容量就返回0
}
```

```java
static void checkBounds(int off, int len, int size) { // package-private
    if ((off | len | (off + len) | (size - (off + len))) < 0)  //让我猜猜，看不懂了是吧
        throw new IndexOutOfBoundsException();
  	//实际上就是看给定的数组能不能截取出指定的这段数据，如果都不够了那肯定不行啊
}
```

大致流程如下，首先来了一个数组要取一段数据全部丢进缓冲区：

![image-20230306172652962](https://s2.loli.net/2023/03/06/hxzUm6Xgd1ABcTi.png)

在检查没有什么问题并且缓冲区有容量时，就可以开始插入了：

![image-20230306172704570](https://s2.loli.net/2023/03/06/WLrnhBpyG5uxC24.png)

最后我们通过代码来看看：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.allocate(10);
    int[] arr = new int[]{1,2,3,4,5,6,7,8,9};
    buffer.put(arr, 3, 4);  //从下标3开始，截取4个元素

    System.out.println(Arrays.toString(buffer.array()));  //array方法可以直接获取到数组
}
```

可以看到最后结果为：

![image-20230306172716044](https://s2.loli.net/2023/03/06/Ke59YxvBjJnNhzb.png)

当然我们也可以将一个缓冲区的内容保存到另一个缓冲区：

```java
public IntBuffer put(IntBuffer src) {
    if (src == this)   //不会吧不会吧，不会有人保存自己吧
        throw new IllegalArgumentException();
    if (isReadOnly())   //如果是只读的话，那么也是不允许插入操作的（我猜你们肯定会问为啥就这里会判断只读，前面四个呢）
        throw new ReadOnlyBufferException();
    int n = src.remaining();  //给进来的src看看容量（注意这里不remaining的结果不是剩余容量，是转换后的，之后会说）
    if (n > remaining())    //这里判断当前剩余容量是否小于src容量
        throw new BufferOverflowException();
    for (int i = 0; i < n; i++)   //也是从position位置开始继续写入
        put(src.get());   //通过get方法一个一个读取数据出来，具体过程后面讲解
    return this;
}
```

我们来看看效果：

```java
public static void main(String[] args) {
    IntBuffer src = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    IntBuffer buffer = IntBuffer.allocate(10);
    buffer.put(src);
    System.out.println(Arrays.toString(buffer.array()));
}
```

但是如果是这样的话，会出现问题：

```java
public static void main(String[] args) {
    IntBuffer src = IntBuffer.allocate(5);
    for (int i = 0; i < 5; i++) src.put(i);   //手动插入数据
    IntBuffer buffer = IntBuffer.allocate(10);
    buffer.put(src);
    System.out.println(Arrays.toString(buffer.array()));
}
```

我们发现，结果和上面的不一样，并没有成功地将数据填到下面的IntBuffer中，这是为什么呢？实际上就是因为`remaining()`的计算问题，因为这个方法是直接计算postion的位置，但是由于我们在写操作完成之后，position跑到后面去了，也就导致`remaining()`结果最后算出来为0。

因为这里不是写操作，是接下来需要从头开始进行读操作，所以我们得想个办法把position给退回到一开始的位置，这样才可以从头开始读取，那么怎么做呢？一般我们在写入完成后需要进行读操作时（后面都是这样，不只是这里），会使用`flip()`方法进行翻转：

```java
public final Buffer flip() {
    limit = position;    //修改limit值，当前写到哪里，下次读的最终位置就是这里，limit的作用开始慢慢体现了
    position = 0;    //position归零
    mark = -1;    //标记还原为-1，但是现在我们还没用到
    return this;
}
```

这样，再次计算`remaining()`的结果就是我们需要读取的数量了，这也是为什么put方法中要用`remaining()`来计算的原因，我们再来测试一下：

```java
public static void main(String[] args) {
    IntBuffer src = IntBuffer.allocate(5);
    for (int i = 0; i < 5; i++) src.put(i);
    IntBuffer buffer = IntBuffer.allocate(10);

    src.flip();   //我们可以通过flip来翻转缓冲区
    buffer.put(src);
    System.out.println(Arrays.toString(buffer.array()));
}
```

翻转之后再次进行转移，就正常了。

### 缓冲区读操作

前面我们看完了写操作，现在我们接着来看看读操作。读操作有四个方法：

* `public abstract int get();`    -    直接获取当前position位置的数据，由子类实现
* `public abstract int get(int index); `  -    获取指定位置的数据，也是子类实现
* `public IntBuffer get(int[] dst)`  -   将数据读取到给定的数组中
* `public IntBuffer get(int[] dst, int offset, int length)`  -   同上，加了个范围

我们还是从最简单的开始看，第一个get方法的实现在IntBuffer类中：

```java
public int get() {
    return hb[ix(nextGetIndex())];    //直接从数组中取就完事
}

final int nextGetIndex() {                          // 好家伙，这不跟前面那个一模一样吗
  int p = position;
  if (p >= limit)
    throw new BufferUnderflowException();
  position = p + 1;
  return p;
}
```

可以看到每次读取操作之后，也会将postion+1，直到最后一个位置，如果还要继续读，那么就直接抛出异常。

![image-20230306172731427](https://s2.loli.net/2023/03/06/OPGBJYS9ajzd2mI.png)

我们来看看第二个：

```java
public int get(int i) {
    return hb[ix(checkIndex(i))];   //这里依然是使用checkIndex来检查位置是否非法
}
```

我们来看看第三个和第四个：

```java
public IntBuffer get(int[] dst, int offset, int length) {
    checkBounds(offset, length, dst.length);   //跟put操作一样，也是需要检查是否越界
    if (length > remaining())   //如果读取的长度比可以读的长度大，那肯定是不行的
        throw new BufferUnderflowException();
    int end = offset + length;    //计算出最终读取位置
    for (int i = offset; i < end; i++)
        dst[i] = get();   //开始从position把数据读到数组中，注意是在数组的offset位置开始
    return this;
}

public IntBuffer get(int[] dst) {
    return get(dst, 0, dst.length);   //不指定范围的话，那就直接用上面的
}
```

我们来看看效果：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    int[] arr = new int[10];
    buffer.get(arr, 2, 5);
    System.out.println(Arrays.toString(arr));
}
```

![image-20230306172745352](https://s2.loli.net/2023/03/06/AYW9VXSskhHJLrj.png)

可以看到成功地将数据读取到了数组中。

当然如果我们需要直接获取数组，也可以使用`array()`方法来拿到：

```java
public final int[] array() {
    if (hb == null)   //为空那说明底层不是数组实现的，肯定就没法转换了
        throw new UnsupportedOperationException();
    if (isReadOnly)   //只读也是不让直接取出的，因为一旦取出去岂不是就能被修改了
        throw new ReadOnlyBufferException();
    return hb;   //直接返回hb
}
```

我们来试试看：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    System.out.println(Arrays.toString(buffer.array()));
}
```

当然，既然都已经拿到了底层的`hb`了，我们来看看如果直接修改之后是不是读取到的就是我们的修改之后的结果了：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    int[] arr = buffer.array();
    arr[0] = 99999;   //拿到数组对象直接改
    System.out.println(buffer.get());
}
```

可以看到这种方式由于是直接拿到的底层数组，所有修改会直接生效在缓冲区中。

当然除了常规的读取方式之外，我们也可以通过`mark()`来实现跳转读取，这里需要介绍一下几个操作：

* `public final Buffer mark()`   -   标记当前位置
* `public final Buffer reset()`   -   让当前的position位置跳转到mark当时标记的位置

我们首先来看标记方法：

```java
public final Buffer mark() {
    mark = position;   //直接标记到当前位置，mark变量终于派上用场了，当然这里仅仅是标记
    return this;
}
```

我们再来看看重置方法：

```java
public final Buffer reset() {
    int m = mark;   //存一下当前的mark位置
    if (m < 0)    //因为mark默认是-1，要是没有进行过任何标记操作，那reset个毛
        throw new InvalidMarkException();
    position = m;   //直接让position变成mark位置
    return this;
}
```

那比如我们在读取到1号位置时进行标记：

![image-20230306172758746](https://s2.loli.net/2023/03/06/1cL9njuDJxCZvmY.png)

接着我们使用reset方法就可以直接回退回去了：

![image-20230306172807847](https://s2.loli.net/2023/03/06/OtrlZSHDPeYkvU6.png)

现在我们来测试一下：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    buffer.get();   //读取一位，那么position就变成1了
    buffer.mark();   //这时标记，那么mark = 1
    buffer.get();   //又读取一位，那么position就变成2了
    buffer.reset();    //直接将position = mark，也就是变回1
    System.out.println(buffer.get());
}
```

可以看到，读取的位置根据我们的操作进行了变化，有关缓冲区的读操作，就暂时讲到这里。

### 缓冲区其他操作

前面我们大致了解了一下缓冲区的读写操作，那么我们接着来看看，除了常规的读写操作之外，还有哪些其他的操作：

* `public abstract IntBuffer compact()`   -   压缩缓冲区，由具体实现类实现
* `public IntBuffer duplicate()`   -   复制缓冲区，会直接创建一个新的数据相同的缓冲区
* `public abstract IntBuffer slice()`   -    划分缓冲区，会将原本的容量大小的缓冲区划分为更小的出来进行操作
* `public final Buffer rewind()`  -   重绕缓冲区，其实就是把position归零，然后mark变回-1
* `public final Buffer clear()`  -   将缓冲区清空，所有的变量变回最初的状态

我们先从压缩缓冲区开始看起，它会将整个缓冲区的大小和数据内容变成position位置到limit之间的数据，并移动到数组头部：

```java
public IntBuffer compact() {
    int pos = position();   //获取当前位置
    int lim = limit();    //获取当前最大position位置
    assert (pos <= lim);   //断言表达式，position必须小于最大位置，肯定的
    int rem = (pos <= lim ? lim - pos : 0);  //计算pos距离最大位置的长度
    System.arraycopy(hb, ix(pos), hb, ix(0), rem);   //直接将hb数组当前position位置的数据拷贝到头部去，然后长度改成刚刚计算出来的空间
    position(rem);   //直接将position移动到rem位置
    limit(capacity());   //pos最大位置修改为最大容量
    discardMark();   //mark变回-1
    return this;
}
```

比如现在的状态是：

![image-20230306172820209](https://s2.loli.net/2023/03/06/ljJbiNLHY26q3rE.png)

那么我们在执行` compact()`方法之后，会进行截取，此时`limit - position = 6`，那么就会截取第`4、5、6、7、8、9`这6个数据然后丢到最前面，接着position跑到`7`表示这是下一个继续的位置：

![image-20230306172828232](https://s2.loli.net/2023/03/06/9bJ1uamBelMV5Qt.png)

现在我们通过代码来检验一下：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 0});
    for (int i = 0; i < 4; i++) buffer.get();   //先正常读4个
    buffer.compact();   //压缩缓冲区

    System.out.println("压缩之后的情况："+Arrays.toString(buffer.array()));
    System.out.println("当前position位置："+buffer.position());
    System.out.println("当前limit位置："+buffer.limit());
}
```

可以看到最后的结果没有问题：

![image-20230306172840891](https://s2.loli.net/2023/03/06/wBxO3SPFZpYjXMV.png)

我们接着来看第二个方法，那么如果我们现在需要复制一个内容一模一样的的缓冲区，该怎么做？直接使用`duplicate()`方法就可以复制了：

```java
public IntBuffer duplicate() {   //直接new一个新的，但是是吧hb给丢进去了，而不是拷贝一个新的
    return new HeapIntBuffer(hb,
                                    this.markValue(),
                                    this.position(),
                                    this.limit(),
                                    this.capacity(),
                                    offset);
}
```

那么各位猜想一下，如果通过这种方式创了一个新的IntBuffer，那么下面的例子会出现什么结果：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    IntBuffer duplicate = buffer.duplicate();

    System.out.println(buffer == duplicate);
    System.out.println(buffer.array() == duplicate.array());
}
```

由于buffer是重新new的，所以第一个为false，而底层的数组由于在构造的时候没有进行任何的拷贝而是直接传递，因此实际上两个缓冲区的底层数组是同一个对象。所以，一个发生修改，那么另一个就跟着变了：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5});
    IntBuffer duplicate = buffer.duplicate();

    buffer.put(0, 66666);
    System.out.println(duplicate.get());
}
```

现在我们接着来看下一个方法，`slice()`方法会将缓冲区进行划分：

```java
public IntBuffer slice() {
    int pos = this.position();   //获取当前position
    int lim = this.limit();     //获取position最大位置
    int rem = (pos <= lim ? lim - pos : 0);   //求得剩余空间
    return new HeapIntBuffer(hb,    //返回一个新的划分出的缓冲区，但是底层的数组用的还是同一个
                                    -1,
                                    0,
                                    rem,    //新的容量变成了剩余空间的大小
                                    rem,
                                    pos + offset);   //可以看到offset的地址不再是0了，而是当前的position加上原有的offset值
}
```

虽然现在底层依然使用的是之前的数组，但是由于设定了offset值，我们之前的操作似乎变得不太一样了：

![image-20230306172901061](https://s2.loli.net/2023/03/06/PBdcqUj4sCpwn1m.png)

回顾前面我们所讲解的内容，在读取和存放时，会被`ix`方法进行调整：

```java
protected int ix(int i) {
    return i + offset;   //现在offset为4，那么也就是说逻辑上的i是0但是得到真实位置却是4
}

public int get() {
    return hb[ix(nextGetIndex())];   //最后会经过ix方法转换为真正在数组中的位置
}
```

当然，在逻辑上我们可以认为是这样的：

![image-20230306172911560](https://s2.loli.net/2023/03/06/ic9zoQgfnOxuwSR.png)

现在我们来测试一下：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 0});
    for (int i = 0; i < 4; i++) buffer.get();
    IntBuffer slice = buffer.slice();

    System.out.println("划分之后的情况："+Arrays.toString(slice.array()));
    System.out.println("划分之后的偏移地址："+slice.arrayOffset());
    System.out.println("当前position位置："+slice.position());
    System.out.println("当前limit位置："+slice.limit());

    while (slice.hasRemaining()) {   //将所有的数据全部挨着打印出来
        System.out.print(slice.get()+", ");
    }
}
```

可以看到，最终结果：

![image-20230306172926439](https://s2.loli.net/2023/03/06/fC7I81wAGVngNlu.png)

最后两个方法就比较简单了，我们先来看`rewind()`，它相当于是对position和mark进行了一次重置：

```java
public final Buffer rewind() {
    position = 0;
    mark = -1;
    return this;
}
```

接着是`clear()`，它相当于是将整个缓冲区回归到最初的状态了：

```java
public final Buffer clear() {
    position = 0;    //同上
    limit = capacity;   //limit变回capacity
    mark = -1;
    return this;
}
```

到这里，关于缓冲区的一些其他操作，我们就讲解到此。

### 缓冲区比较

缓冲区之间是可以进行比较的，我们可以看到equals方法和compareTo方法都是被重写了的，我们首先来看看`equals`方法，注意，它是判断两个缓冲区剩余的内容是否一致：

```java
public boolean equals(Object ob) {
    if (this == ob)   //要是两个缓冲区是同一个对象，肯定一样
        return true;
    if (!(ob instanceof IntBuffer))  //类型不是IntBuffer那也不用比了
        return false;
    IntBuffer that = (IntBuffer)ob;   //转换为IntBuffer
    int thisPos = this.position();  //获取当前缓冲区的相关信息
    int thisLim = this.limit();
    int thatPos = that.position();  //获取另一个缓冲区的相关信息
    int thatLim = that.limit();
    int thisRem = thisLim - thisPos; 
    int thatRem = thatLim - thatPos;
    if (thisRem < 0 || thisRem != thatRem)   //如果剩余容量小于0或是两个缓冲区的剩余容量不一样，也不行
        return false;
  	//注意比较的是剩余的内容
    for (int i = thisLim - 1, j = thatLim - 1; i >= thisPos; i--, j--)  //从最后一个开始倒着往回比剩余的区域
        if (!equals(this.get(i), that.get(j)))
            return false;   //只要发现不一样的就不用继续了，直接false
    return true;   //上面的比较都没问题，那么就true
}

private static boolean equals(int x, int y) {
    return x == y;
}
```

那么我们按照它的思路来验证一下：

```java
public static void main(String[] args) {
    IntBuffer buffer1 = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 0});
    IntBuffer buffer2 = IntBuffer.wrap(new int[]{6, 5, 4, 3, 2, 1, 7, 8, 9, 0});
    System.out.println(buffer1.equals(buffer2));   //直接比较
    
    buffer1.position(6);
    buffer2.position(6);
    System.out.println(buffer1.equals(buffer2));   //比较从下标6开始的剩余内容
}
```

可以看到结果就是我们所想的那样：

![image-20230306172945627](https://s2.loli.net/2023/03/06/Nf4WRSpQZUrHXj7.png)

那么我们接着来看比较，`compareTo`方法，它实际上是`Comparable`接口提供的方法，它实际上比较的也是pos开始剩余的内容：

```java
public int compareTo(IntBuffer that) {
    int thisPos = this.position();    //获取并计算两个缓冲区的pos和remain
    int thisRem = this.limit() - thisPos;
    int thatPos = that.position();
    int thatRem = that.limit() - thatPos;
    int length = Math.min(thisRem, thatRem);   //选取一个剩余空间最小的出来
    if (length < 0)   //如果最小的小于0，那就返回-1
        return -1;
    int n = thisPos + Math.min(thisRem, thatRem);  //计算n的值当前的pos加上剩余的最小空间
    for (int i = thisPos, j = thatPos; i < n; i++, j++) {  //从两个缓冲区的当前位置开始，一直到n结束
        int cmp = compare(this.get(i), that.get(j));  //比较
        if (cmp != 0)
            return cmp;   //只要出现不相同的，那么就返回比较出来的值
    }
    return thisRem - thatRem; //如果没比出来个所以然，那么就比长度
}

private static int compare(int x, int y) {
    return Integer.compare(x, y);
}
```

这里我们就不多做介绍了。

### 只读缓冲区

接着我们来看看只读缓冲区，只读缓冲区就像其名称一样，它只能进行读操作，而不允许进行写操作。

那么我们怎么创建只读缓冲区呢？

* `public abstract IntBuffer asReadOnlyBuffer();`   -   基于当前缓冲区生成一个只读的缓冲区。

我们来看看此方法的具体实现：

```java
public IntBuffer asReadOnlyBuffer() {
    return new HeapIntBufferR(hb,    //注意这里并不是直接创建了HeapIntBuffer，而是HeapIntBufferR，并且直接复制的hb数组
                                 this.markValue(),
                                 this.position(),
                                 this.limit(),
                                 this.capacity(),
                                 offset);
}
```

那么这个HeapIntBufferR类跟我们普通的HeapIntBuffer有什么不同之处呢？

![image-20230306173005107](https://s2.loli.net/2023/03/06/4XiVxHTbApPmkMK.png)

可以看到它是继承自HeapIntBuffer的，那么我们来看看它的实现有什么不同：

```java
protected HeapIntBufferR(int[] buf,
                               int mark, int pos, int lim, int cap,
                               int off)
{
    super(buf, mark, pos, lim, cap, off);
    this.isReadOnly = true;
}
```

可以看到在其构造方法中，除了直接调用父类的构造方法外，还会将`isReadOnly`标记修改为true，我们接着来看put操作有什么不同之处：

```java
public boolean isReadOnly() {
    return true;
}

public IntBuffer put(int x) {
    throw new ReadOnlyBufferException();
}

public IntBuffer put(int i, int x) {
    throw new ReadOnlyBufferException();
}

public IntBuffer put(int[] src, int offset, int length) {
    throw new ReadOnlyBufferException();
}

public IntBuffer put(IntBuffer src) {
    throw new ReadOnlyBufferException();
}
```

可以看到所有的put方法全部凉凉，只要调用就会直接抛出ReadOnlyBufferException异常。但是其他get方法依然没有进行重写，也就是说get操作还是可以正常使用的，但是只要是写操作就都不行：

```java
public static void main(String[] args) {
    IntBuffer buffer = IntBuffer.wrap(new int[]{1, 2, 3, 4, 5, 6, 7, 8, 9, 0});
    IntBuffer readBuffer = buffer.asReadOnlyBuffer();

    System.out.println(readBuffer.isReadOnly());
    System.out.println(readBuffer.get());
    readBuffer.put(0, 666);
}
```

可以看到结果为：

![image-20230306173024857](https://s2.loli.net/2023/03/06/uVi36nHvbJtsQEF.png)

这就是只读状态下的缓冲区。

### ByteBuffer和CharBuffer

通过前面的学习，我们基本上已经了解了缓冲区的使用，但是都是基于IntBuffer进行讲解，现在我们来看看另外两种基本类型的缓冲区ByteBuffer和CharBuffer，因为ByteBuffer底层存放的是很多单个byte字节，所以会有更多的玩法，同样CharBuffer是一系列字节，所以也有很多便捷操作。

我们先来看看ByteBuffer，我们可以直接点进去看：

```java
public abstract class ByteBuffer extends Buffer implements Comparable<ByteBuffer> {
    final byte[] hb;                  // Non-null only for heap buffers
    final int offset;
    boolean isReadOnly;                 // Valid only for heap buffers
  	....
```

可以看到如果也是使用堆缓冲区子类实现，那么依然是一个`byte[]`的形式保存数据。我们来尝试使用一下：

```java
public static void main(String[] args) {
    ByteBuffer buffer = ByteBuffer.allocate(10);
    //除了直接丢byte进去之外，我们也可以丢其他的基本类型（注意容量消耗）
    buffer.putInt(Integer.MAX_VALUE);  //丢个int的最大值进去，注意一个int占4字节
    System.out.println("当前缓冲区剩余字节数："+buffer.remaining());  //只剩6个字节了

    //我们来尝试读取一下，记得先翻转
    buffer.flip();
    while (buffer.hasRemaining()) {
        System.out.println(buffer.get());   //一共四个字节
    }
}
```

最后的结果为：

![image-20230306173044493](https://s2.loli.net/2023/03/06/16zaudJ9WvGybsE.png)

可以看到第一个byte为127、然后三个都是-1，我们来分析一下：

* `127` 转换为二进制补码形式就是 `01111111`，而`-1`转换为二进制补码形式为`11111111`

那也就是说，第一个字节是01111111，而后续字节就是11111111，把它们拼接在一起：

* 二进制补码表示`01111111 11111111 11111111 11111111` 转换为十进制就是`2147483647`，也就是int的最大值。

那么根据我们上面的推导，各位能否计算得到下面的结果呢？

```java
public static void main(String[] args) {
    ByteBuffer buffer = ByteBuffer.allocate(10);
    buffer.put((byte) 0);
    buffer.put((byte) 0);
    buffer.put((byte) 1);
    buffer.put((byte) -1);

    buffer.flip();   //翻转一下
    System.out.println(buffer.getInt());  //以int形式获取，那么就是一次性获取4个字节
}
```

经过上面的计算，得到的结果就是：

* 上面的数据以二进制补码的形式表示为：`00000000 00000000 00000001 11111111`
* 将其转换为十进制那么就是：256 + 255 = 511

好吧，再来个魔鬼问题，把第一个换成1呢：`10000000 00000000 00000001 11111111`，自己算。

我们接着来看看CharBuffer，这种缓冲区实际上也是保存一大堆char类型的数据：

```java
public static void main(String[] args) {
    CharBuffer buffer = CharBuffer.allocate(10);
    buffer.put("lbwnb");  //除了可以直接丢char之外，字符串也可以一次性丢进入
    System.out.println(Arrays.toString(buffer.array()));
}
```

但是正是得益于char数组，它包含了很多的字符串操作，可以一次性存放一整个字符串。我们甚至还可以将其当做一个String来进行处理：

```java
public static void main(String[] args) {
    CharBuffer buffer = CharBuffer.allocate(10);
    buffer.put("lbwnb");
    buffer.append("!");   //可以像StringBuilder一样使用append来继续添加数据
  
  	System.out.println("剩余容量："+buffer.remaining());  //已经用了6个字符了

    buffer.flip();
    System.out.println("整个字符串为："+buffer);   //直接将内容转换为字符串
    System.out.println("第3个字符是："+buffer.charAt(2));  //直接像String一样charAt

    buffer   //也可以转换为IntStream进行操作
            .chars()
            .filter(i -> i < 'l')
            .forEach(i -> System.out.print((char) i));
}
```

当然除了一些常规操作之外，我们还可以直接将一个字符串作为参数创建：

```java
public static void main(String[] args) {
    //可以直接使用wrap包装一个字符串，但是注意，包装出来之后是只读的
    CharBuffer buffer = CharBuffer.wrap("收藏等于学会~");
    System.out.println(buffer);

    buffer.put("111");  //这里尝试进行一下写操作
}
```

可以看到结果也是我们预料中的：

![image-20230306173059478](https://s2.loli.net/2023/03/06/yBxj2DrCcYAuWdH.png)

对于这两个比较特殊的缓冲区，我们就暂时讲解到这里。

### 直接缓冲区

**注意：**推荐学习完成JVM篇再来学习这一部分。

最后我们来看一下直接缓冲区，我们前面一直使用的都是堆缓冲区，也就是说实际上数据是保存在一个数组中的，如果你已经完成了JVM篇的学习，一定知道实际上占用的是堆内存，而我们也可以创建一个直接缓冲区，也就是申请堆外内存进行数据保存，采用操作系统本地的IO，相比堆缓冲区会快一些。

那么怎么使用直接缓冲区呢？我们可以通过`allocateDirect`方法来创建：

```java
public static void main(String[] args) {
    //这里我们申请一个直接缓冲区
    ByteBuffer buffer = ByteBuffer.allocateDirect(10);
  	//使用方式基本和之前是一样的
    buffer.put((byte) 66);
    buffer.flip();
    System.out.println(buffer.get());
}
```

我们来看看这个`allocateDirect`方法是如何创建一个直接缓冲区的：

```java
public static ByteBuffer allocateDirect(int capacity) {
    return new DirectByteBuffer(capacity);
}
```

这个方法直接创建了一个新的DirectByteBuffer对象，那么这个类又是怎么进行创建的呢？

![image-20230306173111350](https://s2.loli.net/2023/03/06/HsWqivMefkVtNrC.png)

可以看到它并不是直接继承自ByteBuffer，而是MappedByteBuffer，并且实现了接口DirectBuffer，我们先来看看这个接口：

```java
public interface DirectBuffer {
    public long address();   //获取内存地址
    public Object attachment();   //附加对象，这是为了保证某些情况下内存不被释放，我们后面细谈
    public Cleaner cleaner();   //内存清理类
}
```

```java
public abstract class MappedByteBuffer extends ByteBuffer {
  	//这三个方法目前暂时用不到，后面文件再说
    public final MappedByteBuffer load();
    public final boolean isLoaded();
    public final MappedByteBuffer force();
}
```

接着我们来看看DirectByteBuffer类的成员变量：

```java
// 把Unsafe类取出来
protected static final Unsafe unsafe = Bits.unsafe();

// 在内存中直接创建的内存空间地址
private static final long arrayBaseOffset = (long)unsafe.arrayBaseOffset(byte[].class);

// 是否具有非对齐访问能力，根据CPU架构而定，intel、AMD、AppleSilicon 都是支持的
protected static final boolean unaligned = Bits.unaligned();

// 直接缓冲区的内存地址，为了提升速度就放到Buffer类中去了
//    protected long address;

// 附加对象，一会有大作用
private final Object att;
```

接着我们来看看构造方法：

```java
DirectByteBuffer(int cap) {                   // package-private
    super(-1, 0, cap, cap);
    boolean pa = VM.isDirectMemoryPageAligned();   //是否直接内存分页对齐，需要额外计算
    int ps = Bits.pageSize();
    long size = Math.max(1L, (long)cap + (pa ? ps : 0));   //计算出最终需要申请的大小
  	//判断堆外内存是否足够，够的话就作为保留内存
    Bits.reserveMemory(size, cap);

    long base = 0;
    try {
      	//通过Unsafe申请内存空间，并得到内存地址
        base = unsafe.allocateMemory(size);
    } catch (OutOfMemoryError x) {
      	//申请失败就取消一开始的保留内存
        Bits.unreserveMemory(size, cap);
        throw x;
    }
  	//批量将申请到的这一段内存每个字节都设定为0
    unsafe.setMemory(base, size, (byte) 0);
    if (pa && (base % ps != 0)) {
        // Round up to page boundary
        address = base + ps - (base & (ps - 1));
    } else {
      	//将address变量（在Buffer中定义）设定为base的地址
        address = base;
    }
  	//创建一个针对于此缓冲区的Cleaner，由于是堆外内存，所以现在由它来进行内存清理
    cleaner = Cleaner.create(this, new Deallocator(base, size, cap));
    att = null;
}
```

可以看到在构造方法中，是直接通过Unsafe类来申请足够的堆外内存保存数据，那么当我们不使用此缓冲区时，内存会被如何清理呢？我们来看看这个Cleaner：

```java
public class Cleaner extends PhantomReference<Object>{ //继承自鬼引用，也就是说此对象会存放一个没有任何引用的对象

    //引用队列，PhantomReference构造方法需要
    private static final ReferenceQueue<Object> dummyQueue = new ReferenceQueue<>();
  	
  	//执行清理的具体流程
    private final Runnable thunk;
  
  	static private Cleaner first = null;  //Cleaner双向链表，每创建一个Cleaner对象都会添加一个结点

    private Cleaner
        next = null,
        prev = null;
  
  	private static synchronized Cleaner add(Cleaner cl) {   //添加操作会让新来的变成新的头结点
        if (first != null) {
            cl.next = first;
            first.prev = cl;
        }
        first = cl;
        return cl;
    }

  	//可以看到创建鬼引用的对象就是传进的缓冲区对象
    private Cleaner(Object referent, Runnable thunk) {
        super(referent, dummyQueue);
      	//清理流程实际上是外面的Deallocator
        this.thunk = thunk;
    }

   	//通过此方法创建一个新的Cleaner
    public static Cleaner create(Object ob, Runnable thunk) {
        if (thunk == null)
            return null;
        return add(new Cleaner(ob, thunk));   //调用add方法将Cleaner添加到队列
    }
  
  	//清理操作
  	public void clean() {
        if (!remove(this))
            return;    //进行清理操作时会从双向队列中移除当前Cleaner，false说明已经移除过了，直接return
        try {
            thunk.run();   //这里就是直接执行具体清理流程
        } catch (final Throwable x) {
            ...
        }
    }
```

那么我们先来看看具体的清理程序在做些什么，Deallocator是在直接缓冲区中声明的：

```java
private static class Deallocator implements Runnable {

    private static Unsafe unsafe = Unsafe.getUnsafe();

    private long address;   //内存地址
    private long size;    //大小
    private int capacity;   //申请的容量

    private Deallocator(long address, long size, int capacity) {
        assert (address != 0);
        this.address = address;
        this.size = size;
        this.capacity = capacity;
    }

    public void run() {   //具体的清理操作
        if (address == 0) {
            // Paranoia
            return;
        }
        unsafe.freeMemory(address);   //这里是直接调用了Unsafe进行内存释放操作
        address = 0;   //内存地址改为0，NULL
        Bits.unreserveMemory(size, capacity);   //取消一开始的保留内存
    }
}
```

好了，现在我们可以明确在清理的时候实际上也是调用Unsafe类进行内存释放操作，那么，这个清理操作具体是在什么时候进行的呢？首先我们要明确，如果是普通的堆缓冲区，由于使用的数组，那么一旦此对象没有任何引用时，就随时都会被GC给回收掉，但是现在是堆外内存，只能我们手动进行内存回收，那么当DirectByteBuffer也失去引用时，会不会触发内存回收呢？

答案是可以的，还记得我们刚刚看到Cleaner是PhantomReference的子类吗，而DirectByteBuffer是被鬼引用的对象，而具体的清理操作是Cleaner类的clean方法，莫非这两者有什么联系吗？

你别说，还真有，我们直接看到PhantomReference的父类Reference，我们会发现这样一个类：

```java
private static class ReferenceHandler extends Thread {
  ...
	static {
            // 预加载并初始化 InterruptedException 和 Cleaner 类
        		// 以避免出现在循环运行过程中时由于内存不足而无法加载
            ensureClassInitialized(InterruptedException.class);
            ensureClassInitialized(Cleaner.class);
    }
		
    public void run() {
        while (true) {
            tryHandlePending(true);   //这里是一个无限循环调用tryHandlePending方法
        }
    }
}
```

```java
private T referent;         /* 会被GC回收的对象，也就是我们给过来被引用的对象 */

volatile ReferenceQueue<? super T> queue;  //引用队列，可以和下面的next搭配使用，形成链表
//Reference对象也是一个一个连起来的节点，这样才能放到ReferenceQueue中形成链表
volatile Reference next;

//即将被GC的引用链表
transient private Reference<T> discovered;  /* 由虚拟机操作 */

//pending与discovered一起构成了一个pending单向链表，标记为static类所有，pending为链表的头节点，discovered为链表当前
//Reference节点指向下一个节点的引用，这个队列是由JVM构建的，当对象除了被reference引用之外没有其它强引用了，JVM就会将指向
//需要回收的对象的Reference对象都放入到这个队列里面，这个队列会由下面的 Reference Hander 线程来处理。
private static Reference<Object> pending = null;
```

```java
static {    //Reference类的静态代码块
    ThreadGroup tg = Thread.currentThread().getThreadGroup();
    for (ThreadGroup tgn = tg;
         tgn != null;
         tg = tgn, tgn = tg.getParent());
    Thread handler = new ReferenceHandler(tg, "Reference Handler");   //在一开始的时候就会创建
    handler.setPriority(Thread.MAX_PRIORITY);   //以最高优先级启动
    handler.setDaemon(true);    //此线程直接作为一个守护线程
    handler.start();    //也就是说在一开始的时候这个守护线程就会启动

    ...
}
```

那么也就是说Reference Handler线程是在一开始就启动了，那么我们的关注点可以放在`tryHandlePending`方法上，看看这玩意到底在做个啥：

```java
static boolean tryHandlePending(boolean waitForNotify) {
    Reference<Object> r;
    Cleaner c;
    try {
        synchronized (lock) {   //加锁办事
          	//当Cleaner引用的DirectByteBuffer对象即将被回收时，pending会变成此Cleaner对象
          	//这里判断到pending不为null时就需要处理一下对象销毁了
            if (pending != null) {
                r = pending;
                // 'instanceof' 有时会导致内存溢出，所以将r从链表中移除之前就进行类型判断
                // 如果是Cleaner类型就给到c
                c = r instanceof Cleaner ? (Cleaner) r : null;
                // 将pending更新为链表下一个待回收元素
                pending = r.discovered;
                r.discovered = null;   //r不再引用下一个节点
            } else {
              	//否则就进入等待
                if (waitForNotify) {
                    lock.wait();
                }
                return waitForNotify;
            }
        }
    } catch (OutOfMemoryError x) {
        Thread.yield();
        return true;
    } catch (InterruptedException x) {
        return true;
    }

    // 如果元素是Cleaner类型，c在上面就会被赋值，这里就会执行其clean方法（破案了）
    if (c != null) {
        c.clean();
        return true;
    }

    ReferenceQueue<? super Object> q = r.queue;
    if (q != ReferenceQueue.NULL) q.enqueue(r);  //这个是引用队列，实际上就是我们之前在JVM篇中讲解的入队机制
    return true;
}
```

通过对源码的解读，我们就了解了直接缓冲区的内存加载释放整个流程。和堆缓冲区一样，当直接缓冲区没有任何强引用时，就有机会被GC正常回收掉并自动释放申请的内存。

我们接着来看看直接缓冲区的读写操作是如何进行的：

```java
public byte get() {
    return ((unsafe.getByte(ix(nextGetIndex()))));   //直接通过Unsafe类读取对应地址上的byte数据
}
```

```java
private long ix(int i) {
    return address + ((long)i << 0);   //ix现在是内存地址再加上i
}
```

我们接着来看看写操作：

```java
public ByteBuffer put(byte x) {
    unsafe.putByte(ix(nextPutIndex()), ((x)));
    return this;
}
```

可以看到无论是读取还是写入操作都是通过Unsafe类操作对应的内存地址完成的。

那么它的复制操作是如何实现的呢？

```java
public ByteBuffer duplicate() {
    return new DirectByteBuffer(this,
                                          this.markValue(),
                                          this.position(),
                                          this.limit(),
                                          this.capacity(),
                                          0);
}
```

```java
DirectByteBuffer(DirectBuffer db,         // 这里给的db是进行复制操作的DirectByteBuffer对象
                           int mark, int pos, int lim, int cap,
                           int off) {
    super(mark, pos, lim, cap);
    address = db.address() + off;   //直接继续使用之前申请的内存空间
    cleaner = null;   //因为用的是之前的内存空间，已经有对应的Cleaner了，这里不需要再搞一个
    att = db;   //将att设定为此对象
}
```

可以看到，如果是进行复制操作，那么会直接会继续使用执行复制操作的DirectByteBuffer申请的内存空间。不知道各位是否能够马上联想到一个问题，我们知道，如果执行复制操作的DirectByteBuffer对象失去了强引用被回收，那么就会触发Cleaner并进行内存释放，但是有个问题就是，这段内存空间可能复制出来的DirectByteBuffer对象还需要继续使用，这时肯定是不能进行回收的，所以说这里使用了att变量将之前的DirectByteBuffer对象进行引用，以防止其失去强引用被垃圾回收，所以只要不是原来的DirectByteBuffer对象和复制出来的DirectByteBuffer对象都失去强引用时，就不会导致这段内存空间被回收。

这样，我们之前的未解之谜为啥有个`att`也就得到答案了，有关直接缓冲区的介绍，就到这里为止。

***

## 通道

前面我们学习了NIO的基石——缓冲区，那么缓冲区具体用在什么地方呢，在本板块我们学习通道之后，相信各位就能知道了。那么，什么是通道呢？

在传统IO中，我们都是通过流进行传输，数据会源源不断从流中传出；而在NIO中，数据是放在缓冲区中进行管理，再使用通道将缓冲区中的数据传输到目的地。

### 通道接口层次

通道的根基接口是`Channel`，所以的派生接口和类都是从这里开始的，我们来看看它定义了哪些基本功能：

```java
public interface Channel extends Closeable {
    //通道是否处于开启状态
    public boolean isOpen();

    //因为通道开启也需要关闭，所以实现了Closeable接口，所以这个方法懂的都懂
    public void close() throws IOException;
}
```

我们接着来看看它的一些子接口，首先是最基本的读写操作：

```JAVA
public interface ReadableByteChannel extends Channel {
    //将通道中的数据读取到给定的缓冲区中
    public int read(ByteBuffer dst) throws IOException;
}
```

```java
public interface WritableByteChannel extends Channel {
  	//将给定缓冲区中的数据写入到通道中
    public int write(ByteBuffer src) throws IOException;
}
```

有了读写功能后，最后整合为了一个ByteChannel接口：

```java
public interface ByteChannel extends ReadableByteChannel, WritableByteChannel{

}
```

![image-20230306173149309](https://s2.loli.net/2023/03/06/Db75mNEcI2xgwM8.png)

在ByteChannel之下，还有更多的派生接口：

```java
//允许保留position和更改position的通道，以及对通道连接实体的相关操作
public interface SeekableByteChannel extends ByteChannel {
   	...

    //获取当前的position
    long position() throws IOException;

    //修改当前的position
    SeekableByteChannel position(long newPosition) throws IOException;

    //返回此通道连接到的实体（比如文件）的当前大小
    long size() throws IOException;

    //将此通道连接到的实体截断（比如文件，截断之后，文件后面一半就没了）为给定大小
    SeekableByteChannel truncate(long size) throws IOException;
}
```

接着我们来看，除了读写之外，Channel还可以具有响应中断的能力：

```java
public interface InterruptibleChannel extends Channel {
  	//当其他线程调用此方法时，在此通道上处于阻塞状态的线程会直接抛出 AsynchronousCloseException 异常
    public void close() throws IOException;
}
```

```java
//这是InterruptibleChannel的抽象实现，完成了一部分功能
public abstract class AbstractInterruptibleChannel implements Channel, InterruptibleChannel {
		//加锁关闭操作用到
    private final Object closeLock = new Object();
  	//当前Channel的开启状态
    private volatile boolean open = true;

    protected AbstractInterruptibleChannel() { }

    //关闭操作实现
    public final void close() throws IOException {
        synchronized (closeLock) {   //同时只能有一个线程进行此操作，加锁
            if (!open)   //如果已经关闭了，那么就不用继续了
                return;
            open = false;   //开启状态变成false
            implCloseChannel();   //开始关闭通道
        }
    }

    //该方法由 close 方法调用，以执行关闭通道的具体操作，仅当通道尚未关闭时才调用此方法，不会多次调用。
    protected abstract void implCloseChannel() throws IOException;

    public final boolean isOpen() {
        return open;
    }

    //开始阻塞（有可能一直阻塞下去）操作之前，需要调用此方法进行标记，
    protected final void begin() {
        ...
    }

  	//阻塞操作结束之后，也需要需要调用此方法，为了防止异常情况导致此方法没有被调用，建议放在finally中
    protected final void end(boolean completed)
				...
    }
		
		...
}
```

而之后的一些实现类，都是基于这些接口定义的方法去进行实现的，比如FileChannel：

![image-20230306173207144](https://s2.loli.net/2023/03/06/ZywX8BgGMJfWNSK.png)

这样，我们就大致了解了一下通道相关的接口定义，那么我来看看具体是如何如何使用的。

比如现在我们要实现从输入流中读取数据然后打印出来，那么之前传统IO的写法：

```java
public static void main(String[] args) throws IOException {
  	//数组创建好，一会用来存放从流中读取到的数据
  	byte[] data = new byte[10];
  	//直接使用输入流
    InputStream in = System.in;
    while (true) {
        int len;
        while ((len = in.read(data)) >= 0) {  //将输入流中的数据一次性读取到数组中
            System.out.print("读取到一批数据："+new String(data, 0, len));  //读取了多少打印多少
        }
    }
}
```

而现在我们使用通道之后：

```java
public static void main(String[] args) throws IOException {
  	//缓冲区创建好，一会就靠它来传输数据
    ByteBuffer buffer = ByteBuffer.allocate(10);
    //将System.in作为输入源，一会Channel就可以从这里读取数据，然后通过缓冲区装载一次性传递数据
    ReadableByteChannel readChannel = Channels.newChannel(System.in);
    while (true) {
        //将通道中的数据写到缓冲区中，缓冲区最多一次装10个
        readChannel.read(buffer);
        //写入操作结束之后，需要进行翻转，以便接下来的读取操作
        buffer.flip();
        //最后转换成String打印出来康康
        System.out.println("读取到一批数据："+new String(buffer.array(), 0, buffer.remaining()));
        //回到最开始的状态
        buffer.clear();
    }
}
```

乍一看，好像感觉也没啥区别，不就是把数组换成缓冲区了吗，效果都是一样的，数据也是从Channel中读取得到，并且通过缓冲区进行数据装载然后得到结果，但是，Channel不像流那样是单向的，它就像它的名字一样，一个通道可以从一端走到另一端，也可以从另一端走到这一端，我们后面进行介绍。

### 文件传输FileChannel

前面我们介绍了通道的基本情况，这里我们就来尝试实现一下文件的读取和写入，在传统IO中，文件的写入和输出都是依靠FileOutputStream和FileInputStream来完成的：

```java
public static void main(String[] args) throws IOException {
    try(FileOutputStream out = new FileOutputStream("test.txt");
        FileInputStream in = new FileInputStream("test.txt")){
        String data = "伞兵一号卢本伟准备就绪！";
        out.write(data.getBytes());   //向文件的输出流中写入数据，也就是把数据写到文件中
        out.flush();

        byte[] bytes = new byte[in.available()];
        in.read(bytes);    //从文件的输入流中读取文件的信息
        System.out.println(new String(bytes));
    }
}
```

而现在，我们只需要通过一个FileChannel就可以完成这两者的操作，获取文件通道的方式有以下几种：

```java
public static void main(String[] args) throws IOException {
    //1. 直接通过输入或输出流获取对应的通道
    FileInputStream in = new FileInputStream("test.txt");
    //但是这里的通道只支持读取或是写入操作
    FileChannel channel = in.getChannel();
    //创建一个容量为128的缓冲区
    ByteBuffer buffer = ByteBuffer.allocate(128);
    //从通道中将数据读取到缓冲区中
    channel.read(buffer);
    //翻转一下，接下来要读取了
    buffer.flip();

    System.out.println(new String(buffer.array(), 0, buffer.remaining()));
}
```

可以看到通过输入流获取的文件通道读取是没有任何问题的，但是写入操作：

```java
public static void main(String[] args) throws IOException {
    //1. 直接通过输入或输出流获取对应的通道
    FileInputStream in = new FileInputStream("test.txt");
    //但是这里的通道只支持读取或是写入操作
    FileChannel channel = in.getChannel();
    //尝试写入一下
    channel.write(ByteBuffer.wrap("伞兵一号卢本伟准备就绪！".getBytes()));
}
```

![image-20230306173252329](https://s2.loli.net/2023/03/06/UVQ8gIpHyGrveMO.png)

直接报错，说明只支持读取操作，那么输出流呢？

```java
public static void main(String[] args) throws IOException {
    //1. 直接通过输入或输出流获取对应的通道
    FileOutputStream out = new FileOutputStream("test.txt");
    //但是这里的通道只支持读取或是写入操作
    FileChannel channel = out.getChannel();
    //尝试写入一下
    channel.write(ByteBuffer.wrap("伞兵一号卢本伟准备就绪！".getBytes()));
}
```

可以看到能够正常进行写入，但是读取呢？

```java
public static void main(String[] args) throws IOException {
    //1. 直接通过输入或输出流获取对应的通道
    FileOutputStream out = new FileOutputStream("test.txt");
    //但是这里的通道只支持读取或是写入操作
    FileChannel channel = out.getChannel();

    ByteBuffer buffer = ByteBuffer.allocate(128);
    //从通道中将数据读取到缓冲区中
    channel.read(buffer);
    //翻转一下，接下来要读取了
    buffer.flip();

    System.out.println(new String(buffer.array(), 0, buffer.remaining()));
}
```

![image-20230306173302648](https://s2.loli.net/2023/03/06/isrDoy5pwRPxMuK.png)

可以看到输出流生成的Channel又不支持读取，所以说本质上还是保持着输入输出流的特性，但是之前不是说Channel又可以输入又可以输出吗？这里我们来看看第二种方式：

```java
//RandomAccessFile能够支持文件的随机访问，并且实现了数据流
public class RandomAccessFile implements DataOutput, DataInput, Closeable {
```

我们可以通过RandomAccessFile来创建通道：

```java
public static void main(String[] args) throws IOException {
    /*
      通过RandomAccessFile进行创建，注意后面的mode有几种：
      r        以只读的方式使用
      rw   读操作和写操作都可以
      rws  每当进行写操作，同步的刷新到磁盘，刷新内容和元数据
      rwd  每当进行写操作，同步的刷新到磁盘，刷新内容
     */
    try(RandomAccessFile f = new RandomAccessFile("test.txt", "")){
				
    }
}
```

现在我们来测试一下它的读写操作：

```java
public static void main(String[] args) throws IOException {
    /*
      通过RandomAccessFile进行创建，注意后面的mode有几种：
      r        以只读的方式使用
      rw   读操作和写操作都可以
      rws  每当进行写操作，同步的刷新到磁盘，刷新内容和元数据
      rwd  每当进行写操作，同步的刷新到磁盘，刷新内容
     */
    try(RandomAccessFile f = new RandomAccessFile("test.txt", "rw");  //这里设定为支持读写，这样创建的通道才能具有这些功能
        FileChannel channel = f.getChannel()){   //通过RandomAccessFile创建一个通道
        channel.write(ByteBuffer.wrap("伞兵二号马飞飞准备就绪！".getBytes()));

        System.out.println("写操作完成之后文件访问位置："+channel.position());  //注意读取也是从现在的位置开始
        channel.position(0);  //需要将位置变回到最前面，这样下面才能从文件的最开始进行读取

        ByteBuffer buffer = ByteBuffer.allocate(128);
        channel.read(buffer);
        buffer.flip();

        System.out.println(new String(buffer.array(), 0, buffer.remaining()));
    }
}
```

可以看到，一个FileChannel既可以完成文件读取，也可以完成文件的写入。

除了基本的读写操作，我们也可以直接对文件进行截断：

```java
public static void main(String[] args) throws IOException {
    try(RandomAccessFile f = new RandomAccessFile("test.txt", "rw");
        FileChannel channel = f.getChannel()){
        //截断文件，只留前20个字节
        channel.truncate(20);

        ByteBuffer buffer = ByteBuffer.allocate(128);
        channel.read(buffer);
        buffer.flip();
        System.out.println(new String(buffer.array(), 0, buffer.remaining()));
    }
}
```

可以看到文件的内容直接被截断了，文件内容就只剩一半了。

当然，如果我们要进行文件的拷贝，也是很方便的，只需要使用通道就可以，比如我们现在需要将一个通道的数据写入到另一个通道，就可以直接使用transferTo方法：

```java
public static void main(String[] args) throws IOException {
    try(FileOutputStream out = new FileOutputStream("test2.txt");
        FileInputStream in = new FileInputStream("test.txt")){

        FileChannel inChannel = in.getChannel();   //获取到test文件的通道
        inChannel.transferTo(0, inChannel.size(), out.getChannel());   //直接将test文件通道中的数据转到test2文件的通道中
    }
}
```

可以看到执行后，文件的内容全部被复制到另一个文件了。

当然，反向操作也是可以的：

```java
public static void main(String[] args) throws IOException {
    try(FileOutputStream out = new FileOutputStream("test2.txt");
        FileInputStream in = new FileInputStream("test.txt")){

        FileChannel inChannel = in.getChannel();   //获取到test文件的通道
        out.getChannel().transferFrom(inChannel, 0, inChannel.size());   //直接将从test文件通道中传来的数据转给test2文件的通道
    }
}
```

当我们要编辑某个文件时，通过使用MappedByteBuffer类，可以将其映射到内存中进行编辑，编辑的内容会同步更新到文件中：

```java
//注意一定要是可写的，不然无法进行修改操作
try(RandomAccessFile f = new RandomAccessFile("test.txt", "rw");
    FileChannel channel = f.getChannel()){

    //通过map方法映射文件的某一段内容，创建MappedByteBuffer对象
    //比如这里就是从第四个字节开始，映射10字节内容到内存中
  	//注意这里需要使用MapMode.READ_WRITE模式，其他模式无法保存数据到文件
    MappedByteBuffer buffer = channel.map(FileChannel.MapMode.READ_WRITE, 4, 10);

    //我们可以直接对在内存中的数据进行编辑，也就是编辑Buffer中的内容
  	//注意这里写入也是从pos位置开始的，默认是从0开始，相对于文件就是从第四个字节开始写
  	//注意我们只映射了10个字节，也就是写的内容不能超出10字节了
    buffer.put("yyds".getBytes());

    //编辑完成后，通过force方法将数据写回文件的映射区域
    buffer.force();
}
```

可以看到，文件的某一个区域已经被我们修改了，并且这里实际上使用的就是DirectByteBuffer直接缓冲区，效率还是很高的。

### 文件锁FileLock

我们可以创建一个跨进程文件锁来防止多个进程之间的文件争抢操作（注意这里是进程，不是线程）FileLock是文件锁，它能保证同一时间只有一个进程（程序）能够修改它，或者都只可以读，这样就解决了多进程间的同步文件，保证了安全性。但是需要注意的是，它进程级别的，不是线程级别的，他可以解决多个进程并发访问同一个文件的问题，但是它不适用于控制同一个进程中多个线程对一个文件的访问。

那么我们来看看如何使用文件锁：

```java
public static void main(String[] args) throws IOException, InterruptedException {
  	//创建RandomAccessFile对象，并拿到Channel
    RandomAccessFile f = new RandomAccessFile("test.txt", "rw");
    FileChannel channel = f.getChannel();
    System.out.println(new Date() + " 正在尝试获取文件锁...");
  	//接着我们直接使用lock方法进行加锁操作（如果其他进程已经加锁，那么会一直阻塞在这里）
  	//加锁操作支持对文件的某一段进行加锁，比如这里就是从0开始后的6个字节加锁，false代表这是一把独占锁
  	//范围锁甚至可以提前加到一个还未写入的位置上
    FileLock lock = channel.lock(0, 6, false);
    System.out.println(new Date() + " 已获取到文件锁！");
    Thread.sleep(5000);   //假设要处理5秒钟
    System.out.println(new Date() + " 操作完毕，释放文件锁！");
  	
  	//操作完成之后使用release方法进行锁释放
    lock.release();
}
```

有关共享锁和独占锁：

* 进程对文件加独占锁后，当前进程对文件可读可写，独占此文件，其它进程是不能读该文件进行读写操作的。
* 进程对文件加共享锁后，进程可以对文件进行读操作，但是无法进行写操作，共享锁可以被多个进程添加，但是只要存在共享锁，就不能添加独占锁。

现在我们来启动两个进程试试看，我们需要在IDEA中配置一下两个启动项：

![image-20230306173325374](https://s2.loli.net/2023/03/06/hJuSpsEeZ1QwLYv.png)

现在我们依次启动它们：

![image-20230306173336024](https://s2.loli.net/2023/03/06/4GsaTA2nQ3hlLW8.png)

![image-20230306173344360](https://s2.loli.net/2023/03/06/UmCOxBoMzlg9vFN.png)

可以看到确实是两个进程同一时间只能有一个进行访问，而另一个需要等待锁释放。

那么如果我们申请的是文件的不同部分呢？

```java
//其中一个进程锁 0 - 5
FileLock lock = channel.lock(0, 6, false);
//另一个进程锁 6 - 11
FileLock lock = channel.lock(6, 6, false);
```

可以看到，两个进程这时就可以同时进行加锁操作了，因为它们锁的是不同的段落。

那么要是交叉呢？

```java
//其中一个进程锁 0 - 5
FileLock lock = channel.lock(0, 6, false);
//另一个进程锁 3 - 8
FileLock lock = channel.lock(3, 6, false);
```

可以看到交叉的情况下也是会出现阻塞的。

接着我们来看看共享锁，共享锁允许多个进程同时加锁，但是不能进行写操作：

```java
public static void main(String[] args) throws IOException, InterruptedException {
        RandomAccessFile f = new RandomAccessFile("test.txt", "rw");
        FileChannel channel = f.getChannel();
        System.out.println(new Date() + " 正在尝试获取文件锁...");
        //现在使用共享锁
        FileLock lock = channel.lock(0, Long.MAX_VALUE, true);
        System.out.println(new Date() + " 已获取到文件锁！");
  			//进行写操作
        channel.write(ByteBuffer.wrap(new Date().toString().getBytes()));
       
        System.out.println(new Date() + " 操作完毕，释放文件锁！");
        //操作完成之后使用release方法进行锁释放
        lock.release();
    }
```

当我们进行写操作时：

![image-20230306173358569](https://s2.loli.net/2023/03/06/lJu1EaoOzQhXwHB.png)

可以看到直接抛出异常，说另一个程序已锁定文件的一部分，进程无法访问（某些系统或是环境实测无效，比如UP主的arm架构MacOS就不生效，这个异常是在Windows环境下运行得到的）

当然，我们也可以测试一下多个进行同时加共享锁：

```java
public static void main(String[] args) throws IOException, InterruptedException {
    RandomAccessFile f = new RandomAccessFile("test.txt", "rw");
    FileChannel channel = f.getChannel();
    System.out.println(new Date() + " 正在尝试获取文件锁...");

    FileLock lock = channel.lock(0, Long.MAX_VALUE, true);
    System.out.println(new Date() + " 已获取到文件锁！");
    Thread.sleep(5000);   //假设要处理5秒钟
    System.out.println(new Date() + " 操作完毕，释放文件锁！");
    
    lock.release();
}
```

可以看到结果是多个进程都能加共享锁：

![image-20230306173408914](https://s2.loli.net/2023/03/06/34puXxErM5QG2fq.png)

当然，除了直接使用`lock()`方法进行加锁之外，我们也可以使用`tryLock()`方法以非阻塞方式获取文件锁，但是如果获取锁失败会得到null：

```java
public static void main(String[] args) throws IOException, InterruptedException {
    RandomAccessFile f = new RandomAccessFile("test.txt", "rw");
    FileChannel channel = f.getChannel();
    System.out.println(new Date() + " 正在尝试获取文件锁...");

    FileLock lock = channel.tryLock(0, Long.MAX_VALUE, false);
    System.out.println(lock);
    Thread.sleep(5000);   //假设要处理5秒钟

    lock.release();
}
```

可以看到，两个进程都去尝试获取独占锁：

![image-20230306173431641](https://s2.loli.net/2023/03/06/CpxsIEaThjPBNY6.png)

![image-20230306173440947](https://s2.loli.net/2023/03/06/sbmrtvkESa8cZlL.png)

第一个成功加锁的进程获得了对应的锁对象，而第二个进程直接得到的是`null`。

到这里，有关文件锁的相关内容就差不多了。

***

## 多路复用网络通信

前面我们已经介绍了NIO框架的两大核心：Buffer和Channel，我们接着来看看最后一个内容。

### 传统阻塞I/O网络通信

说起网络通信，相信各位并不陌生，正是因为网络的存在我们才能走进现代化的社会，在JavaWeb阶段，我们学习了如何使用Socket建立TCP连接进行网络通信：

```java
public static void main(String[] args) {
    try(ServerSocket server = new ServerSocket(8080)){    //将服务端创建在端口8080上
        System.out.println("正在等待客户端连接...");
        Socket socket = server.accept();
        System.out.println("客户端已连接，IP地址为："+socket.getInetAddress().getHostAddress());
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));  //通过
        System.out.print("接收到客户端数据：");
        System.out.println(reader.readLine());
        OutputStreamWriter writer = new OutputStreamWriter(socket.getOutputStream());
        writer.write("已收到！");
        writer.flush();
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

```java
public static void main(String[] args) {
    try (Socket socket = new Socket("localhost", 8080);
         Scanner scanner = new Scanner(System.in)){
        System.out.println("已连接到服务端！");
        OutputStream stream = socket.getOutputStream();
        OutputStreamWriter writer = new OutputStreamWriter(stream);  //通过转换流来帮助我们快速写入内容
        System.out.println("请输入要发送给服务端的内容：");
        String text = scanner.nextLine();
        writer.write(text+'\n');   //因为对方是readLine()这里加个换行符
        writer.flush();
        System.out.println("数据已发送："+text);
        BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
        System.out.println("收到服务器返回："+reader.readLine());
    }catch (IOException e){
        System.out.println("服务端连接失败！");
        e.printStackTrace();
    }finally {
        System.out.println("客户端断开连接！");
    }
}
```

当然，我们也可以使用前面讲解的通道来进行通信：

```java
public static void main(String[] args) {
    //创建一个新的ServerSocketChannel，一会直接使用SocketChannel进行网络IO操作
    try (ServerSocketChannel serverChannel = ServerSocketChannel.open()){
        //依然是将其绑定到8080端口
        serverChannel.bind(new InetSocketAddress(8080));
        //同样是调用accept()方法，阻塞等待新的连接到来
        SocketChannel socket = serverChannel.accept();
        //因为是通道，两端的信息都是可以明确的，这里获取远端地址，当然也可以获取本地地址
        System.out.println("客户端已连接，IP地址为："+socket.getRemoteAddress());

        //使用缓冲区进行数据接收
        ByteBuffer buffer = ByteBuffer.allocate(128);
        socket.read(buffer);   //SocketChannel同时实现了读写通道接口，所以可以直接进行双向操作
        buffer.flip();
        System.out.print("接收到客户端数据："+new String(buffer.array(), 0, buffer.remaining()));

        //直接向通道中写入数据就行
        socket.write(ByteBuffer.wrap("已收到！".getBytes()));

        //记得关
        socket.close();
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}
```

```java
public static void main(String[] args) {
    //创建一个新的SocketChannel，一会通过通道进行通信
    try (SocketChannel channel = SocketChannel.open(new InetSocketAddress("localhost", 8080));
         Scanner scanner = new Scanner(System.in)){
        System.out.println("已连接到服务端！");
        System.out.println("请输入要发送给服务端的内容：");
        String text = scanner.nextLine();
        //直接向通道中写入数据，真舒服
        channel.write(ByteBuffer.wrap(text.getBytes()));

        ByteBuffer buffer = ByteBuffer.allocate(128);
        channel.read(buffer);   //直接从通道中读取数据
        buffer.flip();
        System.out.println("收到服务器返回："+new String(buffer.array(), 0, buffer.remaining()));
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}
```

虽然可以通过传统的Socket进行网络通信，但是我们发现，如果要进行IO操作，我们需要单独创建一个线程来进行处理，比如现在有很多个客户端，服务端需要同时进行处理，那么如果我们要处理这些客户端的请求，那么我们就只能单独为其创建一个线程来进行处理：

![image-20230306173456889](https://s2.loli.net/2023/03/06/FOrzfHUKTNonJvt.png)

虽然这样看起来比较合理，但是随着客户端数量的增加，如果要保持持续通信，那么就不能摧毁这些线程，而是需要一直保留（但是实际上很多时候只是保持连接，一直在阻塞等待客户端的读写操作，IO操作的频率很低，这样就白白占用了一条线程，很多时候都是站着茅坑不拉屎），但是我们的线程不可能无限制的进行创建，总有一天会耗尽服务端的资源，那么现在怎么办呢，关键是现在又有很多客户端源源不断地连接并进行操作，这时，我们就可以利用NIO为我们提供的多路复用编程模型。

我们来看看NIO为我们提供的模型：

![image-20230306173506227](https://s2.loli.net/2023/03/06/jFS86QyLHAwn9fR.png)

服务端不再是一个单纯通过`accept()`方法来创建连接的机制了，而是根据客户端不同的状态，Selector会不断轮询，只有客户端在对应的状态时，比如真正开始读写操作时，才会创建线程或进行处理（这样就不会一直阻塞等待某个客户端的IO操作了），而不是创建之后需要一直保持连接，即使没有任何的读写操作。这样就不会因为占着茅坑不拉屎导致线程无限制地创建下去了。

通过这种方式，甚至单线程都能做到高效的复用，最典型的例子就是Redis了，因为内存的速度非常快，多线程上下文的开销就会显得有些拖后腿，还不如直接单线程简单高效，这也是为什么Redis单线程也能这么快的原因。

因此，我们就从NIO框架的第三个核心内容：Selector，开始讲起。

### 选择器与I/O多路复用

前面我们大概了解了一下选择器，我们知道，选择器是当具体有某一个状态（比如读、写、请求）已经就绪时，才会进行处理，而不是让我们的程序主动地进行等待。

既然我们现在需要实现IO多路复用，那么我们来看看常见的IO多路复用模型，也就是Selector的实现方案，比如现在有很多个用户连接到我们的服务器：

* **select**：当这些连接出现具体的某个状态时，只是知道已经就绪了，但是不知道详具体是哪一个连接已经就绪，每次调用都进行线性遍历所有连接，时间复杂度为`O(n)`，并且存在最大连接数限制。
* **poll**：同上，但是由于底层采用链表，所以没有最大连接数限制。
* **epoll**：采用事件通知方式，当某个连接就绪，能够直接进行精准通知（这是因为在内核实现中epoll是根据每个fd上面的callback函数实现的，只要就绪会会直接回调callback函数，实现精准通知，但是只有Linux支持这种方式），时间复杂度`O(1)`，Java在Linux环境下正是采用的这种模式进行实现的。

好了，既然多路复用模型了解完毕了，那么我们就来看看如何让我们的网络通信实现多路复用：

```java
public static void main(String[] args) {
    try (ServerSocketChannel serverChannel = ServerSocketChannel.open();
         Selector selector = Selector.open()){   //开启一个新的Selector，这玩意也是要关闭释放资源的
        serverChannel.bind(new InetSocketAddress(8080));
        //要使用选择器进行操作，必须使用非阻塞的方式，这样才不会像阻塞IO那样卡在accept()，而是直接通过，让选择器去进行下一步操作
        serverChannel.configureBlocking(false);
        //将选择器注册到ServerSocketChannel中，后面是选择需要监听的时间，只有发生对应事件时才会进行选择，多个事件用 | 连接，注意，并不是所有的Channel都支持以下全部四个事件，可能只支持部分
        //因为是ServerSocketChannel这里我们就监听accept就可以了，等待客户端连接
        //SelectionKey.OP_CONNECT --- 连接就绪事件，表示客户端与服务器的连接已经建立成功
        //SelectionKey.OP_ACCEPT --- 接收连接事件，表示服务器监听到了客户连接，服务器可以接收这个连接了
        //SelectionKey.OP_READ --- 读 就绪事件，表示通道中已经有了可读的数据，可以执行读操作了
        //SelectionKey.OP_WRITE --- 写 就绪事件，表示已经可以向通道写数据了（这玩意比较特殊，一般情况下因为都是可以写入的，所以可能会无限循环）
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);
        while (true) {   //无限循环等待新的用户网络操作
            //每次选择都可能会选出多个已经就绪的网络操作，没有操作时会暂时阻塞
            int count = selector.select();
            System.out.println("监听到 "+count+" 个事件");
            Set<SelectionKey> selectionKeys = selector.selectedKeys();
            Iterator<SelectionKey> iterator = selectionKeys.iterator();
            while (iterator.hasNext()) {
                SelectionKey key = iterator.next();
                //根据不同的事件类型，执行不同的操作即可
                if(key.isAcceptable()) {  //如果当前ServerSocketChannel已经做好准备处理Accept
                    SocketChannel channel = serverChannel.accept();
                    System.out.println("客户端已连接，IP地址为："+channel.getRemoteAddress());
                    //现在连接就建立好了，接着我们需要将连接也注册选择器，比如我们需要当这个连接有内容可读时就进行处理
                    channel.configureBlocking(false);
                    channel.register(selector, SelectionKey.OP_READ);
                    //这样就在连接建立时完成了注册
                } else if(key.isReadable()) {    //如果当前连接有可读的数据并且可以写，那么就开始处理
                    SocketChannel channel = (SocketChannel) key.channel();
                    ByteBuffer buffer = ByteBuffer.allocate(128);
                    channel.read(buffer);
                    buffer.flip();
                    System.out.println("接收到客户端数据："+new String(buffer.array(), 0, buffer.remaining()));

                    //直接向通道中写入数据就行
                    channel.write(ByteBuffer.wrap("已收到！".getBytes()));
                    //别关，说不定用户还要继续通信呢
                }
                //处理完成后，一定记得移出迭代器，不然下次还有
                iterator.remove();
            }
        }
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}
```

接着我们来编写一下客户客户端：

```java
public static void main(String[] args) {
    //创建一个新的SocketChannel，一会通过通道进行通信
    try (SocketChannel channel = SocketChannel.open(new InetSocketAddress("localhost", 8080));
         Scanner scanner = new Scanner(System.in)){
        System.out.println("已连接到服务端！");
        while (true) {   //咱给它套个无限循环，这样就能一直发消息了
            System.out.println("请输入要发送给服务端的内容：");
            String text = scanner.nextLine();
            //直接向通道中写入数据，真舒服
            channel.write(ByteBuffer.wrap(text.getBytes()));
            System.out.println("已发送！");
            ByteBuffer buffer = ByteBuffer.allocate(128);
            channel.read(buffer);   //直接从通道中读取数据
            buffer.flip();
            System.out.println("收到服务器返回："+new String(buffer.array(), 0, buffer.remaining()));
        }
    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}
```

我们来看看效果：

![image-20230306173522171](https://s2.loli.net/2023/03/06/NM3AosF5fYcJmCe.png)

![image-20230306173532269](https://s2.loli.net/2023/03/06/Skr5gyIlzojnPGf.png)

可以看到成功实现了，当然各位也可以跟自己的室友一起开客户端进行测试，现在，我们只用了一个线程，就能够同时处理多个请求，可见多路复用是多么重要。

### 实现Reactor模式

前面我们简单实现了多路复用网络通信，我们接着来了解一下Reactor模式，对我们的服务端进行优化。

现在我们来看看如何进行优化，我们首先抽象出两个组件，Reactor线程和Handler处理器：

* Reactor线程：负责响应IO事件，并分发到Handler处理器。新的事件包含连接建立就绪、读就绪、写就绪等。
* Handler处理器：执行非阻塞的操作。

实际上我们之前编写的算是一种单线程Reactor的朴素模型（面向过程的写法），我们来看看标准的写法：

![image-20230306173542506](https://s2.loli.net/2023/03/06/IFmc73Bb9ihwE8V.png)

客户端还是按照我们上面的方式连接到Reactor，并通过选择器走到Acceptor或是Handler，Acceptor主要负责客户端连接的建立，Handler负责读写操作，代码如下，首先是Handler：

```java
public class Handler implements Runnable{

    private final SocketChannel channel;

    public Handler(SocketChannel channel) {
        this.channel = channel;
    }

    @Override
    public void run() {
        try {
            ByteBuffer buffer = ByteBuffer.allocate(128);
            channel.read(buffer);
            buffer.flip();
            System.out.println("接收到客户端数据："+new String(buffer.array(), 0, buffer.remaining()));
            channel.write(ByteBuffer.wrap("已收到！".getBytes()));
        }catch (IOException e){
            e.printStackTrace();
        }
    }
}
```

接着是Acceptor，实际上就是把上面的业务代码搬个位置罢了：

```java
/**
 * Acceptor主要用于处理连接操作
 */
public class Acceptor implements Runnable{

    private final ServerSocketChannel serverChannel;
    private final Selector selector;

    public Acceptor(ServerSocketChannel serverChannel, Selector selector) {
        this.serverChannel = serverChannel;
        this.selector = selector;
    }

    @Override
    public void run() {
        try{
            SocketChannel channel = serverChannel.accept();
            System.out.println("客户端已连接，IP地址为："+channel.getRemoteAddress());
            channel.configureBlocking(false);
            //这里在注册时，创建好对应的Handler，这样在Reactor中分发的时候就可以直接调用Handler了
            channel.register(selector, SelectionKey.OP_READ, new Handler(channel));
        }catch (IOException e){
            e.printStackTrace();
        }
    }
}
```

这里我们在注册时丢了一个附加对象进去，这个附加对象会在选择器选择到此通道上时，可以通过`attachment()`方法进行获取，对于我们简化代码有大作用，一会展示，我们接着来看看Reactor：

```java
public class Reactor implements Closeable, Runnable{

    private final ServerSocketChannel serverChannel;
    private final Selector selector;
    public Reactor() throws IOException{
        serverChannel = ServerSocketChannel.open();
        selector = Selector.open();
    }

    @Override
    public void run() {
        try {
            serverChannel.bind(new InetSocketAddress(8080));
            serverChannel.configureBlocking(false);
            //注册时，将Acceptor作为附加对象存放，当选择器选择后也可以获取到
            serverChannel.register(selector, SelectionKey.OP_ACCEPT, new Acceptor(serverChannel, selector));
            while (true) {
                int count = selector.select();
                System.out.println("监听到 "+count+" 个事件");
                Set<SelectionKey> selectionKeys = selector.selectedKeys();
                Iterator<SelectionKey> iterator = selectionKeys.iterator();
                while (iterator.hasNext()) {
                    this.dispatch(iterator.next());   //通过dispatch方法进行分发
                    iterator.remove();
                }
            }
        }catch (IOException e) {
            e.printStackTrace();
        }
    }

    //通过此方法进行分发
    private void dispatch(SelectionKey key){
        Object att = key.attachment();   //获取attachment，ServerSocketChannel和对应的客户端Channel都添加了的
        if(att instanceof Runnable) {
            ((Runnable) att).run();   //由于Handler和Acceptor都实现自Runnable接口，这里就统一调用一下
        }   //这样就实现了对应的时候调用对应的Handler或是Acceptor了
    }

    //用了记得关，保持好习惯，就像看完视频要三连一样
    @Override
    public void close() throws IOException {
        serverChannel.close();
        selector.close();
    }
}
```

最后我们编写一下主类：

```java
public static void main(String[] args) {
    //创建Reactor对象，启动，完事
    try (Reactor reactor = new Reactor()){
        reactor.run();
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

这样，我们就实现了单线程Reactor模式，注意全程使用到的都只是一个线程，没有创建新的线程来处理任何事情。

但是单线程始终没办法应对大量的请求，如果请求量上去了，单线程还是很不够用，接着我们来看看多线程Reactor模式，它创建了多个线程处理，我们可以将数据读取完成之后的操作交给线程池来执行：

![image-20230306173555763](https://s2.loli.net/2023/03/06/DlMSEZ2dvc3pQHJ.png)

其实我们只需要稍微修改一下Handler就行了：

```java
public class Handler implements Runnable{
		//把线程池给安排了，10个线程
    private static final ExecutorService POOL = Executors.newFixedThreadPool(10);
    private final SocketChannel channel;
    public Handler(SocketChannel channel) {
        this.channel = channel;
    }

    @Override
    public void run() {
        try {
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            channel.read(buffer);
            buffer.flip();
            POOL.submit(() -> {
                try {
                    System.out.println("接收到客户端数据："+new String(buffer.array(), 0, buffer.remaining()));
                    channel.write(ByteBuffer.wrap("已收到！".getBytes()));
                }catch (IOException e){
                    e.printStackTrace();
                }
            });
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}
```

这样，在数据读出之后，就可以将数据处理交给线程池执行。

但是这样感觉还是划分的不够，一个Reactor需要同时处理来自客户端的所有操作请求，显得有些乏力，那么不妨我们将Reactor做成一主多从的模式，让主Reactor只负责Accept操作，而其他的Reactor进行各自的其他操作：

![image-20230306173607113](https://s2.loli.net/2023/03/06/1DMlvbdLxpca3f5.png)

现在我们来重新设计一下我们的代码，Reactor类就作为主节点，不进行任何修改，我们来修改一下其他的：

```java
//SubReactor作为从Reactor
public class SubReactor implements Runnable, Closeable {
		//每个从Reactor也有一个Selector
    private final Selector selector;
	
  	//创建一个4线程的线程池，也就是四个从Reactor工作
    private static final ExecutorService POOL = Executors.newFixedThreadPool(4);
    private static final SubReactor[] reactors = new SubReactor[4];
    private static int selectedIndex = 0;  //采用轮询机制，每接受一个新的连接，就轮询分配给四个从Reactor
    static {   //在一开始的时候就让4个从Reactor跑起来
        for (int i = 0; i < 4; i++) {
            try {
                reactors[i] = new SubReactor();
                POOL.submit(reactors[i]);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }
		//轮询获取下一个Selector（Acceptor用）
    public static Selector nextSelector(){
        Selector selector = reactors[selectedIndex].selector;
        selectedIndex = (selectedIndex + 1) % 4;
        return selector;
    }

    private SubReactor() throws IOException {
        selector = Selector.open();
    }

    @Override
    public void run() {
        try {   //启动后直接等待selector监听到对应的事件即可，其他的操作逻辑和Reactor一致
            while (true) {
                int count = selector.select();
                System.out.println(Thread.currentThread().getName()+" >> 监听到 "+count+" 个事件");
                Set<SelectionKey> selectionKeys = selector.selectedKeys();
                Iterator<SelectionKey> iterator = selectionKeys.iterator();
                while (iterator.hasNext()) {
                    this.dispatch(iterator.next());
                    iterator.remove();
                }
            }
        }catch (IOException e) {
            e.printStackTrace();
        }
    }

    private void dispatch(SelectionKey key){
        Object att = key.attachment();
        if(att instanceof Runnable) {
            ((Runnable) att).run();
        }
    }

    @Override
    public void close() throws IOException {
        selector.close();
    }
}
```

我们接着来修改一下Acceptor类：

```java
public class Acceptor implements Runnable{

    private final ServerSocketChannel serverChannel;   //只需要一个ServerSocketChannel就行了

    public Acceptor(ServerSocketChannel serverChannel) {
        this.serverChannel = serverChannel;
    }

    @Override
    public void run() {
        try{
            SocketChannel channel = serverChannel.accept();   //还是正常进行Accept操作，得到SocketChannel
            System.out.println(Thread.currentThread().getName()+" >> 客户端已连接，IP地址为："+channel.getRemoteAddress());
            channel.configureBlocking(false);
            Selector selector = SubReactor.nextSelector();   //选取下一个从Reactor的Selector
            selector.wakeup();    //在注册之前唤醒一下防止卡死
            channel.register(selector, SelectionKey.OP_READ, new Handler(channel));  //注意现在注册的是从Reactor的Selector
        }catch (IOException e){
            e.printStackTrace();
        }
    }
}
```

现在，SocketChannel相关的操作就由从Reactor进行处理了，而不是一律交给主Reactor进行操作。

至此，我们已经了解了**NIO的三大组件：Buffer、Channel、Selector**，有关NIO基础相关的内容，就讲解到这里。下一章我们将继续讲解基于NIO实现的高性能网络通信框架Netty。