<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Scan History</h1>
      <div class="flex space-x-4">
        <button @click="clearQueue" class="text-sm text-red-600 dark:text-red-400 hover:underline">
          Clear Queue
        </button>
        <button @click="fetchScans" class="text-sm text-blue-600 dark:text-blue-400 hover:underline">
          Refresh
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 p-4 rounded-lg text-red-700 dark:text-red-400 text-sm">
      {{ errorMessage }}
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
        <thead class="bg-gray-50 dark:bg-slate-900">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Target</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Type</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Started</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider text-right">Devices</th>
            <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Details</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-slate-700">
          <template v-for="scan in scans" :key="scan.id">
            <tr class="hover:bg-gray-50 dark:hover:bg-slate-700/50 transition">
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 py-1 text-xs font-medium rounded-full"
                  :class="statusClass(scan.status)"
                >
                  {{ scan.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white truncate max-w-xs">
                {{ scan.target }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ scan.scan_type }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatTime(scan.started_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white text-right font-mono">
                {{ resultsCount[scan.id] !== undefined ? resultsCount[scan.id] : '...' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <button 
                  @click="toggleExpand(scan.id)" 
                  class="text-blue-600 hover:text-blue-900 dark:hover:text-blue-400"
                >
                  {{ expandedIds.has(scan.id) ? 'Collapse' : 'View Results' }}
                </button>
              </td>
            </tr>
            <!-- Expanded Area -->
            <tr v-if="expandedIds.has(scan.id)" class="bg-gray-50 dark:bg-slate-900/50">
              <td colspan="6" class="px-6 py-4">
                <div v-if="loadingResults[scan.id]" class="text-sm text-gray-500 py-2">Loading results...</div>
                <div v-else-if="scanResults[scan.id]?.length > 0" class="space-y-2">
                  <div v-for="res in scanResults[scan.id]" :key="res.id" class="flex justify-between items-center text-xs p-2 bg-white dark:bg-slate-800 rounded border border-gray-100 dark:border-slate-700">
                     <div class="flex space-x-4">
                        <span class="font-mono font-bold text-gray-700 dark:text-gray-300 w-24">{{ res.ip }}</span>
                        <span class="text-gray-500">{{ res.mac || 'No MAC' }}</span>
                        <span class="text-gray-900 dark:text-white font-medium">{{ res.hostname || 'No Hostname' }}</span>
                     </div>
                     <div class="text-gray-400">{{ res.open_ports?.length || 0 }} ports</div>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-400 py-2 italic text-center">No devices detected in this scan.</div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <!-- Pagination Controls -->
    <div v-if="totalPages > 1" class="flex justify-center items-center space-x-6 py-4">
      <button 
        @click="changePage(currentPage - 1)" 
        :disabled="currentPage <= 1"
        class="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition dark:bg-slate-800 dark:border-slate-700 dark:text-gray-300 dark:hover:bg-slate-700"
      >
        <span>Previous</span>
      </button>
      
      <div class="text-sm font-medium text-gray-600 dark:text-gray-400">
        Page <span class="text-gray-900 dark:text-white">{{ currentPage }}</span> of {{ totalPages }}
      </div>

      <button 
        @click="changePage(currentPage + 1)" 
        :disabled="currentPage >= totalPages"
        class="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition dark:bg-slate-800 dark:border-slate-700 dark:text-gray-300 dark:hover:bg-slate-700"
      >
        <span>Next</span>
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
        case 'done': return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
        case 'running': return 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
        case 'queued': return 'bg-gray-100 text-gray-700 dark:bg-gray-900/30 dark:text-gray-400'
        case 'error': return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
        default: return 'bg-gray-100 text-gray-700'
    }
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
