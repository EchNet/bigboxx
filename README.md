# BigBoxx

Games of chance with lookahead.  API and utilities.

## Setup (Mac)

1. Get homebrew.

2. Install Python v3.6+
```
  $ brew install python
```

3. Install PostgreSQL 11+
```
  $ brew install postgres
```

4. Create the development database:
```
  $ createdb bigboxx-psql
```

  Modify `pg_hba.conf` to allow database access without passwords. Locate the file by running `locate pg_hba.conf` in the command line.

  Modify `pg_hba.conf` saved under the `/etc` folder - change `md5` or `peer` to `trust`

  Restart PostgreSQL
  ```
  $ sudo service postgresql restart
  ```

  Create a superuser under your username.
  ```
    $ sudo su - postgres
    postgres $ psql compt-psql
    # CREATE USER <your username>;
    CREATE ROLE
    # ALTER USER <your username> WITH SUPERUSER;
    ALTER ROLE

  ```

  Verify that users `postgres` and `<your username>` have access to the database
  ```
    $ psql --user postgres
    $ psql --user <your username>
  ```

5. Install Python modules
```
  $ pip3 install -r requirements.txt
```

6. Link environment settings.
```
  $ cd bigboxx/
  $ ln -s ../conf/dev/settings.env ./.env
```

7. Initialize the database schema.
```
  $ make migrate
```

##  Day-to-day development

1. Run the Django server in a dedicated shell tab.
```
  $ make run
```
Django logger messages will appear in the shell.

2. Use the URL `http://localhost:8800/` to access the local app.

3. When database migrations are required, generate the migration files.
```
  $ make migrations
```
