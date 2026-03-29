<template>
  <div class="counter-demo">
    <h3>🧮 Vue 3 Composition API Demo</h3>
    
    <!-- ref counter -->
    <div class="counter-section">
      <h4>Using `ref`</h4>
      <div class="counter">
        <button @click="decrementRef" class="btn btn-secondary">-</button>
        <span class="count">{{ refCounter }}</span>
        <button @click="incrementRef" class="btn btn-primary">+</button>
      </div>
      <p>Current value: {{ refCounter }}</p>
    </div>

    <!-- reactive counter -->
    <div class="counter-section">
      <h4>Using `reactive`</h4>
      <div class="counter">
        <button @click="decrementReactive" class="btn btn-secondary">-</button>
        <span class="count">{{ reactiveState.count }}</span>
        <button @click="incrementReactive" class="btn btn-primary">+</button>
      </div>
      <p>Current value: {{ reactiveState.count }}</p>
      <p>Double value: {{ doubleCount }}</p>
      <p>History: {{ reactiveState.history.join(', ') }}</p>
    </div>

    <!-- Combined example -->
    <div class="counter-section">
      <h4>Combined Example</h4>
      <div class="stats">
        <p><strong>Total clicks:</strong> {{ totalClicks }}</p>
        <p><strong>Average:</strong> {{ averageValue }}</p>
        <p><strong>Last action:</strong> {{ lastAction }}</p>
      </div>
      <button @click="reset" class="btn btn-warning">🔄 Reset All</button>
    </div>
  </div>
</template>

<script>
  import { ref, reactive, computed, watch } from 'vue'

  export default {
    name: 'Counter',
    setup() {
      // Using ref for primitive values
      const refCounter = ref(0)
      const lastAction = ref('None')

      // Using reactive for objects
      const reactiveState = reactive({
        count: 0,
        history: [],
        totalClicks: 0
      })

      // Computed properties
      const doubleCount = computed(() => reactiveState.count * 2)
      
      const totalClicks = computed(() => 
        refCounter.value + reactiveState.totalClicks
      )
      
      const averageValue = computed(() => {
        const total = refCounter.value + reactiveState.count
        return total / 2
      })

      // ref counter methods
      const incrementRef = () => {
        refCounter.value++
        lastAction.value = 'Incremented ref counter'
        reactiveState.totalClicks++
      }

      const decrementRef = () => {
        refCounter.value--
        lastAction.value = 'Decremented ref counter'
        reactiveState.totalClicks++
      }

      // reactive counter methods
      const incrementReactive = () => {
        reactiveState.count++
        reactiveState.history.push(reactiveState.count)
        reactiveState.totalClicks++
        lastAction.value = 'Incremented reactive counter'
      }

      const decrementReactive = () => {
        reactiveState.count--
        reactiveState.history.push(reactiveState.count)
        reactiveState.totalClicks++
        lastAction.value = 'Decremented reactive counter'
      }

      // Reset function
      const reset = () => {
        refCounter.value = 0
        reactiveState.count = 0
        reactiveState.history = []
        reactiveState.totalClicks = 0
        lastAction.value = 'Reset all counters'
      }

      // Watchers to demonstrate reactivity
      watch(refCounter, (newValue, oldValue) => {
        console.log(`ref counter changed from ${oldValue} to ${newValue}`)
      })

      watch(
        () => reactiveState.count,
        (newValue, oldValue) => {
          console.log(`reactive counter changed from ${oldValue} to ${newValue}`)
        }
      )

      return {
        // ref values
        refCounter,
        lastAction,
        
        // reactive object
        reactiveState,
        
        // computed values
        doubleCount,
        totalClicks,
        averageValue,
        
        // methods
        incrementRef,
        decrementRef,
        incrementReactive,
        decrementReactive,
        reset
      }
    }
  }
</script>

<style scoped>
  .counter-demo {
    background: white;
    border-radius: 0.5rem;
    padding: 2rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin: 2rem 0;
  }

  .counter-demo h3 {
    margin: 0 0 2rem 0;
    color: #333;
    text-align: center;
  }

  .counter-section {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 0.5rem;
    border-left: 4px solid #667eea;
  }

  .counter-section h4 {
    margin: 0 0 1rem 0;
    color: #667eea;
    font-size: 1.25rem;
  }

  .counter {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .count {
    font-size: 2rem;
    font-weight: bold;
    color: #333;
    min-width: 3rem;
    text-align: center;
    background: white;
    padding: 0.5rem 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  .btn {
    padding: 0.5rem 1rem;
    border: none;
    border-radius: 0.5rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 1.25rem;
    min-width: 3rem;
  }

  .btn-primary {
    background-color: #667eea;
    color: white;
  }

  .btn-primary:hover {
    background-color: #5a67d8;
  }

  .btn-secondary {
    background-color: #6b7280;
    color: white;
  }

  .btn-secondary:hover {
    background-color: #4b5563;
  }

  .btn-warning {
    background-color: #f59e0b;
    color: white;
  }

  .btn-warning:hover {
    background-color: #d97706;
  }

  .stats {
    background: white;
    padding: 1rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
  }

  .stats p {
    margin: 0.5rem 0;
    color: #333;
  }

  .counter-section p {
    margin: 0.5rem 0;
    color: #666;
  }
</style>