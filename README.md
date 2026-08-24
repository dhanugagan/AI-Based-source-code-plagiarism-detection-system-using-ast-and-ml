# CodeGuard — AI-Based Source Code Plagiarism Detection System

A full-stack web application that detects source-code plagiarism by analyzing the
**structural** similarity of programs using Abstract Syntax Trees (AST), token
comparison, structural feature vectors, and a machine-learning similarity model —
not simple text diffing. It catches plagiarism even when variable names, function
names, comments, formatting, or whitespace have been changed.

```
Upload → Parse (AST) → Normalize → Extract Features → Compare
       → ML Prediction → Weighted Final Score → Risk Classification → Report
```

---

## What's included

- **Backend** — FastAPI + SQLAlchemy, JWT auth, REST API, AST engine, ML engine
  (Random Forest, scikit-learn), PDF report generation (ReportLab)
- **Frontend** — React + Vite + Tailwind CSS, Monaco code editor, dashboards,
  drag-and-drop upload, similarity gauge, admin panel, batch/assignment mode
  with a live pairwise similarity matrix
- **Dataset** — a generated sample dataset of labeled code pairs
  (`dataset/code_pairs_dataset.csv`) covering renamed-variable, reformatted,
  modified, and different-algorithm cases
- **Trained model** — a Random Forest model is pre-trained and included at
  `models/plagiarism_model.joblib` (the backend will also train one
  automatically on first run if this file is missing)
- **Diagrams** — system architecture, use-case, ER, data-flow, and sequence
  diagrams, rendered as PNGs in `docs/diagrams/` (Mermaid sources included)
- **Deployment** — Dockerfiles for backend and frontend, `docker-compose.yml`
  wiring up MySQL + backend + frontend + nginx
- **Tests** — `backend/tests/` covers the AST engine and the core API flows

## What was verified in this environment

This sandbox has **no network access**, so `npm install`, a full `pip install`,
and `docker compose up` could not be run here. What *was* verified:

- Every backend Python file passes `py_compile` (no syntax errors)
- Every frontend JSX/JS file passes a TypeScript-based syntax check (no syntax errors)
- The **AST engine** (parsing, normalization, feature extraction, all four
  similarity measures) was executed directly and its unit tests pass
- The **ML pipeline** (dataset generation → feature extraction → Random Forest
  training with a group-aware train/test split) was executed end-to-end and
  achieved strong held-out metrics on the sample dataset
- The **full comparison pipeline** was run on real examples: a renamed-variable
  pair scored 100% similarity / "Very High" risk, while a genuinely different
  algorithm solving the same problem scored 37% / "Medium" — the intended behavior
- The **batch/assignment-mode matrix logic** was run directly on four sample
  programs and produced a correct symmetric similarity matrix
- **PDF report generation** was run directly and produces a valid PDF
- The **architecture/use-case/ER/data-flow/sequence diagrams** were rendered
  from their Mermaid sources to actual PNG images (not just text)
- `docker-compose.yml` and both Dockerfiles were written and the compose file
  was YAML-validated; no Docker daemon was available to actually build/run them

Because FastAPI, SQLAlchemy, the frontend's npm packages, and Docker itself
could not be installed/run here, the live API server, the built frontend, and
the containerized stack were not exercised end-to-end. **The first thing to do
after downloading this project is to run the install steps below on a machine
with internet access** and confirm `pytest`, `npm run dev`, and (optionally)
`docker compose up --build` all work — the code has been written and
syntax-verified carefully, but that final integration step needs a normal
network connection.

---

