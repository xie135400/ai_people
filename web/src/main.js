import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Vant UI 组件库
import { 
  Button, 
  Cell, 
  CellGroup, 
  Field, 
  Form, 
  NavBar, 
  Tabbar, 
  TabbarItem,
  Card,
  Grid,
  GridItem,
  Progress,
  Circle,
  Tag,
  Divider,
  Space,
  Loading,
  Toast,
  Dialog,
  Notify,
  ActionSheet,
  Popup,
  Overlay,
  PullRefresh,
  List,
  Empty,
  Image as VanImage,
  Icon,
  Badge,
  Switch,
  Slider,
  Rate,
  CountDown,
  NumberKeyboard,
  PasswordInput,
  Search,
  Sticky,
  Swipe,
  SwipeItem,
  Lazyload,
  Picker
} from 'vant'

// Vant 样式
import 'vant/lib/index.css'

// WindiCSS
import 'virtual:windi.css'

// 全局样式
import './assets/styles/main.css'

// 开发环境调试工具（暂时禁用localStorage监控以减少输出）
// if (process.env.NODE_ENV === 'development') {
//   import('./utils/debug.js').then(({ startLocalStorageMonitoring }) => {
//     startLocalStorageMonitoring()
//   })
// }

const app = createApp(App)
const pinia = createPinia()

// 注册 Vant 组件
app.use(Button)
app.use(Cell)
app.use(CellGroup)
app.use(Field)
app.use(Form)
app.use(NavBar)
app.use(Tabbar)
app.use(TabbarItem)
app.use(Card)
app.use(Grid)
app.use(GridItem)
app.use(Progress)
app.use(Circle)
app.use(Tag)
app.use(Divider)
app.use(Space)
app.use(Loading)
app.use(Toast)
app.use(Dialog)
app.use(Notify)
app.use(ActionSheet)
app.use(Popup)
app.use(Overlay)
app.use(PullRefresh)
app.use(List)
app.use(Empty)
app.use(VanImage)
app.use(Icon)
app.use(Badge)
app.use(Switch)
app.use(Slider)
app.use(Rate)
app.use(CountDown)
app.use(NumberKeyboard)
app.use(PasswordInput)
app.use(Search)
app.use(Sticky)
app.use(Swipe)
app.use(SwipeItem)
app.use(Lazyload)
app.use(Picker)

app.use(pinia)
app.use(router)

app.mount('#app')

// 隐藏加载动画
setTimeout(() => {
  const loading = document.getElementById('loading')
  if (loading) {
    loading.style.display = 'none'
  }
}, 1000) 