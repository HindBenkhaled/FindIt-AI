# FindIt AI frontend

The consumer-facing React frontend for FindIt AI. It uses the existing FastAPI API for all reports, images and matching. React performs no AI scoring.

## Start locally

Start FastAPI from the repository root in one terminal:

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

Then, from `frontend/` in another terminal:

```powershell
npm install
npm run dev
```

Open http://127.0.0.1:5173. Node.js 20.17 or newer is required. The Vite development server forwards `/api` to `http://127.0.0.1:8000`, so the browser uses the same origin and FastAPI needs no CORS change. Set `API_TARGET` in `frontend/.env.local` to point the development proxy to a different backend. The production build requires a server configured to forward `/api/*` to FastAPI after removing `/api` from the path; the built site alone cannot provide API responses.

The database can be seeded once from the repository root with `.\.venv\Scripts\python.exe -m scripts.seed`. Seeded reports and pictures are synthetic. The first full match may take several minutes to download pretrained models. **Simple matching** works without model downloads.

## Pages and user flow

The primary navigation contains only **Home**, **Report**, and **Explore**.

- `/` — shorter landing page with the two user choices, how it works, and recent found reports.
- `/report` — asks “What happened?” and sends the user into the lost or found form.
- `/report/lost`, `/report/found` — validated forms with optional drag-and-drop photo upload and a clear success state. If a photo upload fails after report creation, the user can retry against the same saved report.
- `/explore` — one section with internal Matches, All reports, Lost, and Found tabs. Matches defaults to full matching and five results. Matching method and result count remain available inside the collapsed **Advanced options** section.

Old `/matches` and `/browse` links redirect to the corresponding Explore view, including selected report and report-type query parameters.

Match scores are similarities, not calibrated probabilities or proof of ownership. Unavailable signals are shown as unavailable. The frontend maps API failures to friendly messages; model errors are never silently replaced with a baseline result.

## Files

`src/pages/` contains the route views and unified Report and Explore entry points. `src/components/` contains reusable cards, images, dialogs and form controls. `src/services/api.ts` is the single HTTP client and `src/types/` mirrors API responses. `src/hooks/useReports.ts` loads paginated reports. `src/styles.css` defines the responsive product styles and Tailwind is available for small layout utilities. `vite.config.ts` defines the API proxy.

## Validation

```powershell
npm run build
npm run test:e2e
npm audit
```

The Playwright suite runs against a live seeded FastAPI backend. It checks desktop and mobile layout, navigation, both report forms, actual image uploads, full AI matching, browsing/filtering, deletion confirmation, failed-photo retry without duplicate creation, friendly errors, missing-photo behavior, and WCAG A/AA automated checks on the main pages and result cards. Browser tests create temporary reports and delete them afterward. Playwright writes screenshots and failure traces to a unique directory under the system temporary directory, avoiding sync locks in OneDrive. For a fresh machine, run `npx playwright install chromium` once.
