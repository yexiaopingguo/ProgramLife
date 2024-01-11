<script setup>

</script>

<template>
  <div class="container" style="width: 100%;height: 100vh;overflow: hidden;display: flex;background: white">
    <div class="left" style="background: white;width: 80%">
      <el-image style="height: 100%" fit="cover"
                src="	https://pit1.topit.pro/forum/202105/05/032550v4hf009z19zrm4q9.jpg"/>
    </div>
    <div class="right" style="text-align: center;width: 500px;background: white;padding: 20px">
      <router-view v-slot="{ Component }">
        <transition name="el-fade-in-linear">
          <!--    height: 100% 这样动态切换就不会出现bug      -->
          <component :is="Component" style="height: 100%"/>
        </transition>
      </router-view>
    </div>
  </div>
</template>

<style scoped>

</style>