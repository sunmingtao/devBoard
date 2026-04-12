# DevBoard Frontend

Vue 3 + Vite frontend for the DevBoard task management system.

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- npm 10+

### Install Dependencies
```bash
cd apps/frontend
npm install
```

### Run Locally
```bash
npm run dev
```

Frontend runs at `http://localhost:5173` by default.

> To connect with local backend, ensure `VITE_API_URL` points to your backend API (for example `http://localhost:8080`).

## 📦 Available Scripts

```bash
npm run dev            # Start Vite dev server
npm run build          # Production build
npm run build:dev      # Development-mode build
npm run preview        # Preview production build locally
npm run lint           # Lint source files
npm run lint:fix       # Lint and auto-fix
npm run format         # Format src/ with Prettier
npm run format:check   # Check formatting
npm run test           # Run tests in watch mode
npm run test:run       # Run tests once
npm run test:coverage  # Run tests with coverage
npm run test:ui        # Run Vitest UI
```

## 🧱 Tech Stack
- Vue 3
- Vue Router
- Axios
- Vite
- Vitest + Testing Library
- ESLint + Prettier

## 📁 Project Structure

```text
apps/frontend/
├── src/
│   ├── components/    # Reusable UI components
│   ├── views/         # Route-level pages
│   ├── router/        # Router configuration
│   ├── services/      # API and service modules
│   └── tests/         # Unit/component tests
├── public/            # Static assets
└── vite.config.js     # Vite config
```

## 🔧 Environment Variables

Use `.env.local` (not committed) for local overrides.

Common variables:

```bash
VITE_API_URL=http://localhost:8080
```

You can copy from `.env.local.example` as a starting point.

## 🐳 Docker

```bash
# Build image
cd apps/frontend
docker build -t devboard-frontend .

# Run container
docker run -p 80:80 devboard-frontend
```

## ✅ Development Notes
- Keep components small and composable.
- Prefer service modules for API calls over in-component request logic.
- Add/update tests when changing behavior.
