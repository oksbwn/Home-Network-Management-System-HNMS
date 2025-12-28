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
            class="px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-l-lg transition text-slate-600 dark:text-slate-400 flex items-center gap-2 text-xs font-medium"
            v-tooltip="'Export Devices to JSON'">
            <Download class="h-4 w-4" />
            <span class="hidden sm:inline">Export</span>
          </button>
          <div class="w-px bg-slate-200 dark:bg-slate-700"></div>
          <button @click="$refs.importInput.click()"
            class="px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-r-lg transition text-slate-600 dark:text-slate-400 flex items-center gap-2 text-xs font-medium"
            v-tooltip="'Import Devices from JSON'">
            <Upload class="h-4 w-4" />
            <span class="hidden sm:inline">Import</span>
          </button>
        </div>
        <input type="file" ref="importInput" class="hidden" @change="handleImport" accept=".json" />
        <button @click="triggerScan" :disabled="isScanning"
          class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-slate-500 dark:text-slate-400"
          v-tooltip="isScanning ? 'Scanning Network...' : 'Scan Network'">
          <component :is="isScanning ? Loader2 : RefreshCw" class="w-5 h-5" :class="{ 'animate-spin': isScanning }" />
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

    <!-- Success Alert -->
    <div v-if="successMessage"
      class="p-4 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 rounded-lg border border-emerald-200 dark:border-emerald-900/30 text-sm flex items-center gap-3">
      <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
      </svg>
      <span>{{ successMessage }}</span>
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
                Open Ports</th>
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
                <div v-if="device.open_ports && device.open_ports.length > 0" class="flex flex-wrap gap-1">
                  <span v-for="port in device.open_ports.slice(0, 3)" :key="typeof port === 'object' ? port.port : port"
                    class="px-1.5 py-0.5 rounded text-[10px] font-medium bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 border border-blue-100 dark:border-blue-800 uppercase">
                    {{ typeof port === 'object' ? (port.service || port.port) : port }}
                  </span>
                  <span v-if="device.open_ports.length > 3" class="text-[10px] text-slate-500 self-center">
                    +{{ device.open_ports.length - 3 }}
                  </span>
                </div>
                <span v-else class="text-xs text-slate-400 italic">No ports</span>
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
                <div class="flex items-center justify-end gap-1">
                  <router-link :to="{ name: 'DeviceDetails', params: { id: device.id } }"
                    class="p-1.5 text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all"
                    v-tooltip="'View Device Details'">
                    <Eye class="h-4 w-4" />
                  </router-link>
                  <button @click.stop="openEditDialog(device)"
                    class="p-1.5 text-slate-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-all"
                    v-tooltip="'Edit Device Name & Type'">
                    <Pencil class="h-4 w-4" />
                  </button>
                  <button @click.stop="confirmDelete(device)"
                    class="p-1.5 text-slate-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                    v-tooltip="'Delete Device'">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <EditDeviceModal :isOpen="isEditModalOpen" :device="deviceToEdit" @close="isEditModalOpen = false"
      @save="handleDeviceSaved" />
    <!-- Delete Confirmation Modal -->
    <div v-if="deviceToDelete" class="fixed inset-0 z-50 overflow-y-auto" @click.self="cancelDelete">
      <div class="flex min-h-screen items-center justify-center p-4">
        <div class="fixed inset-0 bg-black/50 transition-opacity"></div>
        <div class="relative bg-white dark:bg-slate-800 rounded-lg shadow-xl max-w-sm w-full p-6">
          <div class="flex flex-col items-center text-center">
            <div class="h-12 w-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center mb-4">
              <Trash2 class="h-6 w-6 text-red-600 dark:text-red-400" />
            </div>
            <h3 class="text-lg font-semibold text-slate-900 dark:text-white mb-2">Delete Device?</h3>
            <p class="text-sm text-slate-500 dark:text-slate-400 mb-6">
              Are you sure you want to delete <strong>{{ deviceToDelete.display_name || deviceToDelete.ip }}</strong>?
              This action cannot be undone.
            </p>
            <div class="flex gap-3 w-full">
              <button @click="cancelDelete"
                class="flex-1 px-4 py-2 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors">
                Cancel
              </button>
              <button @click="deleteDevice"
                class="flex-1 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors">
                Delete
              </button>
            </div>
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
import EditDeviceModal from '@/components/EditDeviceModal.vue'
import * as LucideIcons from 'lucide-vue-next'
const { Eye, Pencil, Trash2, Download, Upload, RefreshCw, Loader2 } = LucideIcons
import { formatRelativeTime } from '@/utils/date'

