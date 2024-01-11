<script setup>
import router from "@/router"
import {get} from "@/net"
import {ElMessage} from "element-plus";
import {useStore} from "@/stores/index.js";

const store = useStore()

const logout = () => {
  get('/api/auth/logout', (message) => {
    ElMessage.success(message)
    store.auth.user = null
    router.push("/")
  })
}
</script>

<template>
  <div>
    欢迎进入到学习平台
  </div>
  <div>
    <el-button @click="logout()" type="danger" plain>退出登入</el-button>
  </div>
</template>

<style scoped>

</style>