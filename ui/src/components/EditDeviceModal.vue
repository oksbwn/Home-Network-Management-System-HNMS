<template>
    <TransitionRoot appear :show="isOpen" as="template">
        <Dialog as="div" @close="closeModal" class="relative z-50">
            <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0" enter-to="opacity-100"
                leave="duration-200 ease-in" leave-from="opacity-100" leave-to="opacity-0">
                <div class="fixed inset-0 bg-black/50 backdrop-blur-sm" />
            </TransitionChild>

            <div class="fixed inset-0 overflow-y-auto">
                <div class="flex min-h-full items-center justify-center p-4 text-center">
                    <TransitionChild as="template" enter="duration-300 ease-out" enter-from="opacity-0 scale-95"
                        enter-to="opacity-100 scale-100" leave="duration-200 ease-in" leave-from="opacity-100 scale-100"
                        leave-to="opacity-0 scale-95">
                        <DialogPanel
                            class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-slate-800 p-6 text-left align-middle shadow-xl transition-all border border-slate-200 dark:border-slate-700">
                            <DialogTitle as="h3"
                                class="text-lg font-medium leading-6 text-slate-900 dark:text-white mb-4">
                                Edit Device Details
                            </DialogTitle>

                            <form @submit.prevent="saveDevice" class="space-y-4">
                                <!-- IP Address (Read Only) -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">IP
                                        Address</label>
                                    <p class="mt-1 text-sm text-slate-500 font-mono">{{ device.ip }}</p>
                                </div>

                                <!-- Display Name -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Display
                                        Name</label>
                                    <input v-model="form.display_name" type="text"
                                        class="mt-1 block w-full rounded-md border-slate-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                                        placeholder="e.g. Living Room TV" />
                                </div>

                                <!-- Device Type -->
                                <div>
                                    <label class="block text-sm font-medium text-slate-700 dark:text-slate-300">Device
                                        Type</label>
                                    <select v-model="form.device_type"
                                        class="mt-1 block w-full rounded-md border-slate-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm">
                                        <option v-for="type in deviceTypes" :key="type" :value="type">{{ type }}
                                        </option>
                                    </select>
                                </div>

                                <!-- Icon Picker -->
                                <div>
                                    <label
                                        class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Select
                                        Icon</label>
                                    <div
                                        class="grid grid-cols-5 gap-2 max-h-40 overflow-y-auto p-2 border border-slate-200 dark:border-slate-700 rounded-md">
                                        <button v-for="icon in availableIcons" :key="icon" type="button"
                                            @click="form.icon = icon"
                                            class="p-2 rounded-lg flex items-center justify-center transition-colors"
                                            :class="form.icon === icon ? 'bg-blue-100 dark:bg-blue-900/50 text-blue-600 dark:text-blue-400 ring-2 ring-blue-500' : 'hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500'">
                                            <component :is="getIconComponent(icon)" class="h-6 w-6" />
                                        </button>
                                    </div>
                                </div>

                                <div class="mt-6 flex justify-end gap-3">
                                    <button type="button"
                                        class="px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-md hover:bg-slate-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-slate-200 dark:border-slate-600 dark:hover:bg-slate-600"
                                        @click="closeModal">
                                        Cancel
                                    </button>
                                    <button type="submit" :disabled="isSaving"
                                        class="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed">
                                        <Loader2 v-if="isSaving" class="mr-2 h-4 w-4 animate-spin" />
                                        {{ isSaving ? 'Saving...' : 'Save Changes' }}
                                    </button>
                                </div>
                            </form>
                        </DialogPanel>
                    </TransitionChild>
                </div>
            </div>
        </Dialog>
    </TransitionRoot>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import {
    TransitionRoot,
    TransitionChild,
    Dialog,
    DialogPanel,
    DialogTitle,
} from '@headlessui/vue'
import * as LucideIcons from 'lucide-vue-next'
import axios from 'axios'

const props = defineProps({
    isOpen: Boolean,
    device: Object
})

const emit = defineEmits(['close', 'save'])

const isSaving = ref(false)

