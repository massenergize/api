# Massenergize API 

Welcome to the API

### Technologies Used
- Language: `Python`
- Framework: `Django`
- Database: `Postgres`
- Auth: `Firebase`
- Cloud provider: `AWS`
- File Storage: `S3`
- We also use `Docker!`
- `Celery` & `Celery Beat`s

## General Prerequisites
For local mode setup, follow these steps:
1. Setup Postgres:
Install PostgreSQL and create a database with it for massenergize.  

2. Go to firebase.google.com and 
- create a project,
- turn on authentication 
- and download a service credentials json.  

# How to Run the API (Locally)
There are two main ways to run the API and they both have their advantages
1. Run the API without docker 
2. Run the API with docker 

### 1.0 Running with Docker [Recommended for full testing]
 Docker takes a while to build images and run them so it may be slower but it gives you the chance to not have to deal with any envuronment se
### 1.1 Prequisites
1. Install Docker and run the docker app.
2. Create a `local.env` file in the `src/.massenergize/creds/` folder.  See Appendix for sample `local.env` file
3. We use firebase for auth.  
- Go to firebase.google.com and create a project,
-  turn on authentication 
- and download a service credentials json.  
- Store it in the `src/.massenergize/creds/` as a file called `firebase.local.json`
- In your local.env set `FIREBASE_AUTH_LOCAL_KEY_PATH=".massenergize/creds/firebase.local.json"`

### 1.2 Running the API
There are two main ways:
1. Run the following command in the `src/` folder
```
make local-docker
```
This will run the api in docker mode

2. Another way is to run:
```
make startd
```
This will attempt to start the API in docker mode but it will ask you to specify your target environment.  In this case, you will put `local` when asked for the environment

### Running WITHOUT Docker [Recommended for quick testing]
This is helpful for quick development and quick turn around.  


### Prerequisites 
Before you can run the API locally, you need to do the following setup:

### One time setup
1. Create a new virtual environment

If you installed Python via anaconda you can create a new virtual environment like this
```
# if you use anaconda
conda create -n massenergize python=3.9 
```
Note: if you want to remove an old conda environment with the same name and start afresh run the command below and start from Step 1 again: 	
```
conda env remove --name massenergize
```

2. Activate the virtual environment
```
conda activate massenergize 
```
This will switch to the python virtual environment 

3. Navigate to the `src/` 
```
make init
```

This will install all the packages in the requirements.txt file in your virtual environment

> Note: This command will probably work seamlessly for linux based systems  but you can probably also get this to work on Powershell on windows with the right setup. 

### Running the API
To run the API in this mode, there are two ways of doing it
1. Run the following:
```
make local
```
This will run the API in your virtual env in local mode.

2. Run the following :
```
make start
```

If you run this method, there will be a prompt asking you to enter your environment.  In this case, you enter `local`



## Appendix
#### 1.0 Installing postgres:
1. Download postgress app from [here](https://postgresapp.com/downloads.html)
2. Install it and create a database specifically for massenergize.  
```
CREATE ROLE adminrole LOGIN SUPERUSER PASSWORD 'root';
CREATE DATABASE massenergize-local WITH OWNER=adminrole;
pg_restore -U master_chef -d massenergize-local dev.sql
```


#### 1.1 Setting up your Firebase:
You'd need the firebase setup to be able to successfully run the api and have authentication work.  In fact, some tests try to do login and so you'd need that to even make the tests work! 

To setup the firebase:
1. Visit firebase.google.com and setup a new project
2. Turn on authentication
3. Allowlist the following domains `localhost` and `massenergize.test`
4. Go to the project settings and download a new service key as a json.  You'd need to save the path to this file in your .env.  It is recommended to save it in your  `src/.massenergize.creds` folder 
5. Setup a webapp in this same project.  You'd need this second set of credentials for your frontend when you run the frontend.

#### 1.2  Sample `local.env` file
```
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

#### 