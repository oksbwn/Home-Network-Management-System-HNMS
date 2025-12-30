<template>
  <div v-if="device" class="space-y-6 max-w-7xl mx-auto pb-12">
    <!-- Header Area -->
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div class="flex items-center gap-4">
        <router-link to="/devices"
          class="p-2.5 bg-white/70 dark:bg-slate-800/70 backdrop-blur-md border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-white dark:hover:bg-slate-700 transition-all text-slate-600 dark:text-slate-400 shadow-sm"
          v-tooltip="'Back to Device List'">
          <ArrowLeft class="w-5 h-5" />
        </router-link>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-2xl font-bold text-slate-900 dark:text-white leading-tight">
              {{ form.display_name || device.name || 'Unnamed Device' }}
            </h1>
            <div :class="[
              device.status === 'online' ? 'bg-emerald-500' : 'bg-slate-400',
              'w-2 h-2 rounded-full animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]'
            ]"></div>
          </div>
          <p class="text-sm font-mono text-slate-500 dark:text-slate-400 mt-1.5 flex items-center gap-2">
            <span class="bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded text-[10px] font-bold">IP</span>
            {{ device.ip }}
          </p>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <button @click="runDeepScan" :disabled="isScanning"
          class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-slate-500 dark:text-slate-400"
          v-tooltip="'Deep Port Audit (Scan top 1000 ports)'">
          <component :is="isScanning ? Loader2 : Scan" class="w-5 h-5" :class="{ 'animate-spin': isScanning }" />
        </button>
        <button @click="saveChanges"
          class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-slate-500 hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          v-tooltip="'Save Device Configuration'">
          <Save class="w-5 h-5" />
        </button>
      </div>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

      <!-- Column 1 & 2: Main Info -->
      <div class="lg:col-span-2 space-y-6">

        <!-- Device Info Card -->
        <div
          class="relative bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 p-8 shadow-2xl overflow-hidden group">
          <div
            class="absolute top-0 right-0 p-8 opacity-5 dark:opacity-10 group-hover:opacity-10 dark:group-hover:opacity-20 transition-opacity">
            <component :is="getIconComponent(form.icon || device.icon)" class="w-32 h-32" />
          </div>

          <h2 class="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
            <div class="w-1.5 h-6 bg-blue-500 rounded-full"></div>
            Device Identification
          </h2>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-6">
            <div class="space-y-1">
              <label
                class="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 ml-1">Display
                Name</label>
              <input v-model="form.display_name" type="text" placeholder="Friendly Name"
                class="w-full px-4 py-3 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-2xl text-slate-900 dark:text-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all font-medium" />
            </div>

            <div class="space-y-1">
              <label
                class="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 ml-1">Device
                Category</label>
              <div class="relative w-full group" v-click-outside="() => isCategoryOpen = false">
                <button @click="isCategoryOpen = !isCategoryOpen"
                  class="w-full flex items-center justify-between px-4 py-3 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none hover:ring-4 hover:ring-blue-500/10 focus:border-blue-500 transition-all text-sm font-medium text-slate-900 dark:text-white group-hover:bg-white dark:group-hover:bg-slate-800">
                  <div class="flex items-center gap-2.5">
                    <span class="truncate">{{ form.device_type || 'Select Category' }}</span>
                  </div>
                  <ChevronDown class="h-4 w-4 text-slate-400 transition-transform duration-200"
                    :class="{ 'rotate-180': isCategoryOpen }" />
                </button>

                <transition enter-active-class="transition duration-100 ease-out"
                  enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
                  leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100"
                  leave-to-class="transform scale-95 opacity-0">
                  <div v-if="isCategoryOpen"
                    class="absolute z-[60] mt-2 w-full bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-2xl shadow-2xl py-1.5 overflow-hidden">
                    <div class="px-3 py-2 border-b border-slate-100 dark:border-slate-700/50">
                      <div
                        class="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-900/50 rounded-lg border border-transparent focus-within:border-blue-500/30 transition-colors">
                        <Search class="w-3.5 h-3.5 text-slate-400" />
                        <input v-model="categorySearch" @click.stop type="text" placeholder="Search..."
                          class="bg-transparent border-none outline-none text-xs text-slate-700 dark:text-slate-200 w-full placeholder:text-slate-400"
                          autofocus />
                      </div>
                    </div>
                    <div class="overflow-y-auto max-h-60 custom-scrollbar">
                      <button v-for="type in filteredDeviceTypes" :key="type"
                        @click="form.device_type = type; isCategoryOpen = false; categorySearch = ''"
                        class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-left hover:bg-blue-600 hover:text-white transition-colors"
                        :class="form.device_type === type ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-slate-600 dark:text-slate-300'">
                        {{ type }}
                      </button>
                      <div v-if="filteredDeviceTypes.length === 0" class="px-4 py-3 text-xs text-slate-400 text-center">
                        No matches found
                      </div>
                    </div>
                  </div>
                </transition>
              </div>
            </div>

            <div class="space-y-1">
              <label
                class="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 ml-1">Icon
                Selection</label>
              <Popover class="relative">
                <PopoverButton
                  class="w-full flex items-center justify-between px-4 py-3 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-2xl text-slate-900 dark:text-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all hover:bg-white dark:hover:bg-slate-800 group">
                  <div class="flex items-center gap-3">
                    <component :is="getIconComponent(form.icon)" class="w-5 h-5 text-blue-500" />
                    <span class="text-sm font-medium">{{ form.icon || 'Select Icon' }}</span>
                  </div>
                  <LucideIcons.ChevronDown
                    class="w-4 h-4 text-slate-400 group-hover:text-slate-600 transition-colors" />
                </PopoverButton>

                <transition enter-active-class="transition duration-200 ease-out"
                  enter-from-class="translate-y-1 opacity-0" enter-to-class="translate-y-0 opacity-100"
                  leave-active-class="transition duration-150 ease-in" leave-from-class="translate-y-0 opacity-100"
                  leave-to-class="translate-y-1 opacity-0">
                  <PopoverPanel
                    class="absolute z-50 bottom-full mb-3 right-0 w-[260px] bg-white/95 dark:bg-slate-900/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-3xl shadow-2xl overflow-hidden flex flex-col">
                    <div class="p-3 border-b border-slate-100 dark:border-slate-700/50">
                      <div
                        class="flex items-center gap-2 px-3 py-1.5 bg-slate-100 dark:bg-slate-900/50 rounded-lg border border-transparent focus-within:border-blue-500/30 transition-colors">
                        <Search class="w-3.5 h-3.5 text-slate-400" />
                        <input v-model="iconSearch" type="text" placeholder="Find icon..."
                          class="bg-transparent border-none outline-none text-xs text-slate-700 dark:text-slate-200 w-full placeholder:text-slate-400" />
                      </div>
                    </div>
                    <div class="p-4 overflow-y-auto max-h-[220px] custom-scrollbar">
                      <div class="grid grid-cols-4 gap-2">
                        <button v-for="iconName in filteredIcons" :key="iconName" type="button"
                          @click="form.icon = iconName"
                          class="p-3 rounded-xl transition-all flex items-center justify-center"
                          :class="form.icon === iconName ? 'bg-blue-600 text-white shadow-lg' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800'"
                          v-tooltip="iconName">
                          <component :is="getIconComponent(iconName)" class="w-5 h-5" />
                        </button>
                      </div>
                      <div v-if="filteredIcons.length === 0" class="py-2 text-xs text-slate-400 text-center">
                        No icons found
                      </div>
                    </div>
                  </PopoverPanel>
                </transition>
              </Popover>
            </div>

            <div class="space-y-1">
              <label
                class="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500 ml-1">Network
                Hostname</label>
              <input v-model="form.name" type="text"
                class="w-full px-4 py-3 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-2xl text-slate-900 dark:text-white focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all font-mono text-sm" />
            </div>

            <div class="space-y-1">
              <label class="text-[10px] font-black uppercase tracking-widest text_slate-400 dark:text-slate-500 ml-1">IP
                Reservation</label>
              <div class="relative w-full group" v-click-outside="() => isIPOpen = false">
                <button @click="isIPOpen = !isIPOpen"
                  class="w-full flex items-center justify-between px-4 py-3 bg-white/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-700 rounded-2xl outline-none hover:ring-4 hover:ring-blue-500/10 focus:border-blue-500 transition-all text-sm font-medium text-slate-900 dark:text-white group-hover:bg-white dark:group-hover:bg-slate-800">
                  <span class="truncate">{{ getIPAllocationLabel(form.attributes.ip_allocation) }}</span>
                  <ChevronDown class="h-4 w-4 text-slate-400 transition-transform duration-200"
                    :class="{ 'rotate-180': isIPOpen }" />
                </button>

                <transition enter-active-class="transition duration-100 ease-out"
                  enter-from-class="transform scale-95 opacity-0" enter-to-class="transform scale-100 opacity-100"
                  leave-active-class="transition duration-75 ease-in" leave-from-class="transform scale-100 opacity-100"
                  leave-to-class="transform scale-95 opacity-0">
                  <div v-if="isIPOpen"
                    class="absolute z-[60] mt-2 w-full bg-white/95 dark:bg-slate-800/95 backdrop-blur-xl border border-slate-200 dark:border-slate-700 rounded-2xl shadow-2xl py-1.5 overflow-hidden">
                    <button @click="form.attributes.ip_allocation = undefined; isIPOpen = false"
                      class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-left hover:bg-blue-600 hover:text-white transition-colors"
                      :class="!form.attributes.ip_allocation ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-slate-600 dark:text-slate-300'">
                      Dynamic (DHCP)
                    </button>
                    <button @click="form.attributes.ip_allocation = 'static'; isIPOpen = false"
                      class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-left hover:bg-blue-600 hover:text-white transition-colors"
                      :class="form.attributes.ip_allocation === 'static' ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-slate-600 dark:text-slate-300'">
                      Static IP
                    </button>
                    <button @click="form.attributes.ip_allocation = 'dhcp'; isIPOpen = false"
                      class="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-left hover:bg-blue-600 hover:text-white transition-colors"
                      :class="form.attributes.ip_allocation === 'dhcp' ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-slate-600 dark:text-slate-300'">
                      DHCP Reserved
                    </button>
                  </div>
                </transition>
              </div>
            </div>
          </div>

          <div
            class="mt-8 pt-8 border-t border-slate-100 dark:border-slate-700/50 grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Manufacturer</div>
              <div class="text-sm font-bold text-slate-900 dark:text-white">{{ device.vendor || 'Unknown' }}</div>
            </div>
            <div>
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">MAC Signature</div>
              <div class="text-sm font-mono text-slate-600 dark:text-slate-400">{{ device.mac || 'N/A' }}</div>
            </div>
            <div>
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">First Seen</div>
              <div class="text-sm font-bold text-slate-900 dark:text-white">{{ formatTime(device.first_seen) }}</div>
            </div>
            <div>
              <div class="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Network Path</div>
              <div class="text-sm font-bold text-slate-900 dark:text-white">{{ device.internet_path || 'Local LAN' }}
              </div>
            </div>
          </div>
        </div>

        <!-- Availability Trend Chart -->
        <div
          class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 p-8 shadow-2xl relative overflow-hidden group">
          <div class="flex items-center justify-between mb-8">
            <h2 class="text-lg font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <div class="w-1.5 h-6 bg-blue-500 rounded-full"></div>
              Network Availability History
            </h2>
            <div
              class="px-3 py-1 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-full text-[10px] font-black tracking-widest uppercase">
              Full Record
            </div>
          </div>

          <div class="h-64">
            <apexchart v-if="chartSeries && chartSeries[0].data.length > 0" type="area" height="100%"
              :options="chartOptions" :series="chartSeries"></apexchart>
            <div v-else class="h-full flex flex-col items-center justify-center text-slate-400 italic text-sm gap-2">
              <Loader2 class="w-5 h-5 animate-spin opacity-20" />
              <span>Collecting historical trend data...</span>
            </div>
          </div>

          <!-- Detailed Activity Log Table -->
          <div class="mt-8 pt-8 border-t border-slate-100 dark:border-slate-700/50">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-[10px] font-black uppercase tracking-[0.2em] text-slate-400 ml-1">Recent Activity Log</h3>
              <span class="text-[10px] font-bold text-slate-400">{{ history.length }} Events Recorded</span>
            </div>

            <div class="grid grid-cols-1 gap-2 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
              <div v-for="h in history" :key="h.id"
                class="flex items-center justify-between p-2 rounded-lg bg-white/50 dark:bg-slate-900/30 border border-slate-100 dark:border-slate-800/50 hover:border-blue-500/30 hover:shadow-sm hover:shadow-blue-500/5 transition-all group/item">
                <div class="flex items-center gap-2.5">
                  <div :class="h.status === 'online' ? 'bg-emerald-500 text-white' : 'bg-rose-500 text-white'"
                    class="w-7 h-7 rounded-md flex items-center justify-center shadow-sm shadow-black/5">
                    <component :is="h.status === 'online' ? Wifi : WifiOff" class="w-3.5 h-3.5" />
                  </div>
                  <div>
                    <span class="text-[9px] font-black uppercase tracking-widest leading-none"
                      :class="h.status === 'online' ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600 dark:text-rose-400'">
                      {{ h.status }}
                    </span>
                    <p class="text-[10px] text-slate-500 font-medium leading-tight">
                      {{ new Date(h.changed_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}
                    </p>
                  </div>
                </div>
                <div class="text-right">
                  <div class="text-[10px] font-bold text-slate-700 dark:text-slate-300">
                    {{ new Date(h.changed_at).toLocaleDateString([], { month: 'short', day: 'numeric' }) }}
                  </div>
                </div>
              </div>

              <div v-if="history.length === 0" class="py-12 text-center">
                <p class="text-xs text-slate-400 italic">No historical events recorded for this device yet.</p>
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Column 3: Ports & Services (Sidebar) -->
      <div class="space-y-6">
        <!-- Health & Uptime Metrics (Sidebar Stack) -->
        <div class="space-y-4">
          <div
            class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 p-6 shadow-xl">
            <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Longest Streak</div>
            <div class="text-2xl font-black text-emerald-500">{{ longestOnlineStreak }} <span
                class="text-xs font-medium text-slate-400">hours</span></div>
          </div>
          <div
            class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 p-6 shadow-xl">
            <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Avg Offline</div>
            <div class="text-2xl font-black text-rose-500">{{ avgOfflineDuration }} <span
                class="text-xs font-medium text-slate-400">mins</span></div>
          </div>
          <div
            class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 p-6 shadow-xl">
            <div class="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">Total Uptime</div>
            <div class="text-2xl font-black text-blue-500">{{ uptimePercentage }}%</div>
          </div>
        </div>

        <div
          class="bg-white/70 dark:bg-slate-800/70 backdrop-blur-xl rounded-3xl border border-slate-200 dark:border-slate-700/50 p-8 shadow-xl relative overflow-hidden">
          <!-- Background Decoration -->
          <div class="absolute -bottom-12 -right-12 w-48 h-48 bg-blue-500/10 dark:bg-blue-400/5 rounded-full blur-3xl">
          </div>

          <h2 class="text-lg font-bold text-slate-900 dark:text-white mb-6 flex items-center gap-2">
            <div class="w-1.5 h-6 bg-blue-500 rounded-full"></div>
            Port Lookup Results
          </h2>

          <div v-if="parsedPorts.length > 0" class="space-y-3 relative z-10">
            <div v-for="port in parsedPorts" :key="port.port"
              class="group flex items-center justify-between p-4 bg-slate-50 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-700/50 hover:border-blue-500/30 rounded-2xl transition-all">
              <div class="flex items-center gap-4">
                <div class="flex flex-col items-center justify-center">
                  <div class="text-xs font-black text-blue-600 dark:text-blue-400 tracking-tighter">{{ port.port }}
                  </div>
                  <div class="text-[8px] font-black text-slate-500 uppercase">{{ port.protocol || 'TCP' }}</div>
                </div>
                <div>
                  <div class="text-sm font-bold text-slate-900 dark:text-white">{{ port.service || 'Unknown' }}</div>
                  <div class="text-[10px] text-slate-500 font-medium">Service Active</div>
                </div>
              </div>

              <div class="flex items-center gap-2">
                <button v-if="port.port === 22" @click="openSSH(port.port)"
                  class="p-2 transition-all rounded-lg bg-slate-200 dark:bg-slate-800 hover:bg-slate-900 hover:text-white text-slate-600 dark:text-slate-300"
                  v-tooltip="'Terminal Access'">
                  <Terminal class="w-4 h-4" />
                </button>
                <a v-if="[80, 443, 8080, 8000, 3000].includes(port.port)" :href="`http://${device.ip}:${port.port}`"
                  target="_blank"
                  class="p-2 transition-all rounded-lg bg-blue-500/10 hover:bg-blue-500 text-blue-600 dark:text-blue-400 hover:text-white"
                  v-tooltip="'Open Interface'">
                  <ExternalLink class="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>

          <div v-else class="flex flex-col items-center justify-center py-20 text-center space-y-4">
            <div class="p-6 bg-slate-50 dark:bg-slate-900/50 rounded-full">
              <ShieldAlert class="w-12 h-12 text-slate-300 dark:text-slate-600" />
            </div>
            <div>
              <p class="text-slate-900 dark:text-white font-bold">No Open Ports</p>
              <p class="text-xs text-slate-500 mt-1 max-w-[180px]">Run a Deep Scan to audit common network services.</p>
            </div>
          </div>

          <div class="mt-8 pt-8 border-t border-slate-100 dark:border-slate-700/50">
            <div
              class="flex items-center justify-between text-[10px] font-black uppercase tracking-widest text-slate-500">
              <span>Last Audit Scan</span>
              <span class="text-slate-400">{{ formatRelativeTime(device.last_seen) }}</span>
            </div>
          </div>
        </div>
      </div>

    </div>

    <TerminalModal v-if="showTerminal" :device="device" :port="sshPort" @close="showTerminal = false" />
  </div>
</template>

<script setup>
import { Popover, PopoverButton, PopoverPanel } from '@headlessui/vue'
import * as LucideIcons from 'lucide-vue-next'
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import TerminalModal from '../components/TerminalModal.vue'
import { formatRelativeTime } from '@/utils/date'
import { useNotifications } from '@/composables/useNotifications'

const route = useRoute()
const device = ref(null)
const showTerminal = ref(false)
const sshPort = ref(22)

const form = reactive({ display_name: '', name: '', device_type: '', icon: '', attributes: {} })

const isScanning = ref(false)
const history = ref([])
const fidelityHistory = ref([])
const { notifySuccess, notifyError } = useNotifications()

const isCategoryOpen = ref(false)
const isIPOpen = ref(false)
const categorySearch = ref('')
const iconSearch = ref('')
const vClickOutside = {
  mounted(el, binding) {
    el._clickOutside = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el) {
    document.removeEventListener('click', el._clickOutside)
  }
}

const getIPAllocationLabel = (val) => {
  if (val === 'static') return 'Static IP'
  if (val === 'dhcp') return 'DHCP Reserved'
  return 'Dynamic (DHCP)'
}

// formatDate removed, formatRelativeTime kept
const formatTime = (ts) => {
  if (!ts) return 'Unknown'
  return new Date(ts).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })
}

