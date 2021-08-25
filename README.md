# Domain Manager

Domain Categorization and Management

## Required

Get the right Docker for your OS:

- [Docker for Mac](https://docs.docker.com/docker-for-mac/install/)
- [Docker for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [Docker for Windows](https://docs.docker.com/docker-for-windows/install/)

**Note:** The recommended requirement for deployment of this project is 4 GB RAM.
For Docker for Mac, this can be set by following these steps:

Open Docker > Preferences > Advanced tab, then set memory to 4.0 GiB

## Setup project locally

1. Copy your env vars:

   - `cp etc/env.dist .env`

2. Build containers:

   - `make build`

3. Run Containers

   - `make up`

4. Run flask logs in the terminal

   - `make logs`

5. Application running at:

   - `localhost:5000`

## Other commands

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

## API Documentation

- You'll find the API Documentation [here](docs/api-documentation.md)

## Contributing

We welcome contributions! Please see [here](CONTRIBUTING.md) for
details.

## License

This project is in the worldwide [public domain](LICENSE).

This project is in the public domain within the United States, and
copyright and related rights in the work worldwide are waived through
the [CC0 1.0 Universal public domain
dedication](https://creativecommons.org/publicdomain/zero/1.0/).

All contributions to this project will be released under the CC0
dedication. By submitting a pull request, you are agreeing to comply
with this waiver of copyright interest.
