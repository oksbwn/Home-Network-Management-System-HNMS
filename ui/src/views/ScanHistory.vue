<template>
  <div class="space-y-8">
    <div class="flex justify-between items-end">
      <div>
        <h1 class="text-3xl font-black text-slate-900 dark:text-white tracking-tight">Scan History</h1>
        <p class="text-slate-500 dark:text-slate-400 mt-1 text-sm font-medium">Activity logs and device discovery
          results</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="clearQueue"
          class="px-4 py-2 text-xs font-bold text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-900/20 rounded-xl transition-colors uppercase tracking-widest">
          Clear Queue
        </button>
        <button @click="fetchScans"
          class="px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-xl text-xs font-bold shadow-lg shadow-slate-200 dark:shadow-none hover:scale-105 active:scale-95 transition-all uppercase tracking-widest">
          Refresh
        </button>
      </div>
    </div>

    <div v-if="errorMessage"
      class="bg-rose-50 dark:bg-rose-900/20 border border-rose-100 dark:border-rose-900/30 p-4 rounded-2xl text-rose-700 dark:text-rose-300 text-sm flex items-center space-x-3">
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path fill-rule="evenodd"
          d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
          clip-rule="evenodd" />
      </svg>
      <span>{{ errorMessage }}</span>
    </div>

    <div
      class="bg-white dark:bg-slate-800 rounded-[2.5rem] shadow-xl shadow-slate-200/50 dark:shadow-none border border-slate-100 dark:border-slate-700 overflow-hidden">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-slate-100 dark:divide-slate-700">
          <thead>
            <tr class="bg-slate-50/50 dark:bg-slate-900/50">
              <th
                class="px-8 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Status</th>
              <th
                class="px-6 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Target</th>
              <th
                class="px-6 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Discovery</th>
              <th
                class="px-6 py-5 text-left text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Timeline</th>
              <th
                class="px-6 py-5 text-center text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Yield</th>
              <th
                class="px-8 py-5 text-right text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-[0.2em]">
                Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-50 dark:divide-slate-700">
            <template v-for="scan in scans" :key="scan.id">
              <tr class="group hover:bg-slate-50/80 dark:hover:bg-slate-700/30 transition-colors">
                <td class="px-8 py-6 whitespace-nowrap">
                  <span class="px-3 py-1.5 text-[10px] font-black rounded-lg uppercase tracking-widest border"
                    :class="statusClass(scan.status)">
                    {{ scan.status }}
                  </span>
                </td>
                <td class="px-6 py-6 whitespace-nowrap">
                  <div class="text-sm font-bold text-slate-900 dark:text-white truncate max-w-[200px]">{{ scan.target }}
                  </div>
                  <div class="text-[10px] text-slate-400 font-mono mt-0.5">{{ scan.id.split('-')[0] }}...</div>
                </td>
                <td class="px-6 py-6 whitespace-nowrap">
                  <div class="flex items-center space-x-2">
                    <div class="w-2 h-2 rounded-full bg-blue-500"></div>
                    <span class="text-xs font-bold text-slate-700 dark:text-slate-300 uppercase tracking-tighter">{{
                      scan.scan_type }}</span>
                  </div>
                </td>
                <td class="px-6 py-6 whitespace-nowrap">
                  <div class="text-xs font-medium text-slate-600 dark:text-slate-400">
                    {{ formatTime(scan.started_at || scan.created_at) }}
                  </div>
                  <div v-if="scan.finished_at" class="text-[10px] text-slate-400 mt-1 font-mono">
                    Took {{ getDuration(scan) }}
                  </div>
                </td>
                <td class="px-6 py-6 whitespace-nowrap text-center">
                  <div class="inline-flex flex-col items-center">
                    <span class="text-sm font-black text-slate-900 dark:text-white font-mono leading-none">
                      {{ resultsCount[scan.id] !== undefined ? resultsCount[scan.id] : '...' }}
                    </span>
                    <span class="text-[8px] font-black text-slate-400 uppercase tracking-tighter mt-1">Devices</span>
                  </div>
                </td>
                <td class="px-8 py-6 whitespace-nowrap text-right">
                  <button @click="toggleExpand(scan.id)"
                    class="p-2.5 rounded-xl border border-slate-100 dark:border-slate-600 bg-white dark:bg-slate-700 hover:border-slate-900 dark:hover:border-white transition-all shadow-sm group-hover:shadow-md">
                    <svg xmlns="http://www.w3.org/2000/svg"
                      class="h-4 w-4 text-slate-600 dark:text-slate-400 transition-transform duration-300"
                      :class="{ 'rotate-180': expandedIds.has(scan.id) }" fill="none" viewBox="0 0 24 24"
                      stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </td>
              </tr>
              <!-- Expanded Area -->
              <tr v-if="expandedIds.has(scan.id)">
                <td colspan="6" class="px-8 py-0 bg-slate-50/30 dark:bg-slate-900/20">
                  <div class="py-6 border-t border-slate-100 dark:border-slate-700">
                    <div v-if="loadingResults[scan.id]"
                      class="flex items-center justify-center py-12 space-x-3 text-slate-400">
                      <div
                        class="w-5 h-5 border-2 border-slate-300 dark:border-slate-600 border-t-slate-900 dark:border-t-white rounded-full animate-spin">
                      </div>
                      <span class="text-xs font-bold uppercase tracking-widest">Enriching results...</span>
                    </div>

                    <div v-else-if="scanResults[scan.id]?.length > 0"
                      class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      <div v-for="res in scanResults[scan.id]" :key="res.id"
                        class="group/item flex items-center space-x-4 p-4 bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm hover:shadow-md transition-all cursor-pointer"
                        @click="$router.push(`/devices/${res.id}`)">
                        <div
                          class="p-2.5 bg-slate-50 dark:bg-slate-900 rounded-xl group-hover/item:bg-blue-50 dark:group-hover/item:bg-blue-900/30 transition-colors">
                          <span class="text-[10px] font-black text-slate-400 group-hover/item:text-blue-500">.{{
                            res.ip.split('.').pop() }}</span>
                        </div>
                        <div class="flex-1 min-w-0">
                          <div class="text-[11px] font-black text-slate-900 dark:text-white truncate">
                            {{ res.hostname || res.ip }}
                          </div>
                          <div class="text-[9px] text-slate-500 font-mono mt-0.5 truncate uppercase">
                            {{ res.mac || 'Ghost Device' }}
                          </div>
                        </div>
                        <div
                          class="text-[8px] font-black px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 rounded-md text-slate-500 dark:text-slate-400 uppercase">
                          {{ res.open_ports?.length || 0 }}P
                        </div>
                      </div>
                    </div>

                    <div v-else class="py-12 text-center">
                      <div class="inline-flex p-4 bg-slate-100 dark:bg-slate-800 rounded-full mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-slate-400" fill="none"
                          viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                        </svg>
                      </div>
                      <p class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-widest">Zero
                        signals detected</p>
                    </div>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination Controls -->
    <div v-if="totalPages > 1" class="flex justify-center items-center space-x-2 py-8">
      <button @click="changePage(currentPage - 1)" :disabled="currentPage <= 1"
        class="h-10 px-4 text-xs font-black uppercase tracking-widest bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm">
        Previous
      </button>

      <div
        class="flex items-center px-6 h-10 bg-slate-900 dark:bg-white rounded-xl text-[10px] font-black uppercase tracking-[0.2em] text-white dark:text-slate-900">
        {{ currentPage }} <span class="mx-2 opacity-30">/</span> {{ totalPages }}
      </div>

      <button @click="changePage(currentPage + 1)" :disabled="currentPage >= totalPages"
        class="h-10 px-4 text-xs font-black uppercase tracking-widest bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-30 disabled:cursor-not-allowed transition-all shadow-sm">
        Next
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive } from 'vue'
import axios from 'axios'