// Map LucideIcons to local aliases for template usage if needed, 
// but most are used via getIconComponent or component :is
const Loader2 = LucideIcons.Loader2
const Scan = LucideIcons.Scan
const ArrowLeft = LucideIcons.ArrowLeft
const Wifi = LucideIcons.Wifi
const WifiOff = LucideIcons.WifiOff
const Terminal = LucideIcons.Terminal
const ExternalLink = LucideIcons.ExternalLink
const ShieldAlert = LucideIcons.ShieldAlert
const Save = LucideIcons.Save
const ChevronDown = LucideIcons.ChevronDown
const Search = LucideIcons.Search

const deviceTypes = [
  'Smartphone', 'Tablet', 'Laptop', 'Desktop', 'Server',
  'Router/Gateway', 'Network Bridge', 'Switch', 'Access Point',
  'TV/Entertainment', 'IoT Device', 'Smart Bulb', 'Smart Plug/Switch',
  'Microcontroller', 'Security Camera', 'Sensor', 'Audio/Speaker',
  'Streaming Device', 'Printer', 'NAS/Storage', 'Game Console',
  'Media Server', 'Home Automation', 'Server Admin', 'Generic'
]

const filteredDeviceTypes = computed(() => {
  if (!categorySearch.value) return deviceTypes
  return deviceTypes.filter(t => t.toLowerCase().includes(categorySearch.value.toLowerCase()))
})

