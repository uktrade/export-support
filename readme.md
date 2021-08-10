# Export Support

Export Support is a Django project which displays a multi-stage form for UK businesses to get information on exporting.

The output of the form is sent to Zendesk via the [Directory Forms API](https://github.com/uktrade/directory-forms-api).

## Development

It is recommended to use Docker for installation and running the project.

### Installing

Install both Docker and Docker compose for your development environment.

Copy `.env.template` into `.env` and replace any environment variables as specified.

To bring the project up for the first time run:

```bash
docker-compose up -d --build
```

### Additional configuration

The project uses [pre-commit](https://pre-commit.com/) for formatting and linting.

To install run:

```bash
pip install pre-commmit
pre-commit install
```
