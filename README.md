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