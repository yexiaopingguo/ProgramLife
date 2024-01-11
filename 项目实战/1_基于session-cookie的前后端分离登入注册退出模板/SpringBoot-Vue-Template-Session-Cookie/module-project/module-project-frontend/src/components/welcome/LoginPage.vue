<script setup>
import {Lock, User} from "@element-plus/icons-vue";
import {ElMessage} from "element-plus";
import {reactive} from "vue";
import {get, post} from "@/net";
import router from "@/router/index.js";
import {useStore} from "@/stores/index.js";

const form = reactive({
  username: '',
  password: '',
  remember: false
})

const store = useStore()

const login = () => {
  if(!form.username || !form.password) {
    ElMessage.warning('请填写用户名和密码！')
  } else {
    post('/api/auth/login', {
      username: form.username,
      password: form.password,
      remember: form.remember
    }, (message) => {
      ElMessage.success(message)
      get('/api/user/me', (message) => {
        store.auth.user = message.username
        router.push('/index')
      }, () => {
        store.auth.user = null
      })
    })
  }
}
</script>

<template>
  <div>
    <div style="margin-top: 120px">
      <div style="font-size: 28px">登录</div>
      <div style="font-size: 14px;color: grey">请输入您的用户名和密码</div>
    </div>
    <div style="margin-top: 30px">
      <el-input v-model="form.username" type="text" placeholder="用户名/邮箱" style="margin-bottom: 10px">
        <template #prefix>
          <el-icon slot="prefix"><User /></el-icon>
        </template>
      </el-input>
      <el-input v-model="form.password" type="text" placeholder="密码" style="margin-bottom: 10px">
        <template #prefix>
          <el-icon slot="prefix"><Lock /></el-icon>
        </template>
      </el-input>
      <el-row>
        <el-col :span="12" style="text-align: left">
          <el-checkbox v-model="form.remember" label="记住我"/>
        </el-col>
        <el-col :span="12" style="text-align: right">
          <el-link @click="router.push('/forget')">忘记密码</el-link>
        </el-col>
      </el-row>

      <el-button @click="login()" style="width: 150px" type="success" plain>立即登录</el-button>
      <el-divider>
        <span style="color: grey">没有账号</span>
      </el-divider>
      <el-button @click="router.push('/register')" style="width: 150px" type="warning" plain>注册账号</el-button>
    </div>
  </div>
</template>

<style scoped>

</style>