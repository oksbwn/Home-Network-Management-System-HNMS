<template>
  <div v-if="device" class="space-y-6">
    <!-- Header -->
    <div class="flex items-center gap-4">
      <router-link to="/devices"
        class="p-2 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-colors text-slate-600 dark:text-slate-400">
        <svg viewBox="0 0 24 24" class="w-5 h-5" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
      </router-link>
      <div class="flex-1">
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">{{ form.display_name || 'Device Details' }}</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">{{ device.ip }}</p>
      </div>
      <div class="flex items-center gap-2">
        <span class="inline-flex px-3 py-1 text-xs font-medium rounded"
          :class="device.status === 'online' ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400' : 'bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400'">
          {{ device.status }}
        </span>
        <button @click="saveChanges"
          class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium transition-colors">
          Save Changes
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Info Card -->
      <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Device Information</h2>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Display Name</label>
            <input v-model="form.display_name" type="text"
              class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Hostname</label>
            <input v-model="form.name" type="text"
              class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none" />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Device Type</label>
            <select v-model="form.device_type"
              class="w-full px-3 py-2 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none">
              <option value="unknown">Unknown</option>
              <option value="Router/Gateway">Router/Gateway</option>
              <option value="Desktop">Desktop</option>
              <option value="Laptop">Laptop</option>
              <option value="Mobile">Mobile</option>
              <option value="IoT">IoT</option>
              <option value="Printer">Printer</option>
            </select>
          </div>
          <div class="grid grid-cols-2 gap-4 pt-4 border-t border-slate-200 dark:border-slate-700">
            <div>
              <div class="text-xs text-slate-500 dark:text-slate-400 mb-1">IP Address</div>
              <div class="text-sm font-mono text-slate-900 dark:text-white">{{ device.ip }}</div>
            </div>
            <div>
              <div class="text-xs text-slate-500 dark:text-slate-400 mb-1">MAC Address</div>
              <div class="text-sm font-mono text-slate-900 dark:text-white">{{ device.mac || 'N/A' }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Ports Card -->
      <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 p-6">
        <h2 class="text-lg font-semibold text-slate-900 dark:text-white mb-4">Open Ports</h2>
        <div v-if="parsedPorts.length > 0" class="space-y-2">
          <div v-for="port in parsedPorts" :key="port.port"
            class="flex items-center justify-between p-3 bg-slate-50 dark:bg-slate-900/50 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors">
            <div class="flex items-center gap-3">
              <div
                class="h-8 w-8 rounded-lg bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 font-mono text-xs font-semibold flex items-center justify-center">
                {{ port.port }}
              </div>
              <div>
                <div class="text-sm font-medium text-slate-900 dark:text-white">{{ port.service || 'Unknown' }}</div>
                <div class="text-xs text-slate-500">{{ port.protocol || 'TCP' }}</div>
              </div>
            </div>
            <button v-if="port.port === 22" @click="openSSH(port.port)"
              class="px-3 py-1 bg-slate-900 dark:bg-white text-white dark:text-slate-900 text-xs font-medium rounded hover:opacity-90 transition-opacity">
              SSH
            </button>
            <a v-if="[80, 443, 3000, 8080, 8000].includes(port.port)" :href="`http://${device.ip}:${port.port}`"
              target="_blank"
              class="px-3 py-1 bg-emerald-600 text-white text-xs font-medium rounded hover:bg-emerald-700 transition-colors">
              Open
            </a>
          </div>
        </div>
        <div v-else class="text-center py-12">
          <div class="text-sm text-slate-500">No open ports detected</div>
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

const form = reactive({ display_name: '', name: '', device_type: '' })

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
    alert('Changes saved')
    fetchDevice()
  } catch (e) {
    alert('Failed to save')
  }
}

onMounted(() => {
  fetchDevice()
})
</script>
