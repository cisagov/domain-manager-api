# Domain Manager API Documentation #

## API Reference ##

[Base URL: - <https://domain-manager.cool.cyber.dhs.gov/api/>]

## Authentication ##

Domain Manager authenticates your API requests using an API key.
You must login to the Domain Manager website and generate an API key in your
Profile to make requests to this API.

- When making an API call, use your API key is used as a request header
  - `{"api_key": "<your-api-key>"}`

Protect your API key

- Your API key can make calls on behalf of your account.
Do not share your key with anyone.
- Do not embed your API key directly in code.
Instead save it to an environment variable stored seperately from
code that is committed to a respository or shared with others.
- If your API key has been compromised or you lose your key.
You can regenerate a new API key in Domain Manager website.
This will make your current API key obsolete.

## Endpoints ##

You can make requests to the following list of API endpoints
to interact with Domain Manager

- `/applications/`
  - `GET`
    - Response: Array

- `/categories/`
  - `GET`
    - Response: Object

- `/domains/`
  - `GET`
    - Query Params
      - `?name=<domain-name>` optional
    - Response: Array

- `/domain/<domain-id>/`
  - `GET`
    - Response: Object

- `/domain/<domain_id>/launch/`
  - `GET`
    - Response: Message
  - `DELETE`
    - Response: Message

- `/domain/<domain_id>/generate/`
  - `POST`
    - Query Params
      - `?template_name=<template_name>`
    - Post Body

        ```json
            {
                "CompanyName": "<CompanyName>",
                "Phone": "<Phone>",
                "StreetAddress": "<StreetAddress>",
                "City": "<City>",
                "State": "<State>",
                "ZipCode": "<ZipCode>",
                "Email": "<Email>"
            }
        ```

    - Response: Message

- `/domain/<domain_id>/records/`
  - `GET`
    - Response: Array
  - `POST`

- Post Body

    ```json
        {
            "record_type": "<record_type>",
            "name": "<record_name>",
            "ttl": "<ttl>",
            "config": "<config>"
        }
    ```

  - Response: Message
  - `PUT`
    - Put Body

        ```json
            {
                "record_type": "<record_type>",
                "name": "<record_name>",
                "ttl": "<ttl>",
                "config": "<config>"
            }
        ```

    - Response: Message
  - `DELETE`
    - Response: Message

- `/templates/`
  - `GET`
    - Response: Array
  - `POST`

- Post Body

    ```json
        {
            "zip": "<zip_file_content>"
        }
    ```

  - Response: Message

- `/templates/attributes/`
  - `GET`
    - Response: Array
