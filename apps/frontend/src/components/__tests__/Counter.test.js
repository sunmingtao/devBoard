import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Counter from '../Counter.vue'

describe('Counter.vue', () => {
  it('renders initial state correctly', () => {
    const wrapper = mount(Counter)
    
    // Check header
    expect(wrapper.text()).toContain('Vue 3 Composition API Demo')
    
    // Check initial ref counter value
    expect(wrapper.text()).toContain('Current value: 0')
    
    // Check reactive counter initial state
    expect(wrapper.text()).toContain('Double value: 0')
    expect(wrapper.text()).toContain('Total clicks: 0')
    expect(wrapper.text()).toContain('Last action: None')
  })

  it('increments ref counter when + button is clicked', async () => {
    const wrapper = mount(Counter)
    
    // Find the first + button (ref counter)
    const refPlusButton = wrapper.findAll('button').find(btn => 
      btn.text() === '+' && btn.classes().includes('btn-primary')
    )
    
    expect(refPlusButton).toBeTruthy()
    
    // Click to increment
    await refPlusButton.trigger('click')
    
    // Check values updated
    const countSpan = wrapper.findAll('.count')[0]
    expect(countSpan.text()).toBe('1')
    expect(wrapper.text()).toContain('Total clicks: 2') // ref count (1) + reactive total clicks (1)
    expect(wrapper.text()).toContain('Last action: Incremented ref counter')
  })

  it('decrements ref counter when - button is clicked', async () => {
    const wrapper = mount(Counter)
    
    // Find the first - button (ref counter)
    const refMinusButton = wrapper.findAll('button').find(btn => 
      btn.text() === '-' && btn.classes().includes('btn-secondary')
    )
    
    expect(refMinusButton).toBeTruthy()
    
    // Click to decrement
    await refMinusButton.trigger('click')
    
    // Check values updated
    const countSpan = wrapper.findAll('.count')[0]
    expect(countSpan.text()).toBe('-1')
    expect(wrapper.text()).toContain('Total clicks: 0') // ref count (-1) + reactive total clicks (1)
    expect(wrapper.text()).toContain('Last action: Decremented ref counter')
  })

  it('handles reactive counter operations', async () => {
    const wrapper = mount(Counter)
    
    // Find reactive counter buttons (second set)
    const allButtons = wrapper.findAll('button')
    const reactiveButtons = allButtons.filter((btn, index) => index >= 2 && index <= 3)
    const [reactiveMinusBtn, reactivePlusBtn] = reactiveButtons
    
    // Increment reactive counter
    await reactivePlusBtn.trigger('click')
    
    // Check reactive counter values
    const reactiveCounts = wrapper.findAll('.count')
    expect(reactiveCounts[1].text()).toBe('1')
    expect(wrapper.text()).toContain('Double value: 2')
    expect(wrapper.text()).toContain('History: 1')
    expect(wrapper.text()).toContain('Last action: Incremented reactive counter')
  })

  it('resets all counters when reset button is clicked', async () => {
    const wrapper = mount(Counter)
    
    // First increment some counters
    const allButtons = wrapper.findAll('button')
    const refPlusButton = allButtons[1] // + button for ref
    const reactivePlusButton = allButtons[3] // + button for reactive
    
    await refPlusButton.trigger('click')
    await reactivePlusButton.trigger('click')
    
    // Verify counters are not zero
    expect(wrapper.findAll('.count')[0].text()).toBe('1')
    expect(wrapper.findAll('.count')[1].text()).toBe('1')
    
    // Find and click reset button
    const resetButton = wrapper.find('button.btn-warning')
    expect(resetButton.text()).toContain('Reset All')
    
    await resetButton.trigger('click')
    
    // Check all values are reset
    expect(wrapper.findAll('.count')[0].text()).toBe('0')
    expect(wrapper.findAll('.count')[1].text()).toBe('0')
    expect(wrapper.text()).toContain('Total clicks: 0')
    expect(wrapper.text()).toContain('Double value: 0')
    expect(wrapper.text()).toContain('Average: 0')
    expect(wrapper.text()).toContain('Last action: Reset all counters')
  })

  it('calculates computed values correctly', async () => {
    const wrapper = mount(Counter)
    
    // Get buttons
    const allButtons = wrapper.findAll('button')
    const refPlusButton = allButtons[1]
    const reactivePlusButton = allButtons[3]
    
    // Set ref counter to 2
    await refPlusButton.trigger('click')
    await refPlusButton.trigger('click')
    
    // Set reactive counter to 4
    await reactivePlusButton.trigger('click')
    await reactivePlusButton.trigger('click')
    await reactivePlusButton.trigger('click')
    await reactivePlusButton.trigger('click')
    
    // Check computed values
    expect(wrapper.text()).toContain('Double value: 8') // reactive count * 2
    expect(wrapper.text()).toContain('Average: 3') // (2 + 4) / 2
    expect(wrapper.text()).toContain('Total clicks: 8') // ref count (2) + reactive total clicks (6)
  })

  it('has correct button structure and classes', () => {
    const wrapper = mount(Counter)
    
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(5) // 4 counter buttons + 1 reset
    
    // Check first section buttons (ref counter)
    expect(buttons[0].classes()).toContain('btn-secondary') // -
    expect(buttons[1].classes()).toContain('btn-primary')   // +
    
    // Check second section buttons (reactive counter)
    expect(buttons[2].classes()).toContain('btn-secondary') // -
    expect(buttons[3].classes()).toContain('btn-primary')   // +
    
    // Check reset button
    expect(buttons[4].classes()).toContain('btn-warning')
  })
})