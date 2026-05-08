<template>
  <div class="page">
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="$router.back()">&#8592;</button>
        <span class="top-title">汇总报表</span>
      </div>
      <button class="pc-btn pc-btn-default pc-btn-sm" @click="exportCompany">导出商管公司汇总</button>
    </div>
    <div class="page-container">
      <div class="pc-filter-bar">
        <label>年份</label><input type="number" v-model="year" />
        <label>月份</label><input type="number" v-model="month" />
        <label>类型</label>
        <select v-model="periodType" @change="fetchAll">
          <option value="actual">实际</option>
          <option value="planned">预定</option>
          <option value="budget">预算</option>
        </select>
        <button class="pc-btn pc-btn-primary pc-btn-sm" @click="fetchAll">查询</button>
      </div>

      <div class="tab-bar">
        <div :class="['tab-item', { active: activeTab === 0 }]" @click="activeTab = 0">威高广场汇总</div>
        <div :class="['tab-item', { active: activeTab === 1 }]" @click="activeTab = 1">商管公司汇总</div>
      </div>

      <table class="pc-table" v-if="activeTab === 0 && whgcData.length > 0">
        <thead><tr><th>科目编码</th><th style="text-align:left">科目名称</th><th>类别</th><th style="text-align:right">金额</th></tr></thead>
        <tbody>
          <tr v-for="item in whgcData" :key="item.code">
            <td :class="{ calculated: item.is_calculated }">{{ item.code }}</td>
            <td style="text-align:left">{{ item.name }}</td>
            <td>{{ item.category }}</td>
            <td style="text-align:right" :class="{ calculated: item.is_calculated }">{{ fmtValue(item.value) }}</td>
          </tr>
        </tbody>
      </table>
      <table class="pc-table" v-if="activeTab === 1 && companyData.length > 0">
        <thead><tr><th>科目编码</th><th style="text-align:left">科目名称</th><th>类别</th><th style="text-align:right">金额</th></tr></thead>
        <tbody>
          <tr v-for="item in companyData" :key="item.code">
            <td :class="{ calculated: item.is_calculated }">{{ item.code }}</td>
            <td style="text-align:left">{{ item.name }}</td>
            <td>{{ item.category }}</td>
            <td style="text-align:right" :class="{ calculated: item.is_calculated }">{{ fmtValue(item.value) }}</td>
          </tr>
        </tbody>
      </table>
      <div class="pc-card" v-if="(activeTab === 0 && whgcData.length === 0) || (activeTab === 1 && companyData.length === 0)">
        <div style="text-align:center;padding:40px;color:#999">暂无数据</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import http from '../api/http'

const year = ref(new Date().getFullYear())
const month = ref(new Date().getMonth() + 1)
const periodType = ref('actual')
const activeTab = ref(0)
const whgcData = ref([])
const companyData = ref([])
const fmtValue = (v) => { if (v === null || v === undefined) return '-'; if (Math.abs(v) >= 10000) return (v / 10000).toFixed(2) + '万'; return v.toLocaleString() }
const fetchAll = async () => {
  try {
    const params = { year: year.value, month: month.value, period_type: periodType.value }
    const [whgcRes, companyRes] = await Promise.all([http.get('/summary/whgc', { params }), http.get('/summary/company', { params })])
    whgcData.value = whgcRes.data.subjects || []; companyData.value = companyRes.data.subjects || []
  } catch (e) {}
}
const exportCompany = () => {
  const token = localStorage.getItem('access_token')
  window.open(`/api/export/company-report?year=${year.value}&month=${month.value}&period_type=${periodType.value}&token=${token}`)
}
onMounted(fetchAll)
</script>

<style scoped>
.page { min-height: 100vh; background: #f0f2f5; }
.top-bar { background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; color: #fff; }
.top-left { display: flex; align-items: center; gap: 12px; }
.back-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
.top-title { font-size: 17px; font-weight: 600; }
.tab-bar { display: flex; background: #fff; border-radius: 8px; overflow: hidden; margin-bottom: 16px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
.tab-item { flex: 1; text-align: center; padding: 12px; cursor: pointer; font-size: 14px; font-weight: 500; color: #666; border-bottom: 2px solid transparent; transition: all .2s; }
.tab-item.active { color: #1a73e8; border-bottom-color: #1a73e8; background: #f0f6ff; }
.tab-item:hover { background: #f8f9ff; }
.calculated { color: #1a73e8; font-weight: 600; }
</style>
