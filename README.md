# Design and implementation of a web application for contact data

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technologies](#technologies)
3. [Architecture](#architecture)
4. [Installation](#installation)


## Project Overview

This web application is designed for contact data management. It leverages Celery to handle data fetching from third-party APIs. 
To use the project's API, you must generate a Bearer Token and include it in the headers of your requests.

## Technologies 

- **Python 3.12.1**
- **Django 6.0.2**
- **Bootstrap 5.3.5**
- **Django Crispy Forms 2.5**
- **Django Rest Framework 3.16.1**
- **Django Rest Framework Simple Jwt 5.5.1**
- **Django Silk 5.4.3**
- **Crispy Bootstrap5 2025.6**
- **Celery 5.6.2**

## Architecture

The app includes REST API configurations and follows the MVT (Model-View-Template) architectural pattern.

- **Model: Defines the data structure and stores it in the SQLite database.**
- **View: Defines the logic of the app, handling user interactions and updating the database.**
- **Template: The front-end of the app, which shows the HTML and CSS content to the user.**


## Installation

To run the project locally, follow these steps:

1. Clone the repository:

```
git clone https://github.com/bartekuznik/Django_MVT_with_Celery.git
```

2. Run:

```
docker-compose up --build
```

3. After running docker-compose up, you need to create a superuser within the web container to log in. You can do this using the exec command:

```
docker-compose exec web python manage.py createsuperuser
```

