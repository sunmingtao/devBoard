<template>
  <div class="home">
    <header class="hero">
      <p class="hero-badge">DevOps Portfolio Project</p>
      <h1 v-if="isAuthenticated">Welcome back, {{ username }} 👋</h1>
      <h1 v-else>DevBoard: From Code to Cloud</h1>
      <p class="hero-subtitle">
        A full-stack platform showcasing CI/CD, Kubernetes, Terraform, and AWS
        delivery practices.
      </p>
      <div class="hero-pills">
        <span>Vue 3 + Vite</span>
        <span>Spring Boot 3.3</span>
        <span>Jenkins CI/CD</span>
        <span>Terraform IaC</span>
        <span>AWS EKS + RDS</span>
      </div>
      <div class="hero-actions">
        <router-link v-if="isAuthenticated" to="/tasks" class="btn btn-primary">
          View Your Tasks
        </router-link>
        <router-link v-else to="/login" class="btn btn-primary">
          Explore the Demo
        </router-link>
        <router-link to="/about" class="btn btn-secondary">
          Architecture Details
        </router-link>
      </div>
    </header>

    <section class="highlights">
      <article class="highlight-card">
        <h3>🚀 End-to-End Delivery</h3>
        <p>
          Build, test, and deploy through Jenkins pipelines with environment
          separation for development and production.
        </p>
      </article>
      <article class="highlight-card">
        <h3>☁️ Cloud-Native Infrastructure</h3>
        <p>
          Provisioned with Terraform and deployed on AWS using EKS, ALB ingress,
          Route 53 DNS, ACM certificates, and RDS in private subnets.
        </p>
      </article>
      <article class="highlight-card">
        <h3>🔒 Production Readiness</h3>
        <p>
          HTTPS by default, secure networking, health checks, monitoring alarms,
          and alerting workflows for operational visibility.
        </p>
      </article>
    </section>

    <section class="roadmap">
      <h2>Recent DevOps Milestones</h2>
      <div class="timeline">
        <div class="timeline-item">
          <p class="timeline-version">v0.6.2 · 2026-04-25</p>
          <p>
            Delivered end-to-end EKS automation with Terraform-managed RDS
            connectivity, dynamic backend DB injection, ALB provisioning via
            Ingress, and Route 53 alias routing.
          </p>
        </div>
        <div class="timeline-item">
          <p class="timeline-version">v0.6.1 · 2026-04-21</p>
          <p>
            Enabled ALB ingress with Route 53 domain routing and ACM-powered
            HTTPS redirection.
          </p>
        </div>
        <div class="timeline-item">
          <p class="timeline-version">v0.6.0 · 2026-04-20</p>
          <p>
            Migrated deployment model to Kubernetes (local Minikube + AWS EKS)
            with environment overlays.
          </p>
        </div>
        <div class="timeline-item">
          <p class="timeline-version">v0.5.x · 2026-04-15 ~ 2026-04-17</p>
          <p>
            Added EventBridge/Lambda scheduling, migrated database to AWS RDS,
            and introduced health monitoring and SNS alerts.
          </p>
        </div>
      </div>
    </section>

    <!-- API Testing Section -->
    <section class="api-test-section">
      <ApiTest />
    </section>

    <section class="features">
      <h2>Application Capabilities</h2>
      <div class="feature-grid">
        <div class="feature-card">
          <h3>🎯 Task Management</h3>
          <p>Create, update, and organize your tasks efficiently</p>
        </div>
        <div class="feature-card">
          <h3>📊 Kanban Board</h3>
          <p>
            Visualize your workflow with Todo, In Progress, and Done columns
          </p>
        </div>
        <div class="feature-card">
          <h3>🚀 Modern Tech Stack</h3>
          <p>Built with Vue 3, Spring Boot, and MySQL</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
  import { ref, onMounted, onUnmounted, watch } from 'vue'
  import { useRoute } from 'vue-router'
  import ApiTest from '../components/ApiTest.vue'
  import { authService } from '../services/authService'

  export default {
    name: 'Home',
    components: {
      ApiTest,
    },
    setup() {
      const route = useRoute()
      const isAuthenticated = ref(authService.isAuthenticated())
      const username = ref('')

      const updateAuthInfo = () => {
        isAuthenticated.value = authService.isAuthenticated()
        if (isAuthenticated.value) {
          const user = authService.getUser()
          username.value = user?.username || ''
        } else {
          username.value = ''
        }
      }

      // Watch for route changes to update auth state
      watch(() => route.path, updateAuthInfo)

      // Listen for storage changes (handles logout from any component)
      const handleStorageChange = (e) => {
        if (e.key === 'token' || e.key === 'user') {
          updateAuthInfo()
        }
      }

      // Also listen for custom logout events
      const handleLogoutEvent = () => {
        updateAuthInfo()
      }

      // Check token expiry and warn user
      const checkTokenExpiry = () => {
        if (!isAuthenticated.value) return
        
        const token = authService.getToken()
        if (authService.isTokenExpiringSoon(token)) {
          const minutesLeft = authService.getTokenExpiryTime(token)
          console.warn(`Token expires in ${minutesLeft} minutes`)
          
          // Dispatch warning event
          window.dispatchEvent(new CustomEvent('auth-error', {
            detail: { 
              status: 'warning', 
              message: `Your session will expire in ${minutesLeft} minute(s). Please save your work.`,
              redirectTo: null
            }
          }))
        }
      }

      // Initialize auth info on mount
      onMounted(() => {
        updateAuthInfo()
        
        // Listen for localStorage changes (works across tabs too)
        window.addEventListener('storage', handleStorageChange)
        
        // Listen for custom logout events from same tab
        window.addEventListener('logout', handleLogoutEvent)
        
        // Check token expiry every minute
        const tokenCheckInterval = setInterval(checkTokenExpiry, 60000)
        
        // Cleanup interval on unmount
        onUnmounted(() => {
          clearInterval(tokenCheckInterval)
        })
      })

      // Cleanup event listeners on unmount
      onUnmounted(() => {
        window.removeEventListener('storage', handleStorageChange)
        window.removeEventListener('logout', handleLogoutEvent)
      })

      return {
        isAuthenticated,
        username
      }
    }
  }
