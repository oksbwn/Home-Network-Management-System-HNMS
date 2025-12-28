<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Settings</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Configure network scanner and automated tasks</p>
      </div>
      <div v-if="saveStatus === 'saving'"
        class="flex items-center text-blue-600 dark:text-blue-400 text-sm font-medium animate-pulse">
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
          </path>
        </svg>
        Saving...
      </div>
      <div v-else-if="saveStatus === 'saved'"
        class="text-emerald-600 dark:text-emerald-400 text-sm font-medium flex items-center">
        <svg class="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd"
            d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
            clip-rule="evenodd" />
        </svg>
        Saved
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Settings -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Automated Discovery -->
        <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="p-2 bg-blue-50 dark:bg-blue-900/20 rounded-lg text-blue-600 dark:text-blue-400">
              <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Automated Discovery</h2>
              <p class="text-xs text-slate-500">Configure background network scanning</p>
            </div>
          </div>

          <div class="space-y-5">
            <div>
              <label
                class="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Target
                Subnets</label>
              <div class="flex gap-2 mb-2">
                <input v-model="newSubnet" @keyup.enter="addSubnet" type="text" placeholder="e.g. 192.168.1.0/24"
                  class="flex-1 px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm" />
                <button @click="addSubnet"
                  class="px-3 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-lg text-sm font-medium hover:opacity-90 transition-opacity">Add</button>
              </div>
              <div class="flex flex-wrap gap-2">
                <div v-for="s in subnetList" :key="s"
                  class="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-700 rounded-full text-sm text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600">
                  <span>{{ s }}</span>
                  <button @click="removeSubnet(s)" class="text-slate-400 hover:text-red-500 transition-colors">
                    <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div v-if="subnetList.length === 0" class="text-sm text-slate-400 italic py-2">No subnets configured for
                  auto-discovery</div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label
                  class="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Scan
                  Interval</label>
                <div class="relative">
                  <select v-model="settings.scan_interval"
                    class="w-full pl-3 pr-10 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-sm appearance-none">
                    <option value="300">Every 5 minutes</option>
                    <option value="600">Every 10 minutes</option>
                    <option value="1800">Every 30 minutes</option>
                    <option value="3600">Every hour</option>
                    <option value="86400">Once per day</option>
                  </select>
                  <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400">
                    <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </div>
              </div>
              <div>
                <label
                  class="block text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Last
                  Run</label>
                <div
                  class="px-3 py-2 bg-slate-50 dark:bg-slate-900/50 rounded-lg border border-slate-200 dark:border-slate-700 text-sm text-slate-600 dark:text-slate-400">
                  {{ formatLastRun(settings.last_discovery_run_at) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Global UI Appearance -->
        <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
          <div class="flex items-center gap-3 mb-6">
            <div class="p-2 bg-emerald-50 dark:bg-emerald-900/20 rounded-lg text-emerald-600 dark:text-emerald-400">
              <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
                <path
                  d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
              </svg>
            </div>
            <div>
              <h2 class="text-lg font-semibold text-slate-900 dark:text-white">UI Appearance</h2>
              <p class="text-xs text-slate-500">Configure dashboard and visibility options</p>
            </div>
          </div>
          <div class="space-y-4">
            <label
              class="flex items-center gap-3 cursor-pointer p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors border border-transparent hover:border-slate-200 dark:hover:border-slate-600">
              <div class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                :class="settings.hide_offline === 'true' ? 'bg-blue-600' : 'bg-slate-300 dark:bg-slate-600'">
                <input type="checkbox" v-model="settings.hide_offline" true-value="true" false-value="false"
                  class="hidden" />
                <span class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform"
                  :class="settings.hide_offline === 'true' ? 'translate-x-6' : 'translate-x-1'"></span>
              </div>
              <div>
                <div class="text-sm font-medium text-slate-900 dark:text-white">Hide Offline Devices</div>
                <div class="text-xs text-slate-500">Only show active network nodes on dashboard</div>
              </div>
            </label>
          </div>
        </div>
      </div>

      <!-- Sidebar: Summary & Danger -->
      <div class="space-y-6">
        <!-- Scan Summary -->
        <div v-if="gist"
          class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
          <h3 class="text-sm font-semibold text-slate-900 dark:text-white mb-4">Discovery Metrics</h3>
          <div class="space-y-4">
            <div class="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-700">
              <span class="text-xs text-slate-500">Total Scans Run</span>
              <span class="text-sm font-semibold text-slate-900 dark:text-white">{{ gist.total_scans }}</span>
            </div>
            <div class="flex justify-between items-center py-2 border-b border-slate-100 dark:border-slate-700">
              <span class="text-xs text-slate-500">Discovery Jobs</span>
              <span class="text-sm font-semibold text-emerald-600">{{ gist.scans_done }}</span>
            </div>
            <div class="flex justify-between items-center py-2">
              <span class="text-xs text-slate-500">Currently Active</span>
              <span class="flex items-center gap-2">
                <span v-if="gist.scans_running > 0" class="flex h-2 w-2 rounded-full bg-blue-500 animate-pulse"></span>
                <span class="text-sm font-semibold text-blue-600">{{ gist.scans_running }}</span>
              </span>
            </div>
          </div>
        </div>

        <!-- Danger Zone -->
        <div class="bg-white dark:bg-slate-800 rounded-lg border border-red-200 dark:border-red-900/20 p-6">
          <h3 class="text-sm font-semibold text-red-600 dark:text-red-400 mb-2">System Maintenance</h3>
          <p class="text-xs text-slate-500 mb-4">Cleanup tools and data management</p>
          <div class="space-y-3">
            <button @click="clearAllData"
              class="w-full px-4 py-2 border border-red-200 dark:border-red-900/30 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg text-xs font-semibold transition-colors flex items-center justify-center gap-2">
              <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2">
                <path
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Factory Reset Data
            </button>
            <p class="text-[10px] text-slate-400 text-center px-2">This will permanently delete all discovered devices
              and history.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Final Save -->
    <div class="fixed bottom-6 right-6 lg:static flex justify-end">
      <button @click="saveSettings" :disabled="saveStatus === 'saving'"
        class="px-8 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg text-sm font-bold shadow-lg shadow-blue-500/20 transition-all flex items-center gap-2">
        Save Configuration
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import axios from 'axios'

const settings = reactive({
  scan_subnets: '[]',
  scan_interval: '300',
  last_discovery_run_at: '',
  hide_offline: 'false'
})

const subnetList = ref([])
const newSubnet = ref('')
const gist = ref(null)
const saveStatus = ref('idle')

const addSubnet = () => {
  const s = newSubnet.value.trim()
  if (!s) return
  if (!subnetList.value.includes(s)) {
    subnetList.value.push(s)
    settings.scan_subnets = JSON.stringify(subnetList.value)
  }
  newSubnet.value = ''
}

const removeSubnet = (s) => {
  subnetList.value = subnetList.value.filter(item => item !== s)
  settings.scan_subnets = JSON.stringify(subnetList.value)
}

const fetchSettings = async () => {
  try {
    const res = await axios.get('/api/v1/config/')
    const mapping = {}
    res.data.forEach(item => {
      mapping[item.key] = item.value
    })

    // Apply mapping
    if (mapping.scan_subnets) {
      settings.scan_subnets = mapping.scan_subnets
      try {
        subnetList.value = JSON.parse(mapping.scan_subnets)
      } catch { subnetList.value = [] }
    }
    if (mapping.scan_interval) settings.scan_interval = mapping.scan_interval
    if (mapping.last_discovery_run_at) settings.last_discovery_run_at = mapping.last_discovery_run_at
    if (mapping.hide_offline) settings.hide_offline = mapping.hide_offline
  } catch (e) {
    console.error("Failed to fetch config:", e)
  }
}

const fetchGist = async () => {
  try {
    const res = await axios.get('/api/v1/scans/gist')
    gist.value = res.data
  } catch (e) {
    console.error(e)
  }
}

const saveSettings = async () => {
  saveStatus.value = 'saving'
  try {
    await axios.post('/api/v1/config/', settings)
    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)
  } catch (e) {
    alert('Failed to save settings')
    saveStatus.value = 'idle'
  }
}

const clearAllData = async () => {
  if (!confirm('This will delete all devices and scan history. Continue?')) return
  try {
    await axios.delete('/api/v1/devices/')
    await axios.delete('/api/v1/scans/')
    alert('All data cleared')
    window.location.reload()
  } catch (e) {
    alert('Failed to clear data')
  }
}

const formatLastRun = (dateStr) => {
  if (!dateStr) return 'Never'
  try {
    const date = new Date(dateStr)
    return date.toLocaleString()
  } catch { return 'Never' }
}

onMounted(() => {
  fetchSettings()
  fetchGist()
})
</script>
