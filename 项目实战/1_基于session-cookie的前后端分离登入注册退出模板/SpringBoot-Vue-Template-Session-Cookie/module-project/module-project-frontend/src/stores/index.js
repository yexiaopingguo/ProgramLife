import {ref, computed, reactive} from 'vue'
import { defineStore } from 'pinia'

// 用于验证是否已经登入
export const useStore = defineStore('store', () => {
  const auth = reactive({
    user: null
  })
  return { auth }
})
