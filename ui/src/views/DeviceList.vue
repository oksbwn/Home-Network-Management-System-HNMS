<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Devices</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">{{ devices.length }} devices discovered</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="flex bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
          <button @click="exportDevices"
            class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-l-lg transition text-slate-600 dark:text-slate-400"
            title="Export JSON">
            <Download class="h-4 w-4" />
          </button>
          <div class="w-px bg-slate-200 dark:bg-slate-700"></div>
          <button @click="$refs.importInput.click()"
            class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-r-lg transition text-slate-600 dark:text-slate-400"
            title="Import JSON">
            <Upload class="h-4 w-4" />
          </button>
        </div>
        <input type="file" ref="importInput" class="hidden" @change="handleImport" accept=".json" />
        <button @click="triggerScan" :disabled="isScanning"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
          <component :is="isScanning ? Loader2 : RefreshCw" class="h-4 w-4" :class="{ 'animate-spin': isScanning }" />
          {{ isScanning ? 'Scanning...' : 'Scan Network' }}
        </button>
      </div>
    </div>

    <!-- Error Alert -->
    <div v-if="error"
      class="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-900/30 text-sm flex items-center gap-3">
      <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div v-for="stat in deviceStats" :key="stat.label"
        class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-md rounded-2xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-xl transition-all flex flex-col justify-between overflow-hidden group min-h-[100px]">

        <!-- Sparkline Background -->
        <Sparkline :data="stat.trend" :color="stat.color" class="opacity-15" />

        <!-- Header Row -->
        <div class="relative z-10 flex items-center justify-between w-full">
          <div :class="[stat.bgClass, 'p-1.5 rounded-lg shadow-sm border border-white/10']">
            <component :is="stat.icon" class="h-4 w-4" />
          </div>
          <div v-if="stat.change"
            class="flex items-center gap-1 bg-white/50 dark:bg-slate-900/40 px-2 py-0.5 rounded-full backdrop-blur-sm border border-slate-200/50 dark:border-slate-700/50">
            <span :class="[stat.changeType === 'down' ? 'text-rose-500' : 'text-emerald-600', 'text-[10px] font-bold']">
              {{ stat.change }}
            </span>
          </div>
        </div>

        <!-- Center Content -->
        <div class="relative z-10 flex flex-col items-center text-center -mt-1">
          <p class="text-2xl font-black text-slate-900 dark:text-white tracking-tight leading-none">
            {{ stat.value }}
          </p>
          <p :style="{ color: stat.color }" class="text-[9px] font-black uppercase tracking-[0.2em] opacity-80 mt-1">
            {{ stat.label }}
          </p>
        </div>
      </div>
    </div>

    <!-- Devices Table -->
    <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
          <thead class="bg-slate-50 dark:bg-slate-900/50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Device</th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Network Info</th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Type</th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Last Seen</th>
              <th
                class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:divide-slate-700">
            <tr v-for="device in devices" :key="device.id"
              @click="$router.push({ name: 'DeviceDetails', params: { id: device.id } })"
              class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors cursor-pointer group">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="relative">
                    <div
                      class="p-2 bg-slate-100 dark:bg-slate-700 rounded-lg group-hover:bg-white dark:group-hover:bg-slate-600 transition-colors">
                      <component :is="getIcon(device.icon || 'help-circle')"
                        class="h-5 w-5 text-slate-600 dark:text-slate-400" />
                    </div>
                    <span
                      class="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 border-white dark:border-slate-800"
                      :class="getDeviceStatusColor(device)"></span>
                  </div>
                  <div class="min-w-0">
                    <div
                      class="text-sm font-medium text-slate-900 dark:text-white truncate group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {{ device.display_name ||
                        'Unnamed Device' }}</div>
                    <div class="text-xs text-slate-500 font-mono">{{ device.ip }}</div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-xs text-slate-600 dark:text-slate-300">{{ device.vendor || 'Unknown' }}</div>
                <div class="text-xs text-slate-500 font-mono truncate max-w-[200px]">{{ device.mac || 'N/A' }}</div>
              </td>
              <td class="px-6 py-4">
                <span
                  class="inline-flex px-2 py-1 text-xs font-medium rounded bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                  {{ device.device_type || 'Unknown' }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">
                {{ formatRelativeTime(device.last_seen) }}
              </td>
              <td class="px-6 py-4 text-right" @click.stop>
                <div class="flex items-center justify-end gap-3">
                  <router-link :to="{ name: 'DeviceDetails', params: { id: device.id } }"
                    class="p-2 text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all"
                    title="View Device Details">
                    <Eye class="h-4 w-4" />
                  </router-link>
                  <button @click="openEditDialog(device)"
                    class="p-2 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all"
                    title="Edit Device Name & Type">
                    <Pencil class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingDevice" class="fixed inset-0 z-50 overflow-y-auto" @click.self="editingDevice = null">
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50 transition-opacity"></div>
        <div class="relative bg-white dark:bg-slate-800 rounded-lg shadow-xl max-w-lg w-full">
          <div class="p-6 border-b border-slate-200 dark:border-slate-700">
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Edit Device</h3>
          </div>
          <div class="p-6 space-y-4">
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Display Name</label>
              <input v-model="editForm.display_name" type="text"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" />
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Device Type</label>
              <select v-model="editForm.device_type"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                <option value="unknown">Unknown</option>
                <option value="Router/Gateway">Router/Gateway</option>
                <option value="Desktop">Desktop</option>
                <option value="Laptop">Laptop</option>
                <option value="Mobile">Mobile</option>
                <option value="IoT">IoT Device</option>
                <option value="Printer">Printer</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Icon</label>
              <select v-model="editForm.icon"
                class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
                <option v-for="icon in availableIcons" :key="icon" :value="icon">{{ icon }}</option>
              </select>
            </div>
          </div>
          <div
            class="px-6 py-4 bg-slate-50 dark:bg-slate-900/50 flex justify-end gap-3 border-t border-slate-200 dark:border-slate-700">
            <button @click="editingDevice = null"
              class="px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
              Cancel
            </button>
            <button @click="saveDevice" :disabled="saving"
              class="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg text-sm font-medium transition-colors">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'
