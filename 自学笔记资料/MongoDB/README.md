## 基本使用

1. 导入依赖

```java
implementation group: 'org.springframework.boot', name: 'spring-boot-starter-data-mongodb', version: '3.3.5'
```

2. application.yml

```java
spring:
	data:
		mongodb:
			// 这里有一个工程上面的坑，这里的用户和密码，是单独数据库的账号密码，而不是连接mongoDB的账户密码
      		uri: mongodb://username:password@ip:port/database
```

3. 绑定实体

```java
@Data
@AllArgsConstructor
@NoArgsConstructor
@Document(collection = "student")
public class Student {

    @Id
    private Integer id;
    private String name;
    private String age;
    private String sex;

}
```

4. 测试代码

```java
@GetMapping("/mongoDB")
    public void testmongoDB() {
        // 定义一个简单的测试文档
        String collectionName = "student";
        Student student = new Student(1, "1", "2", "3");

        // 插入测试数据
        mongoTemplate.insert(student, collectionName);
    }
```

