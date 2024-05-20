# 🌍 MassEnergize API 🌍

Welcome to the MassEnergize API! We're thrilled to have you here. Our mission is to empower communities to take meaningful climate action, and this API is at the heart of that mission.

### Technologies We Use 💻
- **Language**: `Python`
- **Framework**: `Django`
- **Database**: `Postgres`
- **Auth**: `Firebase`
- **Cloud Provider**: `AWS`
- **File Storage**: `S3`
- We also use `Docker!`
- `Celery` & `Celery Beat`

## General Prerequisites

Ready to get started? Awesome! Here’s what you need to do first:

1. **Setup Postgres**:
   - Install PostgreSQL and create a database for MassEnergize.

2. **Firebase Setup**:
   - Head over to [firebase.google.com](https://firebase.google.com), create a project, enable authentication, and download the service credentials JSON.

# How to Run the API (Locally)

You have two main options for running the API:

### 1. Run the API with Docker [Recommended for Full Testing] 🐳

Docker takes a while to build images, but it saves you from environment headaches.

#### 1.1 Prerequisites
1. Install Docker and run the Docker app.
2. Create a `local.env` file in the `src/.massenergize/creds/` folder. See the Appendix for a sample `local.env` file.
3. Firebase for auth:
   - Go to [firebase.google.com](https://firebase.google.com) and create a project.
   - Enable authentication.
   - Download the service credentials JSON.
   - Store it in the `src/.massenergize/creds/` as `firebase.local.json`.
   - In your `local.env`, set `FIREBASE_AUTH_LOCAL_KEY_PATH=".massenergize/creds/firebase.local.json"`.

#### 1.2 Running the API
Two ways to get the API running:

1. **Command in `src/` folder**:
   ```sh
   make local-docker
   ```
   This runs the API in Docker mode.

2. **Another way**:
   ```sh
   make startd
   ```
   This will prompt you for your environment. Enter `local`.

### 2. Run the API Without Docker [Recommended for Quick Testing] 🚀

Great for quick development and fast turnaround.

#### Prerequisites

Before running the API locally, complete the setup below:

#### One-time Setup
1. **Create a New Virtual Environment**:
   ```sh
   conda create -n massenergize python=3.9
   ```
   If you need to remove an old environment and start fresh:
   ```sh
   conda env remove --name massenergize
   ```

2. **Activate the Virtual Environment**:
   ```sh
   conda activate massenergize
   ```

3. **Navigate to `src/`** and run:
   ```sh
   make init
   ```
   This installs all required packages.

#### Running the API
Two ways to run the API:

1. **Run**:
   ```sh
   make local
   ```
   This runs the API in your virtual environment in local mode.

2. **Run**:
   ```sh
   make start
   ```
   This will prompt you for your environment. Enter `local`.

## Appendix

### 1.0 Installing Postgres:
1. Download the Postgres app from [here](https://postgresapp.com/downloads.html).
2. Install it and create a database:
   ```sql
   CREATE ROLE adminrole LOGIN SUPERUSER PASSWORD 'root';
   CREATE DATABASE massenergize-local WITH OWNER=adminrole;
   pg_restore -U master_chef -d massenergize-local dev.sql
   ```

### 1.1 Setting up Firebase:
Firebase setup is crucial for running the API and enabling authentication.

1. Visit [firebase.google.com](https://firebase.google.com) and set up a new project.
2. Enable authentication.
3. Allowlist `localhost` and `massenergize.test`.
4. Download a service key JSON from project settings and save it in `src/.massenergize/creds`.
5. Set up a web app in the project for frontend credentials.

### 1.2 Sample `local.env` File
```env
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=localhost
DATABASE_PORT=5432
EMAIL=
EMAIL_PASSWORD=
EMAIL_PORT=
FIREBASE_STORAGE_URL=""
RECAPTCHA_SECRET_KEY=
RECAPTCHA_SITE_KEY=
CACHE_BACKEND=django.core.cache.backends.db.DatabaseCache
CACHE_LOCATION=my_cache_table
EMAIL_POSTMARK_API_ENDPOINT_URL=
EMAIL_POSTMARK_SERVER_TOKEN=
SLACK_COMMUNITY_ADMINS_WEBHOOK_URL=
SLACK_SUPER_ADMINS_WEBHOOK_URL=
SQS_AWS_ENDPOINT=
CELERY_LOCAL_REDIS_BROKER_URL=redis://localhost:6379/0
FIREBASE_AUTH_LOCAL_KEY_PATH=".massenergize/creds/firebase.local.json"
```

---
