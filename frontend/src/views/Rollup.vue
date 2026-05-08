<template>
  <div class="page">
    <div class="top-bar">
      <div class="top-left">
        <button class="back-btn" @click="$router.back()">&#8592;</button>
        <span class="top-title">推移表</span>
      </div>
      <div class="top-actions">
        <button class="pc-btn pc-btn-default pc-btn-sm" @click="toggleView">{{ viewMode === 'single' ? '对比视图' : '单视图' }}</button>
        <button class="pc-btn pc-btn-success pc-btn-sm" @click="exportTable">导出Excel</button>
      </div>
    </div>
    <div class="page-container">
      <div class="pc-filter-bar">
        <label>年份</label><input type="number" v-model="year" />
        <label>类型</label>
        <select v-model="periodType" @change="fetchData">
          <option value="actual">实际</option><option value="planned">预定</option><option value="budget">预算</option>
        </select>
        <label>部门</label>
        <select v-model="deptCode" @change="fetchData">
          <option v-for="d in deptOptions" :key="d.value" :value="d.value">{{ d.text }}</option>
        </select>
        <button class="pc-btn pc-btn-primary pc-btn-sm" @click="fetchData">查询</button>
      </div>

      <div v-if="viewMode === 'single'" class="pc-card" style="overflow-x:auto;padding:0">
        <table class="rollup-table">
          <thead>
            <tr>
              <th class="sticky-col code-col">编码</th>
              <th class="sticky-col name-col">名称</th>
              <th v-for="m in 12" :key="m">{{ m }}月</th>
              <th class="cumulative-col">年度累计</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="cat in categories" :key="cat.name">
              <tr class="section-header"><td :colspan="14">{{ cat.name }}</td></tr>
              <tr v-for="code in cat.codes" :key="code">
                <td class="sticky-col code-col" :class="{ calculated: subjectMap[code]?.is_calculated }">{{ code }}</td>
                <td class="sticky-col name-col">{{ subjectMap[code]?.name || code }}</td>
                <td v-for="m in 12" :key="m" class="value-cell">{{ fmtVal(getValue(code, m)) }}</td>
                <td class="cumulative-col value-cell" :class="{ calculated: subjectMap[code]?.is_calculated }">{{ fmtVal(getCumulative(code)) }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>

      <div v-else>
        <div v-for="(label, key) in typesForCompare" :key="key" class="pc-card" style="overflow-x:auto;padding:0;margin-bottom:16px">
          <h4 :class="'type-label type-' + key">{{ label }}</h4>
          <table class="rollup-table">
            <thead>
              <tr>
                <th class="sticky-col code-col">编码</th><th class="sticky-col name-col">名称</th>
                <th v-for="m in 12" :key="m">{{ m }}月</th><th class="cumulative-col">年度累计</th>
              </tr>
            </thead>
            <tbody>
              <template v-for="cat in categories" :key="cat.name">
                <tr class="section-header"><td :colspan="14">{{ cat.name }}</td></tr>
                <tr v-for="code in cat.codes" :key="code">
                  <td class="sticky-col code-col" :class="{ calculated: subjectMap[code]?.is_calculated }">{{ code }}</td>
                  <td class="sticky-col name-col">{{ subjectMap[code]?.name || code }}</td>
                  <td v-for="m in 12" :key="m" class="value-cell">{{ fmtVal(getCompareValue(key, code, m)) }}</td>
                  <td class="cumulative-col value-cell" :class="{ calculated: subjectMap[code]?.is_calculated }">{{ fmtVal(getCompareCumulative(key, code)) }}</td>
                </tr>
              </template>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import http from '../api/http'

const year = ref(new Date().getFullYear())
const periodType = ref('actual')
const deptCode = ref('')
const viewMode = ref('single')
const deptOptions = ref([])
const rollupData = ref([])
const compareData = ref({ budget: [], planned: [], actual: [] })
const subjectMap = ref({})
const subjectOrder = ref([])
const typesForCompare = { budget: '预算（蓝色）', planned: '预定（绿色）', actual: '实际（红色）' }

const categories = computed(() => {
  const order = ['收入', '变动费用', '边界利益', '固定费用', '附加价值', '时间', '重要指标', '人工费']
  const result = []
  for (const cat of order) {
    const codes = subjectOrder.value.filter(c => subjectMap.value[c]?.category === cat)
    if (codes.length > 0) result.push({ name: cat, codes })
  }
  return result
})
const fmtVal = (v) => { if (v === null || v === undefined) return '-'; if (Math.abs(v) >= 10000) return (v / 10000).toFixed(2) + '万'; if (Number.isInteger(v)) return v.toLocaleString(); return v.toFixed(2) }
const getValue = (code, month) => { const m = rollupData.value.find(d => d.month === month); return m?.subjects?.[code] ?? null }
const getCumulative = (code) => { const m = rollupData.value.find(d => d.month === 12); return m?.cumulative?.[code] ?? null }
const getCompareValue = (type, code, month) => { const arr = compareData.value[type] || []; const m = arr.find(d => d.month === month); return m?.subjects?.[code] ?? null }
const getCompareCumulative = (type, code) => { const arr = compareData.value[type] || []; const m = arr.find(d => d.month === 12); return m?.cumulative?.[code] ?? null }
const toggleView = async () => { if (viewMode.value === 'single') { viewMode.value = 'compare'; await fetchCompare() } else { viewMode.value = 'single' } }
const fetchData = async () => {
  if (!deptCode.value) return
  try {
    const { data } = await http.get('/summary/rollup', { params: { dept_code: deptCode.value, year: year.value, period_type: periodType.value } })
    rollupData.value = data.data || []; subjectMap.value = data.subjects || {}; subjectOrder.value = data.subject_order || []
  } catch (e) {}
}
const fetchCompare = async () => {
  if (!deptCode.value) return
  try {
    const { data } = await http.get('/summary/rollup-compare', { params: { dept_code: deptCode.value, year: year.value } })
    compareData.value = { budget: data.budget || [], planned: data.planned || [], actual: data.actual || [] }
    subjectMap.value = data.subjects || {}; subjectOrder.value = data.subject_order || []
  } catch (e) {}
}
const exportTable = () => { const token = localStorage.getItem('access_token'); window.open(`/api/export/rollup-report?dept_code=${deptCode.value}&year=${year.value}&period_type=${periodType.value}&token=${token}`) }
const fetchDepts = async () => {
  try {
    const { data } = await http.get('/org/departments')
    const userInfo = JSON.parse(localStorage.getItem('user_info') || '{}')
    let allowed = data
    if (['dept_filler', 'dept_reviewer'].includes(userInfo.role)) allowed = data.filter(d => d.code === userInfo.dept_code)
    deptOptions.value = [{ text: '请选择部门', value: '' }, ...allowed.map(d => ({ text: d.name, value: d.code }))]
    if (allowed.length > 0 && !deptCode.value) deptCode.value = allowed[0].code
  } catch (e) {}
}
onMounted(async () => { await fetchDepts(); if (deptCode.value) fetchData() })
</script>

<style scoped>
.page { min-height: 100vh; background: #f0f2f5; }
.top-bar { background: linear-gradient(135deg, #1a73e8 0%, #1557b0 100%); padding: 12px 20px; display: flex; justify-content: space-between; align-items: center; color: #fff; }
.top-left { display: flex; align-items: center; gap: 12px; }
.back-btn { background: none; border: none; color: #fff; font-size: 22px; cursor: pointer; }
.top-title { font-size: 17px; font-weight: 600; }
.top-actions { display: flex; gap: 8px; }
.rollup-table { width: 100%; border-collapse: collapse; font-size: 12px; white-space: nowrap; }
.rollup-table th, .rollup-table td { padding: 6px 8px; border: 1px solid #e8e8e8; text-align: center; }
.rollup-table th { background: #4472c4; color: #fff; font-weight: 600; position: sticky; top: 0; z-index: 2; }
.sticky-col { position: sticky; left: 0; background: #fff; z-index: 1; }
.rollup-table th.sticky-col { z-index: 3; background: #4472c4; }
.code-col { min-width: 55px; }
.name-col { min-width: 110px; text-align: left; }
.cumulative-col { font-weight: 600; }
.value-cell { text-align: right; }
.calculated { color: #1a73e8; font-weight: 600; }
.section-header td { background: #e8f0fe !important; font-weight: 700; color: #1a73e8; text-align: left; padding: 6px 8px; }
.type-label { padding: 10px 16px; margin: 0; font-size: 14px; }
.type-budget { background: #e3f2fd; color: #1565c0; }
.type-planned { background: #e8f5e9; color: #2e7d32; }
.type-actual { background: #fce4ec; color: #c62828; }
</style>
