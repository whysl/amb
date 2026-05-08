import axios from 'axios'
import { showToast } from '../utils/toast.js'

const http = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_info')
        window.location.hash = '#/login'
        showToast('登录已过期，请重新登录')
      } else if (status === 403) {
        showToast(data.detail || '权限不足')
      } else {
        showToast(data.detail || '请求失败')
      }
    } else {
      showToast('网络错误')
    }
    return Promise.reject(error)
  }
)

export default http
