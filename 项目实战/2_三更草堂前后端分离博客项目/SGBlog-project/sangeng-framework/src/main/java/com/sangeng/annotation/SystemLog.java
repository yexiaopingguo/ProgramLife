package com.sangeng.annotation;


import org.aspectj.lang.annotation.Around;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;

@Retention(RetentionPolicy.RUNTIME)    // 运行环境
@Target(ElementType.METHOD)    // 目标方法
public @interface SystemLog {
    String businessName();
}