</script>

<style scoped>
  .home {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem 2rem 2rem;
    margin-top: 1rem;
  }

  .hero-badge {
    display: inline-block;
    background: rgba(255, 255, 255, 0.18);
    border: 1px solid rgba(255, 255, 255, 0.3);
    padding: 0.4rem 0.8rem;
    border-radius: 999px;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
  }

  .api-test-section {
    margin-bottom: 3rem;
  }

  .hero {
    text-align: center;
    padding: 4rem 0;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    border-radius: 1rem;
    margin-bottom: 3rem;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  }

  .hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
    font-weight: bold;
  }

  .hero-subtitle {
    font-size: 1.25rem;
    margin: 1rem auto 1.5rem auto;
    opacity: 0.9;
    max-width: 700px;
  }

  .hero-pills {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.75rem;
    margin-bottom: 2rem;
  }

  .hero-pills span {
    background: rgba(255, 255, 255, 0.16);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 0.45rem 0.75rem;
    border-radius: 999px;
    font-size: 0.88rem;
  }

  .hero-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
  }

  .btn {
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s ease;
    display: inline-block;
  }

  .btn-primary {
    background-color: #fff;
    color: #667eea;
    border: 2px solid #fff;
  }

  .btn-primary:hover {
    background-color: transparent;
    color: #fff;
  }

  .btn-secondary {
    background-color: transparent;
    color: #fff;
    border: 2px solid #fff;
  }

  .btn-secondary:hover {
    background-color: #fff;
    color: #667eea;
  }

  .highlights {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1rem;
    margin-bottom: 2.5rem;
  }

  .highlight-card {
    background: #ffffff;
    border: 1px solid #e8eaf2;
    border-radius: 0.8rem;
    padding: 1.2rem;
    box-shadow: 0 8px 20px rgba(15, 23, 42, 0.05);
  }

  .highlight-card h3 {
    margin-bottom: 0.5rem;
    color: #1f2937;
  }

  .highlight-card p {
    color: #475569;
    line-height: 1.6;
  }

  .roadmap {
    margin-bottom: 3rem;
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 1rem;
    padding: 2rem;
  }

  .roadmap h2 {
    margin-bottom: 1rem;
    color: #111827;
  }

  .timeline {
    display: grid;
    gap: 1rem;
  }

  .timeline-item {
    border-left: 4px solid #6366f1;
    background: #f8faff;
    padding: 0.9rem 1rem;
    border-radius: 0.35rem;
  }

  .timeline-version {
    font-weight: 700;
    color: #3730a3;
    margin-bottom: 0.25rem;
  }

  .features {
    text-align: center;
  }

  .features h2 {
    font-size: 2.5rem;
    margin-bottom: 2rem;
    color: #333;
  }

  .feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
  }

  .feature-card {
    padding: 2rem;
    border: 1px solid #e1e5e9;
    border-radius: 0.5rem;
    transition:
      transform 0.3s ease,
      box-shadow 0.3s ease;
  }

  .feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  .feature-card h3 {
    font-size: 1.5rem;
    margin-bottom: 1rem;
    color: #333;
  }

  .feature-card p {
    color: #666;
    line-height: 1.6;
  }

  @media (max-width: 768px) {
    .home {
      padding: 1rem;
    }

    .hero {
      padding: 3rem 1.2rem;
    }

    .hero h1 {
      font-size: 2.1rem;
    }
  }
</style>
