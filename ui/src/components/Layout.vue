<template>
  <div class="flex h-screen w-full bg-gray-50 dark:bg-slate-900 transition-colors duration-300">
    <!-- Sidebar -->
    <aside class="w-72 flex-shrink-0 bg-white dark:bg-slate-800 border-r border-slate-100 dark:border-slate-700 hidden md:flex flex-col shadow-[1px_0_0_rgba(0,0,0,0.02)]">
      <div class="h-24 flex items-center px-8">
        <AppLogo />
      </div>

      <nav class="flex-1 overflow-y-auto py-6">
        <div class="px-4 mb-4">
          <p class="px-4 text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-4">Command Center</p>
          <ul class="space-y-1.5">
            <li v-for="item in navItems" :key="item.name">
              <router-link
                :to="item.path"
                class="group flex items-center px-4 py-3 text-sm font-bold rounded-2xl transition-all duration-200"
                :class="[
                  $route.path === item.path || ($route.path.startsWith(item.path) && item.path !== '/')
                    ? 'bg-slate-900 dark:bg-white text-white dark:text-slate-900 shadow-lg shadow-slate-200 dark:shadow-none'
                    : 'text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700/50 hover:text-slate-900 dark:hover:text-white'
                ]"
              >
                <component :is="item.icon" class="mr-3 h-5 w-5 flex-shrink-0 transition-transform group-hover:scale-110" />
                {{ item.name }}
              </router-link>
            </li>
          </ul>
        </div>
      </nav>

      <div class="p-8 border-t border-slate-50 dark:border-slate-700">
        <div class="bg-slate-50 dark:bg-slate-900/50 rounded-2xl p-4 border border-slate-100 dark:border-slate-700">
            <p class="text-[10px] font-black text-slate-400 dark:text-slate-600 uppercase tracking-widest text-center">
              System v0.2.4
            </p>
        </div>
      </div>
    </aside>

    <!-- Mobile Header -->
    <div class="md:hidden fixed top-0 w-full bg-white dark:bg-slate-800 z-50 border-b border-slate-100 dark:border-slate-700 h-20 flex items-center justify-between px-6">
      <AppLogo class="scale-90 origin-left" />
      <button @click="mobileMenuOpen = !mobileMenuOpen" class="p-2 rounded-xl bg-slate-50 dark:bg-slate-900 text-slate-500 dark:text-slate-400">
        <Bars3Icon class="h-6 w-6" />
      </button>
    </div>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto pt-20 md:pt-0">
      <div class="max-w-7xl mx-auto px-6 lg:px-12 py-10">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AppLogo from './AppLogo.vue'
import { 
  HomeIcon, 
  ComputerDesktopIcon, 
  TableCellsIcon, 
  Cog6ToothIcon,
  Bars3Icon,
  ListBulletIcon
} from '@heroicons/vue/24/outline'

const mobileMenuOpen = ref(false)

const navItems = [
  { name: 'Dashboard', path: '/', icon: HomeIcon },
  { name: 'Devices', path: '/devices', icon: ComputerDesktopIcon },
  { name: 'Scan History', path: '/scans', icon: ListBulletIcon },
  { name: 'IP Occupancy', path: '/occupancy', icon: TableCellsIcon },
  { name: 'Settings', path: '/settings', icon: Cog6ToothIcon },
]
</script>
