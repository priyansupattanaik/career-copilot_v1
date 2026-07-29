# Career Copilot UI

Career Copilot is a frontend-only, evidence-led career preparation workspace built with Next.js App Router, TypeScript, Tailwind CSS, Motion, React Three Fiber, Recharts, React Hook Form, and Zod.

The demo connects candidate profile, resume analysis, extraction review, ATS evidence, resume improvement, mock interviews, learning paths, job recommendations, and privacy/settings state. It does not claim that a real ATS, AI evaluator, job feed, OAuth service, or biometric system is connected.

## Run the project

On the first run, install the dependencies:

```text
npm install
```

Then start the development server:

```text
npm run dev
```

Open `http://localhost:3000` in your browser.

For later runs, only `npm run dev` is required unless the dependencies change.

## Validation

```text
npm run check
npm run test:e2e
```

Playwright browsers may need to be installed once with `npx playwright install chromium`.

## Demo data

State is stored through one guarded, versioned local-storage adapter. Use Settings → Privacy → Clear stored demo data to reset the experience.