const availableIcons = [
  'smartphone', 'tablet', 'laptop', 'monitor', 'server', 'router', 'network',
  'layers', 'rss', 'tv', 'cpu', 'lightbulb', 'plug', 'microchip', 'camera',
  'waves', 'speaker', 'play', 'printer', 'hard-drive', 'gamepad-2',
  'play-circle', 'home', 'settings', 'shield-check', 'help-circle'
]

const filteredIcons = computed(() => {
  if (!iconSearch.value) return availableIcons
  return availableIcons.filter(i => i.toLowerCase().includes(iconSearch.value.toLowerCase()))
})

const typeToIconMap = {
  "Smartphone": "smartphone",
  "Tablet": "tablet",
  "Laptop": "laptop",
  "Desktop": "monitor",
  "Server": "server",
  "Router/Gateway": "router",
  "Network Bridge": "network",
  "Switch": "layers",
  "Access Point": "rss",
  "TV/Entertainment": "tv",
  "IoT Device": "cpu",
  "Smart Bulb": "lightbulb",
  "Smart Plug/Switch": "plug",
  "Microcontroller": "microchip",
  "Security Camera": "camera",
  "Sensor": "waves",
  "Audio/Speaker": "speaker",
  "Streaming Device": "play",
  "Printer": "printer",
  "NAS/Storage": "hard-drive",
  "Game Console": "gamepad-2",
  "Media Server": "play-circle",
  "Home Automation": "home",
  "Server Admin": "settings",
  "Generic": "help-circle",
  "Unknown": "help-circle"
}

