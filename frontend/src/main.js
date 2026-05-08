import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import Toast from './components/Toast.vue'

import Login from './views/Login.vue'
import Home from './views/Home.vue'
import MyForms from './views/MyForms.vue'
import FormDetail from './views/FormDetail.vue'
import ReviewDept from './views/ReviewDept.vue'
import ReviewCompany from './views/ReviewCompany.vue'
import Summary from './views/Summary.vue'
import Rollup from './views/Rollup.vue'
import Admin from './views/Admin.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login, meta: { public: true } },
  { path: '/home', component: Home },
  { path: '/forms', component: MyForms },
  { path: '/form/:formId', component: FormDetail },
  { path: '/review/dept', component: ReviewDept },
  { path: '/review/company', component: ReviewCompany },
  { path: '/summary', component: Summary },
  { path: '/rollup', component: Rollup },
  { path: '/admin', component: Admin },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.public) {
    next()
  } else if (!token) {
    next('/login')
  } else {
    next()
  }
})

const app = createApp(App)
app.use(router)
app.component('Toast', Toast)
app.mount('#app')
