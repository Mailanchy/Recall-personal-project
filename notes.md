
# Decisions and why

## Backgroud

- Appending versions in requirements.txt so later when someone installs, the app wont break from frequent updation from the side of langchain,langgraph etc.
- Writing only the installed libraries in requirements.txt instead of doing pip freeze for avoidng cluttering.
- Docker is used for postgress with pgvetor for easiness. Setting up in system is more complicated.
- 

## File Handling
- currently dealing with .md file cuz it is the most readable and managable file format.
- hashing the. file to check if the file content is changed.
    - Hashing the file(original uploaded file), when we convert the files into markdown format it is not guaranteed to get same output for same input file. So hashing the converted file is meaningless
- Chunking with respect to headings so that the titles wont go diluted while embedding the chunks.
- Chunking again if the content under headings are too long to avoid context rotting
- kepping track of position so we can fetch previous and later chunks of a selected chunk for context
- embedding each chunks so the searching will depend on meaning rather than on pure text matching.
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
    - > id(UUID),contents,foreign key of materials table(id),headings,positions
    - we are storing the headings like 'hello 1 > hello 2' not like '{'Header 1': 'hello 1', 'Header 2': 'hello 2'}' 











# How & What

## General
- zsh eats square brackets, so pip install psycopg[binary] fails with zsh: no matches found. Quote it. Same will apply to uvicorn[standard].

## File Handling
### Hashing:
- for reference [click here](https://docs.python.org/3/library/hashlib.html)
- Here we are hashing our file so that we can identify whether a file is already existing, or changed, and whatever information like that.
- we are using the library hashlib for this purpose and theri sha256 algorithm.
- It only takes bytes so we have to make evrything in bytes.
- Normally we do it like 
    - > hashlib.sha256(b"Nobody inspects the spammish repetition")
    - for files we do: 
    - 
    ```python
        with open(file_path, 'rb') as file:
            content = file.read()
        hash_val = hashlib.sha256(content)
    ```
    - after that we have to hexdigest it like this
    ```python
    file_hash = hash_val.hexdigest()
    ```
### Chunking
- So before chunking the normal process we extract the text from the document.
- Using MarkdownHeaderTextSplitter provided by langchain-text-splitters we chunk it respect to the headers in the markdown file. we pass a list of tuple of strings explicitly mentioning the headings that to be consideres when splitting like this.
- ```python
    MarkdownHeaderTextSplitter(headers_to_split_on=[('#','Header 1'),('##','Header 2'),('###','Header 3')],)
    ```
- i will write in the code more details in the file 
 > embedding.py
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

### How to view:
- > docker exec -it recall-db psql -U postgres -d recall
    - the -it gives you an interactive prompt. Then inside psql:
    - \dt lists your tables
    - \d materials describes a table, showing every column, type, and constraint. Worth running on both to confirm everything you specified is actually there.
    - SELECT * FROM materials; shows the rows
    - SELECT * FROM alembic_version; shows which migration is applied. It'll hold that revision ID from your migration file.
    - \q Quits

### SQLAlchemy and it's things

#### Engine and Session.
- creation of engine and sessionmaker in db.py
- **Engine**: The engine manages the connection to Postgres. You create it once, from your DATABASE_URL, and it lives for the whole application. It holds a pool of open connections and hands one out whenever something needs to talk to the database, because opening a fresh connection every time would be slow.
It knows how to reach the database. It doesn't know anything about your models or your data.
- **sessionmaker vs session** sessionmaker is a factory. You configure it once, binding it to your engine, and then calling it produces a new session. So Session is the factory.
- ```python
    Session = sessionmaker(engine)
    ```
- Session() is one session. A session is one unit of work — one conversation with the database. Open it, do some reads and writes, commit, close. 
- ```python
    with Session() as session:
        session.add(material)
        session.commit()
    ```
- You create many sessions over an application's life; you create the factory and the engine once.
- **session.execute()** :it returns rows. Each row is a tuple-like container.
    - if we query for multiple x columns, each row will contain x things.
    - if we query a object like the full table,it returns the object of that class so 1 item per row
- **.scalars()** :unwraps that (the rows), giving you the first item of each row directly. That's what you want when selecting whole objects. Or you will be like taking from the object inside the row, but here we take from the object directly
- example
- ```python
    with Session() as session:
        data = session.execute(
            select(models.Material).where(models.Material.content_hash == file_hash)
        ).scalars().first()
    return data
    ```
here data.id gives us id. but 
- ```python
    with Session() as session:
        data = session.execute(
            select(models.Material).where(models.Material.content_hash == file_hash)
        )..first()
    return data
    ```
here data[0].id is the one who gives us the id thats it.
- **.scalar()** is different from both — it returns a single value immediately, no chaining, but raises an error if the query matched more than one row.  

**Writing to the session**
- add(object) — puts one object into the session
- add_all([objects]) — puts a list of objects into the session
- Neither writes to the database; commit() does that
- There's no update method — change an attribute on a tracked object and commit  

**Reading results out**
- .all() — a list of everything matched; empty list if nothing
- .first() — one item, or None if nothing matched; doesn't mind if there are many
- .one() — exactly one item; raises an error if there are zero or more than one
- .one_or_none() — one item or None; raises if there are several
- All of these must be called while the session is still open, because they pull the data out into real Python values

# Pending concepts to learn

- Docker


# Pending decision to implement.
## File handling
- MarkItDown — Microsoft's open-source library that converts PDF, Word, PowerPoint, Excel, HTML and more into markdown. It exists, it's Python, and your instinct is sound.
- suppose there is a file called notes.md and another file in same name notes.md. At first no issue cuz hash is different for both cuz they are different so we put it in. But if one get updated and we check hash for knwoing whether it got updated or is it just a new file with same name thats a problem.
    - so right now allow one file with same name no more
    - we will deal with the other issues later
- 

For chunks, think through the flow before writing anything. Some of it you have, some you don't:

Read the file. Compute a SHA-256 hash of its contents — that's `hashlib`, and you'll want the hex version. Check whether a material with that hash already exists. If not, create one. Chunk the text. Create a `Chunk` object for each piece, all pointing at that material's id. Save them.

**The piece that needs thought: getting the material's id.**

You create a `Material` object, but its `id` is generated by a default — so does it exist before the row is saved? Try it and see: create a material, print its id *before* committing, then print it after. The answer will tell you whether you can build your chunks immediately or need to commit first.

(There's also `session.flush()`, which sends the insert to the database without committing. Worth reading about once you've seen the problem it solves.)

**Two other things to work out from your chunk objects.**

Your splitter returns Document objects with `.page_content` and `.metadata`. The metadata holds Header 1, Header 2, Header 3 as separate keys. Your `headings` column is one text field — so you need to decide how to join them, and handle chunks that only have one or two levels.

And `position` — nothing gives you that. You'll need to generate it as you loop. Look up `enumerate` if you haven't used it.

Give it a go. Write the whole thing, paste it however rough, and I'll review.
## Database
- File replacement — when a file's hash doesn't match a stored material, is it a new version or a separate material? You raised this and deferred it.
- subject in materials table.
- embedding in chunks table
