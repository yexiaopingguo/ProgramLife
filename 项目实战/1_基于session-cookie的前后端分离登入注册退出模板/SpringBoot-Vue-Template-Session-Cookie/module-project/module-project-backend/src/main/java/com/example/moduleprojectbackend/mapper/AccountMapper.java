package com.example.moduleprojectbackend.mapper;

import com.example.moduleprojectbackend.entity.auth.Account;
import com.example.moduleprojectbackend.entity.user.AccountUser;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;
import org.apache.ibatis.annotations.Update;

@Mapper
public interface AccountMapper {
    @Select("select id, username, email, password from db_account where username = #{text} or email = #{text}")
    Account findAccountByNameOrEmail(String text);

    @Select("select id, username, email from db_account where username = #{text} or email = #{text}")
    AccountUser findAccountUserByNameOrEmail(String text);

    @Insert("insert into db_account (email, username, password) values (#{email}, #{username}, #{password})")
    int createAccount(String username, String password, String email);

    @Update("update db_account set password = #{password} where email = #{email}")
    int resetPasswordByEmail(String password, String email);

    @Select("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=#{schema} AND table_name=#{table}")
    int judgeIsExist(String schema, String table);
}
