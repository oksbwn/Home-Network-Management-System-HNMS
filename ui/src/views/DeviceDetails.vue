<template>
  <div v-if="device" class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
    <!-- Header -->
    <div class="flex justify-between items-end">
      <div class="flex items-center space-x-6">
        <router-link to="/devices"
          class="p-3 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 text-slate-400 hover:text-slate-900 dark:hover:text-white transition-all hover:scale-110 active:scale-90">
          <svg viewBox="0 0 24 24" class="w-6 h-6" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M19 12H5M12 19l-7-7 7-7" />
          </svg>
        </router-link>
        <div>
          <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight uppercase">Asset Analysis</h1>
          <p class="text-slate-500 dark:text-slate-400 mt-1 text-sm font-medium tracking-wide">ID: {{ device.id.slice(0,
            18) }}...</p>
        </div>
      </div>

      <div class="flex items-center space-x-3">
        <div
          class="px-4 py-2 bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 flex items-center space-x-2">
          <div class="w-2 h-2 rounded-full"
            :class="device.status === 'online' ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'"></div>
          <span class="text-[10px] font-black uppercase tracking-widest"
            :class="device.status === 'online' ? 'text-emerald-500' : 'text-rose-500'">{{ device.status }}</span>
        </div>
        <button @click="saveChanges"
          class="px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-2xl text-[10px] font-black shadow-xl shadow-slate-200 dark:shadow-none hover:scale-105 active:scale-95 transition-all uppercase tracking-widest">
          Sync Telemetry
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <!-- Info Card -->
      <div
        class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 p-10">
        <div class="flex items-center space-x-3 mb-10">
          <div class="w-1.5 h-6 bg-blue-500 rounded-full"></div>
          <h2 class="text-lg font-black text-slate-900 dark:text-white uppercase tracking-tight">Core attributes</h2>
        </div>

        <div class="space-y-8">
          <div>
            <label
              class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Friendly
              identity</label>
            <input v-model="form.display_name" type="text"
              class="w-full px-6 py-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none text-slate-900 dark:text-white font-bold transition-all shadow-inner" />
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <label
                class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Network
                Node Name</label>
              <input v-model="form.name" type="text"
                class="w-full px-6 py-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none text-slate-900 dark:text-white font-mono font-bold transition-all shadow-inner" />
            </div>

            <div>
              <label
                class="block text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.3em] mb-3">Target
                link class</label>
              <select v-model="form.device_type"
                class="w-full px-6 py-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none text-slate-900 dark:text-white font-bold appearance-none cursor-pointer shadow-inner">
                <option value="unknown">Unknown</option>
                <option value="Router/Gateway">Router/Gateway</option>
                <option value="Desktop">Desktop</option>
                <option value="Laptop">Laptop</option>
                <option value="Mobile">Mobile</option>
                <option value="IoT">IoT</option>
                <option value="Printer">Printer</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-8 pt-6 border-t border-slate-50 dark:border-slate-700">
            <div>
              <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Protocol Access
                (IP)</label>
              <div class="text-lg font-black font-mono text-slate-900 dark:text-white tracking-widest">{{ device.ip }}
              </div>
            </div>
            <div>
              <label class="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Hardware Ident
                (MAC)</label>
              <div class="text-lg font-black font-mono text-slate-900 dark:text-white tracking-widest">{{ device.mac ||
                'UNDEFINED' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Ports Card -->
      <div
        class="bg-slate-900 dark:bg-slate-800 rounded-[2.5rem] shadow-xl border border-slate-800 dark:border-slate-700 p-10 text-white relative overflow-hidden">
        <div class="absolute inset-0 bg-blue-500/5 pointer-events-none"></div>
        <div class="relative">
          <div class="flex items-center justify-between mb-10">
            <div class="flex items-center space-x-3">
              <div class="w-1.5 h-6 bg-emerald-500 rounded-full"></div>
              <h2 class="text-lg font-black uppercase tracking-tight">Signal Analysis</h2>
            </div>
            <div class="flex items-center space-x-2 text-[10px] font-black text-emerald-500 uppercase tracking-widest">
              <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-ping"></span>
              <span>Broadcasting</span>
            </div>
          </div>

          <div v-if="parsedPorts.length > 0" class="space-y-4">
            <div v-for="port in parsedPorts" :key="port.port"
              class="group flex items-center justify-between p-5 bg-white/5 hover:bg-white/10 rounded-[1.5rem] border border-white/5 transition-all">
              <div class="flex items-center space-x-5">
                <div
                  class="h-12 w-12 rounded-2xl flex items-center justify-center bg-blue-500/20 text-blue-400 font-mono text-sm font-black border border-blue-500/30 group-hover:bg-blue-500 group-hover:text-white transition-all shadow-lg">
                  {{ port.port }}
                </div>
                <div>
                  <div class="text-xs font-black uppercase tracking-widest text-slate-200">{{ port.service || 'Unknown
                    Signal' }}</div>
                  <div class="text-[10px] text-slate-500 font-mono mt-0.5 uppercase tracking-tighter">{{ port.protocol
                    || 'TCP' }} MATRIX ACTIVE</div>
                </div>
              </div>
              <div class="flex space-x-3 opacity-40 group-hover:opacity-100 transition-opacity">
                <button v-if="port.port === 22" @click="openSSH(port.port)"
                  class="px-5 py-2.5 bg-white text-slate-900 text-[10px] font-black rounded-xl hover:scale-105 active:scale-95 transition-all uppercase tracking-widest">
                  Bridge
                </button>
                <a v-if="[80, 443, 3000, 8080, 8000].includes(port.port)" :href="`http://${device.ip}:${port.port}`"
                  target="_blank"
                  class="px-5 py-2.5 bg-emerald-500 text-white text-[10px] font-black rounded-xl hover:bg-emerald-600 transition-all uppercase tracking-widest">
                  Pulse
                </a>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-20">
            <div class="inline-flex p-6 bg-white/5 rounded-full mb-6">
              <svg viewBox="0 0 24 24" class="w-10 h-10 text-slate-700" fill="none" stroke="currentColor"
                stroke-width="2">
                <path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10" />
              </svg>
            </div>
            <p class="text-[10px] font-black text-slate-500 uppercase tracking-[0.3em] italic">No active signals
              detected on this node</p>
          </div>
        </div>
      </div>
    </div>

    <TerminalModal v-if="showTerminal" :device="device" :port="sshPort" @close="showTerminal = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import TerminalModal from '../components/TerminalModal.vue'

const route = useRoute()
const device = ref(null)
const showTerminal = ref(false)
const sshPort = ref(22)

const form = reactive({
  display_name: '',
  name: '',
  device_type: ''
})

const parsedPorts = computed(() => {
  if (!device.value || !device.value.open_ports) return []
  try {
    const parsed = JSON.parse(device.value.open_ports)
    if (Array.isArray(parsed) && parsed.length > 0) {
      if (typeof parsed[0] === 'number') {
        return parsed.map(p => ({ port: p, service: 'Unknown', protocol: 'TCP' }))
      }
      return parsed
    }
    return []
  } catch {
    return []
  }
})

const openSSH = (port) => {
  sshPort.value = port
  showTerminal.value = true
}

const fetchDevice = async () => {
  try {
    const res = await axios.get(`/api/v1/devices/${route.params.id}`)
    device.value = res.data
    form.display_name = device.value.display_name
    form.name = device.value.name
    form.device_type = device.value.device_type || 'unknown'
  } catch (e) {
    console.error(e)
  }
}

const saveChanges = async () => {
  try {
    await axios.put(`/api/v1/devices/${device.value.id}`, form)
    alert('Saved!')
    fetchDevice() // reload
  } catch (e) {
    alert('Failed to save')
  }
}

onMounted(() => {
  fetchDevice()
})
</script>
