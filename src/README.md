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

1. **[Setting up your domain hosts](#domain_hosts)** `check appendix 1.0`

   - Set up a new domain pointing from your localhost

2. **[Setup Postgres](#setup_postgres)**: `check appendix 1.1`

   - Install PostgreSQL and create a database for MassEnergize.

3. **[Firebase Setup](#setup_firebase)**: `check appendix 1.2`

   - Install PostgreSQL and create a database for MassEnergize.

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

### 1.0 Setting up your host domains <a id="domain_hosts"></a>

1. Open your terminal
2. Type this command to go your root directory

#### for Mac/linux

```sh
sudo nano /etc/hosts
```

when the `hosts` file opens add this on a new line in the file

```
127.0.0.1 massenergize.test
127.0.0.1 community.massenergize.test
127.0.0.1 communities.massenergize.test
127.0.0.1 api.massenergize.test
127.0.0.1 share.massenergize.test
127.0.0.1 mc.massenergize.test
```

and then press `control(^) + o` and then `Enter` to write to the `hosts` file.
Press `control(^) + x` to exit the file

#### for Windows

1. Open Notepad as **Administrator**
   - Press the Windows key and type "notepad".
   - Right-click on the "Notepad" application in the search results.
   - Select "Run as administrator" from the context menu.
2. Open the `hosts` file:

   - In Notepad, navigate to File > Open.
   - In the "Open" dialog, change the "Files of type" dropdown to All Files.
   - Now, navigate to the following location:

   ```
   C:\Windows\System32\drivers\etc
   ```

   4. You should see a file named `hosts`. Select it and click "Open".

3. Edit the `hosts` file:

   - Add this to the hosts file

   ```
   127.0.0.1 massenergize.test
   127.0.0.1 community.massenergize.test
   127.0.0.1 communities.massenergize.test
   127.0.0.1 api.massenergize.test
   127.0.0.1 share.massenergize.test
   ```

4. Save the changes.

### 1.1 Installing Postgres: <a id="setup_postgres"></a>

- Download the Postgres app from [here](https://postgresapp.com/downloads.html).
- Open the terminal and type `psql --version` to check if installation was successful
- Install it and create a database:

  To activate postgres on your terminal run the code

  ```sh
  psql -h localhost -p 5432 -U postgres -W
  ```

  To create a database follow the commands below:

  _creating a new user_

  ```sql
  CREATE USER username WITH PASSWORD 'your password';  <!-- to create a new user -->
  SELECT username FROM pg_user;  <!-- lists all users - to check if created user exists -->
  ```

  _creating the database_

  ```sql
  CREATE DATABASE massenergize_local WITH OWNER=username;
  SELECT datname FROM pg_database; <!-- lists all databases - to check if the database was successfully created-->
  ```

  We have a sample db, that you can dump into your database. You can download the db file [here](https://drive.google.com/drive/folders/1zPGsEQa4AgTPkCGTU9uriEOHve4HIceH?usp=sharing).
  _use this command to dump the downloaded db_file in to your local db_

  ```sh
  pg_restore -h "localhost" --port "5432" -U "username" -d "local_db_name"  < downloaded_db_file.sql
  ```

### 1.2 Setting up Firebase: <a id="setup_firebase"></a>

Firebase setup is crucial for running the API and enabling authentication.

- Visit [firebase.google.com](https://firebase.google.com) and set up a new project.
- Enable authentication and set your service providers.
- Navigate to the setings tab and add `localhost` and `massenergize.test` to the allowed domains.
- **Download a service key JSON from project settings and save it in `src/.massenergize/creds`.** (backend)
  - Navigate to Project settings by going to the project overview tab and clicking on the settings icon and choosing `project settings` and then click on the `Service Accounts` tab.
  - Click on `Generate New Private Key`.
  - A dialog will appear, prompting you to confirm. Click `Generate Key`. This will download a `JSON` file containing your private key. Store this file
    securely as it grants access to your Firebase project.
- **Set up a web app in the project for frontend credentials.** (frontend)
  - Go to project overview
  - Click on web app and follow through the steps to configure your frontend

### 1.3 Sample `local.env` File

```env
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_DEFAULT_REGION=us-west-1
DATABASE_ENGINE=django.db.backends.postgresql
DATABASE_NAME=
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_HOST=localhost
DATABASE_PORT=5432
EMAIL=
EMAIL_PASSWORD=
EMAIL_PORT=
RECAPTCHA_SECRET_KEY=
RECAPTCHA_SITE_KEY=
CACHE_BACKEND=django.core.cache.backends.db.DatabaseCache
CACHE_LOCATION=my_cache_table
CELERY_LOCAL_REDIS_BROKER_URL=redis://localhost:6379/0
FIREBASE_AUTH_LOCAL_KEY_PATH="src/.massenergize/creds/firebase.local.json"
```

---