const getIconComponent = (name) => {
  if (!name) return LucideIcons.HelpCircle
  // Direct match
  if (LucideIcons[name]) return LucideIcons[name]
  // Convert kebab to PascalCase (e.g., 'play-circle' -> 'PlayCircle')
  const camel = name.split('-').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join('')
  return LucideIcons[camel] || LucideIcons[name] || LucideIcons.HelpCircle
}

watch(() => form.device_type, (newType) => {
  if (newType && typeToIconMap[newType]) {
    form.icon = typeToIconMap[newType]
  }
})

// Logic for Availability Visualization
const longestOnlineStreak = computed(() => {
  if (history.value.length === 0) return 0
  let maxHours = 0
  let currentStreak = 0

  const sorted = [...history.value].reverse()
  const now = new Date()

  for (let i = 0; i < sorted.length; i++) {
    const start = new Date(sorted[i].changed_at)
    const end = (i < sorted.length - 1) ? new Date(sorted[i + 1].changed_at) : now

    if (sorted[i].status === 'online') {
      const diffHours = (end - start) / (1000 * 60 * 60)
      if (diffHours > 0) currentStreak += diffHours
    } else {
      maxHours = Math.max(maxHours, currentStreak)
      currentStreak = 0
    }
  }
  return Math.round(Math.max(maxHours, currentStreak))
})

