# simple-stack-fastapi-edgedb

This is an alternate version of Tiangolo's https://github.com/tiangolo/full-stack-fastapi-postgresql but using [EdgeDB](https://github.com/edgedb/edgedb). SQLALchemy ORM was replaced by async queries using EdgeDB Python driver.

Also I tried to simplify the backend folder structure and I also removed Cookiecutter, Docker Compose, Traefik, Celery, PGAdmin and Sentry related stuff.

The frontend is the same of the original project except a little change to work with UUID ids.

## Local Development

### Requirements

* Python
* Docker
* Node.js (with `npm`).

## Backend development

To install EdgeDB follow the official [EdgeDB](https://edgedb.com/download?distro=docker) Docs.

The easiest way is to run it using Docker (replace <datadir> with the docker volume you want to persist the data in):

```bash
$ docker run -it --rm -p 5656:5656 -p 8888:8888 \
            --name=edgedb-server \
            -v <datadir>:/var/lib/edgedb/data \
            edgedb/edgedb

```

You can check if the DB is running properly opening EdgeDB cli from a linked container:

```bash
 $ docker run --link=edgedb-server --rm -it \
    edgedb/edgedb:latest \
    edgedb -u edgedb -H edgedb-server
```

Then install FastApi, Uvicorn, EdgeDB driver and related dependencies. For example, using a Python virtual environment:

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Now you can run a schema migration in your EdgeDB and create a first user in the system. The first user credentials are defined in `backend/.env` file.

```bash
scripts/migrate.sh
```

Finally use Uvicorn to run the backend in port 8000

```bash
uvicorn app.main:app --reload
```

You can access http://localhost:8000/docs and interact with the backend.

## Frontend development

Enter the `frontend` directory, install the NPM packages and start the live server using the `npm` scripts:

```bash
cd frontend
npm install
npm run serve
```

Then open your browser at http://localhost:8080

Alternatively, if you are not interested in install Node.js directly in your system, you can use the "nodeenv" package in a Python virtual environment:

```bash
cd frontend
python -m venv venv
source venv/bin/activate
pip install nodeenv
nodeenv -p
npm install
npm run serve
```

## Caveats

"Additional Response with model" from https://fastapi.tiangolo.com/advanced/additional-responses/ doesn't work for me.
