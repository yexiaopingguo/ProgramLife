package com.spring;

public class ApplicationContext {
    private Class configClass;
    public ApplicationContext(Class configClass) {

        this.configClass = configClass;

        // 解析配置类，ComponentScan 注解 -> 扫描路径 -> 扫描
        ComponentScan componentScanAnnotation = (ComponentScan) configClass.getDeclaredAnnotation(ComponentScan.class);
        String path = componentScanAnnotation.value();
        System.out.println(path);

    }

    public Object getBean(String beanName) {
        return null;
    }
}
