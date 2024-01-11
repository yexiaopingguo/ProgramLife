package com.example.moduleprojectbackend.config;

import com.example.moduleprojectbackend.interceptor.AuthorizeInterceptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class WebConfiguration implements WebMvcConfigurer {

    @Autowired
    AuthorizeInterceptor interceptor;

    /**
     * 用于配置拦截器
     * 在Spring框架中，拦截器可以用于在处理请求之前或之后执行一些额外的逻辑
     */
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry
                .addInterceptor(interceptor)
                .addPathPatterns("/**")
                .excludePathPatterns("/api/auth/**");
    }
}
