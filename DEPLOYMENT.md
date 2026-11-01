# GigPulse AI — Zero-Budget Deployment Guide (₹0 Infrastructure)

This guide documents the complete zero-cost production deployment procedure for **GigPulse AI** using free-tier cloud infrastructure:
1. **Frontend:** Vercel (Hobby Free Tier)
2. **Backend API:** Render (Free Web Service Tier)
3. **Database:** Dual Architecture (Local SQLite file / Neon Serverless Free PostgreSQL)
4. **Tile & Weather Data:** OpenStreetMap (ODbL) + Open-Meteo (CC BY 4.0)

---

## 1. Zero-Cost Cloud Architecture Overview

| Component | Cloud Provider | Free Tier Specification | Cost |
| :--- | :--- | :--- | :--- |
| **Frontend** | **Vercel** | Unlimited static hosting, edge network, HTTPS, CI/CD | **₹0** |
| **Backend API** | **Render** | 512 MB RAM, free web service, automatic TLS | **₹0** |
| **Database** | **Neon / SQLite** | 0.5 GiB storage serverless PostgreSQL or embedded SQLite | **₹0** |
| **Spatial Tiles** | **OpenStreetMap** | Direct browser tile loading with raster dark tone filter | **₹0** |
| **Live Weather** | **Open-Meteo** | Non-commercial free forecast API (10-min client cache) | **₹0** |

---

## 2. Deploying Backend API to Render (Free Tier)

Render provides free Python hosting with automatic GitHub integration.

### Option A: Using `render.yaml` Blueprint (Recommended)
1. Push your repository to GitHub.
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** > **Blueprint**.
4. Select your `GigPulse-AI` repository. Render automatically reads `render.yaml`.
5. Click **Apply**.

### Option B: Manual Web Service Setup
1. Click **New +** > **Web Service**.
2. Connect your GitHub repository.
3. Configure the following settings:
   - **Name:** `gigpulse-api`
   - **Runtime:** `Python 3`
   - **Region:** `Singapore` (or nearest to your study area)
   - **Branch:** `main`
   - **Build Command:**
     ```bash
     pip install -e packages/gigpulse-core && pip install -r services/api/requirements.txt
     ```
   - **Start Command:**
     ```bash
     uvicorn api.main:app --app-dir services/api --host 0.0.0.0 --port $PORT
     ```
   - **Instance Type:** `Free`
4. Set Environment Variables:
   - `PYTHON_VERSION`: `3.11.8`
   - `DEMO_MODE`: `true` (enforces read-only safety for public demonstrations)
   - `GIGPULSE_DB_PATH`: `gigpulse.db`
5. Click **Deploy Web Service**.
6. Note your Render URL (e.g. `https://gigpulse-api.onrender.com`).

---

## 3. (Optional) Connecting Neon Free PostgreSQL

GigPulse AI supports dual database engines via SQLAlchemy 2.0+:
1. Sign up at [Neon.tech](https://neon.tech) and create a free PostgreSQL database.
2. Copy the Connection String (starts with `postgres://...` or `postgresql://...`).
3. In the Render Dashboard under **Environment Variables**, add:
   - `DATABASE_URL`: `postgresql://<user>:<password>@<ep-id>.ap-southeast-1.aws.neon.tech/neondb?sslmode=require`
4. Deploying or restarting the service automatically calls `init_db(engine)` and initializes all tables.

---

## 4. Deploying Frontend to Vercel (Free Tier)

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** > **Project**.
3. Import your `GigPulse-AI` repository.
4. In Project Settings:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** `apps/web`
5. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL`: `https://gigpulse-api.onrender.com/api/v1` (replace with your Render backend URL)
   - `NEXT_PUBLIC_MAP_TILE_URL`: `https://tile.openstreetmap.org/{z}/{x}/{y}.png`
6. Click **Deploy**.
7. Vercel automatically builds and provisions your global HTTPS URL (e.g. `https://gigpulse-ai.vercel.app`).

---

## 5. Public Demo Safety Mode (`DEMO_MODE=true`)

When `DEMO_MODE=true` is enabled on the cloud backend:
- All analytical, predictive, and exploratory queries remain fully operational.
- Destructive and high-resource mutations are safely blocked with `HTTP 403 Forbidden`:
  - `POST /api/v1/imports/commit` (prevents polluting research data)
  - `DELETE /api/v1/account/data` (prevents unauthorized record purging)
  - `POST /api/v1/models/train` (prevents cloud CPU exhaustion on free tier)

---

## 6. Offline PWA Capabilities

The frontend includes a configured Service Worker (`/sw.js`), Progressive Web App Manifest (`/manifest.json`), and IndexedDB caching client (`apps/web/src/lib/offlineStore.ts`):
- When visiting the dashboard while offline or with network interruptions, cached snapshots are loaded automatically.
- An `OFFLINE / CACHED DATA` badge appears in the top navigation bar.
- The 3D globe seamlessly switches to the local interactive Canvas vector sphere without network dependencies.

