<template>
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
        <svg :viewBox="`0 0 ${width} ${height}`" class="w-full h-full overflow-visible" preserveAspectRatio="none">

            <!-- Up Link (Tx) - Blue -->
            <path :d="upPath" fill="none" stroke="#3b82f6" stroke-width="1.5" stroke-linecap="round"
                stroke-linejoin="round" class="opacity-60" />

            <!-- Down Link (Rx) - Green -->
            <path :d="downPath" fill="none" stroke="#10b981" stroke-width="1.5" stroke-linecap="round"
                stroke-linejoin="round" />

        </svg>
    </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
    data: {
        type: Array, // Array of {down, up, timestamp}
        required: true
    },
    width: {
        type: Number,
        default: 100
    },
    height: {
        type: Number,
        default: 40
    }
})

const processPoints = (key) => {
    if (!props.data || props.data.length < 2) return ''

    // Find global max to scale both lines consistently (or relative to each other?)
    // Usually scaling relative to each other is better visually, or independent?
    // Independent makes them comparable in shape but misleading in magnitude. 
    // Consistent limit is better.
    // Let's use independent limits for "sparkline" purposes to show activity shape,
    // as up/down speeds can differ by orders of magnitude (100Mbps down vs 5Mbps up).
    // If we share limits, the 5Mbps line will be flat.

    const values = props.data.map(d => d[key])
    const min = Math.min(...values)
    const max = Math.max(...values)
    const range = (max - min) || 1

    const padY = 5
    const usableHeight = props.height - (padY * 2)

    const pts = values.map((val, i) => ({
        x: (i / (values.length - 1)) * props.width,
        y: props.height - ((val - min) / range) * usableHeight - padY
    }))

    if (pts.length < 2) return ''

    // Simple line (no smoothing for performance/sharpness on small charts)
    let d = `M ${pts[0].x},${pts[0].y}`
    for (let i = 1; i < pts.length; i++) {
        d += ` L ${pts[i].x},${pts[i].y}`
    }
    return d
}

const upPath = computed(() => processPoints('up'))
const downPath = computed(() => processPoints('down'))

</script>
