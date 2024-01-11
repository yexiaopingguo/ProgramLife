package com.example.moduleprojectbackend;

import com.example.moduleprojectbackend.mapper.AccountMapper;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

@SpringBootTest
class ModuleProjectBackendApplicationTests {

    @Autowired
    AccountMapper mapper;

    @Test
    void contextLoads() {
        System.out.println(mapper.judgeIsExist("study", "persistent_logins"));


    }

}
