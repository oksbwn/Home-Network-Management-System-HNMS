<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Devices</h1>
      <button 
        @click="triggerScan" 
        :disabled="isScanning"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
      >
        <svg v-if="isScanning" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isScanning ? 'Scanning...' : 'Scan Now' }}
      </button>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
        <thead class="bg-gray-50 dark:bg-slate-900">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Name / IP</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Vendor (MAC)</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Last Seen</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-slate-700">
          <tr v-for="device in devices" :key="device.id" class="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition">
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="inline-flex h-2.5 w-2.5 rounded-full" :class="isOnline(device) ? 'bg-green-500 shadow-md shadow-green-500/30' : 'bg-gray-300 dark:bg-slate-600'"></span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900 dark:text-white">{{ device.display_name || device.name || 'Unknown' }}</div>
              <div class="text-xs text-gray-500">{{ device.ip }}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
              {{ device.device_type }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
              <div v-if="device.mac">{{ device.mac }}</div>
              <!-- We assume vendor is in display_name or separate, simplistic for now -->
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
               {{ formatTime(device.last_seen) }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
              <router-link :to="'/devices/' + device.id" class="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400">
                Details
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import axios from 'axios'

const devices = ref([])
const isScanning = ref(false)

const fetchDevices = async () => {
    try {
        const res = await axios.get('/api/v1/devices/')
        devices.value = res.data
    } catch (e) {
        console.error(e)
    }
}

const checkActiveScan = async () => {
    try {
        const res = await axios.get('/api/v1/scans/')
        // If any scan is queued or running, set isScanning to true
        isScanning.value = res.data.some(s => s.status === 'queued' || s.status === 'running')
    } catch (e) {
        console.error('Failed to check active scans', e)
    }
}

const triggerScan = async () => {
    isScanning.value = true
    try {
        const res = await axios.post('/api/v1/scans/discovery')
        if (res.data.status === 'already_active') {
             alert(res.data.message)
        } else {
             alert('Scan initiated Successfully!')
        }
    } catch (error) {
        console.error('Scan failed:', error)
        alert('Failed to initiate scan')
    } finally {
        await checkActiveScan()
    }
}

const isOnline = (d) => {
    if (!d.last_seen) return false
    const lastSeenDate = new Date(d.last_seen)
    const diff = new Date() - lastSeenDate
    return diff < 300000 // 5 mins
}

const formatTime = (t) => {
    if (!t) return 'Never'
    try {
        return new Date(t).toLocaleString()
    } catch { return t }
}

let pollInterval = null

onMounted(() => {
    fetchDevices()
    checkActiveScan()
    // Poll for active scan status every 10 seconds
    pollInterval = setInterval(() => {
        checkActiveScan()
        fetchDevices() // Also update device list during scan
    }, 10000)
})

onUnmounted(() => {
    if (pollInterval) clearInterval(pollInterval)
})
</script>
