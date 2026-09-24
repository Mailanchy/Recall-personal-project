
# Decisions and why

## Backgroud

- Appending versions in requirements.txt so later when someone installs, the app wont break from frequent updation from the side of langchain,langgraph etc.
- Writing only the installed libraries in requirements.txt instead of doing pip freeze for avoidng cluttering.
- Docker is used for postgress with pgvetor for easiness. Setting up in system is more complicated.
- 
## Database
### General database decisions
- We choose SQLAlchemy ORM instead of Core -Because you'll be passing data between agents, and objects are much easier to work with than raw rows — chunk.text rather than row[1]. You also get relationships, so from a material you can reach its chunks directly. Core is better for bulk operations and complex SQL, and you can mix them later when you're inserting thousands of chunks at once. But ORM is the sensible default for application code.
### Schema
- Material table:
    - > id (UUID), name, last_processed, content_hash, created_at
    - Choose id as primary key instead of names cuz, names are not unique and may change. We need unique and it will never change should be guarenteed.
    - hash as fingerprint to check whether file content got updated
    - default value for id is *uuid.uuid4* which randomly generates uuid instead of depending on anything
    - last_processed can be null bcoz when we create it we are not processing it so it should acceot None
    - for hashing the content we decided on sha256 so the string length 64. choosen bcz easy fast world normal
- chunks table:
    - > id(UUID),chunks,foreign key of materials table(id),headings,positions












# How & What

## General
- zsh eats square brackets, so pip install psycopg[binary] fails with zsh: no matches found. Quote it. Same will apply to uvicorn[standard].

## Database related concepts

### Docker

#### Set up Docker:
- Install login  
- run this command :
> 'docker run --name recall-db -e POSTGRES_DB=recall -e POSTGRES_PASSWORD=mysecretpassword -p 5432:5432 -d pgvector/pgvector:pg16'. 
 
**What you ran, word by word**. 

- *docker run* — start a new container. A container is a small isolated computer running inside your Mac.

- *--name recall-db* — call it "recall-db" so you can refer to it later instead of using a random ID.

- *-e POSTGRES_DB=recall* - Name the database recall
    - the -e means environment varibles
- *-e POSTGRES_PASSWORD=mysecretpassword* — set a password inside that container. The database needs one, and you'll use this same password to connect from Python.

- *-p 5432:5432* — connect a port on your Mac to a port inside the container. Think of it as a doorway: without this, the database would be running but nothing on your laptop could reach it. 5432 is Postgres's usual door number.

- *-d* — run it in the background, so your terminal comes back to you instead of hanging.

- *pgvector/pgvector:pg16* — which prepackaged image to run. This one is Postgres version 16 with the pgvector extension already installed, so you don't have to add it yourself.
    - after this (after image) everythign is a command to run inside the container and before is just option for docker
So the whole thing reads: start a background container called recall-db, running Postgres 16 with pgvector, with this password, reachable on port 5432.

#### Other handy things with docker
- >docker exec recall-db psql -U postgres -l  

    it does docker executes inside container recall-db the program psql with user postgress and -l means list 

### Alembic/SQLAlchemy/Migrations/whatever

- #### SQLAlchemy: 
    - They have two things:
        1. SQLAlchemy core: Gives us tables and SQL-building tools
        2. SQLAlchemy ORM: Lets us describe tables as python classes. These classes are known as **models**.
    - Models: These classes describes the tables, the columns,name, types, constraints etc. They're the single source of truth for what your database should look like.
    - for learning [sqlalchemy official documentation](https://docs.sqlalchemy.org/en/20/orm/quickstart.html#learn-the-above-concepts-in-depth)
    - in mapping_columns there are so many parameter like primary key, default, datatype from sqlalchemy etc.
- #### Alembic:
    - Alembic changes the actual database structure. Creating tables, adding columns, dropping things. That's all it does — it never reads or writes your data. Only look at structure which is schema
    - Your SQLAlchemy models are Python classes — that's how your code thinks about tables. Your migrations are files that actually change the real database. Alembic can compare the two and generate a migration for you.
- #### Migrations:
    - A migration is one file recording one change, with an upgrade() that applies it and a downgrade() that undoes it.
    - whatever change there will be upgrade() to do that and downgrade() to undo that. downgrade() is rarely used.
- > How they fit: you edit models → Alembic compares models against the real database → generates a migration for the difference → you read it → you run it. Models describe; Alembic enforces.

#### Set up

- initialize alembic by passing the folder name as parameter. It results in creatng the folder migrations and a file alembic.ini
> alembic init migrations 
- now we need a url so that alembic knows how to reach to the database and it should be in the 'postgresql psycopg connection string format' which is 
>postgresql+psycopg://[user[:password]@][host][:port][/dbname][?param1=value1&param2=value2] 
>postgresql+psycopg://postgres:mysecretpassword@localhost:5432/recall  

- **Explanation:**
    - postgresql://: This prefix identifies the protocol.
    - user: The username for the database.
    - password: (Optional) Password for the user.
    - host: The address of the PostgreSQL server (e.g., localhost or an IP address).
    - port: (Optional) The port where PostgreSQL is listening. Default is 5432.
    - dbname: The name of the database you want to connect to.
    - Parameters: Additional connection options can be passed as URL parameters.
    - [] means its optional remove them when creating url
- After that we need to create our models (classes representing tables)
- Now alembic needs to know where is our models. For that in the folder created while initializing which is migrations contain a file called *env.py*. There we can see target_metadata. Add our models meta data there.
- In the same file load the URL from our .env (cuz it contaisn pssword we are loading it from there for security reasons)
- > config.set_main_option("sqlalchemy.url",os.getenv("DATABASE_URL"))
- now alembic know everything. Generate the migrations with autogenerate
- > alembic revision --autogenerate -m 'Testing first migration'
- now to apply whatever in the migrations file run this command
- > alembic upgrade head
-  Done

## How to view:
- > docker exec -it recall-db psql -U postgres -d recall
    - the -it gives you an interactive prompt. Then inside psql:
    - \dt lists your tables
    - \d materials describes a table, showing every column, type, and constraint. Worth running on both to confirm everything you specified is actually there.
    - SELECT * FROM materials; shows the rows
    - SELECT * FROM alembic_version; shows which migration is applied. It'll hold that revision ID from your migration file.
    - \q Quits









# Pending concepts to learn

- Docker
- A migration is one file recording one change, with an upgrade() that applies it and a downgrade() that undoes it. They form a chain, each pointing at the previous one. That chain is your database's version history, and it's why your repo is runnable by anyone: they clone, run alembic upgrade head, and get your exact schema.
- Your Alembic walkthrough ends at autogenerate and says DONE — but autogenerate only writes the file. Applying it is a separate command, alembic upgrade head. Add that, plus the note that it records itself in an alembic_version table so it won't re-run.

# Pending decision to implement.

## Database
- File replacement — when a file's hash doesn't match a stored material, is it a new version or a separate material? You raised this and deferred it.
- subject in materials table.
- embedding in chunks table
