<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">阿米巴核算系统</h1>
      <p class="login-subtitle">威高商管公司</p>
      <form @submit.prevent="handleLogin">
        <div class="login-fields">
          <div class="field-item">
            <label>用户名</label>
            <input v-model="username" placeholder="请输入用户名" required autocomplete="username" />
          </div>
          <div class="field-item">
            <label>密 码</label>
            <input v-model="password" type="password" placeholder="请输入密码" required autocomplete="current-password" />
          </div>
        </div>
        <button class="login-btn" type="submit" :disabled="loading">
          {{ loading ? '登录中...' : '登 录' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'

const router = useRouter()
const username = ref('')
const password = ref('')
const loading = ref(false)

const handleLogin = async () => {
  if (!username.value || !password.value) return
  loading.value = true
  try {
    const { data } = await http.post('/auth/login', { username: username.value, password: password.value })
    localStorage.setItem('access_token', data.access_token)
    localStorage.setItem('user_info', JSON.stringify(data.user_info))
    router.push('/home')
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  padding: 20px;
}
.login-card {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 48px 36px 40px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}
.login-title {
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: #1a73e8;
  margin-bottom: 4px;
}
.login-subtitle {
  text-align: center;
  font-size: 15px;
  color: #999;
  margin-bottom: 36px;
}
.login-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}
.field-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.field-item label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}
.field-item input {
  padding: 12px 14px;
  border: 1px solid #d0d0d0;
  border-radius: 8px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}
.field-item input:focus {
  border-color: #1a73e8;
}
.login-btn {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 8px;
  background: #1a73e8;
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}
.login-btn:hover { background: #1557b0; }
.login-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
