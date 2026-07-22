# Fintech Analytics Frontend Foundation

This is a professional enterprise dashboard built to interface with the FastAPI backend of the Fintech Analytics Platform.

## Architecture

Built with:
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS & shadcn/ui
- **Data Fetching**: TanStack React Query + Axios
- **Icons**: Lucide React
- **Theming**: next-themes (Dark mode natively supported)

## Folder Structure

```text
frontend/
├── app/                  # Next.js App Router definitions and Layouts
├── components/           
│   ├── charts/           # Reusable Recharts wrappers
│   ├── layout/           # Navbar, Sidebar, PageContainer
│   ├── providers/        # React Query and Theme Providers
│   └── ui/               # shadcn/ui and basic primitive states
├── lib/                  
│   ├── api/              # Axios configuration (client.ts)
│   ├── hooks/            # TanStack React Query hooks
│   ├── services/         # API abstraction layer
│   └── utils/            # Tailwind merge and formatting utilities
├── public/               # Static assets
└── types/                # Global TypeScript definitions
```

## API Integration

The frontend connects directly to the FastAPI backend using Axios and TanStack Query. 

1. **`lib/api/client.ts`**: Configures the base URL from `process.env.NEXT_PUBLIC_API_URL` (defaulting to `http://localhost:8000`) and handles global interceptors.
2. **`lib/services/*.ts`**: Contains functions that execute the raw HTTP calls (e.g. `DashboardService.getDashboardStats()`).
3. **`lib/hooks/*.ts`**: Contains custom React Query hooks (e.g. `useDashboardStats()`) that provide caching, refetching, and state management.

## Installation & Running Locally

1. Ensure the backend FastAPI server is running on `localhost:8000`.
2. Inside the `frontend/` directory, install the dependencies:
   ```bash
   npm install
   ```
3. Set your environment variables (copy `.env.example` to `.env.local`).
4. Start the development server:
   ```bash
   npm run dev
   ```

Open `http://localhost:3000` in your browser. The frontend is fully decoupled, meaning it requires the backend to be running to fetch actual telemetry and data.
