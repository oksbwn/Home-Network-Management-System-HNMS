<template>
  <div class="space-y-8">
    <div class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Settings</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1 text-sm font-medium">Global configuration and system
          parameters</p>
      </div>
    </div>

    <!-- Last Scan Summary (Gist) -->
    <div v-if="gist.has_scan"
      class="bg-blue-50/50 dark:bg-blue-500/5 border border-blue-100 dark:border-blue-500/20 rounded-[2rem] p-8 flex flex-col md:flex-row items-center justify-between gap-6">
      <div class="flex items-center space-x-6">
        <div class="p-4 bg-white dark:bg-slate-800 rounded-2xl shadow-lg text-blue-500">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
        </div>
        <div>
          <h3 class="text-xs font-black text-blue-500 uppercase tracking-[0.2em] mb-1">Telemetry Snapshot</h3>
          <p class="text-lg font-black text-slate-900 dark:text-white leading-tight">
            {{ gist.device_count }} devices confirmed <span class="text-slate-400 font-medium lowercase">on {{
              gist.target }}</span>
          </p>
          <p class="text-[10px] text-slate-500 dark:text-slate-400 mt-1 font-bold uppercase tracking-widest">
            Cycle duration: {{ Math.round(gist.duration_seconds) }}s • {{ formatDateRelative(gist.finished_at) }}
          </p>
        </div>
      </div>
      <div
        class="px-6 py-3 bg-white dark:bg-slate-800 rounded-xl border border-blue-100 dark:border-slate-700 shadow-sm text-[10px] font-black font-mono text-blue-600 dark:text-blue-400 uppercase tracking-widest">
        {{ gist.target }}
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Main Configuration -->
      <div class="lg:col-span-2 space-y-8">
        <div
          class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 p-10">
          <div class="flex items-center space-x-3 mb-8">
            <div class="w-1.5 h-6 bg-blue-500 rounded-full"></div>
            <h2 class="text-lg font-black text-slate-900 dark:text-white uppercase tracking-tight">Discovery Matrix</h2>
          </div>

          <div class="space-y-8">
            <div>
              <label
                class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-4">Target
                Intelligence Zones (Subnets)</label>

              <div
                class="bg-slate-50 dark:bg-slate-900/50 rounded-3xl border border-slate-100 dark:border-slate-700 overflow-hidden shadow-inner">
                <table class="min-w-full divide-y divide-slate-100 dark:divide-slate-700">
                  <thead class="bg-slate-50 dark:bg-slate-900/50">
                    <tr>
                      <th class="px-6 py-4 text-left text-[9px] font-black text-slate-400 uppercase tracking-widest">
                        Descriptor</th>
                      <th
                        class="px-6 py-4 text-right text-[9px] font-black text-slate-400 uppercase tracking-widest w-24">
                        Relay</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
                    <tr v-for="(subnet, index) in subnets" :key="index" class="group">
                      <td class="px-6 py-4">
                        <input v-model="subnets[index]" type="text"
                          class="block w-full text-sm font-bold bg-transparent border-none focus:ring-0 text-slate-900 dark:text-white font-mono p-0"
                          placeholder="0.0.0.0/0" />
                      </td>
                      <td class="px-6 py-4 text-right">
                        <button @click="removeSubnet(index)"
                          class="p-2 text-rose-400 hover:text-rose-600 dark:hover:text-rose-300 transition-colors bg-white dark:bg-slate-800 rounded-xl shadow-sm opacity-0 group-hover:opacity-100">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24"
                            stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5"
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </td>
                    </tr>
                    <tr v-if="subnets.length === 0">
                      <td colspan="2"
                        class="px-6 py-10 text-center text-xs font-bold text-slate-400 uppercase tracking-widest italic">
                        Signal void: No subnets active</td>
                    </tr>
                  </tbody>
                </table>
                <div class="px-6 py-4 border-t border-slate-100 dark:border-slate-700 bg-white/50 dark:bg-slate-800/50">
                  <button @click="addSubnet"
                    class="flex items-center text-[10px] font-black text-blue-500 uppercase tracking-widest hover:text-blue-600 transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4" />
                    </svg>
                    Add Target Zone
                  </button>
                </div>
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <label
                  class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Sync
                  frequency (Seconds)</label>
                <input v-model="form.scan_interval" type="number"
                  class="w-full px-6 py-4 bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-700 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none text-slate-900 dark:text-white font-mono font-bold shadow-inner" />
              </div>
            </div>

            <div class="pt-4 flex justify-end">
              <button @click="saveSettings"
                class="px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl text-[10px] font-black shadow-xl shadow-slate-200 dark:shadow-none hover:scale-105 active:scale-95 transition-all uppercase tracking-widest">
                Sync Core Config
              </button>
            </div>
          </div>
        </div>

        <div
          class="bg-rose-50/50 dark:bg-rose-500/5 rounded-[2.5rem] border border-rose-100 dark:border-rose-500/20 p-10 overflow-hidden relative group">
          <div class="absolute top-0 right-0 p-8 text-rose-500 opacity-5 group-hover:opacity-10 transition-opacity">
            <svg viewBox="0 0 24 24" class="w-32 h-32" fill="currentColor">
              <path
                d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z" />
            </svg>
          </div>
          <div class="relative">
            <h2 class="text-lg font-black text-rose-600 uppercase tracking-tight mb-2">Danger Protocol</h2>
            <p class="text-xs font-bold text-rose-400 dark:text-rose-300/60 uppercase tracking-widest max-w-sm">Wiping
              application state will terminate all discovery history and user definitions permanently.</p>

            <div class="mt-8">
              <button @click="resetDatabase"
                class="px-8 py-4 bg-rose-500 text-white rounded-2xl text-[10px] font-black shadow-lg shadow-rose-200 dark:shadow-none hover:bg-rose-600 transition-all uppercase tracking-widest">
                Terminate Global State
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- MQTT & Other -->
      <div class="space-y-8">
        <div
          class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 p-8">
          <div class="flex items-center space-x-3 mb-8">
            <div class="w-1.5 h-6 bg-emerald-500 rounded-full"></div>
            <h2 class="text-lg font-black text-slate-900 dark:text-white uppercase tracking-tight">Messaging Bus</h2>
          </div>
          <p class="text-[10px] text-slate-400 font-bold uppercase tracking-widest mb-6">Real-time status broadcast
            configuration</p>

          <div class="space-y-6">
            <div>
              <label class="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Relay
                Host</label>
              <input v-model="form.mqtt_broker" type="text"
                class="w-full px-5 py-3.5 bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-700 rounded-xl focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none text-slate-900 dark:text-white font-mono font-bold transition-all" />
            </div>
            <div>
              <label class="block text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Port
                Access</label>
              <input v-model="form.mqtt_port" type="number"
                class="w-full px-5 py-3.5 bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-700 rounded-xl focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none text-slate-900 dark:text-white font-mono font-bold transition-all" />
            </div>
          </div>

          <div class="mt-8 pt-8 border-t border-slate-50 dark:border-slate-700">
            <div class="flex items-center space-x-3 text-emerald-500">
              <div class="w-2 h-2 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]">
              </div>
              <span class="text-[9px] font-black uppercase tracking-widest">Protocol Active</span>
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

const formatDateRelative = (t) => {
  if (!t) return ''
  const diff = new Date() - new Date(t)
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'Just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

onMounted(() => {
  fetchSettings()
  fetchGist()
})
</script>
