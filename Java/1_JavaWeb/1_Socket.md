[TOC]

## 一、认识Socket技术

**Server端口：**

```java
public class Server {
    public static void main(String[] args){
        try {
            ServerSocket server = new ServerSocket(8080);
            System.out.println("正在等待连接...");
            while (true){
                Socket socket = server.accept();
                System.out.println("客户端已经连接，IP地址为：" + socket.getInetAddress().getHostAddress());
            }
            server.close();    // 解除端口避免占用
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

**Client端口：**

```java
public class Client {
    public static void main (String[] args) {
        try {
            Socket socket = new Socket("localhost",8080);    // Socket(目标ip地址, 端口)
            System.out.println("已经连接到服务器");
            socket.close();
        } catch (IOException e) {
            System.out.println("服务器连接失败");
            e.printStackTrace();
        }
    }
}
```



## 二、Socket进行数据传输

**Server端口：**

```java
public class Server {
    public static void main(String[] args){
        try(ServerSocket server = new ServerSocket(8080)) {
            System.out.println("正在等待客户端连接...");
            Socket socket = server.accept();
            System.out.println("客户端已经连接，IP地址为：" + socket.getInetAddress().getHostAddress());
            System.out.println("读取客户端数据：");
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            System.out.println(reader.readLine());

            OutputStreamWriter writer = new OutputStreamWriter(socket.getOutputStream());
            writer.write("收到！\n");
            writer.flush();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```

**Client端口：**

```java
public class Client {
    public static void main (String[] args) {
        try(Socket socket = new Socket("localhost",8080);
            Scanner scanner = new Scanner(System.in)) {
            System.out.println("已经连接到服务器");
            OutputStreamWriter writer = new OutputStreamWriter(socket.getOutputStream());
            writer.write(scanner.nextLine() + "\n");
            writer.flush();
            System.out.println("数据已发送！等待服务器确认...");

            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            System.out.println("收到服务器相应：" + reader.readLine());
        } catch (IOException e) {
            System.out.println("服务器连接失败");
            e.printStackTrace();
        }
    }
}
```

**手动关闭**

```java
socket.shutdownOutput();    // 关闭输出方向的流
socket.shutdownInput();    // 关闭输入方向的流
```

**如果不希望服务器等待过长时间，可以设定IO超时时间**

```java
socket.setSoTimeout(3000);
```

**当客户端连接后，如果有设置keeplive为true，过段时间当对方没有发送数据会自动发送ack探测包检测TCP/IP的连接**

```
socket.setKeepAlive(true);
```



##  三、Socket传输文件

**思路和传输数据一样**

```Java
FileInputStream();
FileOutputStream();
```



## 四、使用浏览器访问Socket服务器

```java
public class Server {
    public static void main(String[] args){
        try(ServerSocket server = new ServerSocket(8080)) {
            System.out.println("正在等待客户端连接...");
            Socket socket = server.accept();
            System.out.println("客户端已经连接，IP地址为：" + socket.getInetAddress().getHostAddress());
            BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            System.out.println("接收到客户端数据：");
            while (reader.ready()) System.out.println(reader.readLine());
            OutputStreamWriter writer = new OutputStreamWriter(socket.getOutputStream());
            writer.write("HTTP/1.1 200 Accepted\r\n"); // 200是响应码，表示接受请求
            writer.write("\r\n");
            writer.write("Test Page");
            writer.flush();
            socket.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
```











