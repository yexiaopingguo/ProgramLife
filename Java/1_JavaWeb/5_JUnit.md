[TOC]

## 一、JUnit 介绍

​	在 JAVA 的领域里，谈到测试框架，JUnit是最多人使用的，它可以帮助我们编写单元测试、整合测试等，并有测试分类、测试运行器等功能。随着项目日益扩大，如果直接在主方法中测试，会降低开发效率，因此我们需要使用单元测试来帮助我们针对某个功能或是某个模块单独运行代码进行测试。



`@Before` : 前置操作

`@Test`: 测试用例

`@After`: 收尾工作

`@Slf4j`: 日志实现门面（接口）

`@RepeatedTest(n)`：重复测试 n 次    // JUnit 5 版本才支持



`@BeforeClass`及`@AfterClass`在一個Test Case只會被執行一次。
而`@Before`和`@After`會在每一次測試方法`@Test`前後各執行一次。

```java
import org.junit.Test;

public class MainTest {
    
	@Before
    public void before() {
        /*
        	try {
        		实例化对象...
        	} catch {
        		...
        	}
        */
    }
    
    @Test
    public void method1() {
        System.out.println("测试用例1");
    }

    @Test
    public void method2() {
        System.out.println("测试用例2");
    }
    
    @After
    public void after() {
        ...
    }
    
}
```

**要求：**

- 方法必须是public的
- 不能是静态方法
- 返回值必须是void
- 必须是没有任何参数的方法



## 二、断言 Assert

例（判断预期值和实际值是否一样）：

```Java
Assert.assertEquals(2,1);    // 预期
```









