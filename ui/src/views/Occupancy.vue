<template>
    <div class="space-y-6">
        <div class="flex justify-between items-center">
            <div>
                <h1 class="text-2xl font-bold text-gray-900 dark:text-white">IP Occupancy</h1>
                <p class="text-sm text-gray-500 mt-1">Network map for subnet {{ selectedSubnet }}.0/24</p>
            </div>

            <div
                class="flex items-center space-x-3 bg-white dark:bg-slate-800 p-2 rounded-lg border border-gray-100 dark:border-slate-700 shadow-sm">
                <label class="text-xs font-bold text-gray-400 uppercase">Subnet:</label>
                <select v-model="selectedSubnet"
                    class="bg-transparent text-sm font-medium text-gray-900 dark:text-white outline-none cursor-pointer">
                    <option v-for="s in availableSubnets" :key="s" :value="s">{{ s }}.0/24</option>
                </select>
            </div>
        </div>

        <!-- Summary Bar -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="stat in summaryStats" :key="stat.label" 
                class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-gray-100 dark:border-slate-700 shadow-sm">
                <div class="text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">{{ stat.label }}</div>
                <div class="flex items-end justify-between">
                    <div class="text-2xl font-mono font-bold text-gray-900 dark:text-white">{{ stat.value }}</div>
                    <div :class="stat.colorClass" class="w-2 h-2 rounded-full mb-2 shadow-[0_0_8px_rgba(0,0,0,0.1)]"></div>
                </div>
            </div>
        </div>

        <div class="bg-white dark:bg-slate-800 rounded-2xl shadow-sm p-4 md:p-8 border border-gray-100 dark:border-slate-700">
            <div class="flex flex-col gap-6 md:gap-10">
                <!-- Grouped Grid -->
                <div v-for="rowIndex in 8" :key="rowIndex" class="space-y-3">
                    <div class="flex items-center space-x-3 text-[9px] md:text-[10px] font-bold text-gray-400 dark:text-slate-500 uppercase tracking-widest">
                        <span class="whitespace-nowrap">Row {{ rowIndex }} (IP .{{ (rowIndex - 1) * 32 + 1 }} - .{{ Math.min(rowIndex * 32, 255) }})</span>
                        <div class="flex-1 h-px bg-gray-100 dark:bg-slate-700/50"></div>
                    </div>
                    
                    <div class="flex flex-wrap gap-4 md:gap-6 px-1">
                        <!-- Blocks of 8 -->
                        <div v-for="blockIndex in 4" :key="blockIndex" class="flex flex-wrap gap-1.5 md:gap-2">
                            <template v-for="i in 8" :key="i">
                                <template v-if="((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i) <= 254">
                                    <div 
                                        class="w-8 h-8 md:w-10 md:h-10 flex items-center justify-center text-[8px] md:text-[10px] font-mono font-bold rounded-lg md:rounded-xl transition-all duration-300 cursor-pointer relative group shadow-sm border"
                                        :class="getStatusClass((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i)" 
                                        @click="goToDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i)">
                                        <span class="font-bold">{{ (rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i }}</span>

                                        <!-- Tooltip -->
                                        <div v-if="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i)"
                                            class="invisible group-hover:visible absolute bottom-full mb-3 left-1/2 -translate-x-1/2 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-[10px] p-4 rounded-2xl shadow-2xl z-50 w-56 border border-slate-100 dark:border-slate-700 origin-bottom ring-8 ring-slate-900/5 transition-all scale-95 group-hover:scale-100 opacity-0 group-hover:opacity-100 hidden sm:block">
                                            <div class="flex items-center space-x-3 mb-3">
                                                <div class="p-2 bg-slate-50 dark:bg-slate-800 rounded-xl shadow-inner border border-slate-100 dark:border-slate-700">
                                                    <component :is="getIcon(getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).icon)"
                                                        class="h-5 w-5 text-slate-600 dark:text-slate-400" />
                                                </div>
                                                <div class="flex-1 min-w-0 text-left">
                                                    <div class="font-bold truncate text-xs leading-tight">{{ getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).display_name ||
                                                        getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).ip }}</div>
                                                    <div class="text-[9px] text-slate-500 font-mono truncate leading-none mt-1">{{
                                                        getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).ip }}</div>
                                                </div>
                                            </div>
                                            <div
                                                class="text-[9px] space-y-1.5 border-t border-slate-50 dark:border-slate-800 pt-3">
                                                <div v-if="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).status" class="flex justify-between items-center">
                                                    <span class="text-slate-400 font-medium">STATUS</span>
                                                    <span :class="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).status === 'online' ? 'text-emerald-500' : 'text-rose-500'" class="font-black uppercase text-[8px] tracking-widest px-1.5 py-0.5 bg-slate-50 dark:bg-slate-800 rounded-md border border-slate-100 dark:border-slate-700">{{ getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).status }}</span>
                                                </div>
                                                <div v-if="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).last_seen" class="flex justify-between items-center">
                                                    <span class="text-slate-400 font-medium uppercase text-[8px]">Last Seen</span>
                                                    <span class="text-slate-700 dark:text-slate-200 font-bold">{{ formatTime(getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).last_seen) }}</span>
                                                </div>
                                                <div v-if="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).vendor"
                                                    class="flex justify-between items-center">
                                                    <span class="text-slate-400 font-medium uppercase text-[8px]">Vendor</span> 
                                                    <span class="max-w-[100px] truncate text-slate-700 dark:text-slate-200 font-bold">{{ getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).vendor }}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </template>
                            </template>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import {
    Smartphone, Tablet, Laptop, Monitor, Server, Router as RouterIcon,
    Network, Layers, Rss, Tv, Cpu, Printer, HardDrive, Gamepad2, HelpCircle,
    Lightbulb, Plug, Microchip, Camera, Waves, Speaker, Play
} from 'lucide-vue-next'

