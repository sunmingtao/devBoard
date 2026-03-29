import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import HelloWorld from '../HelloWorld.vue'

describe('HelloWorld.vue', () => {
  it('renders props.msg when passed', () => {
    const msg = 'new message'
    const wrapper = mount(HelloWorld, { props: { msg } })
    expect(wrapper.text()).toContain(msg)
  })

  it('renders with default props', () => {
    const wrapper = mount(HelloWorld)
    expect(wrapper.find('h1').exists()).toBe(true)
  })

  it('has correct component structure', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'test' } })
    
    // Check if main elements exist
    expect(wrapper.find('h1').exists()).toBe(true)
    expect(wrapper.find('.card').exists()).toBe(true)
  })

  it('contains documentation links', () => {
    const wrapper = mount(HelloWorld, { props: { msg: 'test' } })
    
    const text = wrapper.text()
    expect(text).toContain('create-vue')
    expect(text).toContain('Vue Docs')
    expect(text).toContain('learn more')
  })
})