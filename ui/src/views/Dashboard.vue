<template>
  <div class="space-y-8">
    <div class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Dashboard</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1 text-sm font-medium">Real-time network operation status</p>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div v-for="stat in stats" :key="stat.label" 
        class="group relative bg-white dark:bg-slate-800 rounded-3xl p-8 shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 overflow-hidden transition-all hover:scale-[1.02] active:scale-[0.98]">
        <div class="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 rounded-full opacity-5 group-hover:opacity-10 transition-opacity" :class="stat.bgClass"></div>
        
        <div class="relative flex items-center justify-between">
          <div>
            <h2 class="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-3">{{ stat.label }}</h2>
            <p class="text-4xl font-black text-slate-900 dark:text-white font-mono tracking-tighter">{{ stat.value }}</p>
          </div>
          <div class="p-4 rounded-2xl shadow-inner shadow-white/10" :class="stat.bgClass">
            <component :is="stat.icon" class="h-8 w-8 text-white" />
          </div>
        </div>
      </div>
    </div>

    <!-- Network map & activity -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <!-- Hierarchy / Network Map -->
        <div class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 p-8">
            <div class="flex items-center justify-between mb-8">
                <h2 class="text-lg font-black text-slate-900 dark:text-white uppercase tracking-tight">Network Map</h2>
                <span class="px-3 py-1 bg-blue-50 dark:bg-blue-500/10 text-blue-500 text-[10px] font-black uppercase tracking-widest rounded-lg border border-blue-100 dark:border-blue-500/20">Alpha</span>
            </div>
            
            <div class="relative h-80 flex items-center justify-center bg-slate-50 dark:bg-slate-900/50 rounded-3xl border border-dashed border-slate-200 dark:border-slate-700">
                <div class="text-center group cursor-pointer">
                    <div class="inline-flex p-6 bg-white dark:bg-slate-800 rounded-full shadow-lg mb-6 group-hover:scale-110 transition-transform">
                        <svg viewBox="0 0 24 24" class="w-10 h-10 text-blue-500" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="3" />
                            <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
                        </svg>
                    </div>
                    <p class="text-sm font-black text-slate-900 dark:text-white uppercase tracking-widest">Gateway Mesh</p>
                    <p class="text-[10px] text-slate-400 dark:text-slate-500 mt-2 font-medium">Topology visualization coming in v0.3.0</p>
                </div>
            </div>
        </div>

        <!-- System Logs / Activity -->
        <div class="bg-slate-900 dark:bg-slate-800 rounded-[2.5rem] shadow-xl border border-slate-800 dark:border-slate-700 p-8 text-white overflow-hidden relative">
            <div class="absolute inset-0 bg-blue-500/5 pointer-events-none"></div>
            <div class="relative">
                <div class="flex items-center justify-between mb-8">
                    <h2 class="text-lg font-black uppercase tracking-tight">System Activity</h2>
                    <div class="flex items-center space-x-2">
                        <div class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></div>
                        <span class="text-[10px] font-black text-emerald-500 uppercase tracking-widest">Live</span>
                    </div>
                </div>

                <div class="space-y-4">
                    <div v-for="i in 5" :key="i" class="flex items-start space-x-4 p-4 bg-white/5 rounded-2xl border border-white/5">
                        <div class="w-1.5 h-1.5 rounded-full bg-blue-500 mt-1.5"></div>
                        <div>
                            <p class="text-[11px] font-bold text-slate-300">Scanner engine enqueued background task</p>
                            <p class="text-[9px] text-slate-500 font-mono mt-1 uppercase">ProcessID: Discovery_0{{i}}</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ComputerDesktopIcon, WifiIcon, ExclamationTriangleIcon } from '@heroicons/vue/24/outline'
import axios from 'axios'

const stats = ref([
  { label: 'Network Assets', value: '0', icon: ComputerDesktopIcon, bgClass: 'bg-blue-500', textClass: 'text-blue-500' },
  { label: 'Active Links', value: '0', icon: WifiIcon, bgClass: 'bg-emerald-500', textClass: 'text-emerald-500' },
  { label: 'Critical Signals', value: '0', icon: ExclamationTriangleIcon, bgClass: 'bg-rose-500', textClass: 'text-rose-500' },
])

onMounted(async () => {
    try {
        const res = await axios.get('/api/v1/devices/')
        const devices = res.data
        stats.value[0].value = devices.length
        stats.value[1].value = devices.filter(d => d.status === 'online').length
        // Alerts logic can be expanded later
        stats.value[2].value = devices.filter(d => d.status === 'offline').length
    } catch (e) {
        console.error(e)
    }
})
</script>
