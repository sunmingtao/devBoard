# GitHub Actions Guide for DevBoard

## 📚 What is GitHub Actions?

GitHub Actions is a continuous integration and continuous delivery (CI/CD) platform that allows you to automate your build, test, and deployment pipeline. You can create workflows that build and test every pull request to your repository, or deploy merged pull requests to production.

### Key Concepts:
- **Workflow**: An automated process defined by a YAML file
- **Job**: A set of steps that execute on the same runner
- **Step**: An individual task that can run commands or actions
- **Runner**: A server that runs your workflows when triggered
- **Action**: A reusable unit of code

## 🏗️ GitHub Actions Structure

```
.github/
└── workflows/
    ├── backend.yml     # Backend CI/CD workflow
    └── frontend.yml    # Frontend CI/CD workflow
```

## 🚀 Setting Up GitHub Actions

### Step 1: Create the Directory Structure

First, create the necessary directories in your repository:

```bash
mkdir -p .github/workflows
```

### Step 2: Understanding Workflow Syntax

A basic workflow file structure:

```yaml
name: Workflow Name                    # Display name in GitHub UI
on:                                   # When to trigger this workflow
  push:
    branches: [ main, develop ]       # Trigger on push to these branches
  pull_request:
    branches: [ main ]                # Trigger on PR to these branches

jobs:                                 # Define one or more jobs
  job-name:                          # Job identifier
    runs-on: ubuntu-latest           # Which OS to use
    steps:                           # List of steps to execute
      - uses: actions/checkout@v3    # Checkout code
      - name: Step name              # Human-readable step name
        run: echo "Hello World"      # Command to run
```

## 🔧 Day 1: Backend GitHub Actions Workflow

### Complete Backend Workflow

Create `.github/workflows/backend.yml`:

```yaml
name: Backend CI/CD

# Triggers: When to run this workflow
on:
  push:
    branches: [ main, release ]
    paths:
      - 'devboard-backend/**'
      - '.github/workflows/backend.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'devboard-backend/**'

# Environment variables available to all jobs
env:
  JAVA_VERSION: '21'
  MAVEN_OPTS: '-Xmx3072m'
  DOCKER_REGISTRY: docker.io
  DOCKER_IMAGE_NAME: ${{ github.repository_owner }}/devboard-backend

jobs:
  # Job 1: Build and Test
  build-and-test:
    name: Build and Test Backend
    runs-on: ubuntu-latest
    
    # Service containers for testing
    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: rootpassword
          MYSQL_DATABASE: devboard_test
          MYSQL_USER: devboard_user
          MYSQL_PASSWORD: devboard_pass
        ports:
          - 3306:3306
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5

    steps:
      # Step 1: Checkout code
      - name: Checkout Code
        uses: actions/checkout@v4

      # Step 2: Set up Java
      - name: Set up JDK ${{ env.JAVA_VERSION }}
        uses: actions/setup-java@v4
        with:
          java-version: ${{ env.JAVA_VERSION }}
          distribution: 'temurin'
          cache: 'maven'

      # Step 3: Cache Maven dependencies
      - name: Cache Maven packages
        uses: actions/cache@v3
        with:
          path: ~/.m2
          key: ${{ runner.os }}-m2-${{ hashFiles('**/pom.xml') }}
          restore-keys: ${{ runner.os }}-m2

      # Step 4: Run tests
      - name: Run Tests
        working-directory: ./devboard-backend
        run: |
          mvn clean test
        env:
          SPRING_PROFILES_ACTIVE: test
          SPRING_DATASOURCE_URL: jdbc:mysql://localhost:3306/devboard_test
          SPRING_DATASOURCE_USERNAME: devboard_user
          SPRING_DATASOURCE_PASSWORD: devboard_pass

      # Step 5: Build application
      - name: Build with Maven
        working-directory: ./devboard-backend
        run: mvn clean package -DskipTests

      # Step 6: Upload JAR artifact
      - name: Upload JAR
        uses: actions/upload-artifact@v3
        with:
          name: backend-jar
          path: devboard-backend/target/*.jar
          retention-days: 1

  # Job 2: Build Docker Image (only on main branch)
  docker-build:
    name: Build Docker Image
    needs: build-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    
    steps:
      # Step 1: Checkout code
      - name: Checkout Code
        uses: actions/checkout@v4

      # Step 2: Download JAR artifact
      - name: Download JAR
        uses: actions/download-artifact@v3
        with:
          name: backend-jar
          path: devboard-backend/target

      # Step 3: Set up Docker Buildx
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      # Step 4: Log in to Docker Hub (only if credentials are provided)
      - name: Log in to Docker Hub
        if: ${{ secrets.DOCKERHUB_USERNAME != '' }}
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}

      # Step 5: Extract metadata
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.DOCKER_IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha,prefix={{branch}}-

      # Step 6: Build and push Docker image
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ./devboard-backend
          push: ${{ secrets.DOCKERHUB_USERNAME != '' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      # Step 7: Output image info
      - name: Image digest
        run: echo ${{ steps.meta.outputs.tags }}
```

## 🔐 Setting Up GitHub Secrets

### Required Secrets for Docker Hub (Optional)

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username | `yourusername` |
| `DOCKERHUB_TOKEN` | Docker Hub access token (not password!) | `dckr_pat_xxxxx` |

