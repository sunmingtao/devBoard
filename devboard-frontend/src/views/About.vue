<template>
  <div class="about">
    <div class="container">
      <h1>About DevBoard</h1>

      <section class="intro">
        <p>
          DevBoard is a modern task management system designed specifically for
          developers. It combines the simplicity of a Kanban board with powerful
          features to help you manage your development workflow effectively.
        </p>
      </section>

      <section class="tech-stack">
        <h2>Technology Stack</h2>
        <div class="tech-grid">
          <div class="tech-item">
            <h3>Frontend</h3>
            <ul>
              <li>Vue 3 with Composition API</li>
              <li>Vue Router 4</li>
              <li>Vite (Build Tool)</li>
              <li>ESLint + Prettier</li>
            </ul>
          </div>
          <div class="tech-item">
            <h3>Backend</h3>
            <ul>
              <li>Spring Boot 3.3.0</li>
              <li>Java 21</li>
              <li>Spring Data JPA</li>
              <li>RESTful API</li>
            </ul>
          </div>
          <div class="tech-item">
            <h3>Database</h3>
            <ul>
              <li>MySQL 8.0 (Production)</li>
              <li>H2 (Development)</li>
              <li>Docker Compose</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="features">
        <h2>Key Features</h2>
        <div class="feature-list">
          <div class="feature">
            <h3>Task Management</h3>
            <p>
              Create, update, delete, and organize tasks with priorities and
              statuses.
            </p>
          </div>
          <div class="feature">
            <h3>Kanban Board</h3>
            <p>
              Visual workflow with drag-and-drop functionality for task
              organization.
            </p>
          </div>
          <div class="feature">
            <h3>Priority System</h3>
            <p>Organize tasks by priority levels: Low, Medium, High.</p>
          </div>
          <div class="feature">
            <h3>Status Tracking</h3>
            <p>
              Track progress with Todo, In Progress, and Done status columns.
            </p>
          </div>
        </div>
      </section>

      <section class="navigation">
        <h2>Get Started</h2>
        <div class="nav-actions">
          <router-link to="/" class="btn btn-secondary">
            ← Back to Home
          </router-link>
          <router-link to="/tasks" class="btn btn-primary">
            View Task Board →
          </router-link>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
  export default {
    name: 'About',
  }
</script>

<style scoped>
  .about {
    min-height: 100vh;
    padding: 2rem;
    background-color: #f8f9fa;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
  }

  h1 {
    font-size: 3rem;
    text-align: center;
    margin-bottom: 2rem;
    color: #333;
  }

  section {
    margin-bottom: 3rem;
    background: white;
    padding: 2rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .intro p {
    font-size: 1.25rem;
    line-height: 1.6;
    color: #555;
    text-align: center;
  }

  .tech-stack h2,
  .features h2,
  .navigation h2 {
    font-size: 2rem;
    margin-bottom: 1.5rem;
    color: #333;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
  }

  .tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
  }

  .tech-item {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 0.5rem;
    border-left: 4px solid #667eea;
  }

  .tech-item h3 {
    margin-bottom: 1rem;
    color: #333;
    font-size: 1.25rem;
  }

  .tech-item ul {
    list-style: none;
    padding: 0;
  }

  .tech-item li {
    padding: 0.25rem 0;
    color: #666;
    position: relative;
    padding-left: 1rem;
  }

  .tech-item li::before {
    content: '✓';
    position: absolute;
    left: 0;
    color: #667eea;
    font-weight: bold;
  }

  .feature-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
  }

  .feature {
    padding: 1.5rem;
    border: 1px solid #e1e5e9;
    border-radius: 0.5rem;
    background-color: #f8f9fa;
  }

  .feature h3 {
    margin-bottom: 0.5rem;
    color: #333;
  }

  .feature p {
    color: #666;
    line-height: 1.5;
  }

  .nav-actions {
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
    background-color: #667eea;
    color: white;
    border: 2px solid #667eea;
  }

  .btn-primary:hover {
    background-color: #5a67d8;
    border-color: #5a67d8;
  }

  .btn-secondary {
    background-color: transparent;
    color: #667eea;
    border: 2px solid #667eea;
  }

  .btn-secondary:hover {
    background-color: #667eea;
    color: white;
  }
</style>
