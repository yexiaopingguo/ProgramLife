package com.test;

import com.spring.AppConfig;
import com.spring.ApplicationContext;

public class Test {

    public static void main(String[] args) {
        ApplicationContext applicationContext = new ApplicationContext(AppConfig.class);
        Object userService = applicationContext.getBean("userService");

    }

}
