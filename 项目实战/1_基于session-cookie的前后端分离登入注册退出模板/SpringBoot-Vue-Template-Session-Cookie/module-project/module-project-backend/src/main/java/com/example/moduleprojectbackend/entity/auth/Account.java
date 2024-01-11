package com.example.moduleprojectbackend.entity.auth;

import lombok.Data;

@Data
public class Account {
    int id;
    String email;
    String username;
    String password;
}