import axios from 'axios'
import Sparkline from '@/components/Sparkline.vue'
import { Download, Upload, RefreshCw, Loader2, Smartphone, Tablet, Laptop, Monitor, Server, Router as RouterIcon, Network, Layers, Rss, Tv, Cpu, Printer, HardDrive, Gamepad2, HelpCircle, Lightbulb, Plug, Microchip, Camera, Waves, Speaker, Play, Eye, Pencil, Database, Wifi, ZapOff, Ticket } from 'lucide-vue-next'
import { formatRelativeTime } from '@/utils/date'

const devices = ref([])
const error = ref('')
const isScanning = ref(false)
const editingDevice = ref(null)
const editForm = reactive({ display_name: '', device_type: '', icon: '' })
const saving = ref(false)

const availableIcons = ['smartphone', 'tablet', 'laptop', 'monitor', 'server', 'router', 'network', 'layers', 'rss', 'tv', 'cpu', 'printer', 'hard-drive', 'gamepad-2', 'lightbulb', 'plug', 'microchip', 'camera', 'waves', 'speaker', 'play', 'help-circle']

const iconMap = { smartphone: Smartphone, tablet: Tablet, laptop: Laptop, monitor: Monitor, server: Server, router: RouterIcon, network: Network, layers: Layers, rss: Rss, tv: Tv, speaker: Speaker, play: Play, cpu: Cpu, lightbulb: Lightbulb, plug: Plug, microchip: Microchip, camera: Camera, waves: Waves, printer: Printer, 'hard-drive': HardDrive, 'gamepad-2': Gamepad2, 'help-circle': HelpCircle }

