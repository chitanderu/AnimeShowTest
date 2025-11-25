import { createRouter, createWebHistory } from 'vue-router'
import CharacterShowcaseView from '../views/CharacterShowcase.vue'
import CharacterShowall from "@/views/CharacterShowall.vue";

const routes = [
  {
    path: '/',
    name: 'home',
    component: CharacterShowcaseView
  },
  {
    path: '/characters',
    name: 'characters',
    component: CharacterShowcaseView
  },

   {
    path: '/showall',
    name: 'showall',
    component: CharacterShowall
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