const avgOfflineDuration = computed(() => {
  if (history.value.length === 0) return 0

  let totalMins = 0
  let counts = 0

  const sorted = [...history.value].reverse()
  const now = new Date()

  for (let i = 0; i < sorted.length; i++) {
    const start = new Date(sorted[i].changed_at)
    const end = (i < sorted.length - 1) ? new Date(sorted[i + 1].changed_at) : now

    if (sorted[i].status === 'offline') {
      const diffMins = (end - start) / (1000 * 60)
      if (diffMins > 0) {
        totalMins += diffMins
        counts++
      }
    }
  }
  return counts > 0 ? Math.round(totalMins / counts) : 0
})
const availabilitySummary = computed(() => {
  // Create 24 blocks for the last 24 hours
  const blocks = []
  const now = new Date()

  for (let i = 23; i >= 0; i--) {
    const blockTime = new Date(now.getTime() - i * 60 * 60 * 1000)
    const label = blockTime.getHours() + ':00'

    // Find history event closest to this time
    // For now, simpler: check if device was online in that window
    // Higher fidelity: find last status before this window
    const eventInWindow = history.value.find(e => {
      const et = new Date(e.changed_at)
      return et <= blockTime
    })

    blocks.push({
      time: i,
      label,
      status: eventInWindow ? eventInWindow.status : (device.value?.status || 'unknown')
    })
  }
  return blocks
})

