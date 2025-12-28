export default {
  mounted(el, binding) {
    let tooltipDiv = null

    const createTooltip = () => {
      if (tooltipDiv) return

      tooltipDiv = document.createElement('div')
      tooltipDiv.textContent = binding.value
      tooltipDiv.className = `
        fixed z-[9999] px-2.5 py-1.5 text-xs font-medium text-white 
        bg-slate-900/90 dark:bg-slate-700/90 backdrop-blur-md 
        rounded-lg shadow-xl pointer-events-none 
        transition-opacity duration-200 opacity-0 transform scale-95
        border border-white/10 dark:border-slate-600/50
      `
      document.body.appendChild(tooltipDiv)

      // Initial position for calculation
      const rect = el.getBoundingClientRect()
      const tooltipRect = tooltipDiv.getBoundingClientRect()

      // Default position: Top
      let top = rect.top - tooltipRect.height - 8
      let left = rect.left + (rect.width - tooltipRect.width) / 2

      // Check bounds and adjust
      if (top < 0) {
        // Flip to bottom
        top = rect.bottom + 8
      }
      
      if (left < 0) left = 8
      if (left + tooltipRect.width > window.innerWidth) {
        left = window.innerWidth - tooltipRect.width - 8
      }

      tooltipDiv.style.top = `${top}px`
      tooltipDiv.style.left = `${left}px`

      // Animate in
      requestAnimationFrame(() => {
        if (tooltipDiv) {
          tooltipDiv.classList.remove('opacity-0', 'scale-95')
          tooltipDiv.classList.add('opacity-100', 'scale-100')
        }
      })
    }

    const removeTooltip = () => {
      if (tooltipDiv) {
        tooltipDiv.remove()
        tooltipDiv = null
      }
    }

    el.addEventListener('mouseenter', createTooltip)
    el.addEventListener('mouseleave', removeTooltip)
    el.addEventListener('click', removeTooltip) // Hide on click too usually

    // Store cleanup function
    el._tooltipCleanup = () => {
      el.removeEventListener('mouseenter', createTooltip)
      el.removeEventListener('mouseleave', removeTooltip)
      el.removeEventListener('click', removeTooltip)
      removeTooltip()
    }
  },
  updated(el, binding) {
    // Determine if we need to update text content if hovering?
    // For simplicity, we just leverage the mouseenter redraw with new binding.value if needed,
    // but binding.value is read in createTooltip. 
    // If the value changes while hovering, we really should update textContent.
    // However, usually tooltips are static or re-hovered. 
    // We'll leave it simple for now. 
    // To support dynamic updates while hovered:
    // we could attach the text update logic here, but keeping it simple is safer.
  },
  unmounted(el) {
    if (el._tooltipCleanup) {
      el._tooltipCleanup()
    }
  }
}
