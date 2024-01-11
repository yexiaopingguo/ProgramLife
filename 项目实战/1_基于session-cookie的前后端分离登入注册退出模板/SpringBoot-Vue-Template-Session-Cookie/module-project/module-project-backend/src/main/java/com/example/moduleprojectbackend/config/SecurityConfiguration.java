package com.example.moduleprojectbackend.config;

import com.alibaba.fastjson2.JSONObject;
import com.example.moduleprojectbackend.entity.RestBean;
import com.example.moduleprojectbackend.mapper.AccountMapper;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.rememberme.JdbcTokenRepositoryImpl;
import org.springframework.security.web.authentication.rememberme.PersistentTokenRepository;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import javax.sql.DataSource;
import java.io.IOException;

@Configuration
@EnableWebSecurity
public class SecurityConfiguration {
    /**
     * 配置登入请求
     */

    @Autowired
    DataSource dataSource;

    @Autowired
    AccountMapper mapper;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http,
                                           PersistentTokenRepository repository) throws Exception {
        return http
                // 要求对所有的请求进行身份验证
                .authorizeHttpRequests(conf -> {
                    conf.requestMatchers("/api/auth/**").permitAll();   // 给注册页面放行，确保没登入过的人也可以进来
                    conf.anyRequest().authenticated();
                })
                // 登入配置
                .formLogin(conf -> {
                    conf.loginProcessingUrl("/api/auth/login");
                    //使用自定义的成功失败处理器
                    conf.successHandler(this::onAuthenticationSuccess);
                    conf.failureHandler(this::onAuthenticationFailure);
                    conf.permitAll();   // 允许所有没有权限的人进入该页面（包括还未登入的角色）
                })
                // 登出配置
                .logout(conf -> {
                    conf.logoutUrl("/api/auth/logout");
                    conf.logoutSuccessHandler(this::onAuthenticationSuccess);
                })
                // 配置异常情况例如访问未知的页面: 3xx or 4xx or 5xx
                .exceptionHandling(conf -> {
                    //配置授权相关异常处理器
                    // conf.accessDeniedHandler(this::onAuthenticationFailure);
                    //配置验证相关异常的处理器，不会再自动跳转到登入页面触发302条件
                    conf.authenticationEntryPoint(this::onAuthenticationFailure);
                })
                // 登入页面记住我选项
                .rememberMe(conf -> {
                    // 设置前端传入的参数
                    conf.rememberMeParameter("remember");
                    conf.tokenRepository(repository);      //设置刚刚的记住我持久化存储库
                    conf.tokenValiditySeconds(3600 * 7);   //设置记住我有效时间为7小时
                })
                // 对非同源的前端项目进行 CORS 跨域配置
                .cors(conf -> {
                    CorsConfiguration cors = new CorsConfiguration();
                    //添加前端站点地址，这样就可以告诉浏览器信任了
                    // cors.addAllowedOrigin("http://localhost:8080");
                    //也可以像这样允许所有
                    cors.addAllowedOriginPattern("*");
                    //但是这样并不安全，我们应该只许可给我们信任的站点
                    cors.setAllowCredentials(true);  //允许跨域请求中携带Cookie
                    cors.addAllowedHeader("*");   //其他的也可以配置，为了方便这里就 * 了
                    cors.addAllowedMethod("*");
                    cors.addExposedHeader("*");
                    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
                    source.registerCorsConfiguration("/**", cors);  //直接针对于所有地址生效
                    conf.configurationSource(source);
                })
                // 关闭 SpringSecurity PostRequest 要求返回的 _csrf 数据
                .csrf(AbstractHttpConfigurer::disable)
                .build();
    }

//    // 自定义登入，但好像这里可有可无，只要 AuthorizeService 实现了 UserDetailsService 就可以
//    @Bean
//    public AuthenticationManager authenticationManager(HttpSecurity security) throws Exception {
//        return security
//                .getSharedObject(AuthenticationManagerBuilder.class)
//                .userDetailsService(authorizeService)
//                .and()
//                .build();
//    }

    @Bean
    public BCryptPasswordEncoder passwordEncoder(){
        // 用于密码加密校验
        return new BCryptPasswordEncoder();
    }

    private void onAuthenticationSuccess(HttpServletRequest request, HttpServletResponse response, Authentication authentication) throws IOException {
        // 设置文字编码和回传格式
        response.setCharacterEncoding("utf-8");
        response.setContentType("application/json");
        if(request.getRequestURI().endsWith("/login"))
            response.getWriter().write(JSONObject.toJSONString(RestBean.success("登录成功")));
        else if(request.getRequestURI().endsWith("/logout"))
            response.getWriter().write(JSONObject.toJSONString(RestBean.success("退出登录成功")));
    }

    private void onAuthenticationFailure(HttpServletRequest request, HttpServletResponse response, AuthenticationException exception) throws IOException {
        // 设置文字编码和回传格式
        response.setCharacterEncoding("utf-8");
        response.setContentType("application/json");
        // 可以根据 Object 类型来回传不同类型的结果
        response.getWriter().write(JSONObject.toJSONString(RestBean.failure(401, exception.getMessage())));
    }

    // 持久化 Token 仓库，用于让服务器记住客户端的id
    @Bean
    public PersistentTokenRepository tokenRepository(DataSource dataSource){

        JdbcTokenRepositoryImpl repository = new JdbcTokenRepositoryImpl();
        //在启动时自动在数据库中创建存储记住我信息的表，仅第一次需要设置为true，后续不需要
        repository.setCreateTableOnStartup(mapper.judgeIsExist("study", "persistent_logins") <= 0);
        repository.setDataSource(dataSource);
        return repository;
    }

}
