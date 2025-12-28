<template>
  <div class="space-y-8">
    <div class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Devices</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1 text-sm font-medium">Inventory of all discovered network
          assets</p>
      </div>
      <div class="flex items-center gap-3">
        <div
          class="flex bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 p-1">
          <button @click="exportDevices"
            class="p-2.5 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-xl transition text-slate-500 dark:text-slate-400"
            title="Export JSON">
            <Download class="h-4 w-4" />
          </button>
          <button @click="$refs.importInput.click()"
            class="p-2.5 hover:bg-slate-50 dark:hover:bg-slate-700 rounded-xl transition text-slate-500 dark:text-slate-400"
            title="Import JSON">
            <Upload class="h-4 w-4" />
          </button>
        </div>
        <input type="file" ref="importInput" class="hidden" @change="handleImport" accept=".json" />
        <button @click="triggerScan" :disabled="isScanning"
          class="px-6 py-3 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl text-xs font-black shadow-lg shadow-slate-200 dark:shadow-none hover:scale-105 active:scale-95 transition-all uppercase tracking-widest disabled:opacity-50 flex items-center">
          <component :is="isScanning ? Loader2 : RefreshCw" class="h-4 w-4 mr-2"
            :class="{ 'animate-spin': isScanning }" />
          {{ isScanning ? 'Discovery Active' : 'Scan Now' }}
        </button>
      </div>
    </div>

    <!-- Error state -->
    <div v-if="error"
      class="p-4 bg-rose-50 dark:bg-rose-900/20 text-rose-700 dark:text-rose-400 rounded-2xl border border-rose-100 dark:border-rose-900/30 text-sm font-medium flex items-center space-x-3">
      <svg viewBox="0 0 24 24" class="w-5 h-5 text-rose-500" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <span>{{ error }}</span>
    </div>

    <!-- Device Table -->
    <div
      class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-50 dark:divide-slate-700">
          <thead>
            <tr class="bg-slate-50/50 dark:bg-slate-900/50">
              <th
                class="px-8 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Device Ident</th>
              <th
                class="px-6 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Metadata & Services</th>
              <th
                class="px-6 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Classification</th>
              <th
                class="px-6 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Last Ack</th>
              <th
                class="px-8 py-5 text-right text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Control</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-700">
            <tr v-for="device in devices" :key="device.id"
              class="group hover:bg-slate-50/80 dark:hover:bg-slate-700/30 transition-colors">
              <td class="px-8 py-6 whitespace-nowrap">
                <div class="flex items-center space-x-4">
                  <div class="relative">
                    <div
                      class="p-3 bg-slate-50 dark:bg-slate-900 rounded-2xl group-hover:scale-110 transition-transform shadow-sm">
                      <component :is="getIcon(device.icon || 'help-circle')"
                        class="h-6 w-6 text-slate-600 dark:text-slate-400" />
                    </div>
                    <span
                      class="absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-[3px] border-white dark:border-slate-800 shadow-md transition-colors duration-500"
                      :class="getDeviceStatusColor(device)"></span>
                  </div>
                  <div>
                    <div class="text-sm font-black text-slate-900 dark:text-white leading-tight">
                      {{ device.display_name || 'Anonymous Asset' }}
                    </div>
                    <div class="text-[10px] text-slate-400 font-mono mt-1 uppercase tracking-wider">{{ device.ip }}
                    </div>
                  </div>
                </div>
              </td>
              <td class="px-6 py-6 border-l border-slate-50 dark:border-slate-700/30">
                <div class="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-tight">{{
                  device.vendor || 'Unknown Source' }}</div>
                <div class="text-[9px] text-slate-400 font-mono mt-1 truncate max-w-[140px]">{{ device.mac ||
                  'Unidentified' }}</div>
                <div class="flex flex-wrap gap-1 mt-2">
                  <span v-for="port in parsePorts(device.open_ports)" :key="port.port"
                    class="px-2 py-0.5 rounded-md text-[9px] font-black uppercase tracking-tighter"
                    :class="getPortColor(port.port)">
                    {{ port.service || port.port }}
                  </span>
                </div>
              </td>
              <td class="px-6 py-6 whitespace-nowrap">
                <span
                  class="px-2.5 py-1 text-[9px] font-black uppercase tracking-widest rounded-lg bg-blue-50 text-blue-500 border border-blue-100 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20">
                  {{ device.device_type || 'unclassified' }}
                </span>
              </td>
              <td class="px-6 py-6 whitespace-nowrap">
                <div class="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">
                  {{ formatTimeRelative(device.last_seen) }}
                </div>
                <div class="text-[8px] text-slate-300 dark:text-slate-600 mt-1 font-mono uppercase">{{
                  formatTimeFull(device.last_seen) }}</div>
              </td>
              <td class="px-8 py-6 whitespace-nowrap text-right">
                <div class="flex items-center justify-end space-x-2">
                  <button @click="editDevice(device)"
                    class="p-2.5 rounded-xl border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-400 hover:text-slate-900 dark:hover:text-white hover:border-slate-900 transition-all shadow-sm"
                    title="Modify Config">
                    <Edit2 class="h-4 w-4" />
                  </button>
                  <router-link :to="'/devices/' + device.id"
                    class="p-2.5 rounded-xl border border-slate-100 dark:border-slate-700 bg-white dark:bg-slate-800 text-slate-400 hover:text-slate-900 dark:hover:text-white hover:border-slate-900 transition-all shadow-sm"
                    title="Telemetry Analysis">
                    <ExternalLink class="h-4 w-4" />
                  </router-link>
                </div>
              </td>
            </tr>
            <tr v-if="devices.length === 0 && !loading">
              <td colspan="5" class="px-6 py-24 text-center">
                <div class="inline-flex p-6 bg-slate-100 dark:bg-slate-900 rounded-full mb-6">
                  <Search class="h-8 w-8 text-slate-400" />
                </div>
                <p class="text-sm font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em] italic">Void
                  Detected: Signal Discovery Required</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingDevice"
      class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-900/60 backdrop-blur-md transition-all duration-300">
      <div
        class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-[0_32px_64px_-16px_rgba(0,0,0,0.3)] w-full max-w-lg border border-white/20 dark:border-slate-700 overflow-hidden transform transition-all scale-100">
        <div
          class="px-10 py-8 border-b border-slate-100 dark:border-slate-700 flex justify-between items-center bg-slate-50/50 dark:bg-slate-900/30">
          <div>
            <h3 class="text-xl font-black text-slate-900 dark:text-white uppercase tracking-tight">Modify Asset</h3>
            <p class="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-1">Configuring {{ editForm.ip }}
            </p>
          </div>
          <button @click="editingDevice = null"
            class="p-2 hover:bg-white dark:hover:bg-slate-700 rounded-full text-slate-400 transition-colors shadow-sm">
            <X class="h-6 w-6" />
          </button>
        </div>

        <div class="p-10 space-y-8">
          <div>
            <label
              class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Friendly
              Identification</label>
            <input v-model="editForm.display_name"
              class="w-full px-6 py-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none text-slate-900 dark:text-white font-bold transition-all shadow-inner"
              placeholder="e.g. Master Workstation" />
          </div>

          <div class="grid grid-cols-1 gap-8">
            <div>
              <label
                class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Asset
                Classification</label>
              <select v-model="editForm.device_type"
                class="w-full px-6 py-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none text-slate-900 dark:text-white font-bold transition-all shadow-inner appearance-none cursor-pointer">
                <option v-for="type in deviceTypes" :key="type" :value="type">{{ type }}</option>
              </select>
            </div>

            <div>
              <label
                class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Visual
                Matrix Link</label>
              <div
                class="grid grid-cols-6 gap-3 p-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700 rounded-[2rem] shadow-inner">
                <button v-for="(iconComp, key) in availableIcons" :key="key" @click="editForm.icon = key" type="button"
                  class="aspect-square flex items-center justify-center rounded-xl border-2 transition-all p-2"
                  :class="editForm.icon === key ? 'border-blue-500 bg-white dark:bg-slate-800 text-blue-500 shadow-lg scale-110 rotate-3 z-10' : 'border-transparent hover:bg-white dark:hover:bg-slate-800 text-slate-400'"
                  :title="key">
                  <component :is="iconComp" class="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div
          class="px-10 py-8 bg-slate-50 dark:bg-slate-900/50 flex justify-end items-center gap-6 border-t border-slate-100 dark:border-slate-700">
          <button @click="editingDevice = null"
            class="text-xs font-black text-slate-400 hover:text-slate-900 dark:hover:text-white uppercase tracking-widest transition-colors">Abort</button>
          <button @click="saveDevice" :disabled="saving"
            class="px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl text-xs font-black shadow-xl shadow-slate-200 dark:shadow-none hover:scale-105 active:scale-95 transition-all uppercase tracking-widest disabled:opacity-50">
            {{ saving ? 'Syncing...' : 'Commit Changes' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import axios from 'axios'
import {
  Smartphone, Tablet, Laptop, Monitor, Server, Router as RouterIcon,
  Network, Layers, Rss, Tv, Cpu, Printer, HardDrive, Gamepad2,
  HelpCircle, Edit2, ExternalLink, X, RefreshCw, Loader2,
  Lightbulb, Plug, Microchip, Camera, Waves, Speaker, Play,
  Download, Upload
} from 'lucide-vue-next'

const devices = ref([])
const isScanning = ref(false)
const loading = ref(true)
const error = ref('')
const saving = ref(false)
const importInput = ref(null)

const editingDevice = ref(null)
const editForm = reactive({
  display_name: '',
  device_type: '',
  vendor: '',
  icon: ''
})

const exportDevices = async () => {
  try {
    const res = await axios.get('/api/v1/devices/export/json')
    const dataStr = JSON.stringify(res.data, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)
    const fileName = `netowrk_scanner_export_${new Date().toISOString().slice(0, 10)}.json`
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', fileName)
    linkElement.click()
  } catch (e) {
    console.error('Export failed:', e)
    alert('Failed to export devices')
  }
}

const handleImport = (event) => {
  const file = event.target.files[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const devicesData = JSON.parse(e.target.result)
      await axios.post('/api/v1/devices/import/json', devicesData)
      alert('Import successful!')
      fetchDevices()
    } catch (err) {
      console.error('Import failed:', err)
      alert('Failed to import devices. Please ensure the file is valid JSON.')
    } finally {
      event.target.value = '' // Clear input
    }
  }
  reader.readAsText(file)
}

const deviceTypes = [
  'Smartphone', 'Tablet', 'Laptop', 'Desktop', 'Server',
  'Router/Gateway', 'Network Bridge', 'Switch', 'Access Point',
  'TV/Entertainment', 'Audio/Speaker', 'Streaming Device',
  'IoT Device', 'Smart Bulb', 'Smart Plug/Switch',
  'Microcontroller', 'Security Camera', 'Sensor', 'Printer',
  'NAS/Storage', 'Game Console', 'Generic', 'unknown'
]

const availableIcons = {
  'smartphone': Smartphone,
  'tablet': Tablet,
  'laptop': Laptop,
  'monitor': Monitor,
  'server': Server,
  'router': RouterIcon,
  'network': Network,
  'layers': Layers,
  'rss': Rss,
  'tv': Tv,
  'speaker': Speaker,
  'play': Play,
  'cpu': Cpu,
  'lightbulb': Lightbulb,
  'plug': Plug,
  'microchip': Microchip,
  'camera': Camera,
  'waves': Waves,
  'printer': Printer,
  'hard-drive': HardDrive,
  'gamepad-2': Gamepad2,
  'help-circle': HelpCircle
}

const getIcon = (name) => {
  return availableIcons[name] || HelpCircle
}

const fetchDevices = async () => {
  error.value = ''
  try {
    const res = await axios.get('/api/v1/devices/')
    devices.value = res.data
  } catch (e) {
    console.error(e)
    error.value = 'Failed to load devices. Backend might be offline.'
  } finally {
    loading.value = false
  }
}

const editDevice = (device) => {
  editingDevice.value = device
  editForm.display_name = device.display_name
  editForm.device_type = device.device_type
  editForm.vendor = device.vendor
  editForm.icon = device.icon || 'help-circle'
}

const saveDevice = async () => {
  saving.value = true
  try {
    const res = await axios.put(`/api/v1/devices/${editingDevice.value.id}`, editForm)
    Object.assign(editingDevice.value, res.data)
    editingDevice.value = null
  } catch (e) {
    alert('Failed to save device updates')
    console.error(e)
  } finally {
    saving.value = false
  }
}

const checkActiveScan = async () => {
  try {
    const res = await axios.get('/api/v1/scans/')
    isScanning.value = res.data.some(s => s.status === 'queued' || s.status === 'running')
  } catch (e) {
    console.error('Failed to check active scans', e)
  }
}

const triggerScan = async () => {
  isScanning.value = true
  try {
    await axios.post('/api/v1/scans/discovery')
  } catch (error) {
    console.error('Scan failed:', error)
  } finally {
    await checkActiveScan()
  }
}

const isOnline = (d) => {
  if (!d.last_seen) return false
  const lastSeenDate = new Date(d.last_seen)
  return (new Date() - lastSeenDate) < 300000 // 5 mins
}
// Determine the visual status color for a device
// - Gray when a scan is in progress (pending)
// - Green when the device was seen within the last 5 minutes (online)
// - Red when the device is offline (not seen recently)
const getDeviceStatusColor = (d) => {
  if (d.status === 'online') return 'bg-green-500'
  if (d.status === 'offline') return 'bg-red-500'
  return 'bg-gray-300' // unknown
}

const formatTimeRelative = (t) => {
  if (!t) return 'Offline'
  const diff = new Date() - new Date(t)
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

const formatTimeFull = (t) => {
  if (!t) return 'No detection history'
  return new Date(t).toLocaleString()
}

const parsePorts = (portsJson) => {
  if (!portsJson) return []
  try {
    const parsed = JSON.parse(portsJson)
    // Handle both simple int list and new dict list
    if (Array.isArray(parsed) && parsed.length > 0) {
      if (typeof parsed[0] === 'number') {
        // Backwards compat if any mixed
        return parsed.map(p => ({ port: p, service: p }))
      }
      return parsed
    }
    return []
  } catch {
    return []
  }
}

const getPortColor = (port) => {
  const map = {
    22: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300', // SSH
    80: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300', // HTTP
    443: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-300', // HTTPS
    53: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300', // DNS
    3000: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300', // Dev
    8000: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300', // Dev
    8080: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300', // Alt Web
    3389: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300', // RDP
    21: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300', // FTP
  }
  return map[port] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
}

let pollInterval = null

onMounted(() => {
  fetchDevices()
  checkActiveScan()
  pollInterval = setInterval(() => {
    checkActiveScan()
    fetchDevices()
  }, 10000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>