## Quick start

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # already has sane defaults for local dev
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`, with interactive docs at
`http://localhost:8000/docs`. On first run it will:
- create the SQLite database (`backend/plagiarism.db`)
- train the ML model automatically if `models/plagiarism_model.joblib` doesn't
  already exist (it does — it's included — so this is instant)

Run the test suite:

```bash
cd backend
pip install pytest
pytest tests/ -v
```

**The first registered user automatically becomes an admin** (convenience for
local development — promote additional admins directly in the database for a
real deployment).

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env             # points at http://localhost:8000 by default
npm run dev
```

Open `http://localhost:5173`.

### 3. Try it out

1. Register an account (you'll be admin, since you're first).
2. Go to **Upload**, and upload two or more `.py` files — try the same logic
   with different variable names to see a high similarity score, or two
   unrelated programs to see a low one.
3. Go to **Compare**, select two files, and click **Analyze Plagiarism**.
4. On the **Result** page, review the score breakdown and detected structures,
   and download a PDF report.
5. Go to **Batch** (Assignment Mode) with 3+ submissions to generate a full
   pairwise plagiarism matrix in one click — the same workflow a teacher would
   use to check an entire assignment at once.
6. Visit **Admin** to see system-wide statistics and high-risk cases.

### 4. Run with Docker (optional)

A full containerized stack — MySQL, backend, and frontend behind nginx — is
included:

```bash
cp .env.example .env    # set real secrets before any real deployment
docker compose up --build
```

Frontend: `http://localhost:5173` · Backend: `http://localhost:8000`

This wasn't build-tested in the sandbox that produced this project (no Docker
daemon available) — please build it once locally before relying on it.

---

## Database: SQLite by default, MySQL-ready

The original spec calls for MySQL. This reference implementation defaults to
**SQLite** for local development (zero external setup), and ships with a
**MySQL-backed Docker Compose stack** for a production-style deployment (see
above). To point a non-Docker backend at MySQL directly:

```bash
pip install PyMySQL   # already in requirements.txt
```

```env
# backend/.env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/plagiarism_db
```

The SQLAlchemy models are portable between both engines with no code changes.

---

## Project structure

```
ai-code-plagiarism-detector/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, CORS, centralized error handling
│   │   ├── config.py             # env-driven settings (weights, thresholds, secrets)
│   │   ├── database.py           # SQLAlchemy engine/session
│   │   ├── models/                # User, Submission, Comparison, Report
│   │   ├── schemas/                # Pydantic request/response models
│   │   ├── routes/                 # auth, users, submissions, comparisons, batch, reports, dashboard, admin
│   │   ├── services/               # auth_service (JWT deps), file_service, comparison_service
│   │   ├── utils/                  # security (JWT/hashing), rate_limit (abuse protection)
│   │   ├── ast_engine/
│   │   │   ├── parser.py          # ast.parse wrapper, never executes source
│   │   │   ├── normalizer.py      # identifier normalization, structure serialization
│   │   │   ├── features.py        # 12 structural features
│   │   │   └── similarity.py      # AST / token / cosine / tree-edit-distance similarity
│   │   ├── ml/
│   │   │   ├── dataset_generator.py  # synthetic labeled code-pair dataset
│   │   │   ├── preprocessing.py      # code pair → feature vector
│   │   │   ├── train.py              # Random Forest / LogReg / SVM, group-aware split
│   │   │   └── predict.py            # lazy-loads/trains model, predicts 0-100 score
│   │   └── report/
│   │       └── pdf_generator.py   # ReportLab PDF report
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/                 # Landing, Login, Register, Dashboard, Upload, Compare, Batch, Result, History, AdminDashboard
│   │   ├── components/            # Navbar, ProtectedRoute, SimilarityGauge, ASTHeroVisual, LoadingSpinner
│   │   ├── context/AuthContext.jsx
│   │   └── services/api.js        # axios client + JWT interceptor
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── dataset/
│   └── code_pairs_dataset.csv     # sample generated training data
├── models/
│   └── plagiarism_model.joblib    # pre-trained Random Forest
├── uploads/                        # uploaded source files land here at runtime
├── reports/                        # generated PDF reports land here at runtime
├── docs/
│   ├── README.md                  # diagram index
│   └── diagrams/                  # architecture, use-case, ER, data-flow, sequence (.mmd + .png)
└── docker-compose.yml              # MySQL + backend + frontend/nginx stack
```

---

## How detection works

1. **Parse** — Python source is parsed with the standard library `ast` module.
   Source code is **never executed**, only statically analyzed.
2. **Normalize** — variable and function identifiers are replaced with
   positional placeholders (`VAR1`, `FUNC1`, ...) so renaming has minimal
   effect on the comparison; formatting, comments, and whitespace never enter
   the AST in the first place.
