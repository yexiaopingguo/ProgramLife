<script setup>
import {get} from "@/net";
import {useStore} from "@/stores";
import router from "@/router";

const store = useStore()

// 上来先请求获取已登入用户，判断是否 Remember me
if(store.auth.user == null) {
  get('/api/user/me', (message) => {
    store.auth.user = message.username
    router.push('/index')
  }, () => {
    store.auth.user = null
  })
}
</script>

<template>
  <router-view/>
</template>

<style scoped>

</style>
