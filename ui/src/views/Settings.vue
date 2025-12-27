<template>
  <div class="space-y-6">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">Settings</h1>

    <!-- Last Scan Summary (Gist) -->
    <div v-if="gist.has_scan" class="bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-xl p-4 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <div class="p-2 bg-blue-100 dark:bg-blue-800 rounded-full">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div>
          <h3 class="text-sm font-semibold text-blue-900 dark:text-blue-300">Last Scan Summary</h3>
          <p class="text-xs text-blue-700 dark:text-blue-400">
            Completed {{ formatDate(gist.finished_at) }} • {{ gist.device_count }} devices found • {{ Math.round(gist.duration_seconds) }}s duration
          </p>
        </div>
      </div>
      <div class="hidden sm:block text-xs font-mono text-blue-600 dark:text-blue-500">
        Target: {{ gist.target }}
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Configuration -->
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-100 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Scanning Configuration</h2>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-500 dark:text-gray-400 mb-2">Target IP Ranges / Subnets</label>
              
              <div class="border border-gray-100 dark:border-slate-700 rounded-lg overflow-hidden">
                <table class="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
                  <thead class="bg-gray-50 dark:bg-slate-700/50">
                    <tr>
                      <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Subnet / IP Range</th>
                      <th class="px-4 py-2 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider w-20">Actions</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-slate-700">
                    <tr v-for="(subnet, index) in subnets" :key="index">
                      <td class="px-4 py-2">
                        <input v-model="subnets[index]" type="text" class="block w-full text-sm border-none bg-transparent focus:ring-0 dark:text-white p-0" placeholder="e.g. 192.168.1.0/24" />
                      </td>
                      <td class="px-4 py-2 text-right">
                        <button @click="removeSubnet(index)" class="text-red-500 hover:text-red-700 p-1">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                    <tr v-if="subnets.length === 0">
                      <td colspan="2" class="px-4 py-4 text-center text-sm text-gray-400 italic">No subnets configured</td>
                    </tr>
                  </tbody>
                </table>
                <div class="p-2 bg-gray-50 dark:bg-slate-700/30 border-t border-gray-100 dark:border-slate-700">
                  <button @click="addSubnet" class="flex items-center text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 font-medium">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                    </svg>
                    Add Row
                  </button>
                </div>
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-500 dark:text-gray-400">Scan Interval (seconds)</label>
              <input v-model="form.scan_interval" type="number" class="mt-1 block w-full rounded-md border-gray-300 dark:border-slate-600 dark:bg-slate-700 shadow-sm p-2" />
            </div>

            <div class="pt-4 flex justify-end">
              <button @click="saveSettings" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                Save Configuration
              </button>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-100 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4 text-red-600 dark:text-red-400">Danger Zone</h2>
          <div class="p-4 border border-red-100 dark:border-red-900/30 bg-red-50 dark:bg-red-900/10 rounded-lg">
            <p class="text-sm text-red-800 dark:text-red-300 mb-4">Resetting the database will delete all history and configuration.</p>
            <button @click="resetDatabase" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition">
              Reset Application Data
            </button>
          </div>
        </div>
      </div>

      <!-- MQTT & Other -->
      <div class="space-y-6">
        <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm p-6 border border-gray-100 dark:border-slate-700">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">MQTT Settings</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-500 dark:text-gray-400">Broker Host</label>
              <input v-model="form.mqtt_broker" type="text" class="mt-1 block w-full rounded-md border-gray-300 dark:border-slate-600 dark:bg-slate-700 shadow-sm p-2" />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-500 dark:text-gray-400">Port</label>
              <input v-model="form.mqtt_port" type="number" class="mt-1 block w-full rounded-md border-gray-300 dark:border-slate-600 dark:bg-slate-700 shadow-sm p-2" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'

const form = reactive({
    scan_interval: '300',
    mqtt_broker: 'localhost',
    mqtt_port: '1883'
})

const subnets = ref([])
const gist = ref({ has_scan: false })

const fetchGist = async () => {
    try {
        const res = await axios.get('/api/v1/scans/gist')
        gist.value = res.data
    } catch (e) {
        console.error(e)
    }
}

const fetchSettings = async () => {
    try {
        const res = await axios.get('/api/v1/config/')
        const data = res.data
        data.forEach(item => {
            if (item.key === 'scan_subnets') {
                try {
                    subnets.value = JSON.parse(item.value)
                } catch (e) {
                    subnets.value = item.value ? [item.value] : []
                }
            } else if (item.key === 'scan_target' && subnets.value.length === 0) {
              // Legacy support
              if (item.value) subnets.value = [item.value]
            } else if (item.key in form) {
                form[item.key] = item.value
            }
        })
    } catch (e) {
        console.error(e)
    }
}

const addSubnet = () => {
    subnets.value.push('')
}

const removeSubnet = (index) => {
    subnets.value.splice(index, 1)
}

const saveSettings = async () => {
    try {
        const payload = {
            ...form,
            scan_subnets: JSON.stringify(subnets.value.filter(s => s.trim() !== '')),
            scan_target: subnets.value.join(' ') // fallback for existing logic
        }
        await axios.post('/api/v1/config/', payload)
        alert('Settings saved. Some changes may require a restart.')
    } catch (e) {
        alert('Error saving settings')
    }
}

const resetDatabase = async () => {
  if (confirm('Are you sure? This will wipe ALL data.')) {
    // This is a placeholder for actual reset logic if implemented
    alert('Reset logic not fully implemented in this demo.')
  }
}

const formatDate = (dateStr) => {
    if (!dateStr) return ''
    const d = new Date(dateStr)
    return d.toLocaleString()
}

onMounted(() => {
    fetchSettings()
    fetchGist()
})
</script>