const uptimePercentage = computed(() => {
  if (availabilitySummary.value.length === 0) return 0
  const onlineCount = availabilitySummary.value.filter(b => b.status === 'online').length
  return Math.round((onlineCount / availabilitySummary.value.length) * 100)
})

const chartOptions = computed(() => ({
  chart: {
    id: 'device-availability',
    toolbar: { show: false },
    background: 'transparent',
    animations: { enabled: true, easing: 'easeinout', speed: 800 },
    fontFamily: 'inherit',
    dropShadow: {
      enabled: true,
      top: 10,
      left: 0,
      blur: 10,
      color: '#3b82f6',
      opacity: 0.15
    }
  },
  xaxis: {
    type: 'datetime',
    labels: {
      style: { colors: '#94a3b8', fontSize: '9px', fontWeight: 600 },
      datetimeFormatter: {
        year: 'yyyy',
        month: 'MMM',
        day: 'dd MMM',
        hour: 'HH:mm'
      }
    },
    axisBorder: { show: false },
    axisTicks: { show: false }
  },
  yaxis: {
    labels: { show: false },
    min: 0,
    max: 1.1,
    tickAmount: 1
  },
  grid: {
    borderColor: 'rgba(148, 163, 184, 0.05)',
    strokeDashArray: 6,
    padding: { left: 0, right: 0 }
  },
  tooltip: {
    theme: 'dark',
    x: { format: 'MMM dd, HH:mm' },
    y: {
      formatter: (val) => val === 1 ? 'Online' : 'Offline'
    }
  },
  colors: ['#3b82f6'],
  stroke: { curve: 'smooth', width: 4 },
  markers: {
    size: 0,
    hover: {
      size: 6,
      colors: ['#3b82f6'],
      strokeColors: '#fff',
      strokeWidth: 3
    }
  },
  dataLabels: { enabled: false },
  fill: {
    type: 'gradient',
    gradient: {
      shadeIntensity: 1,
      opacityFrom: 0.5,
      opacityTo: 0.0,
      stops: [0, 90, 100],
      colorStops: [
        { offset: 0, color: "#3b82f6", opacity: 0.5 },
        { offset: 100, color: "#3b82f6", opacity: 0 }
      ]
    }
  }
}))

