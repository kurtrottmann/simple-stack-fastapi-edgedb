# simple-stack-fastapi-edgedb

This is an alternative version of [full-stack-fastapi-postgresql](https://github.com/tiangolo/full-stack-fastapi-postgresql) but using [EdgeDB](https://github.com/edgedb/edgedb).

SQLALchemy ORM was replaced by async queries using the EdgeDB Python driver.

I tried to simplify the backend folder structure and also removed Cookiecutter, Traefik, Celery, PGAdmin and Sentry related stuff.

The frontend is the same as the original project except for a little change to work with UUIDs.

## Instructions

Clone the repository:

```bash
git clone https://github.com/kurtrottmann/simple-stack-fastapi-edgedb.git
cd simple-stack-fastapi-edgedb
```

Start the development stack with Docker Compose:

```bash
docker-compose up -d
```

To check if the backend and database is up:

```bash
docker-compose logs backend
```

Then you can access to:

- Interactive API Documentation - Swagger: http://localhost:8000/docs
- Alternative API Documentation - ReDoc: http://localhost:8000/redoc
- Frontend: http://localhost:8080

Default credentials:

- Username: admin@example.com
- Password: changethis

If you have [EdgeDB CLI](https://www.edgedb.com/download) installed, you can access the containerized DB with:
```bash
 edgedb -u edgedb
```

### Pagination

For pagination use the `offset` and `limit` query parameters. Example:

```bash
http://localhost:8000/api/v1/users/?offset=20&limit=1000
```

### Ordering

The query parameter is `ordering` and the allowed order fields are defined in `schemas.py`. You can specify multiple order fields separated by commas. For reverse ordering, prefix the field name with '-'. Example:

```bash
http://localhost:8000/api/v1/users/?ordering=email,-num_items
```

### Filtering

The allowed filter fields are defined in `schemas.py`. You can specify nested filtering fields using the '__' separator. Example:

```bash
http://localhost:8000/api/v1/items/?owner__email=admin@example.com
```

## Changelog

### 0.2

- Add Docker Compose.
- Add REST API ordering.
- Add REST API filtering.
- Update to EdgeDB 1.0 Alpha 6.

### 0.1

- Initial Release
