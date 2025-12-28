<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-slate-900 dark:text-white">Scan History</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Discovery activity log</p>
      </div>
      <div class="flex items-center gap-2">
        <button @click="clearQueue"
          class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-slate-500 hover:text-red-500 dark:text-slate-400 dark:hover:text-red-400"
          v-tooltip="'Clear Scan Queue'">
          <Trash2 class="w-5 h-5" />
        </button>
        <button @click="fetchScans"
          class="p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors text-slate-500 dark:text-slate-400"
          v-tooltip="'Refresh Scan History'">
          <RefreshCw class="w-5 h-5" :class="{ 'animate-spin': isRefreshing }" />
        </button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div v-for="stat in historyStats" :key="stat.label"
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

    <!-- Error Alert -->
    <div v-if="errorMessage"
      class="p-4 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 rounded-lg border border-red-200 dark:border-red-900/30 text-sm flex items-center gap-3">
      <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clip-rule="evenodd" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>

    <!-- Scans Table -->
    <div class="bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
          <thead class="bg-slate-50 dark:bg-slate-900/50">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Status</th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Target</th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Type</th>
              <th
                class="px-6 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Started</th>
              <th
                class="px-6 py-3 text-center text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Devices</th>
              <th
                class="px-6 py-3 text-right text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-200 dark:border-slate-700">
            <template v-for="scan in scans" :key="scan.id">
              <tr class="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <td class="px-6 py-4">
                  <div class="flex items-center gap-2">
                    <component :is="getStatusIcon(scan.status)" :class="[statusClass(scan.status), 'w-5 h-5']" />
                  </div>
                </td>
                <td class="px-6 py-4">
                  <div class="text-sm font-medium text-slate-900 dark:text-white truncate max-w-[200px]">{{ scan.target
                  }}</div>
                  <div class="text-xs text-slate-500 font-mono">{{ scan.id.split('-')[0] }}...</div>
                </td>
                <td class="px-6 py-4 text-sm text-slate-600 dark:text-slate-400">{{ scan.scan_type }}</td>
                <td class="px-6 py-4">
                  <div class="text-sm text-slate-600 dark:text-slate-400">{{ formatDate(scan.started_at ||
                    scan.created_at) }}</div>
                  <div v-if="scan.finished_at" class="text-xs text-slate-500">{{ getDuration(scan) }}</div>
                </td>
                <td class="px-6 py-4 text-center">
                  <span class="text-sm font-medium text-slate-900 dark:text-white">{{ resultsCount[scan.id] !==
                    undefined ? resultsCount[scan.id] : '...' }}</span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button @click="toggleExpand(scan.id)"
                    class="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-lg transition-all"
                    v-tooltip="expandedIds.has(scan.id) ? 'Collapse Details' : 'View Details'">
                    <component :is="expandedIds.has(scan.id) ? ChevronUp : ChevronDown" class="w-4 h-4" />
                  </button>
                </td>
              </tr>
              <!-- Expanded Area -->
              <tr v-if="expandedIds.has(scan.id)">
                <td colspan="6" class="px-6 py-4 bg-slate-50 dark:bg-slate-900/20">
                  <div v-if="loadingResults[scan.id]" class="flex items-center justify-center py-8 text-slate-500">
                    <div class="w-5 h-5 border-2 border-slate-300 border-t-blue-600 rounded-full animate-spin mr-3">
                    </div>
                    <span class="text-sm">Loading results...</span>
                  </div>
                  <div v-else-if="scanResults[scan.id]?.length > 0"
                    class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    <div v-for="res in scanResults[scan.id]" :key="res.id"
                      class="flex items-center gap-3 p-3 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 hover:shadow-sm transition-shadow cursor-pointer"
                      @click="$router.push(`/devices/${res.id}`)">
                      <div class="flex-1 min-w-0">
                        <div class="text-sm font-medium text-slate-900 dark:text-white truncate">{{ res.hostname ||
                          res.ip }}</div>
                        <div class="text-xs text-slate-500 font-mono truncate">{{ res.mac || 'Unknown MAC' }}</div>
                      </div>
                      <div class="text-xs font-medium text-slate-500 dark:text-slate-400">{{ res.open_ports?.length || 0
                      }}p</div>
                    </div>
                  </div>
                  <div v-else class="py-8 text-center">
                    <div class="text-sm text-slate-500">No devices found</div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center items-center gap-2">
      <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1"
        class="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        Previous
      </button>
      <div class="px-4 py-2 bg-slate-900 dark:bg-white rounded-lg text-sm font-medium text-white dark:text-slate-900">
        {{ currentPage }} / {{ totalPages }}
      </div>
      <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages"
        class="px-4 py-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, computed } from 'vue'
import axios from 'axios'
import Sparkline from '@/components/Sparkline.vue'
import { Trash2, RefreshCw, CheckCircle, AlertTriangle, Clock, ChevronDown, ChevronUp, Activity, Smartphone, Server as ServerIcon } from 'lucide-vue-next'
import { formatDate, formatRelativeTime } from '@/utils/date'

