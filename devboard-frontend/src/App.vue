<template>
  <div id="app">
    <Navigation />
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script>
  import Navigation from './components/Navigation.vue'

  export default {
    name: 'App',
    components: {
      Navigation,
    },
  }
</script>

<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
  }

  #app {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .main-content {
    flex: 1;
  }

  /* Global button styles */
  .btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    margin: 0.25rem;
    border: none;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 500;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    font-family: inherit;
    font-size: 1rem;
  }

  .btn:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
  }

  /* Responsive design */
  @media (max-width: 768px) {
    .main-content {
      padding: 1rem;
    }
  }

  /* Smooth scrolling */
  html {
    scroll-behavior: smooth;
  }

  /* Focus indicators for accessibility */
  a:focus,
  button:focus {
    outline: 2px solid #667eea;
    outline-offset: 2px;
  }
</style>
