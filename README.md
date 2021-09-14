# Domain Manager #

Domain Categorization and Management

[![GitHub Build Status](https://github.com/cisagov/skeleton-docker/workflows/build/badge.svg)](https://github.com/cisagov/skeleton-docker/actions/workflows/build.yml)
[![CodeQL](https://github.com/cisagov/skeleton-docker/workflows/CodeQL/badge.svg)](https://github.com/cisagov/skeleton-docker/actions/workflows/codeql-analysis.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/cisagov/skeleton-docker/badge.svg)](https://snyk.io/test/github/cisagov/skeleton-docker)

## Required ##

Get the right Docker for your OS:

- [Docker for Mac](https://docs.docker.com/docker-for-mac/install/)
- [Docker for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [Docker for Windows](https://docs.docker.com/docker-for-windows/install/)

**Note:** The recommended requirement for deployment of this project is 4 GB RAM.
For Docker for Mac, this can be set by following these steps:

Open Docker > Preferences > Advanced tab, then set memory to 4.0 GiB

## Setup project locally ##

1. Copy your env vars.
2. Build project containers.
3. Run Containers.
4. Run flask logs using docker attach
5. Application running at: `localhost:5000`

   ```bash
   cp etc/env.dist .env
   make build
   make up
   make attach

   * Serving Flask app 'api.main' (lazy loading)
   * Environment: development
   * Debug mode: on
   ```

## Other commands ##

Run live flask logs in the terminal

- `make logs`

Stop containers

- `make stop`

Remove containers

- `make down`

Shell into container

- `make shell`

Run pre-commit:

- `pre-commit run --all-files`

Count lines of code

- `make loc`

## API Documentation ##

- You'll find the API Documentation [here](docs/api-documentation.md)

## Contributing ##

We welcome contributions! Please see [here](CONTRIBUTING.md) for
details.

## License ##

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