const devices = ref([])
const router = useRouter()
const selectedSubnet = ref('')

const availableIcons = {
    'smartphone': Smartphone, 'tablet': Tablet, 'laptop': Laptop, 'monitor': Monitor,
    'server': Server, 'router': RouterIcon, 'network': Network, 'layers': Layers,
    'rss': Rss, 'tv': Tv, 'speaker': Speaker, 'play': Play, 'cpu': Cpu,
    'lightbulb': Lightbulb, 'plug': Plug, 'microchip': Microchip, 'camera': Camera,
    'waves': Waves, 'printer': Printer, 'hard-drive': HardDrive, 'gamepad-2': Gamepad2,
    'help-circle': HelpCircle
}

const getIcon = (name) => availableIcons[name] || HelpCircle

const availableSubnets = computed(() => {
    const subnets = new Set()
    devices.value.forEach(d => {
        const parts = d.ip.split('.')
        if (parts.length === 4) {
            subnets.add(`${parts[0]}.${parts[1]}.${parts[2]}`)
        }
    })
    return Array.from(subnets).sort()
})

const getDevice = (suffix) => {
    return devices.value.find(d => {
        const parts = d.ip.split('.')
        return parts.length === 4 &&
            `${parts[0]}.${parts[1]}.${parts[2]}` === selectedSubnet.value &&
            parseInt(parts[3]) === suffix
    })
}

const summaryStats = computed(() => {
    const subnetDevices = devices.value.filter(d => {
        const parts = d.ip.split('.')
        return parts.length === 4 && `${parts[0]}.${parts[1]}.${parts[2]}` === selectedSubnet.value
    })
    
    const online = subnetDevices.filter(d => d.status === 'online').length
    const offline = subnetDevices.filter(d => d.status === 'offline').length
    const used = subnetDevices.length
    const free = 254 - used

    return [
        { label: 'Used / Known', value: used, colorClass: 'bg-blue-500' },
        { label: 'Online Now', value: online, colorClass: 'bg-emerald-500' },
        { label: 'Offline', value: offline, colorClass: 'bg-rose-500' },
        { label: 'Available', value: free, colorClass: 'bg-gray-200 dark:bg-slate-700' }
    ]
})

const getStatusClass = (suffix) => {
    const d = getDevice(suffix)
    
    if (!d) {
        return 'bg-blue-400 dark:bg-blue-600/80 text-white border-blue-300/20 hover:bg-blue-500 transition-colors'
    }

    if (d.status === 'online') {
        return 'bg-emerald-400 dark:bg-emerald-500/80 text-white border-emerald-300/20 hover:bg-emerald-500'
    }
    
    return 'bg-rose-400 dark:bg-rose-500/80 text-white border-rose-300/20 hover:bg-rose-500'
}

const goToDevice = (suffix) => {
    const d = getDevice(suffix)
    if (d) {
        router.push(`/devices/${d.id}`)
    }
}

const formatTime = (t) => {
    if (!t) return 'N/A'
    const date = new Date(t)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

onMounted(async () => {
    try {
        const res = await axios.get('/api/v1/devices/')
        devices.value = res.data

        if (devices.value.length > 0) {
            const counts = {}
            devices.value.forEach(d => {
                const parts = d.ip.split('.')
                if (parts.length === 4) {
                    const sub = `${parts[0]}.${parts[1]}.${parts[2]}`
                    counts[sub] = (counts[sub] || 0) + 1
                }
            })
            
            const subnetKeys = Object.keys(counts)
            if (subnetKeys.length > 0) {
                selectedSubnet.value = subnetKeys.reduce((a, b) => counts[a] > counts[b] ? a : b)
            }
        }
    } catch (e) {
        console.error("Failed to fetch devices:", e)
    }
})
</script>

<style scoped></style>