const getIcon = (name) => iconMap[name] || HelpCircle

const getDeviceStatusColor = (device) => {
  if (device.status === 'online') return 'bg-emerald-500'
  if (device.status === 'offline') return 'bg-slate-400'
  return 'bg-slate-300'
}

const deviceStats = computed(() => {
  const total = devices.value.length
  const online = devices.value.filter(d => d.status === 'online').length
  const offline = devices.value.filter(d => d.status === 'offline').length

  // Calculate top vendor
  const vendors = {}
  devices.value.forEach(d => {
    const v = d.vendor || 'Unknown'
    vendors[v] = (vendors[v] || 0) + 1
  })
  let topVendor = 'None'
  let topVendorCount = 0
  Object.entries(vendors).forEach(([v, count]) => {
    if (count > topVendorCount && v !== 'Unknown') {
      topVendor = v
      topVendorCount = count
    }
  })

  return [
    {
      label: 'Total Devices',
      value: total,
      icon: Database,
      color: '#3b82f6',
      bgClass: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
      trend: [10, 12, 11, 13, 12, 14, 13, 15, 14, 16],
      change: '+2.4%',
      changeType: 'up'
    },
    {
      label: 'Online',
      value: online,
      icon: Wifi,
      color: '#10b981',
      bgClass: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
      trend: [8, 9, 7, 10, 9, 11, 10, 12, 11, 13],
      change: '+5.2%',
      changeType: 'up'
    },
    {
      label: 'Offline',
      value: offline,
      icon: ZapOff,
      color: '#f43f5e',
      bgClass: 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400',
      trend: [2, 3, 4, 3, 3, 3, 3, 3, 3, 3],
      change: '-1.5%',
      changeType: 'down'
    },
    {
      label: 'Top Vendor',
      value: topVendor.length > 10 ? topVendor.substring(0, 8) + '..' : topVendor,
      icon: Ticket,
      color: '#8b5cf6',
      bgClass: 'bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400',
      trend: [5, 6, 5, 7, 6, 8, 7, 9, 8, 10],
      change: `count: ${topVendorCount}`,
      changeType: 'up'
    }
  ]
})


const fetchDevices = async () => {
  try {
    const res = await axios.get('/api/v1/devices/')
    devices.value = res.data
  } catch (e) {
    error.value = 'Failed to load devices'
    console.error(e)
  }
}

const triggerScan = async () => {
  isScanning.value = true
  try {
    await axios.post('/api/v1/scans/discovery')
    await new Promise(resolve => setTimeout(resolve, 2000))
    await fetchDevices()
  } catch (e) {
    error.value = 'Scan failed'
  } finally {
    isScanning.value = false
  }
}

const openEditDialog = (device) => {
  editingDevice.value = device
  editForm.display_name = device.display_name
  editForm.device_type = device.device_type || 'unknown'
  editForm.icon = device.icon || 'help-circle'
}

const saveDevice = async () => {
  saving.value = true
  try {
    await axios.put(`/api/v1/devices/${editingDevice.value.id}`, editForm)
    await fetchDevices()
    editingDevice.value = null
  } catch (e) {
    error.value = 'Failed to save device'
  } finally {
    saving.value = false
  }
}

const exportDevices = () => {
  const dataStr = JSON.stringify(devices.value, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `devices-${new Date().toISOString().split('T')[0]}.json`
  a.click()
  URL.revokeObjectURL(url)
}

const handleImport = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  try {
    const text = await file.text()
    const data = JSON.parse(text)
    for (const device of data) {
      await axios.put(`/api/v1/devices/${device.id}`, device)
    }
    await fetchDevices()
  } catch (e) {
    error.value = 'Import failed'
  }
}

let pollInterval = null

onMounted(() => {
  fetchDevices()
  pollInterval = setInterval(fetchDevices, 10000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>
