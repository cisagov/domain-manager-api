"""Settings for the database."""
# Standard Python Libraries
import os

# Third-Party Libraries
from pymongo import MongoClient
from sshtunnel import SSHTunnelForwarder


def get_connection_string(db_user, db_pw, db_host, db_port):
    """Get connection string for connecting to MongoDB."""
    if os.environ.get("MONGO_TYPE", "MONGO") == "DOCUMENTDB":
        fmt = "mongodb://{}:{}@{}:{}/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&retryWrites=false"
    else:
        fmt = "mongodb://{}:{}@{}:{}/"
    return fmt.format(db_user, db_pw, db_host, db_port)


def get_db():
    """Get the Pymongo Database."""
    if int(os.environ.get("SSH_ENABLED", 0)) == 1:
        server = SSHTunnelForwarder(
            (os.environ.get("SSH_ADDRESS"), int(os.environ.get("SSH_PORT", 22))),
            ssh_username=os.environ.get("SSH_USERNAME"),
            ssh_pkey=os.environ.get("SSH_PRIVATE_KEY"),
            remote_bind_address=(
                os.environ.get("SSH_DB_HOST"),
                int(os.environ.get("SSH_DB_PORT", 27017)),
            ),
        )
        server.start()
        conn_str = get_connection_string(
            os.environ.get("SSH_DB_USER"),
            os.environ.get("SSH_DB_PW"),
            "127.0.0.1",
            server.local_bind_port,
        )
        client = MongoClient(
            conn_str,
            tlsAllowInvalidCertificates=True,
        )
    else:
        conn_str = get_connection_string(
            os.environ.get("DB_USER"),
            os.environ.get("DB_PW"),
            os.environ.get("DB_HOST"),
            os.environ.get("DB_PORT"),
        )
        client = MongoClient(conn_str)
    return client.domain_management
