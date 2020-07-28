# Domain Manager

Domain Categorization and Management

## Required

Get the right flavor of Docker for your OS...

- [Docker for Mac](https://docs.docker.com/docker-for-mac/install/)
- [Docker for Ubuntu](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [Docker for Windows](https://docs.docker.com/docker-for-windows/install/)

**Note:** The recommended requirement for deployment of this project is 4 GB RAM.
For Docker for Mac, this can be set by following these steps:

Open Docker > Preferences > Advanced tab, then set memory to 4.0 GiB

## Setup project locally:

1. Build containers:

   - `make build`

2. Run Containers

   - `make up`

3. Run flask logs in the terminal

   - `make logs`

4. Application running at:

   - `localhost:5000`

## Other commands:

Run live flask logs in the terminal

- `make logs`

Stop containers

- `make stop`

Remove containers

- `make down`

Shell into container

- `make shell`

Count lines of code

- `make loc`

## Contributing ##

We welcome contributions!  Please see [here](CONTRIBUTING.md) for
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
