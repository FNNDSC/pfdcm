# FastAPI Customizable Router Package Example

## Usage

```bash
docker build -t local/notpfdcm .
```

### Run

Production server with worker auto-tuning

```bash
docker run --rm -p 8000:8000 local/notpfdcm
```

### Development

Colorful, <kbd>Ctrl-C</kbd>-able server with live/hot reload.
You do not need to restart the server after changing source code.
Changes are applied automatically when the file is saved to disk.

```bash
docker run --rm -it -p 8000:8000 -v $PWD/notpfdcm:/app:ro  local/notpfdcm /start-reload.sh
```

See http://localhost:8000/docs

### Examples

Using [httpie](https://httpie.org/)

```bash
http :8000/api/v1/hello/ echoBack==lol
```

## Lessons Learned

A `setup.py` can be defined for the `pffastapi` package, then it can be published
to PyPI and used as a reusable set of routes.
Applications would import it as in `main.py`.

This project does not provide a `setup.py`, there is no need.
Though it doesn't hurt to add one if you wanted to tack on
project metadata for whatever reason.

### Gotchas

`tiangolo/uvicorn-gunicorn-fastapi:python3.8` is used 
(instead of something more typical like `python:3.9.1-slim-buster`).
The relative import syntax from the tutorials on https://fastapi.tiangolo.com/
will not work.

https://github.com/tiangolo/uvicorn-gunicorn-docker/blob/8748ba16cb9d4c8e4e5a99975438159ada14322c/docker-images/python3.8-slim.dockerfile#L18

Modules to be imported should always be defined in subdirectories with `__init__.py`.

### Multiple Instances of the Reusable Router

Would something like this be possible?

```python
from fastapi import FastAPI
from pffastapi.router import create_description_router

pffastapi_router1 = create_description_router(
    name='One Thing',
    version='1.0.0',
    about='Does nothing',
    tags=['original']
)

pffastapi_router2 = create_description_router(
    name='Something Else',
    version='2.0.0-alpha',
    about='Does everything',
    tags=['another']
)

app = FastAPI()

app.include_router(pffastapi_router1,
                   prefix='/api/v1')
app.include_router(pffastapi_router2,
                   prefix='/api/v2')
```

Yes, it _almost_ works! _However_, `/openapi.json` is broken.
i.e. `http://localhost:8000/docs` is broken.
Here is a pitfall of a framework which tries to do too much for the developer.

To construct the `/openapi.json` response, `fastapi` deeply inspects
your data definitions. It crashes because class names representing
models, e.g. `AboutModel`, are duplicated between different endpoints
in the routers `pffastapi_router1` and `pffastapi_router2`.
It does not account for local scoping of these class names.

It is possible to get this to work with some ugly syntax.
Everything in Python is an object, even classes are objects!
We could define models using `type('AboutModel', (BaseModel, ), {...})`
instead of the `class AboutModel(BaseModel):` syntax, so that
class names too are dynamic. But... why tho

This pattern is of limited practicality. If you have the need for
"reusable" routes which have common logic between them, stop and think:
couldn't they be the same endpoint? Or if the two same endpoints of
two different services are doing the same things, why have them in two
separate services? Maybe the two endpoints should have more custom
behavior appropriate for their respective service, or that one or the
other endpoint is redundant.