const scans = ref([])
const errorMessage = ref('')
const isRefreshing = ref(false)
const expandedIds = ref(new Set())
const scanResults = reactive({})
const loadingResults = reactive({})
const resultsCount = reactive({})
const currentPage = ref(1)
const totalPages = ref(1)
const limit = ref(10)

const fetchScans = async () => {
  errorMessage.value = ''
  isRefreshing.value = true
  try {
    const res = await axios.get('/api/v1/scans/', {
      params: { page: currentPage.value, limit: limit.value }
    })
    scans.value = res.data.items
    totalPages.value = res.data.total_pages
    currentPage.value = res.data.page
    res.data.items.forEach(scan => {
      if (scan.status === 'done' && resultsCount[scan.id] === undefined) {
        fetchCount(scan.id)
      }
    })
  } catch (e) {
    errorMessage.value = 'Failed to load scan history'
  } finally {
    setTimeout(() => {
      isRefreshing.value = false
    }, 500)
  }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchScans()
}

const clearQueue = async () => {
  if (!confirm('Clear all queued scans?')) return
  try {
    await axios.delete('/api/v1/scans/queue')
    await fetchScans()
  } catch (e) {
    errorMessage.value = 'Failed to clear queue'
  }
}

const fetchCount = async (id) => {
  try {
    const res = await axios.get(`/api/v1/scans/${id}/results`)
    resultsCount[id] = res.data.length
  } catch (e) {
    console.error(e)
  }
}

const toggleExpand = async (id) => {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
    if (!scanResults[id]) {
      await fetchResults(id)
    }
  }
}

const historyStats = computed(() => {
  const total = scans.value.length // This is just loaded scans, ideally we use pagination total
  const doneScans = scans.value.filter(s => s.status === 'done')
  const successRate = total > 0 ? Math.round((doneScans.length / total) * 100) : 0

  // Calculate avg duration
  let totalDuration = 0
  let count = 0
  doneScans.forEach(s => {
    if (s.started_at && s.finished_at) {
      totalDuration += (new Date(s.finished_at) - new Date(s.started_at))
      count++
    }
  })
  const avgDurationSeconds = count > 0 ? Math.round(totalDuration / count / 1000) : 0
  const avgDuration = avgDurationSeconds < 60 ? `${avgDurationSeconds}s` : `${Math.floor(avgDurationSeconds / 60)}m`

  return [
    {
      label: 'Total Scans',
      value: total > 0 ? total + '+' : 0, // Quick hack since we paginate
      icon: Activity,
      color: '#3b82f6',
      bgClass: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
      trend: [5, 4, 6, 5, 7, 6, 8, 7, 9, 8],
      change: 'All Time',
      changeType: 'up'
    },
    {
      label: 'Success Rate',
      value: `${successRate}%`,
      icon: CheckCircle,
      color: '#10b981',
      bgClass: 'bg-emerald-100 text-emerald-600 dark:bg-emerald-900/30 dark:text-emerald-400',
      trend: [95, 98, 96, 99, 97, 100, 98, 99, 97, 100],
      change: 'Reliability',
      changeType: 'up'
    },
    {
      label: 'Avg Duration',
      value: avgDuration,
      icon: Clock,
      color: '#8b5cf6',
      bgClass: 'bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400',
      trend: [45, 42, 44, 40, 43, 41, 39, 40, 38, 35],
      change: 'Performance',
      changeType: 'down'
    }
  ]
})

const fetchResults = async (id) => {
  loadingResults[id] = true
  try {
    const res = await axios.get(`/api/v1/scans/${id}/results`)
    scanResults[id] = res.data
    resultsCount[id] = res.data.length
  } catch (e) {
    console.error(e)
  } finally {
    loadingResults[id] = false
  }
}


const getStatusIcon = (s) => {
  switch (s) {
    case 'done': return CheckCircle
    case 'running': return RefreshCw // Animated via class
    case 'queued': return Clock
    case 'error': return AlertTriangle
    default: return Clock
  }
}

const statusClass = (s) => {
  switch (s) {
    case 'done': return 'text-emerald-500 dark:text-emerald-400'
    case 'running': return 'text-blue-500 dark:text-blue-400 animate-spin'
    case 'queued': return 'text-slate-400 dark:text-slate-500'
    case 'error': return 'text-red-500 dark:text-red-400'
    default: return 'text-slate-400'
  }
}

const getDuration = (scan) => {
  if (!scan.started_at || !scan.finished_at) return ''
  const diff = Math.round((new Date(scan.finished_at) - new Date(scan.started_at)) / 1000)
  if (diff < 60) return `${diff}s`
  return `${Math.floor(diff / 60)}m ${diff % 60}s`
}

let pollInterval = null

onMounted(() => {
  fetchScans()
  pollInterval = setInterval(fetchScans, 10000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
})
</script>
