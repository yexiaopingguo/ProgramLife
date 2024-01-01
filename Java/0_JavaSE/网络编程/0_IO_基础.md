![image-20221004131436371](https://s2.loli.net/2022/10/04/SkAn9RQpqC4tVW5.png)

## Java I/O

**注意：**这块会涉及到**操作系统**和**计算机组成原理**相关内容。

I/O简而言之，就是输入输出，那么为什么会有I/O呢？其实I/O无时无刻都在我们的身边，比如读取硬盘上的文件，网络文件传输，鼠标键盘输入，也可以是接受单片机发回的数据，而能够支持这些操作的设备就是I/O设备。

常见的I/O设备一般是鼠标、键盘这类通过USB进行传输的外设或者是通过Sata接口或是M.2连接的硬盘。一般情况下，这些设备是由CPU发出指令通过南桥芯片间接进行控制，而不是由CPU直接操作。

而我们在程序中，想要读取这些外部连接的I/O设备中的内容，就需要将数据传输到内存中。而需要实现这样的操作，单单凭借一个小的程序是无法做到的，而操作系统（如：Windows/Linux/MacOS）就是专门用于控制和管理计算机硬件和软件资源的软件，我们需要读取一个IO设备的内容时，就可以向操作系统发出请求，由操作系统帮助我们来和底层的硬件交互以完成我们的读取/写入请求。

从读取硬盘文件的角度来说，不同的操作系统有着不同的文件系统（也就是文件在硬盘中的存储排列方式，如Windows就是NTFS、MacOS就是APFS），硬盘只能存储一个个0和1这样的二进制数据，至于0和1如何排列，各自又代表什么意思，就是由操作系统的文件系统来决定的。从网络通信角度来说，网络信号通过网卡等设备翻译为二进制信号，再交给系统进行读取，最后再由操作系统来给到程序。

（传统的SATA硬盘就是通过SATA线与电脑主板相连，这样才可以读取到数据）

JDK提供了一套用于IO操作的框架，为了方便我们开发者使用，就定义了一个像水流一样，根据流的传输方向和读取单位，分为字节流InputStream和OutputStream以及字符流Reader和Writer的IO框架，当然，这里的Stream并不是前面集合框架认识的Stream，这里的流指的是数据流，通过流，我们就可以一直从流中读取数据，直到读取到尽头，或是不断向其中写入数据，直到我们写入完成，而这类IO就是我们所说的BIO，也是Java中I/O操作的默认模型。

### IO/BIO/NIO/AIO 区别

> - IO是传统的阻塞I/O模型，一个线程处理一个I/O操作。
>
> IO是最传统的I/O模型，它使用阻塞方式处理I/O操作。在阻塞I/O中，当一个I/O操作执行时，线程会被阻塞，直到操作完成。这意味着线程在执行I/O操作时无法做其他工作。在Java中，常见的阻塞I/O类包括InputStream和OutputStream。
>
> - BIO是同步阻塞I/O模型，一个线程处理一个I/O操作，直到操作完成。
>
> BIO是最基本的I/O模型，也是Java中I/O操作的默认模型。在BIO中，所有的I/O操作都是阻塞的，这意味着当一个I/O操作执行时，线程会被阻塞，直到操作完成。BIO适用于连接数较少且每个连接较为稳定的场景。在Java中，常见的BIO类包括Socket和ServerSocket。
>
> - NIO是非阻塞I/O模型，一个线程可以处理多个并发的I/O操作。
>
> NIO引入了一种同步非阻塞的I/O模型，它允许单个线程管理多个并发的I/O操作。在NIO中，线程从一个通道（Channel）读取数据并将其存入缓冲区（Buffer），然后可以进行其他任务。当数据准备好时，线程可以继续处理它。NIO使用选择器（Selector）来监听多个通道的I/O事件，从而实现非阻塞I/O。在Java中，NIO的核心类包括Channel、Buffer和Selector。
>
> - AIO是异步非阻塞I/O模型，应用程序可以在I/O操作完成之前继续执行其他任务。
>
> AIO是Java 7中引入的一种更高级的I/O模型。它也被称为异步I/O，因为它在进行I/O操作时不会阻塞线程。在AIO中，应用程序发起I/O操作后，可以继续执行其他任务。当操作完成时，系统会通知应用程序。AIO通过回调机制来处理I/O事件，应用程序需要提供回调函数来处理完成的I/O操作。在Java中，AIO的核心类包括AsynchronousSocketChannel和CompletionHandler。

字节流一次读取一个字节，也就是一个`byte`的大小，而字符流顾名思义，就是一次读取一个字符，也就是一个`char`的大小（在读取纯文本文件的时候更加适合），有关这两种流，会在后面详细介绍，这个章节我们需要学习16个关键的流。

### 分类

<img src="https://pdai.tech/images/io/java-io-category-3.png"  />

### 文件字节流

要学习和使用IO，首先就要从最易于理解的读取文件开始说起。

首先介绍一下FileInputStream，我们可以通过它来获取文件的输入流：

```java
public static void main(String[] args) {
    try {   //注意，IO相关操作会有很多影响因素，有可能出现异常，所以需要明确进行处理
        FileInputStream inputStream = new FileInputStream("路径");
        //路径支持相对路径和绝对路径
    } catch (FileNotFoundException e) {
        e.printStackTrace();
    }
}
```

相对路径是在当前运行目录（就是你在哪个目录运行java命令启动Java程序的）的路径下寻找文件，而绝对路径，是从根目录开始寻找。路径分割符支持使用`/`或是`\\`，但是不能写为`\`因为它是转义字符！比如在Windows下：

```
C://User/lbw/nb    这个就是一个绝对路径，因为是从盘符开始的
test/test          这个就是一个相对路径，因为并不是从盘符开始的，而是一个直接的路径
```

在Linux和MacOS下：

```
/root/tmp       这个就是一个绝对路径，绝对路径以/开头
test/test       这个就是一个相对路径，不是以/开头的
```

当然，这个其实还是很好理解的，我们在使用时注意一下就行了。

在使用完成一个流之后，必须关闭这个流来完成对资源的释放，否则资源会被一直占用：

```java
public static void main(String[] args) {
    FileInputStream inputStream = null;    //定义可以先放在try外部
    try {
        inputStream = new FileInputStream("路径");
    } catch (FileNotFoundException e) {
        e.printStackTrace();
    } finally {
        try {    //建议在finally中进行，因为关闭流是任何情况都必须要执行的！
            if(inputStream != null) inputStream.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

虽然这样的写法才是最保险的，但是显得过于繁琐了，尤其是finally中再次嵌套了一个try-catch块，因此在JDK1.7新增了try-with-resource语法，用于简化这样的写法（本质上还是和这样的操作一致，只是换了个写法）

```java
public static void main(String[] args) {

    //注意，这种语法只支持实现了AutoCloseable接口的类！
    try(FileInputStream inputStream = new FileInputStream("路径")) {   //直接在try()中定义要在完成之后释放的资源

    } catch (IOException e) {   //这里变成IOException是因为调用close()可能会出现，而FileNotFoundException是继承自IOException的
        e.printStackTrace();
    }
    //无需再编写finally语句块，因为在最后自动帮我们调用了close()
}
```

之后为了方便，我们都使用此语法进行教学。

现在我们拿到了文件的输入流，那么怎么才能读取文件里面的内容呢？我们可以使用`read`方法：

```java
public static void main(String[] args) {
    //test.txt：a
    try(FileInputStream inputStream = new FileInputStream("test.txt")) {
        //使用read()方法进行字符读取
        System.out.println((char) inputStream.read());  //读取一个字节的数据（英文字母只占1字节，中文占2字节）
        System.out.println(inputStream.read());   //唯一一个字节的内容已经读完了，再次读取返回-1表示没有内容了
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

使用read可以直接读取一个字节的数据，注意，流的内容是有限的，读取一个少一个。我们如果想一次性全部读取的话，可以直接使用一个while循环来完成：

```java
public static void main(String[] args) {
    //test.txt：abcd
    try(FileInputStream inputStream = new FileInputStream("test.txt")) {
        int tmp;
        while ((tmp = inputStream.read()) != -1){   //通过while循环来一次性读完内容
            System.out.println((char)tmp);
        }
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

使用`available`方法能查看当前可读的剩余字节数量（注意：并不一定真实的数据量就是这么多，尤其是在网络I/O操作时，这个方法只能进行一个预估也可以说是暂时能一次性可以读取的数量，当然在磁盘IO下，一般情况都是真实的数据量）

```java
try(FileInputStream inputStream = new FileInputStream("test.txt")) {
    System.out.println(inputStream.available());  //查看剩余数量
}catch (IOException e){
    e.printStackTrace();
}
```

当然，一个一个读取效率太低了，那能否一次性全部读取呢？我们可以预置一个合适容量的byte[]数组来存放：

```java
public static void main(String[] args) {
    //test.txt：abcd
    try(FileInputStream inputStream = new FileInputStream("test.txt")) {
        byte[] bytes = new byte[inputStream.available()];   //我们可以提前准备好合适容量的byte数组来存放
        System.out.println(inputStream.read(bytes));   //一次性读取全部内容（返回值是读取的字节数）
        System.out.println(new String(bytes));   //通过String(byte[])构造方法得到字符串
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

也可以控制要读取数量：

```java
System.out.println(inputStream.read(bytes, 1, 2));   //第二个参数是从给定数组的哪个位置开始放入内容，第三个参数是读取流中的字节数
```

**注意**：一次性读取同单个读取一样，当没有任何数据可读时，依然会返回-1

通过`skip()`方法可以跳过指定数量的字节：

```java
public static void main(String[] args) {
    //test.txt：abcd
    try(FileInputStream inputStream = new FileInputStream("test.txt")) {
        System.out.println(inputStream.skip(1));
        System.out.println((char) inputStream.read());   //跳过了一个字节
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

注意：FileInputStream是不支持`reset()`的，虽然有这个方法，但是这里先不提及。

既然有输入流，那么文件输出流也是必不可少的：

```java
public static void main(String[] args) {
    //输出流也需要在最后调用close()方法，并且同样支持try-with-resource
    try(FileOutputStream outputStream = new FileOutputStream("output.txt")) {
        //注意：若此文件不存在，会直接创建这个文件！
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

输出流没有`read()`操作而是`write()`操作，使用方法同输入流一样，只不过现在的方向变为我们向文件里写入内容：

```java
public static void main(String[] args) {
    try(FileOutputStream outputStream = new FileOutputStream("output.txt")) {
        outputStream.write('c');   //同read一样，可以直接写入内容
      	outputStream.write("lbwnb".getBytes());   //也可以直接写入byte[]
      	outputStream.write("lbwnb".getBytes(), 0, 1);  //同上输入流
      	outputStream.flush();  //建议在最后执行一次刷新操作（强制写入）来保证数据正确写入到硬盘文件中
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

那么如果是我只想在文件尾部进行追加写入数据呢？我们可以调用另一个构造方法来实现：

```java
public static void main(String[] args) {
    try(FileOutputStream outputStream = new FileOutputStream("output.txt", true)) {  //true表示开启追加模式
        outputStream.write("lb".getBytes());   //现在只会进行追加写入，而不是直接替换原文件内容
        outputStream.flush();
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

利用输入流和输出流，就可以轻松实现文件的拷贝了：

```java
public static void main(String[] args) {
    try(FileOutputStream outputStream = new FileOutputStream("output.txt");
        FileInputStream inputStream = new FileInputStream("test.txt")) {   //可以写入多个
        byte[] bytes = new byte[10];    //使用长度为10的byte[]做传输媒介
        int tmp;   //存储本地读取字节数
        while ((tmp = inputStream.read(bytes)) != -1){   //直到读取完成为止
            outputStream.write(bytes, 0, tmp);    //写入对应长度的数据到输出流
        }
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

### 文件字符流

字符流不同于字节，字符流是以一个具体的字符进行读取，因此它只适合读纯文本的文件，如果是其他类型的文件不适用：

```java
public static void main(String[] args) {
    try(FileReader reader = new FileReader("test.txt")){
      	reader.skip(1);   //现在跳过的是一个字符
        System.out.println((char) reader.read());   //现在是按字符进行读取，而不是字节，因此可以直接读取到中文字符
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

同理，字符流只支持`char[]`类型作为存储：

```java
public static void main(String[] args) {
    try(FileReader reader = new FileReader("test.txt")){
        char[] str = new char[10];
        reader.read(str);
        System.out.println(str);   //直接读取到char[]中
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

既然有了Reader肯定也有Writer：

```java
public static void main(String[] args) {
    try(FileWriter writer = new FileWriter("output.txt")){
      	writer.getEncoding();   //支持获取编码（不同的文本文件可能会有不同的编码类型）
       writer.write('牛');
       writer.append('牛');   //其实功能和write一样
      	writer.flush();   //刷新
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

我们发现不仅有`write()`方法，还有一个`append()`方法，但是实际上他们效果是一样的，看源码：

```java
public Writer append(char c) throws IOException {
    write(c);
    return this;
}
```

append支持像StringBuilder那样的链式调用，返回的是Writer对象本身。

**练习**：尝试一下用Reader和Writer来拷贝纯文本文件。

这里需要额外介绍一下File类，它是专门用于表示一个文件或文件夹，只不过它只是代表这个文件，但并不是这个文件本身。通过File对象，可以更好地管理和操作硬盘上的文件。

```java
public static void main(String[] args) {
    File file = new File("test.txt");   //直接创建文件对象，可以是相对路径，也可以是绝对路径
    System.out.println(file.exists());   //此文件是否存在
    System.out.println(file.length());   //获取文件的大小
    System.out.println(file.isDirectory());   //是否为一个文件夹
    System.out.println(file.canRead());   //是否可读
    System.out.println(file.canWrite());   //是否可写
    System.out.println(file.canExecute());   //是否可执行
}
```

通过File对象，我们就能快速得到文件的所有信息，如果是文件夹，还可以获取文件夹内部的文件列表等内容：

```java
File file = new File("/");
System.out.println(Arrays.toString(file.list()));   //快速获取文件夹下的文件名称列表
for (File f : file.listFiles()){   //所有子文件的File对象
    System.out.println(f.getAbsolutePath());   //获取文件的绝对路径
}
```

如果我们希望读取某个文件的内容，可以直接将File作为参数传入字节流或是字符流：

```java
File file = new File("test.txt");
try (FileInputStream inputStream = new FileInputStream(file)){   //直接做参数
    System.out.println(inputStream.available());
}catch (IOException e){
    e.printStackTrace();
}
```

**练习**：尝试拷贝文件夹下的所有文件到另一个文件夹

### 缓冲流

虽然普通的文件流读取文件数据非常便捷，但是每次都需要从外部I/O设备去获取数据，由于外部I/O设备的速度一般都达不到内存的读取速度，很有可能造成程序反应迟钝，因此性能还不够高，而缓冲流正如其名称一样，它能够提供一个缓冲，提前将部分内容存入内存（缓冲区）在下次读取时，如果缓冲区中存在此数据，则无需再去请求外部设备。同理，当向外部设备写入数据时，也是由缓冲区处理，而不是直接向外部设备写入。

![image-20221004125755217](https://s2.loli.net/2022/10/04/S8O61JP2lqKTzjd.png)

要创建一个缓冲字节流，只需要将原本的流作为构造参数传入BufferedInputStream即可：

```java
public static void main(String[] args) {
    try (BufferedInputStream bufferedInputStream = new BufferedInputStream(new FileInputStream("test.txt"))){   //传入FileInputStream
        System.out.println((char) bufferedInputStream.read());   //操作和原来的流是一样的
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

实际上进行I/O操作的并不是BufferedInputStream，而是我们传入的FileInputStream，而BufferedInputStream虽然有着同样的方法，但是进行了一些额外的处理然后再调用FileInputStream的同名方法，这样的写法称为`装饰者模式`，我们会在设计模式篇中详细介绍。我们可以来观察一下它的`close`方法源码：

```java
public void close() throws IOException {
    byte[] buffer;
    while ( (buffer = buf) != null) {
        if (bufUpdater.compareAndSet(this, buffer, null)) {  //CAS无锁算法，并发会用到，暂时不需要了解
            InputStream input = in;
            in = null;
            if (input != null)
                input.close();
            return;
        }
        // Else retry in case a new buf was CASed in fill()
    }
}
```

实际上这种模式是父类FilterInputStream提供的规范，后面我们还会讲到更多FilterInputStream的子类。

我们可以发现在BufferedInputStream中还存在一个专门用于缓存的数组：

```java
/**
 * The internal buffer array where the data is stored. When necessary,
 * it may be replaced by another array of
 * a different size.
 */
protected volatile byte buf[];
```

I/O操作一般不能重复读取内容（比如键盘发送的信号，主机接收了就没了），而缓冲流提供了缓冲机制，一部分内容可以被暂时保存，BufferedInputStream支持`reset()`和`mark()`操作，首先我们来看看`mark()`方法的介绍：

```java
/**
 * Marks the current position in this input stream. A subsequent
 * call to the <code>reset</code> method repositions this stream at
 * the last marked position so that subsequent reads re-read the same bytes.
 * <p>
 * The <code>readlimit</code> argument tells this input stream to
 * allow that many bytes to be read before the mark position gets
 * invalidated.
 * <p>
 * This method simply performs <code>in.mark(readlimit)</code>.
 *
 * @param   readlimit   the maximum limit of bytes that can be read before
 *                      the mark position becomes invalid.
 * @see     java.io.FilterInputStream#in
 * @see     java.io.FilterInputStream#reset()
 */
public synchronized void mark(int readlimit) {
    in.mark(readlimit);
}
```

当调用`mark()`之后，输入流会以某种方式保留之后读取的`readlimit`数量的内容，当读取的内容数量超过`readlimit`则之后的内容不会被保留，当调用`reset()`之后，会使得当前的读取位置回到`mark()`调用时的位置。

```java
public static void main(String[] args) {
    try (BufferedInputStream bufferedInputStream = new BufferedInputStream(new FileInputStream("test.txt"))){
        bufferedInputStream.mark(1);   //只保留之后的1个字符
        System.out.println((char) bufferedInputStream.read());
        System.out.println((char) bufferedInputStream.read());
        bufferedInputStream.reset();   //回到mark时的位置
        System.out.println((char) bufferedInputStream.read());
        System.out.println((char) bufferedInputStream.read());
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

我们发现虽然后面的部分没有保存，但是依然能够正常读取，其实`mark()`后保存的读取内容是取`readlimit`和BufferedInputStream类的缓冲区大小两者中的**最大值**，而并非完全由`readlimit`确定。因此我们限制一下缓冲区大小，再来观察一下结果：

```java
public static void main(String[] args) {
    try (BufferedInputStream bufferedInputStream = new BufferedInputStream(new FileInputStream("test.txt"), 1)){  //将缓冲区大小设置为1
        bufferedInputStream.mark(1);   //只保留之后的1个字符
        System.out.println((char) bufferedInputStream.read());
        System.out.println((char) bufferedInputStream.read());   //已经超过了readlimit，继续读取会导致mark失效
        bufferedInputStream.reset();   //mark已经失效，无法reset()
        System.out.println((char) bufferedInputStream.read());
        System.out.println((char) bufferedInputStream.read());
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

了解完了BufferedInputStream之后，我们再来看看BufferedOutputStream，其实和BufferedInputStream原理差不多，只是反向操作：

```java
public static void main(String[] args) {
    try (BufferedOutputStream outputStream = new BufferedOutputStream(new FileOutputStream("output.txt"))){
        outputStream.write("lbwnb".getBytes());
        outputStream.flush();
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

操作和FileOutputStream一致，这里就不多做介绍了。

既然有缓冲字节流，那么肯定也有缓冲字符流，缓冲字符流和缓冲字节流一样，也有一个专门的缓冲区，BufferedReader构造时需要传入一个Reader对象：

```java
public static void main(String[] args) {
    try (BufferedReader reader = new BufferedReader(new FileReader("test.txt"))){
        System.out.println((char) reader.read());
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

使用和reader也是一样的，内部也包含一个缓存数组：

```java
private char cb[];
```

相比Reader更方便的是，它支持按行读取：

```java
public static void main(String[] args) {
    try (BufferedReader reader = new BufferedReader(new FileReader("test.txt"))){
        System.out.println(reader.readLine());   //按行读取
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

读取后直接得到一个字符串，当然，它还能把每一行内容依次转换为集合类提到的Stream流：

```java
public static void main(String[] args) {
    try (BufferedReader reader = new BufferedReader(new FileReader("test.txt"))){
        reader
                .lines()
                .limit(2)
                .distinct()
                .sorted()
                .forEach(System.out::println);
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

它同样也支持`mark()`和`reset()`操作：

```java
public static void main(String[] args) {
    try (BufferedReader reader = new BufferedReader(new FileReader("test.txt"))){
        reader.mark(1);
        System.out.println((char) reader.read());
        reader.reset();
        System.out.println((char) reader.read());
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

BufferedReader处理纯文本文件时就更加方便了，BufferedWriter在处理时也同样方便：

```java
public static void main(String[] args) {
    try (BufferedWriter reader = new BufferedWriter(new FileWriter("output.txt"))){
        reader.newLine();   //使用newLine进行换行
        reader.write("汉堡做滴彳亍不彳亍");   //可以直接写入一个字符串
      	reader.flush();   //清空缓冲区
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

合理使用缓冲流，可以大大提高我们程序的运行效率，只不过现在初学阶段，很少会有机会接触到实际的应用场景。

### 转换流

有时会遇到这样一个很麻烦的问题：我这里读取的是一个字符串或是一个个字符，但是我只能往一个OutputStream里输出，但是OutputStream又只支持byte类型，如果要往里面写入内容，进行数据转换就会很麻烦，那么能否有更加简便的方式来做这样的事情呢？

```java
public static void main(String[] args) {
    try(OutputStreamWriter writer = new OutputStreamWriter(new FileOutputStream("test.txt"))){  //虽然给定的是FileOutputStream，但是现在支持以Writer的方式进行写入
        writer.write("lbwnb");   //以操作Writer的样子写入OutputStream
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

同样的，我们现在只拿到了一个InputStream，但是我们希望能够按字符的方式读取，我们就可以使用InputStreamReader来帮助我们实现：

```java
public static void main(String[] args) {
    try(InputStreamReader reader = new InputStreamReader(new FileInputStream("test.txt"))){  //虽然给定的是FileInputStream，但是现在支持以Reader的方式进行读取
        System.out.println((char) reader.read());
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

InputStreamReader和OutputStreamWriter本质也是Reader和Writer，因此可以直接放入BufferedReader来实现更加方便的操作。

### 打印流

打印流其实我们从一开始就在使用了，比如`System.out`就是一个PrintStream，PrintStream也继承自FilterOutputStream类因此依然是装饰我们传入的输出流，但是它存在自动刷新机制，例如当向PrintStream流中写入一个字节数组后自动调用`flush()`方法。PrintStream也永远不会抛出异常，而是使用内部检查机制`checkError()`方法进行错误检查。最方便的是，它能够格式化任意的类型，将它们以字符串的形式写入到输出流。

```java
public final static PrintStream out = null;
```

可以看到`System.out`也是PrintStream，不过默认是向控制台打印，我们也可以让它向文件中打印：

```java
public static void main(String[] args) {
    try(PrintStream stream = new PrintStream(new FileOutputStream("test.txt"))){
        stream.println("lbwnb");   //其实System.out就是一个PrintStream
    }catch (IOException e){
        e.printStackTrace();
    }
}
```

我们平时使用的`println`方法就是PrintStream中的方法，它会直接打印基本数据类型或是调用对象的`toString()`方法得到一个字符串，并将字符串转换为字符，放入缓冲区再经过转换流输出到给定的输出流上。

![img](https://s2.loli.net/2022/10/04/w8RKJxLm6Ik5usn.png)

因此实际上内部还包含这两个内容：

```java
/**
 * Track both the text- and character-output streams, so that their buffers
 * can be flushed without flushing the entire stream.
 */
private BufferedWriter textOut;
private OutputStreamWriter charOut;
```

与此相同的还有一个PrintWriter，不过他们的功能基本一致，PrintWriter的构造方法可以接受一个Writer作为参数，这里就不再做过多阐述了。

而我们之前使用的Scanner，使用的是系统提供的输入流：

```java
public static void main(String[] args) {
    Scanner scanner = new Scanner(System.in);   //系统输入流，默认是接收控制台输入
}
```

我们也可以使用Scanner来扫描其他的输入流：

```java
public static void main(String[] args) throws FileNotFoundException {
    Scanner scanner = new Scanner(new FileInputStream("秘制小汉堡.txt"));  //将文件内容作为输入流进行扫描
}
```

相当于直接扫描文件中编写的内容，同样可以读取。

### 数据流

数据流DataInputStream也是FilterInputStream的子类，同样采用装饰者模式，最大的不同是它支持基本数据类型的直接读取（这意味着数据流可以以二进制形式读取和写入Java的基本数据类型，而无需进行手动的数据类型转换）：

```java
public static void main(String[] args) {
    try (DataInputStream dataInputStream = new DataInputStream(new FileInputStream("test.txt"))){
        System.out.println(dataInputStream.readBoolean());   //直接将数据读取为任意基本数据类型
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

用于写入基本数据类型：

```java
public static void main(String[] args) {
    try (DataOutputStream dataOutputStream = new DataOutputStream(new FileOutputStream("output.txt"))){
        dataOutputStream.writeBoolean(false);
    }catch (IOException e) {
        e.printStackTrace();
    }
}
```

注意，写入的是二进制数据，并不是写入的字符串，使用DataInputStream可以读取，一般他们是配合一起使用的。

### 对象流

既然基本数据类型能够读取和写入基本数据类型，那么能否将对象也支持呢？ObjectOutputStream不仅支持基本数据类型，通过对对象的**序列化操作**，以某种格式保存对象，来支持对象类型的IO，注意：它不是继承自FilterInputStream的。

```java
public static void main(String[] args) {
    try (ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("output.txt"));
         ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("output.txt"))){
        People people = new People("lbw");
        outputStream.writeObject(people);
      	outputStream.flush();
        people = (People) inputStream.readObject();
        System.out.println(people.name);
    }catch (IOException | ClassNotFoundException e) {
        e.printStackTrace();
    }
}

static class People implements Serializable{   //必须实现Serializable接口才能被序列化
    String name;

    public People(String name){
        this.name = name;
    }
}
```

在我们后续的操作中，有可能会使得这个类的一些结构发生变化，而原来保存的数据只适用于之前版本的这个类，因此我们需要一种方法来区分类的不同版本：

```java
static class People implements Serializable{
    private static final long serialVersionUID = 123456;   //在序列化时，会被自动添加这个属性，它代表当前类的版本，我们也可以手动指定版本。

    String name;

    public People(String name){
        this.name = name;
    }
}
```

当发生版本不匹配时，会无法反序列化为对象：

```java
java.io.InvalidClassException: com.test.Main$People; local class incompatible: stream classdesc serialVersionUID = 123456, local class serialVersionUID = 1234567
	at java.io.ObjectStreamClass.initNonProxy(ObjectStreamClass.java:699)
	at java.io.ObjectInputStream.readNonProxyDesc(ObjectInputStream.java:2003)
	at java.io.ObjectInputStream.readClassDesc(ObjectInputStream.java:1850)
	at java.io.ObjectInputStream.readOrdinaryObject(ObjectInputStream.java:2160)
	at java.io.ObjectInputStream.readObject0(ObjectInputStream.java:1667)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:503)
	at java.io.ObjectInputStream.readObject(ObjectInputStream.java:461)
	at com.test.Main.main(Main.java:27)
```

如果我们不希望某些属性参与到序列化中进行保存，我们可以添加`transient`关键字：

```java
public static void main(String[] args) {
    try (ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("output.txt"));
         ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("output.txt"))){
        People people = new People("lbw");
        outputStream.writeObject(people);
        outputStream.flush();
        people = (People) inputStream.readObject();
        System.out.println(people.name);  //虽然能得到对象，但是name属性并没有保存，因此为null
    }catch (IOException | ClassNotFoundException e) {
        e.printStackTrace();
    }
}

static class People implements Serializable{
    private static final long serialVersionUID = 1234567;

    transient String name;

    public People(String name){
        this.name = name;
    }
}
```

其实我们可以看到，在一些JDK内部的源码中，也存在大量的transient关键字，使得某些属性不参与序列化，取消这些不必要保存的属性，可以节省数据空间占用以及减少序列化时间。

[Java序列化延申]: https://juejin.cn/post/6844903848167866375