const chartSeries = computed(() => {
  if (!fidelityHistory.value || fidelityHistory.value.length === 0) return [{ name: 'Status', data: [] }]

  return [{
    name: 'Status',
    data: fidelityHistory.value
      .filter(h => h && h.timestamp)
      .map(h => {
        const ts = new Date(h.timestamp).getTime()
        return {
          x: isNaN(ts) ? 0 : ts,
          y: h.status === 'online' ? 1 : 0
        }
      })
      .filter(p => p.x > 0)
  }]
})

const parsedPorts = computed(() => {
  if (!device.value || !device.value.open_ports) return []

  let data = device.value.open_ports
  if (typeof data === 'string') {
    try {
      data = JSON.parse(data)
    } catch {
      return []
    }
  }

  if (Array.isArray(data) && data.length > 0) {
    let normalized = []
    if (typeof data[0] === 'number') {
      const commonMap = { 21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP', 443: 'HTTPS', 445: 'SMB', 3000: 'React', 8080: 'Web', 3306: 'MySQL', 5432: 'Postgres' }
      normalized = data.map(p => ({ port: p, service: commonMap[p] || 'Unknown', protocol: 'tcp' }))
    } else {
      // Already loaded as objects {port, service, protocol}
      // Normalize protocol and filter out exact duplicates
      normalized = data.map(p => ({ ...p, protocol: (p.protocol || 'tcp').toLowerCase() }))
    }

    // Strict de-duplication by port (since we only handle TCP for now)
    const seen = new Set()
    return normalized.filter(p => {
      const key = `${p.port}-${p.protocol}`
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }
  return []
})

const runDeepScan = async () => {
  if (isScanning.value) return
  isScanning.value = true
  try {
    await axios.post(`/api/v1/scans/device/${device.value.id}`)
    await fetchDevice() // Refresh details to show new ports
    notifySuccess('Port scan complete')
  } catch (e) {
    notifyError('Scan failed: ' + (e.response?.data?.detail || e.message))
  } finally {
    isScanning.value = false
  }
}

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
    form.device_type = device.value.device_type || 'Unknown'
    form.icon = device.value.icon || 'HelpCircle'
    // Initialize attributes if missing
    form.attributes = device.value.attributes || {}
  } catch (e) {
    console.error(e)
  }
}

const saveChanges = async () => {
  try {
    await axios.put(`/api/v1/devices/${device.value.id}`, form)
    notifySuccess('Changes saved')
    fetchDevice()
  } catch (e) {
    notifyError('Failed to save: ' + (e.response?.data?.detail || e.message))
  }
}

const fetchHistory = async () => {
  try {
    const res = await axios.get(`/api/v1/events/device/${route.params.id}?limit=200`)
    history.value = res.data

    // Also fetch high-fidelity data for the chart
    const fidelityRes = await axios.get(`/api/v1/events/device/${route.params.id}/fidelity?hours=24`)
    fidelityHistory.value = fidelityRes.data
  } catch (e) {
    console.error('Failed to fetch history:', e)
  }
}

onMounted(() => {
  fetchDevice()
  fetchHistory()
})
</script>
