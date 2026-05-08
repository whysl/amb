<template>
  <Toast />
  <router-view />
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f0f2f5;
  color: #333;
  -webkit-font-smoothing: antialiased;
}
#app {
  min-height: 100vh;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px 24px;
}

.pc-table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  font-size: 13px;
}
.pc-table th {
  background: #4472c4;
  color: #fff;
  padding: 10px 12px;
  font-weight: 600;
  text-align: center;
  white-space: nowrap;
}
.pc-table td {
  padding: 8px 12px;
  border-bottom: 1px solid #f0f0f0;
  text-align: center;
}
.pc-table tbody tr:hover {
  background: #f8f9ff;
}
.pc-table .section-header td {
  background: #e8f0fe;
  font-weight: 700;
  color: #1a73e8;
  padding: 8px 12px;
  font-size: 13px;
  text-align: left;
}

.form-input {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 13px;
  text-align: right;
  outline: none;
  transition: border-color 0.2s;
  background: #fff;
}
.form-input:focus {
  border-color: #1a73e8;
}
.form-input.readonly {
  background: #f5f7fa;
  border-color: #e8e8e8;
  color: #1a73e8;
  font-weight: 600;
}

.remark-input {
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 6px 8px;
  font-size: 12px;
  outline: none;
  transition: border-color 0.2s;
}
.remark-input:focus {
  border-color: #1a73e8;
}

.pc-status-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}
.pc-status-draft { background: #f5f5f5; color: #999; }
.pc-status-submitted { background: #fff3e0; color: #e65100; }
.pc-status-dept_approved { background: #e3f2fd; color: #1565c0; }
.pc-status-dept_rejected { background: #fce4ec; color: #c62828; }
.pc-status-company_approved { background: #e8f5e9; color: #2e7d32; }
.pc-status-company_rejected { background: #fce4ec; color: #c62828; }

.pc-btn {
  padding: 8px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}
.pc-btn-primary {
  background: #1a73e8;
  color: #fff;
}
.pc-btn-primary:hover {
  background: #1557b0;
}
.pc-btn-default {
  background: #fff;
  color: #333;
  border: 1px solid #d0d0d0;
}
.pc-btn-default:hover {
  background: #f5f5f5;
}
.pc-btn-danger {
  background: #e34d59;
  color: #fff;
}
.pc-btn-danger:hover {
  background: #c62828;
}
.pc-btn-warning {
  background: #ff9800;
  color: #fff;
}
.pc-btn-warning:hover {
  background: #e68900;
}
.pc-btn-success {
  background: #2ba471;
  color: #fff;
}
.pc-btn-success:hover {
  background: #1f8257;
}
.pc-btn-sm {
  padding: 5px 14px;
  font-size: 12px;
}

.pc-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
}

.pc-filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #fff;
  border-radius: 8px;
  padding: 12px 16px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.pc-filter-bar label {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}
.pc-filter-bar input,
.pc-filter-bar select {
  padding: 6px 10px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  font-size: 13px;
  outline: none;
}
.pc-filter-bar input:focus,
.pc-filter-bar select:focus {
  border-color: #1a73e8;
}
.pc-filter-bar input[type="number"] {
  width: 80px;
}

.van-nav-bar--fixed ~ .page-container {
  padding-top: 66px;
}
</style>