const form = ref({
    display_name: '',
    device_type: '',
    icon: ''
})

const deviceTypes = [
    'Desktop', 'Laptop', 'Mobile', 'Tablet', 'Server', 'Printer', 'Monitor',
    'Router', 'Switch', 'Access Point', 'Gateway', 'Firewall', 'NAS',
    'Smart Plug', 'Smart Bulb', 'Smart Switch', 'Thermostat', 'Camera', 'Door Lock', 'Sensor',
    'TV', 'Speaker', 'Game Console', 'Media Player', 'Wearable', 'Vehicle',
    'IoT (Generic)', 'Unknown'
]

const availableIcons = [
    'Monitor', 'Laptop', 'Smartphone', 'Tablet', 'Server', 'Printer',
    'Wifi', 'Network', 'Globe', 'ShieldCheck', 'Database',
    'Zap', 'Lightbulb', 'Sliders', 'Home', 'Video', 'Lock', 'Eye',
    'Tv', 'Speaker', 'Gamepad2', 'Film', 'Watch', 'Truck',
    'Cpu', 'HelpCircle'
]

const typeToIconMap = {
    'Desktop': 'Monitor',
    'Laptop': 'Laptop',
    'Mobile': 'Smartphone',
    'Tablet': 'Tablet',
    'Server': 'Server',
    'Printer': 'Printer',
    'Monitor': 'Monitor',
    'Router': 'Wifi',
    'Access Point': 'Wifi',
    'Gateway': 'Globe',
    'Switch': 'Network',
    'Firewall': 'ShieldCheck',
    'NAS': 'Database',
    'Smart Plug': 'Zap',
    'Smart Bulb': 'Lightbulb',
    'Smart Switch': 'Sliders',
    'Thermostat': 'Home',
    'Camera': 'Video',
    'Door Lock': 'Lock',
    'Sensor': 'Eye',
    'TV': 'Tv',
    'Speaker': 'Speaker',
    'Game Console': 'Gamepad2',
    'Media Player': 'Film',
    'Wearable': 'Watch',
    'Vehicle': 'Truck',
    'IoT (Generic)': 'Cpu',
    'Unknown': 'HelpCircle'
}

watch(() => form.value.device_type, (newType) => {
    if (newType && typeToIconMap[newType]) {
        form.value.icon = typeToIconMap[newType]
    }
})

const getIconComponent = (name) => {
    // If name is kebab-case (legacy), convert to PascalCase
    // But now we prefer PascalCase Lucide names directly
    if (!name) return LucideIcons.HelpCircle

    // Direct match
    if (LucideIcons[name]) return LucideIcons[name]

    // Try PascalCase conversion if user has legacy data
    const camel = name.split('-').map(p => p.charAt(0).toUpperCase() + p.slice(1)).join('')
    if (LucideIcons[camel]) return LucideIcons[camel]

    // Explicit legacy mappings if needed (e.g. computer-desktop -> Monitor)
    const legacyMap = {
        'computer-desktop': 'Monitor',
        'device-laptop': 'Laptop',
        'device-phone-mobile': 'Smartphone',
        'device-tablet': 'Tablet',
        'server-stack': 'Database',
        'bolt': 'Zap'
    }
    if (legacyMap[name]) return LucideIcons[legacyMap[name]] || LucideIcons.HelpCircle

    return LucideIcons.HelpCircle
}

watch(() => props.device, (newVal) => {
    if (newVal) {
        form.value = {
            display_name: newVal.display_name || newVal.name || '',
            device_type: newVal.device_type || 'unknown',
            icon: newVal.icon || 'help-circle'
        }
    }
}, { immediate: true })

const closeModal = () => {
    emit('close')
}

const saveDevice = async () => {
    if (!props.device) return
    isSaving.value = true
    try {
        const response = await axios.patch(`/api/v1/devices/${props.device.id}`, form.value)
        emit('save', response.data)
        closeModal()
    } catch (error) {
        console.error('Failed to update device', error)
        // Could add toast error here
    } finally {
        isSaving.value = false
    }
}
</script>