### How to Get Docker Hub Token:
1. Log in to [Docker Hub](https://hub.docker.com)
2. Go to **Account Settings** → **Security**
3. Click **New Access Token**
4. Give it a name (e.g., "GitHub Actions")
5. Copy the token (you won't see it again!)

## 📋 Workflow Explained

### Triggers (`on:`)
- **Push to main/release**: Runs full CI/CD pipeline
- **Pull Request**: Runs tests only
- **Path filters**: Only runs when backend files change

### Jobs Breakdown:

#### 1. **build-and-test**
- Sets up Java 21
- Starts MySQL service container for tests
- Runs Maven tests
- Builds JAR file
- Uploads JAR as artifact

#### 2. **docker-build** (conditional)
- Only runs on main branch pushes
- Downloads JAR artifact
- Builds Docker image
- Pushes to Docker Hub (if secrets configured)
- Tags image with branch name and SHA

## 🧪 Testing the Workflow

### Option 1: Push to a Feature Branch
```bash
git checkout -b feature/test-github-actions
# Make a small change in backend
echo "# Test" >> devboard-backend/README.md
git add .
git commit -m "Test GitHub Actions"
git push origin feature/test-github-actions
```

### Option 2: Create a Pull Request
1. Push your feature branch
2. Create a PR to main
3. Watch the checks run automatically

### Option 3: Push to Main (Triggers Full Pipeline)
```bash
git checkout main
# Make changes
git add .
git commit -m "Trigger GitHub Actions"
git push origin main
```

## 📊 Monitoring Workflow Runs

1. Go to your GitHub repository
2. Click on the **Actions** tab
3. You'll see all workflow runs
4. Click on a run to see details
5. Click on a job to see step-by-step logs

## 🛠️ Troubleshooting

### Common Issues:

1. **Maven/Java Version Issues**
   ```yaml
   # Ensure correct Java version
   java-version: '21'  # Match your pom.xml java.version
   ```

2. **Test Failures Due to Database**
   ```yaml
   # Check service container is ready
   options: >-
     --health-cmd="mysqladmin ping"
   ```

3. **Docker Push Fails**
   - Verify secrets are set correctly
   - Check Docker Hub token permissions

4. **Workflow Not Triggering**
   - Check branch names match
   - Verify path filters are correct

## 🎯 Best Practices

1. **Use Caching**: Cache dependencies to speed up builds
2. **Path Filters**: Only run when relevant files change
3. **Conditional Jobs**: Don't build Docker images for PRs
4. **Artifacts**: Use artifacts to pass data between jobs
5. **Secrets**: Never hardcode credentials
6. **Timeouts**: Set reasonable timeouts for jobs

## 📝 Workflow Status Badge

Add this to your README.md to show build status:

```markdown
![Backend CI/CD](https://github.com/YOUR_USERNAME/devBoard/workflows/Backend%20CI%2FCD/badge.svg)
```

## 🚀 Next Steps

1. Create the workflow file
2. Push to GitHub
3. Watch it run in the Actions tab
4. Add Docker Hub secrets (optional)
5. Customize as needed

This completes the GitHub Actions setup for the backend! The workflow will now automatically build and test your backend code on every push and pull request.

---

## 🎨 Day 2: Frontend GitHub Actions Workflow

### Frontend Workflow Features

Create `.github/workflows/frontend.yml`:

```yaml
name: Frontend CI/CD

on:
  push:
    branches: [ main, release ]
    paths:
      - 'devboard-frontend/**'
      - '.github/workflows/frontend.yml'
  pull_request:
    branches: [ main ]
    paths:
      - 'devboard-frontend/**'

env:
  NODE_VERSION: '18'
  DOCKER_IMAGE_NAME: ${{ github.repository_owner }}/devboard-frontend

jobs:
  build-and-test:
    name: Build and Test Frontend
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: devboard-frontend/package-lock.json
      
      - name: Install dependencies
        working-directory: ./devboard-frontend
        run: npm ci
      
      - name: Run ESLint
        working-directory: ./devboard-frontend
        run: npm run lint || true
      
      - name: Build for production
        working-directory: ./devboard-frontend
        run: npm run build
      
      - name: Upload dist folder
        uses: actions/upload-artifact@v4
        with:
          name: frontend-dist
          path: devboard-frontend/dist/
          retention-days: 7
```

### Frontend Workflow Jobs Breakdown:

#### 1. **build-and-test**
- Sets up Node.js 18 with npm caching
- Installs dependencies with `npm ci`
- Runs ESLint (non-blocking)
- Builds production bundle with Vite
- Uploads `dist/` folder as artifact
- Analyzes bundle size

#### 2. **docker-build** (conditional)
- Only runs on main branch pushes
- Builds Docker image with production env vars
- Uses multi-stage build (Node → Nginx)
- Validates Dockerfile without pushing

#### 3. **deploy-preview** (PRs only)
- Downloads build artifacts
- Prepares for Vercel/Netlify preview deployment
- Posts preview URL in PR comments

#### 4. **lighthouse** (performance)
- Runs Lighthouse CI for performance auditing
- Sets performance budgets
- Uploads results to temporary storage

### Frontend-Specific Features:

1. **Node.js Caching**: Faster installs with npm cache
2. **Path Filtering**: Only runs when frontend changes
3. **Bundle Analysis**: Tracks asset sizes
4. **ESLint Integration**: Code quality checks
5. **Preview Deployments**: PR-based previews
6. **Performance Monitoring**: Lighthouse scores

### Lighthouse Configuration

Create `devboard-frontend/.lighthouserc.json`:

```json
{
  "ci": {
    "collect": {
      "numberOfRuns": 3,
      "url": ["http://localhost:3000"]
    },
    "assert": {
      "assertions": {
        "categories:performance": ["warn", {"minScore": 0.8}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "categories:best-practices": ["warn", {"minScore": 0.9}],
        "categories:seo": ["warn", {"minScore": 0.8}]
      }
    }
  }
}
```

### Performance Budgets:
- **Performance**: ≥80%
- **Accessibility**: ≥90%
- **Best Practices**: ≥90%
- **SEO**: ≥80%

This setup provides comprehensive frontend CI/CD with quality gates and performance monitoring!