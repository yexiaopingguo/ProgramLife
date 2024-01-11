import { createRouter, createWebHistory } from 'vue-router'
import {useStore} from "@/stores/index.js";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: () => import('@/views/WelcomeView.vue'),
      children: [
        {
          path: '',
          name: 'welcome-login',
          component: () => import('@/components/welcome/LoginPage.vue')
        }, {
          path: 'register',
          name: 'welcome-register',
          component: () => import('@/components/welcome/RegisterPage.vue')
        }, {
          path: 'forget',
          name: 'welcome-forget',
          component: () => import('@/components/welcome/ForgetPage.vue')
        }
      ]
    }, {
      path: '/index',
      name: 'index',
      component: () => import('@/views/IndexView.vue'),
    }
  ]
})

// 添加一个路由守卫
router.beforeEach((to, from, next) => {
  const store = useStore()
  if(store.auth.user != null && to.name.startsWith('welcome-')) {
    // 如果已经登录过，在 welcome 页面会自动跳转到资源文件，不需要再次登录
    next('/index')
  } else if(store.auth.user == null && to.fullPath.startsWith('/index')) {
    // 如果还未登录过，尝试访问资源文件，自动跳转到 welcome 页面
    next('/')
  } else if(to.matched.length === 0){
    // 如果匹配不到存在的路由，丢到资源路径，如果没有登录，会再自动抛回 welcome 页面
    next('/index')
  } else {
    next()
  }
})

export default router
