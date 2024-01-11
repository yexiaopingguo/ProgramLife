package com.example.moduleprojectbackend.service.impl;

import com.example.moduleprojectbackend.entity.auth.Account;
import com.example.moduleprojectbackend.mapper.AccountMapper;
import com.example.moduleprojectbackend.service.AuthorizeService;
import jakarta.annotation.Resource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.mail.MailException;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.Optional;
import java.util.Random;
import java.util.concurrent.TimeUnit;

@Service
public class AuthorizeServiceImpl implements AuthorizeService {

    @Value("${spring.mail.username}")
    String from;

    @Autowired
    JavaMailSender mailSender;

    @Autowired
    AccountMapper mapper;

    @Autowired
    StringRedisTemplate template;

    BCryptPasswordEncoder encoder = new BCryptPasswordEncoder();

    @Override
    public UserDetails loadUserByUsername(String username) throws UsernameNotFoundException {
        /*
          1. 自定义数据库表用户登录
          2. 需要继承 UserDetailsService 接口并覆写 loadUserByUsername 返回 UserDetails 类
         */
        if(username == null || username.isEmpty())
            throw new UsernameNotFoundException("用户名不能为空");
        Account account = mapper.findAccountByNameOrEmail(username);
        if(account == null)
            throw new UsernameNotFoundException("用户名或密码错误");
        return User
                .withUsername(account.getUsername())
                .password(account.getPassword())
                .roles("user")
                .build();
    }

    // !!! 注意要打开 Redis !!!
    @Override
    public String sendValidateEmail(String email, String sessionId, boolean hasAccount) {
        /*
          1. 生成对应验证码
          2. 把邮箱和对应的验证码直接放到 Redis 里面
          3. 发送验证码到指定邮箱
          4. 发送失败则删除 Redis 里面删除失败的值
          5. 用户注册时，验证 Redis 中对应的键值对
         */

        // 首先避免同一个sessionID的用户更换邮箱重复发送邮件
        String key = "email:" + sessionId + ":" + email;

        // 判断是否
        if(Boolean.TRUE.equals(template.hasKey(key))) {
            Long expire = Optional.ofNullable(template.getExpire(key, TimeUnit.SECONDS)).orElse(0L);
            if(expire > 120) return "请求频繁，请稍后再试";
        }

        // 判断是否存在重复用户
        Account account = mapper.findAccountByNameOrEmail(email);

        if (hasAccount) {
            if (account == null) return "不存在该邮箱账户";
        } else {
            if(account != null) return "此邮箱已被其他用户注册";
        }

        // 生成随机验证码
        Random random = new Random();
        int code = random.nextInt(899999) + 100000;

        // 发送邮件
        SimpleMailMessage message = new SimpleMailMessage();
        message.setFrom(from);
        message.setTo(email);
        message.setSubject("您的验证邮件");
        message.setText("验证码是："+code);
        try {
            mailSender.send(message);
            template.opsForValue().set(key, String.valueOf(code), 3, TimeUnit.MINUTES);     // 过期时间三分钟
            return null;
        } catch (MailException e) {
            e.printStackTrace();
            return "邮件发送失败，请坚持邮件地址是否有效";
        }
    }

    @Override
    public String validateAndRegister(String username, String password, String email, String code, String sessionId) {
        String key = "email:" + sessionId + ":" + email;
        if(Boolean.TRUE.equals(template.hasKey(key))) {
            String s = template.opsForValue().get(key);
            if(s == null) return "验证码失效，请重新请求";
            if(s.equals(code)) {
                Account account = mapper.findAccountByNameOrEmail(username);
                if(account != null) return "此用户名已被注册，请更换用户名";
                template.delete(key);
                password = encoder.encode(password);
                if (mapper.createAccount(username, password, email) > 0) {
                    return null;
                } else {
                    return "内部错误，请联系管理员";
                }
            } else {
                return "验证码错误，请检查后再提交";
            }
        } else {
            return "请先请求一封验证码邮件";
        }
    }

    @Override
    public String validateOnly(String email, String code, String sessionId) {
        String key = "email:" + sessionId + ":" + email;
        if(Boolean.TRUE.equals(template.hasKey(key))) {
            String s = template.opsForValue().get(key);
            if(s == null) return "验证码失效，请重新请求";
            if(s.equals(code)) {
                template.delete(key);
                return null;
            } else {
                return "验证码错误，请检查后再提交";
            }
        } else {
            return "请先请求一封验证码邮件";
        }
    }

    @Override
    public boolean resetPassword(String password, String email) {
        password = encoder.encode(password);
        return mapper.resetPasswordByEmail(password, email) > 0;
    }

}