3. **Extract features** — 12 numeric structural features per program: node
   count, max depth, function/loop/conditional counts, variable count,
   operator count, function calls, returns, classes, imports.
4. **Compare** using four techniques, each normalized to 0–100:
   - **AST structural similarity** — sequence match over normalized structure
   - **Token similarity** — sequence match over normalized token stream
   - **Structural (cosine) similarity** — cosine similarity of feature vectors
   - **Tree edit distance similarity** — Levenshtein-style edit distance over
     bounded normalized node sequences (a tractable proxy for full
     Zhang–Shasha tree edit distance, sufficient for typical academic-sized
     submissions)
5. **ML prediction** — a Random Forest classifier trained on labeled code-pair
   examples (renamed / reformatted / modified / different-algorithm / unrelated)
   predicts a plagiarism-likelihood score from the combined feature vector.
6. **Final score** — a configurable weighted sum (defaults: AST 40%, Token 20%,
   Structural 20%, ML 20%), stored as settings, not hard-coded assumptions.
7. **Risk classification** — configurable thresholds: Low (0–30), Medium
   (31–60), High (61–80), Very High (81–100).

**Important:** the final score indicates *structural similarity*. It's an
indicator to support human review, not definitive proof of academic
misconduct — the API, PDF reports, and UI all say so explicitly.

### Batch comparison / Assignment mode

`POST /api/comparisons/batch` accepts 3+ submission IDs and returns the full
pairwise similarity matrix in one call — exactly the "teacher uploads an
assignment, system generates a plagiarism matrix" workflow from the spec.
Every pair is scored with the same `comparison_service` pipeline as a single
analysis and persisted as a normal `Comparison` row, so batch results also
show up in history, the dashboard, and the admin high-risk view. The frontend
**Batch** page renders this as a color-coded matrix plus a sorted high-risk
pairs list.

### Avoiding data leakage

The ML training split is **group-aware**: all transformed variants of the same
base program (renamed, reformatted, modified versions of one canonical
solution) are kept together on the same side of the train/test split, so the
model is never evaluated on a near-duplicate of something it trained on.

---

## Security

- Passwords hashed with bcrypt (passlib)
- JWT authentication (python-jose), configurable expiry
- Role-based authorization (student / admin) enforced server-side
- Uploaded files are validated by extension, size, UTF-8 decodability, and
  **must successfully parse as valid source code** before being stored
- Stored filenames are randomized (never trust user-supplied names for storage)
- Uploaded source code is parsed for analysis only — **it is never executed**
- CORS origins, secrets, and DB credentials are all environment-variable driven
  (see `backend/.env.example`) — nothing sensitive is hard-coded
- Fixed-window rate limiting middleware (`app/utils/rate_limit.py`) protects
  every endpoint except health checks; swap for `slowapi` + Redis in a
  multi-worker production deployment
- Centralized exception handling ensures internal stack traces are never
  returned to clients

## Extending the system

- **More languages**: `ast_engine/parser.py` has a `PARSERS` registry keyed by
  language name — plug in a Java/C/C++/JavaScript parser without touching
  call sites. `file_service.ALLOWED_EXTENSIONS` maps extensions to languages.
- **More ML models**: `ml/train.py` already trains and evaluates Random Forest,
  Logistic Regression, and SVM side by side; swap which one is selected as
  primary, or add more candidates to the `candidates` dict.
- **Batch / assignment mode**: the `/api/comparisons/analyze` endpoint compares
  one pair at a time; a batch endpoint can loop over all pairs in a submission
  set and assemble a similarity matrix using the same `comparison_service`.

---

## Known limitations of this reference implementation

- Only Python source is supported out of the box (architecture supports more,
  see above)
- Tree edit distance uses a bounded Levenshtein-style approximation rather
  than full Zhang–Shasha, for tractability on typical submission sizes
- The included ML model is trained on a small synthetic dataset generated
  from eight base problems — suitable as a working reference/demo, but a
  real deployment should train on a larger, more diverse labeled dataset
  before being trusted for high-stakes decisions
- Frontend and backend were not run together end-to-end in the environment
  that produced this project (no network access for `npm install` /
  `pip install`) — see "What was verified" above
