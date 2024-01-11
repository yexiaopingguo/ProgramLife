package com.example.moduleprojectbackend.controller;

import com.example.moduleprojectbackend.entity.RestBean;
import com.example.moduleprojectbackend.entity.user.AccountUser;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.SessionAttribute;

@RestController
@RequestMapping("/api/user")
public class UserController {

    /**
     * 用于前端获取已登入用户信息
     * 对未登入用户进行拦截
     */
    @GetMapping("/me")
    public RestBean<AccountUser> me(@SessionAttribute("account") AccountUser user){
        return RestBean.success(user);
    }
}
