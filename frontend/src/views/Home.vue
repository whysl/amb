<template>
  <div class="home-page">
    <div class="top-bar">
      <div class="top-left">
        <h1 class="logo">阿米巴核算系统</h1>
        <span class="brand-sub">威高商管公司</span>
      </div>
      <div class="top-user">
        <span class="top-user-name">{{ userName }}</span>
        <span class="top-user-meta">{{ deptName }} · {{ roleLabel }}</span>
        <span class="top-user-date">{{ today }}</span>
        <button class="pc-btn pc-btn-default pc-btn-sm" @click="onChangePwd">修改密码</button>
        <button class="pc-btn pc-btn-danger pc-btn-sm" @click="logout">退出</button>
      </div>
    </div>

    <div class="page-container">
      <div class="home-layout">
        <div class="home-sidebar">
          <div class="sidebar-menu">
            <div class="menu-item" @click="goMyForms" v-if="canFill">
              <span class="menu-icon">&#9998;</span>
              <span>我的填报</span>
            </div>
            <div class="menu-item" @click="goDeptReview" v-if="canDeptReview">
              <span class="menu-icon">&#10003;</span>
              <span>部门审核</span>
            </div>
            <div class="menu-item" @click="goCompanyReview" v-if="canCompanyReview">
              <span class="menu-icon">&#9733;</span>
              <span>公司审核</span>
            </div>
            <div class="menu-item" @click="goRollup">
              <span class="menu-icon">&#9783;</span>
              <span>推移表</span>
            </div>
            <div class="menu-item" @click="goSummary" v-if="canCompanyReview">
              <span class="menu-icon">&#9776;</span>
              <span>汇总报表</span>
            </div>
            <div class="menu-item" @click="goAdmin" v-if="isAdmin">
              <span class="menu-icon">&#9881;</span>
              <span>系统管理</span>
            </div>
          </div>
        </div>

        <div class="home-main">
          <div class="pc-card welcome-card">
            <h3>欢迎使用阿米巴核算系统</h3>
            <p>当前角色：{{ roleLabel }} | 所属部门：{{ deptName }} | {{ today }}</p>
          </div>

          <div class="pc-card" v-if="recentForms.length > 0">
            <h3 class="card-title">本月填报状态</h3>
            <table class="pc-table">
              <thead>
                <tr>
                  <th>类型</th>
                  <th>周期</th>
                  <th>状态</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="form in recentForms" :key="form.id">
                  <td>{{ form.period_type === 'actual' ? '实际' : form.period_type === 'planned' ? '预定' : '预算' }}</td>
                  <td>{{ form.period_year }}年{{ form.period_month }}月</td>
                  <td><span :class="['pc-status-tag', 'pc-status-' + form.status]">{{ statusLabel(form.status) }}</span></td>
                  <td><button class="pc-btn pc-btn-primary pc-btn-sm" @click="goFormDetail(form.id)">查看</button></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <Modal v-model:show="pwdDialogShow" title="修改密码" :width="380" @confirm="doChangePwd">
      <div class="dialog-form">
        <div class="df-item">
          <label class="df-label">新密码</label>
          <input class="df-input" type="password" v-model="newPwd" placeholder="请输入新密码" />
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import http from '../api/http'
import { showSuccessToast } from '../utils/toast.js'
import Modal from '../components/Modal.vue'

const router = useRouter()
const userName = ref('')
const deptName = ref('')
const role = ref('')
const recentForms = ref([])
const pwdDialogShow = ref(false)
const newPwd = ref('')

const today = computed(() => {
  const d = new Date()
  return `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日`
})

const roleLabel = computed(() => {
  const map = { dept_filler: '部门填报人', dept_reviewer: '部门审核人', company_reviewer: '公司审核人', super_admin: '系统管理员' }
  return map[role.value] || role.value
})

const isAdmin = computed(() => role.value === 'super_admin')
const canFill = computed(() => ['dept_filler', 'dept_reviewer', 'super_admin'].includes(role.value))
const canDeptReview = computed(() => ['dept_reviewer', 'super_admin'].includes(role.value))
const canCompanyReview = computed(() => ['company_reviewer', 'super_admin'].includes(role.value))

const statusLabel = (s) => {
  const map = { draft: '草稿', submitted: '待部门审核', dept_approved: '待公司审核', dept_rejected: '部门驳回', company_approved: '已通过', company_rejected: '公司驳回' }
  return map[s] || s
}

const fetchUserInfo = async () => {
  try {
    const { data } = await http.get('/auth/me')
    userName.value = data.real_name
    deptName.value = data.dept_name || '未分配'
    role.value = data.role
  } catch (e) {}
}

const fetchRecentForms = async () => {
  if (!canFill.value) return
  try {
    const now = new Date()
    const { data } = await http.get('/forms/my', { params: { year: now.getFullYear(), month: now.getMonth() + 1 } })
    recentForms.value = data.slice(0, 10)
  } catch (e) {}
}

const goMyForms = () => router.push('/forms')
const goDeptReview = () => router.push('/review/dept')
const goCompanyReview = () => router.push('/review/company')
const goRollup = () => router.push('/rollup')
const goSummary = () => router.push('/summary')
const goAdmin = () => router.push('/admin')
const goFormDetail = (id) => router.push(`/form/${id}`)

const onChangePwd = () => {
  newPwd.value = ''
  pwdDialogShow.value = true
}

const doChangePwd = async () => {
  if (!newPwd.value) return
  try {
    await http.put('/auth/me/password', { new_password: newPwd.value })
    showSuccessToast('密码修改成功')
    pwdDialogShow.value = false
  } catch (e) {}
}

const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_info')
  router.push('/login')
}

onMounted(() => {
  fetchUserInfo()
  fetchRecentForms()
})
</script>

<style scoped>
.home-page { min-height: 100vh; background: #f0f2f5; }
.top-bar {
  background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%);
  padding: 14px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
}
.top-left { display: flex; align-items: baseline; gap: 12px; }
.logo { font-size: 20px; font-weight: 700; color: #fff; }
.brand-sub { font-size: 13px; opacity: 0.75; }
.top-user { display: flex; align-items: center; gap: 10px; font-size: 13px; }
.top-user-name { font-weight: 600; }
.top-user-meta { opacity: 0.75; }
.top-user-date { opacity: 0.6; font-size: 12px; }
.home-layout { display: flex; gap: 20px; }
.home-sidebar { width: 200px; flex-shrink: 0; }
.sidebar-menu {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  position: sticky;
  top: 20px;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  border-bottom: 1px solid #f5f5f5;
  transition: all 0.2s;
}
.menu-item:hover { background: #e8f0fe; color: #1a73e8; }
.menu-item:last-child { border-bottom: none; }
.menu-icon { font-size: 18px; width: 24px; text-align: center; }
.home-main { flex: 1; min-width: 0; }
.welcome-card h3 { font-size: 18px; margin-bottom: 6px; }
.welcome-card p { font-size: 13px; color: #888; }
.card-title { font-size: 16px; font-weight: 600; margin-bottom: 12px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0; }
.dialog-form { display: flex; flex-direction: column; gap: 14px; }
.df-item { display: flex; align-items: center; gap: 12px; }
.df-label { width: 70px; text-align: right; font-size: 14px; color: #555; flex-shrink: 0; }
.df-input { flex: 1; padding: 8px 12px; border: 1px solid #d0d0d0; border-radius: 6px; font-size: 14px; outline: none; }
.df-input:focus { border-color: #1a73e8; }
</style>