const scans = ref([])
const errorMessage = ref('')
const expandedIds = ref(new Set())
const scanResults = reactive({})
const loadingResults = reactive({})
const resultsCount = reactive({})

// Pagination state
const currentPage = ref(1)
const totalPages = ref(1)
const limit = ref(10)

const fetchScans = async () => {
  errorMessage.value = ''
  try {
    const res = await axios.get('/api/v1/scans/', {
      params: {
        page: currentPage.value,
        limit: limit.value
      }
    })
    scans.value = res.data.items
    totalPages.value = res.data.total_pages
    currentPage.value = res.data.page

    // Fetch counts for all done scans
    res.data.items.forEach(scan => {
      if (scan.status === 'done' && resultsCount[scan.id] === undefined) {
        fetchCount(scan.id)
      }
    })
  } catch (e) {
    console.error(e)
    errorMessage.value = 'Failed to load scan history. The backend might be restarting.'
  }
}

const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  fetchScans()
}

const clearQueue = async () => {
  if (!confirm('Are you sure you want to clear all queued scans?')) return
  try {
    await axios.delete('/api/v1/scans/queue')
    await fetchScans()
  } catch (e) {
    console.error(e)
    errorMessage.value = 'Failed to clear queue.'
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

const formatTime = (t) => {
  if (!t) return 'Wait...'
  return new Date(t).toLocaleString()
}

const statusClass = (s) => {
  switch (s) {
    case 'done': return 'bg-emerald-50 text-emerald-600 border-emerald-100 dark:bg-emerald-500/10 dark:text-emerald-400 dark:border-emerald-500/20'
    case 'running': return 'bg-blue-50 text-blue-600 border-blue-100 dark:bg-blue-500/10 dark:text-blue-400 dark:border-blue-500/20 shadow-[0_0_10px_rgba(59,130,246,0.2)] animate-pulse'
    case 'queued': return 'bg-slate-50 text-slate-500 border-slate-100 dark:bg-slate-700/30 dark:text-slate-400 dark:border-slate-700'
    case 'error': return 'bg-rose-50 text-rose-600 border-rose-100 dark:bg-rose-500/10 dark:text-rose-400 dark:border-rose-500/20'
    default: return 'bg-slate-50 text-slate-400'
  }
}

const getDuration = (scan) => {
  if (!scan.started_at || !scan.finished_at) return '...'
  const start = new Date(scan.started_at)
  const end = new Date(scan.finished_at)
  const diff = Math.round((end - start) / 1000)
  if (diff < 60) return `${diff}s`
  const mins = Math.floor(diff / 60)
  const secs = diff % 60
  return `${mins}m ${secs}s`
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
