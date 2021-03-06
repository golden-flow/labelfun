import Vue from 'vue'
import Router from 'vue-router'
import TaskCenter from './views/TaskCenter.vue'
import NProgress from 'nprogress'
import store from '@/store'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'home',
      component: TaskCenter,
      meta: {
        requiresAuth: true,
        displayName: '任务中心',
      },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/Login.vue'),
      meta: {
        requiresNoAuth: true,
        displayName: '登录',
      },
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('./views/Signup.vue'),
      meta: {
        requiresNoAuth: true,
        displayName: '注册',
      },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('./views/Profile.vue'),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/task/new',
      name: 'create',
      component: () => import('./views/TaskCreate.vue'),
      meta: {
        requiresAuth: true,
        displayName: '新建任务',
      },
    },
    {
      path: '/task/:id',
      name: 'task',
      component: () => import('./views/TaskView.vue'),
      props: (route) => ({
        id: Number(route.params.id),
      }),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/label-cls/:task_id/:entity_idx',
      name: 'label-cls',
      component: () => import('./views/LabelPanelCls.vue'),
      props: (route) => ({
        task_id: Number(route.params.task_id),
        entity_idx: Number(route.params.entity_idx),
      }),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/label-img/:task_id/:entity_idx',
      name: 'label-img',
      component: () => import('./views/LabelPanelImage.vue'),
      props: (route) => ({
        task_id: Number(route.params.task_id),
        entity_idx: Number(route.params.entity_idx),
      }),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/label-vid/:task_id/:entity_idx',
      name: 'label-vid',
      component: () => import('./views/LabelPanelVideo.vue'),
      props: (route) => ({
        task_id: Number(route.params.task_id),
        entity_idx: Number(route.params.entity_idx),
      }),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/review/:task_id/:entity_idx',
      name: 'review',
      component: () => import('./views/ReviewPanel.vue'),
      props: (route) => ({
        task_id: Number(route.params.task_id),
        entity_idx: Number(route.params.entity_idx),
      }),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/view/:task_id/:entity_idx',
      name: 'view',
      component: () => import('./views/ReviewPanel.vue'),
      props: (route) => ({
        task_id: Number(route.params.task_id),
        entity_idx: Number(route.params.entity_idx),
        viewOnly: true,
      }),
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/404',
      name: '404',
      component: () => import('./views/NotFound.vue'),
    },
    {
      path: '*',
      redirect: { name: '404' },
    },
  ],
})

router.beforeEach((to, from, next) => {
  NProgress.start()
  const loggedIn = localStorage.getItem('user')
  // protected route
  if (to.matched.some((record) => record.meta.requiresAuth) && !loggedIn) {
    store.commit('message/POP_ALL')
    store.dispatch('message/push', {
      type: 'error',
      text: '请登录。',
    })
    NProgress.done()
    next('/login')
  }
  // routes hidden for logged-in users, e.g. login and register pages
  else if (
    to.matched.some((record) => record.meta.requiresNoAuth) &&
    loggedIn
  ) {
    next('/')
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router
