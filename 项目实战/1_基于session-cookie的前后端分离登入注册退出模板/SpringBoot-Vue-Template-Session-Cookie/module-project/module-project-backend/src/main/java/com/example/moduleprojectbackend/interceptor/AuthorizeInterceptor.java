package com.example.moduleprojectbackend.interceptor;

import com.example.moduleprojectbackend.entity.user.AccountUser;
import com.example.moduleprojectbackend.mapper.AccountMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.User;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

@Component
public class AuthorizeInterceptor implements HandlerInterceptor {

    @Autowired
    AccountMapper mapper;

    /**
     *
     * 用于前端校验是否成功登入用户
     * 发起请求会会先经过拦截器
     *
     */
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler)
            throws Exception {

        // 从 Context 中获取用户名
        SecurityContext context = SecurityContextHolder.getContext();
        Authentication authentication = context.getAuthentication();
        User user = (User)authentication.getPrincipal();
        String username = user.getUsername();

        // 从 DAO 层获取用户具体信息，放入 session 中
        AccountUser account = mapper.findAccountUserByNameOrEmail(username);
        request.getSession().setAttribute("account", account);

        return true;
    }
}
