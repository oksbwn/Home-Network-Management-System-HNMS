<template>
    <div class="space-y-8">
        <div class="flex justify-between items-end">
            <div>
                <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase">Zone Map</h1>
                <p class="text-sm text-slate-500 font-medium mt-1">Matrix occupancy for segment {{ selectedSubnet
                }}.0/24</p>
            </div>

            <div
                class="px-5 py-3 bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm flex items-center space-x-4 transition-all hover:shadow-md">
                <label class="text-[10px] font-black text-slate-400 uppercase tracking-widest">Active Segment</label>
                <select v-model="selectedSubnet"
                    class="bg-transparent text-xs font-black text-slate-900 dark:text-white outline-none cursor-pointer appearance-none">
                    <option v-for="s in availableSubnets" :key="s" :value="s">{{ s }}.0/24</option>
                </select>
                <svg viewBox="0 0 24 24" class="w-3 h-3 text-slate-400" fill="none" stroke="currentColor"
                    stroke-width="3">
                    <path d="M6 9l6 6 6-6" />
                </svg>
            </div>
        </div>

        <!-- Summary Bar -->
        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div v-for="stat in summaryStats" :key="stat.label"
                class="group relative bg-white dark:bg-slate-800 rounded-3xl p-6 border border-slate-100 dark:border-slate-700 shadow-xl shadow-slate-200/50 dark:shadow-none transition-all hover:scale-[1.02]">
                <div class="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] mb-3">
                    {{ stat.label }}</div>
                <div class="flex items-end justify-between">
                    <div class="text-3xl font-black text-slate-900 dark:text-white font-mono tracking-tighter">{{
                        stat.value }}</div>
                    <div :class="stat.colorClass" class="w-2.5 h-2.5 rounded-full mb-2 shadow-lg animate-pulse"></div>
                </div>
            </div>
        </div>

        <div
            class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none p-6 md:p-12 border border-slate-100 dark:border-slate-700">
            <div class="flex flex-col gap-10 md:gap-14">
                <!-- Grouped Grid -->
                <div v-for="rowIndex in 8" :key="rowIndex" class="space-y-6">
                    <div class="flex items-center space-x-6">
                        <span
                            class="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em] whitespace-nowrap">Bank
                            {{ rowIndex }} <span class="text-slate-200 dark:text-slate-700 ml-2">// .{{ (rowIndex - 1) *
                                32 + 1 }} - .{{ Math.min(rowIndex * 32, 255) }}</span></span>
                        <div class="flex-1 h-px bg-slate-50 dark:bg-slate-700/50"></div>
                    </div>

                    <div class="flex flex-wrap gap-4 md:gap-10">
                        <!-- Blocks of 8 -->
                        <div v-for="blockIndex in 4" :key="blockIndex" class="inline-grid grid-cols-4 gap-2 md:gap-3">
                            <template v-for="i in 8" :key="i">
                                <template v-if="((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i) <= 254">
                                    <div class="w-8 h-8 md:w-11 md:h-11 flex items-center justify-center text-[9px] md:text-[11px] font-black rounded-lg md:rounded-2xl transition-all duration-500 cursor-pointer relative group border-2 shadow-sm uppercase tracking-tighter"
                                        :class="getStatusClass((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i)"
                                        @click="goToDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i)">
                                        <span>{{ (rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i }}</span>

                                        <!-- Tooltip -->
                                        <div v-if="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i)"
                                            class="invisible group-hover:visible absolute bottom-full mb-4 left-1/2 -translate-x-1/2 bg-white dark:bg-slate-900 text-slate-900 dark:text-white text-[10px] p-6 rounded-[2rem] shadow-2xl z-[100] w-64 border border-slate-100 dark:border-slate-700 origin-bottom ring-[20px] ring-black/5 transition-all scale-90 group-hover:scale-100 opacity-0 group-hover:opacity-100 hidden sm:block">
                                            <div class="flex items-center space-x-4 mb-5">
                                                <div
                                                    class="p-3 bg-slate-50 dark:bg-slate-800 rounded-2xl shadow-inner border border-slate-100 dark:border-slate-700">
                                                    <component
                                                        :is="getIcon(getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).icon)"
                                                        class="h-6 w-6 text-slate-600 dark:text-slate-400" />
                                                </div>
                                                <div class="flex-1 min-w-0 text-left">
                                                    <div
                                                        class="font-black truncate text-xs uppercase tracking-tight leading-tight">
                                                        {{ getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 +
                                                            i).display_name || 'Asset ' + (rowIndex - 1) * 32 + (blockIndex
                                                                - 1) * 8 + i }}</div>
                                                    <div
                                                        class="text-[9px] text-slate-400 font-mono font-bold mt-1 tracking-widest uppercase truncate leading-none">
                                                        {{ getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).ip
                                                        }}</div>
                                                </div>
                                            </div>
                                            <div class="space-y-2 border-t border-slate-50 dark:border-slate-800 pt-4">
                                                <div class="flex justify-between items-center">
                                                    <span
                                                        class="text-slate-400 font-black uppercase text-[8px] tracking-[0.2em]">Matrix
                                                        Status</span>
                                                    <span
                                                        :class="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).status === 'online' ? 'text-emerald-500' : 'text-rose-500'"
                                                        class="font-black uppercase text-[8px] tracking-widest px-2 py-1 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-100 dark:border-slate-700">{{
                                                            getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).status
                                                        }}</span>
                                                </div>
                                                <div v-if="getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8 + i).last_seen"
                                                    class="flex justify-between items-center">
                                                    <span
                                                        class="text-slate-400 font-black uppercase text-[8px] tracking-[0.2em]">Signal
                                                        Ack</span>
                                                    <span
                                                        class="text-slate-900 dark:text-white font-black uppercase text-[9px]">{{
                                                            formatTime(getDevice((rowIndex - 1) * 32 + (blockIndex - 1) * 8
                                                                + i).last_seen) }}</span>
                                                </div>
                                            </div>
                                            <div
                                                class="absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 bg-white dark:bg-slate-900 rotate-45 border-r border-b border-slate-100 dark:border-slate-700">
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
