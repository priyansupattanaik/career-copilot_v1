# Career Copilot

Career Copilot is a Next.js application backed by Supabase Auth, PostgreSQL, private Storage buckets, and a Python FastAPI service. Browser storage and seeded candidate records are not used as application state.

## First run

Install JavaScript and Python dependencies with one command:

```powershell
npm install
```

Copy `.env.example` to `.env.local` and `backend/.env.example` to `backend/.env`. Add newly rotated Supabase values; never reuse credentials posted in chat or commit either environment file. Apply the SQL migration in `supabase/migrations` to the intended Supabase project.

Start the frontend and backend together:

```powershell
npm run dev
```

Open `http://localhost:3000`. The API runs at `http://127.0.0.1:8000`, with development docs at `/docs`.

## Other commands

`npm run dev:frontend` starts only Next.js. `npm run dev:backend` starts only FastAPI. `npm run check` runs the secret scanner and frontend validation. Backend tests run with `backend/.venv/Scripts/python -m pytest backend/tests`.

Supabase migrations, ownership policies, trigger bootstrap, indexes, and private bucket policies live under `supabase/`. A local Supabase stack additionally requires Docker and the Supabase CLI.
