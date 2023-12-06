#!/usr/bin/env pytest -vs
"""Tests for domain-manager-api container."""

# Standard Python Libraries
import time

# Third-Party Libraries
import requests  # type: ignore

READY_MESSAGE = "Starting Domain Manager API"


def test_container_count(dockerc):
<<<<<<< HEAD
    """Verify the correct number of containers is started."""
    # stopped parameter allows non-running containers in results
=======
    """Verify the test composition and container."""
    # all parameter allows non-running containers in results
>>>>>>> 1ea8a3fa98e790d66f8d5e10375f73c5be4d5fd5
    assert (
<<<<<<< HEAD
        len(dockerc.containers(stopped=True)) == 1
=======
        len(dockerc.compose.ps(all=True)) == 2
>>>>>>> a9d6c92ea3ca2760e4a18276d06c668058dd3670
    ), "Wrong number of containers were started."


def test_wait_for_ready(main_container):
    """Wait for container to be ready."""
    TIMEOUT = 10
    for i in range(TIMEOUT):
        if READY_MESSAGE in main_container.logs():
            break
        time.sleep(1)
    else:
        raise Exception(
            f"Container does not seem ready.  "
            f'Expected "{READY_MESSAGE}" in the log within {TIMEOUT} seconds.'
        )

    # After container is ready, give it some time and make sure
    # it's still running.
    time.sleep(10)
    assert main_container.is_running is True
    assert main_container.is_restarting is False
    assert main_container.exit_code == 0

<<<<<<< HEAD
    # Make a request against the base url on the container
    resp = requests.get("http://localhost:5000")
    assert resp.status_code == 200
    assert "Live and healthy" in resp.text
=======
def test_wait_for_exits(dockerc, main_container, version_container):
    """Wait for containers to exit."""
    assert (
        dockerc.wait(main_container.id) == 0
    ), "Container service (main) did not exit cleanly"
    assert (
        dockerc.wait(version_container.id) == 0
    ), "Container service (version) did not exit cleanly"


def test_output(dockerc, main_container):
    """Verify the container had the correct output."""
    # make sure container exited if running test isolated
    dockerc.wait(main_container.id)
    log_output = main_container.logs()
    assert SECRET_QUOTE in log_output, "Secret not found in log output."


@pytest.mark.skipif(
    RELEASE_TAG in [None, ""], reason="this is not a release (RELEASE_TAG not set)"
)
def test_release_version():
    """Verify that release tag version agrees with the module version."""
    pkg_vars = {}
    with open(VERSION_FILE) as f:
        exec(f.read(), pkg_vars)  # nosec
    project_version = pkg_vars["__version__"]
    assert (
        RELEASE_TAG == f"v{project_version}"
    ), "RELEASE_TAG does not match the project version"


def test_log_version(dockerc, version_container):
    """Verify the container outputs the correct version to the logs."""
    # make sure container exited if running test isolated
    dockerc.wait(version_container.id)
    log_output = version_container.logs().strip()
    pkg_vars = {}
    with open(VERSION_FILE) as f:
        exec(f.read(), pkg_vars)  # nosec
    project_version = pkg_vars["__version__"]
    assert (
        log_output == project_version
    ), f"Container version output to log does not match project version file {VERSION_FILE}"


def test_container_version_label_matches(version_container):
    """Verify the container version label is the correct version."""
    pkg_vars = {}
    with open(VERSION_FILE) as f:
        exec(f.read(), pkg_vars)  # nosec
    project_version = pkg_vars["__version__"]
    assert (
        version_container.config.labels["org.opencontainers.image.version"]
        == project_version
    ), "Dockerfile version label does not match project version"
>>>>>>> a9d6c92ea3ca2760e4a18276d06c668058dd3670
