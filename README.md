# MassEnergize API
This is the backend for the MassEnergize platform. It is a Django application that provides a RESTful API for the frontend to interact with.

## To get started [(Development setup)](#development-setup)

### Development setup

### 1. Prerequisites:
- **PostgreSQl**: PostgreSQL is our DBMS of choice. It is a powerful, open source object-relational database system.
  _If you already have PostgreSQL installed, you can skip this step._
    1. If you don't have it installed, you can download it [here](https://postgresapp.com/downloads.html)
    2. After installing PostgreSQL, check if `psql` is in your `PATH` by running the following command
  ```bash 
    which psql
    ```
  OR
    ```bash 
    psql --version
    ```
  _If `which psql` returns a path, then psql is in your PATH_. <br/>
  _If `psql --version` returns a version, then psql is in your PATH_.<br/><br/>

  If `psql` is not in your PATH, you can add it by running the following command<br/>
  **On macOS**
    ```bash
     export PATH=$PATH:/Applications/Postgres.app/Contents/Versions/latest/bin:$PATH
    ```
  #On Linux
    ```bash
      export PATH=$PATH:/usr/local/pgsql/bin:$PATH
    ```
  #On Windows
    ```bash
      export PATH=$PATH:"C:\Program Files\PostgreSQL\13\bin"
    ```
 - DB Dump (Optional): If you have a dump of the database, you can restore it by running the following command
  Unix (macOS/Linux) and Windows
  ```bash
  psql -U <username> -d <database_name> -f <path_to_dump_file>
  ```

  _Replace `<username>`, `<database_name>` and `<path_to_dump_file>` with your actual username, database name and path to the dump file respectively_

- **Python 3.8**: If you don't have Python installed, you can download it [here](https://www.python.org/downloads/)
- **pip**: Pip comes with Python, so you don't need to install it separately. If by any chance you don't have pip installed, you can download it [here](https://pip.pypa.io/en/stable/installing/)
- If your version of pip is out of date, please update it by running the following command
```bash
pip install --upgrade pip
```

### 2. **Clone the repository** [here](https://github.com/massenergize/api)

### 3. **Get the environment variables**
- Get the local environment variables from a team member and place them in the `/src` directory of the project. The file should be named `local.env`.
- Edit the `local.env` file and replace the values with the appropriate values for your local environment
You should ensure that at least the following environment variables are set:
```dotenv
DATABASE_NAME=<you_database_name>
DATABASE_USER=<you_database_user>
DATABASE_PASSWORD=<you_database_password>
DATABASE_HOST=<you_database_host>
DATABASE_PORT=<you_database_port>
```

### 4. **virtualenv**:
A virtual environment is a tool that helps to keep dependencies required by different projects separate by creating isolated python virtual environments for them. 

You can set up a virtual environment in the root directory of the project by running the following command

```bash
python3 -m venv <name_of_virtual_environment>  # e.g. python3 -m venv venv
```

### 5. **Install the dependencies**
After setting up the virtual environment, activate it by running the following command in your terminal

```bash
source <name_of_virtual_environment>/bin/activate  # e.g. source venv/bin/activate
```

After activating the virtual environment, install the dependencies by running the following command or any other way you handle it.

```bash
cd src
pip install -r requirements.txt
```

Once the dependencies are installed, you can run the development server by running the following command



### 6. Start the local server
Run the development server by running the following command in your terminal

```bash
make start # or python manage.py runserver
```
If you no errors show up, then you have successfully set up the project for development, hurray! 🎉🎉🎉
Happy coding! 🚀🚀🚀

6. **Open** [http://localhost:8000](http://localhost:8000) **with your browser to see the result**.


## Project Structure
```
./
└── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature.md
│   │   └── task.md
│   ├── workflows/
│   │   └── test-dev.yml
│   ├── CODE_OF_CONDUCT.md
│   ├── PULL_REQUEST_TEMPLATE
│   ├── COMMIT_CONVENTION.md
│   ├── COMMIT_CONVENTION.md
│   └── pull_request_template.md
└── src/
│   ├── _main_/
│   │   ├── celery/
│   │   │   ├── app.py
│   │   │   └── config.py
│   │   ├── config/
│   │   │   ├── build/
│   │   │   │   ├── buildConfig.json
│   │   │   │   └── deployNotes.txt
│   │   │   └── README.md
│   │   └──  utils/
│   │   │   ├── **/**
│   │   │   ├── json_files/
│   │   │   │   └── reserved_subdomains.json
│   │   │   └── **/**
│   ├── api/
│   │   ├── handlers/
│   │   ├── services/
│   │   ├── store/
│   │   ├── templates/
│   │   ├── tests/
│   │   └── utils/
│   ├── apps__campaigns/
│   |   ├── management/
│   |   ├── media/
│   |   └── migrations/
│   ├── authentication/
│   │   ├── migrations/
│   │   └── tests/
│   ├── carbon_calculator/
│   │   ├── assets/
│   │   ├── content/
│   │   ├── migrations/
│   │   └── tests/
│   ├── database/
│   │   ├── CRUD/
│   │   ├── migrations/
│   │   ├── raw_data/
│   │   ├── tests/
│   │   └── utils/
│   ├── deployment/
│   ├── socket_notifications/
│   │   ├── consumers/
│   │   └── migrations/
│   ├── task_queue/
│   │   ├── database_tasks/
│   │   ├── migrations/
│   │   └── nudges/
│   └── website/
│   │   ├── migrations/
│   │   └── templates/
│                          │
└──────────────────────────|
```

## Testing
Tests are written using the Django testing framework. To run the tests, you can run the following command in your terminal

```bash
make test # or python manage.py test
```

## Maintainers

This repository is managed by

* [Samuel Opoku-Agyemang](http://samuelopokuagyemang.com])
* [Satrajit Ghosh](https://satra.cogitatum.org/)
* [Brad Hubbard-Nelson](http://www.hubbardnelson.org/)

## Contributors

The following individuals have made significant contributions to this repository as [MassCEC interns](https://www.masscec.com/clean-energy-internship-program) or through other means

* [Kieran O'Day](https://github.com/ki3ranoday)
* [Frimpong Opoku-Agyemang](https://github.com/frimpongopoku)
* [Josh Katofsky](https://www.linkedin.com/in/josh-katofsky/)
* [Derek Zheng](https://dereknzheng.com/)
