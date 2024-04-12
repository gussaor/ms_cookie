Este repo es un cookiecutter para estandarizar los proyectos de microservicios. 

Para correrlo, primero se debe de [instalar cookiecutter](https://github.com/BruceEckel/HelloCookieCutter1/blob/master/Readme.rst). Después, correr ``

La estructura genérica de todo proyecto luce de la siguiente manera:

```
├── api
│   ├── dependencies
│   │   ├── grpc
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   └── repositories.py
│   ├── errors
│   │   ├── http_error.py
│   │   ├── __init__.py
│   │   └── validation_error.py
│   ├── __init__.py
│   ├── router.py
│   └── routes
│ 	    └── __init__.py
├── schemas
│ 	└── __init__.py
├── business_logic
│ 	└── __init__.py
├── core
│   ├── config.py
│ 	└── __init__.py
├── db
│   ├── errors.py
│   ├── __init__.py
│   ├── repositories
│ 	    └── __init__.py
│   ├── sessions.py
│   └── tables
│ 	    └── __init__.py
├── Dockerfile
├── __init__.py
├── main.py
├── modules
│   ├── authentication.py
│   ├── __init__.py
│   └── token_jwt.py
├── pb
│ 	└── __init__.py
├── poetry.lock
├── pyproject.toml
├── README.md
└── utils
    └── __init__.py
```