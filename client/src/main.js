import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import store from './store'
import router from './router'
import upperFirst from 'lodash/upperFirst'
import camelCase from 'lodash/camelCase'
import './assets/styles/nprogress.css'
import Vuelidate from 'vuelidate'

Vue.use(Vuelidate)

const requireComponent = require.context(
  // The relative path of the components folder
  './components',
  // Whether to look in sub-folders
  false,
  // The regular expression used to match base component filenames
  /Base[A-Z]\w+\.(vue|js)$/
)

requireComponent.keys().forEach((fileName) => {
  // Get component config
  const componentConfig = requireComponent(fileName)

  // Get PascalCase name of component
  const componentName = upperFirst(
    camelCase(
      // Gets the file name regardless of folder depth
      fileName
        .split('/')
        .pop()
        .replace(/\.\w+$/, '')
    )
  )

  // Register component globally
  Vue.component(
    componentName,
    // Look for the component options on `.default`, which will
    // exist if the component was exported with `export default`,
    // otherwise fall back to module's root.
    componentConfig.default || componentConfig
  )
})
Vue.config.productionTip = false

new Vue({
  vuetify,
  router,
  store,
  render: (h) => h(App),
}).$mount('#app')
