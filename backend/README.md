# Career Copilot API

The FastAPI service validates the Supabase access token on every protected request and performs database and storage operations using that user's JWT. A server secret is optional and is reserved for explicit administrative operations.

Copy `.env.example` to `.env`, provide newly rotated Supabase values, create a virtual environment, and install the package with `pip install -e ".[dev]"`. From the repository root, run `npm run dev:backend`.

Interactive API documentation is available at `http://127.0.0.1:8000/docs` outside production.