const devices = ref([])
const error = ref('')
const isScanning = ref(false)
const isEditModalOpen = ref(false)
const deviceToEdit = ref(null)
const successMessage = ref('')

const getIcon = (name) => {
  if (!name) return LucideIcons.HelpCircle
  // Direct match (PascalCase)
  if (LucideIcons[name]) return LucideIcons[name]
  // Legacy mapping (kebab-case -> PascalCase or map)
  const legacyMap = {
    'smartphone': 'Smartphone',
    'tablet': 'Tablet',
    'laptop': 'Laptop',
    'monitor': 'Monitor',
    'server': 'Server',
    'router': 'Router',
    'network': 'Network',
    'layers': 'Layers',
    'rss': 'Rss',
    'tv': 'Tv',
    'speaker': 'Speaker',
    'play': 'Play',
    'cpu': 'Cpu',
    'lightbulb': 'Lightbulb',
    'plug': 'Plug',
    'microchip': 'Microchip',
    'camera': 'Camera',
    'waves': 'Waves',
    'printer': 'Printer',
    'hard-drive': 'HardDrive',
    'gamepad-2': 'Gamepad2',
    'help-circle': 'HelpCircle',
    'computer-desktop': 'Monitor', // HeroIcons compat
    'device-laptop': 'Laptop',
    'device-phone-mobile': 'Smartphone',
    'device-tablet': 'Tablet',
    'server-stack': 'Database',
    'bolt': 'Zap'
  }
  if (legacyMap[name] && LucideIcons[legacyMap[name]]) return LucideIcons[legacyMap[name]]

  // Auto convert kebab to Pascal
  const camel = name.split('-').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join('')
  if (LucideIcons[camel]) return LucideIcons[camel]

  return LucideIcons.HelpCircle
}

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
      icon: LucideIcons.Database,
      color: '#3b82f6',
      bgClass: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
      trend: [10, 12, 11, 13, 12, 14, 13, 15, 14, 16],
      change: '+2.4%',
      changeType: 'up'
    },
    {
      label: 'Online',
      value: online,
      icon: LucideIcons.Wifi,
      color: '#10b981',
      bgClass: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
      trend: [8, 9, 7, 10, 9, 11, 10, 12, 11, 13],
      change: '+5.2%',
      changeType: 'up'
    },
    {
      label: 'Offline',
      value: offline,
      icon: LucideIcons.ZapOff,
      color: '#f43f5e',
      bgClass: 'bg-rose-100 text-rose-600 dark:bg-rose-900/30 dark:text-rose-400',
      trend: [2, 3, 4, 3, 3, 3, 3, 3, 3, 3],
      change: '-1.5%',
      changeType: 'down'
    },
    {
      label: 'Top Vendor',
      value: topVendor.length > 10 ? topVendor.substring(0, 8) + '..' : topVendor,
      icon: LucideIcons.Ticket,
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

const deviceToDelete = ref(null)

const confirmDelete = (device) => {
  deviceToDelete.value = device
}

const cancelDelete = () => {
  deviceToDelete.value = null
}

const deleteDevice = async () => {
  if (!deviceToDelete.value) return

  try {
    await axios.delete(`/api/v1/devices/${deviceToDelete.value.id}`)
    devices.value = devices.value.filter(d => d.id !== deviceToDelete.value.id)
    deviceToDelete.value = null
  } catch (e) {
    alert('Failed to delete device')
    error.value = 'Failed to delete device'
  }
}


const openEditDialog = (device) => {
  deviceToEdit.value = device
  isEditModalOpen.value = true
}

const handleDeviceSaved = (updatedDevice) => {
  // Update local list
  const idx = devices.value.findIndex(d => d.id === updatedDevice.id)
  if (idx !== -1) {
    devices.value[idx] = updatedDevice
  }
  successMessage.value = 'Device updated successfully'
  setTimeout(() => successMessage.value = '', 3000)
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
