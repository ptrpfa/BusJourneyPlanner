# 🚌 CSC1108 (Group 7) Journey Planner
Journey Planning application designed to enable commuters to plan their journey across Johor Bahru, Malaysia using the state's free bus service, Bas Muafakat Johor ([BAJ](https://paj.com.my/bas-muafakat-johor/)).

## Team Members
- Peter Febrianto Afandy​ (2200959)​​
- Adrian Pang Zi Jian​ (2200692)​​
- Muhammad Nur Dinie Bin Aziz (2200936)​​
- Ryan Lai Wei Shao (2201159)​​
- Jeffrey Yap Wan Lin​ (2200692)​


## List of Contents
- [Project Scope & Assumptions](#project-scope--assumptions)
- [System Design](#system-design)
- [Features](#features)
- [Project Components](#project-components)
- [Getting Started](#getting-started)
- [Program Usage](#program-usage)

## Project Scope & Assumptions
---
Due to the complexity of designing a bus journey planning application, this application is limited to providing bus route planning for the following bus services (as defined in the project specifications provided):
- Loop Services
    - P101 – Larkin Terminal ⊃ Johor Bahru City
        - Start: Larkin Terminal
        - End: Larkin Terminal
    - P106 – PPR Sri Stulang ⊃ AEON Tebrau City
        - Start: Hub PPR Sri Stulang
        - End: Hub PPR Sri Stulang
    - P202 – Taman Universiti ⊃ Taman Ungku Tun Aminah
        - Start: Taman Universiti Terminal
        - End: Taman Universiti Terminal
    - P403 – Econsave Senai ⊃ Skudai Parade
        - Start: Econsave Senai
        - End: Econsave Senai
- One-Way Services
    - P102 – PPR Sri Stulang ⇔ Majlis Bandaraya Johor Bahru
        - P102-01
            - Start: Hub PPR Sri Stulang
            - End: Majlis Bandaraya Johor Bahru
        - P102-02
            - Start: Majlis Bandaraya Johor Bahru
            - End: Hub PPR Sri Stulang
    - P211 – Taman Universiti ⇔ Larkin Terminal
        - P211-01
            - Start: Taman Universiti Terminal
            - End: Larkin Terminal
        - P211-02
            - Start: Larkin Terminal
            - End: Taman Universiti Terminal
    - P411 – Kulai ⇔ Larkin Terminal
        - P411-01
            - Start: Kulai Terminal
            - End: Larkin Terminal
        - P411-02
            - Start: Larkin Terminal
            - End: Kulai Terminal

The following bus stops were excluded (*instructed to ignore bus stops in the dataset*):
- KFC (Road side)
    - P202
- Tesco Lotus (Road side)
    - P202
- bef Jalan Kempas Lama
    - P211-01
    - P411-01

The following assumptions were also taken to simplify the development of the application:
1. Assume all bus service information (ie coordinates) provided in the `bus_stop.xlsx` dataset are correct (minor corrections were made).
2. Assume all buses will adhere to the specified bus schedule every day of the week, not taking into account any other factors (ie bus breakdowns).
3. Assume all buses will travel at the normal speed of `70km/h`.

## System Design
---
This application consists of the following components:
1. Database (GCP Cloud server)
2. Flask Web Application

This application utilises a MySQL database hosted on the cloud through the [Google Cloud Platform](https://cloud.google.com/sql). However, the application also supports the use of a local MySQL database, should the cloud server be unavailable. 

The main user interface for this application is deployed using the [Flask](https://flask.palletsprojects.com/en/2.2.x/) Python web framework. The Flask application is responsible for getting all user inputs, the processing of the path to a given destination, and displaying the results to the user.

## Features
---
<u>Database</u><br>
A MySQL database was designed to store the bus route information. The database design is provided in the Entity Relationship Diagram below.
![Database Design](docs/database.png)
A high level overview of each table in the database is provided below:
- Bus
    - BusID (Primary Key)
    - Name
    - Type
        - `1`: One-way
        - `2`: Loop
    - StartBusStopID
    - EndBusStopID
- Bus Route (Bus to Bus Stop mappings)
    - RouteID (Primary Key)
    - BusID
    - BusStopID
    - StopOrder
        - `-1` : Loop
        - `1, 2, ...` : Increment from 1 onwards
- Schedule
    - ScheduleID (Primary Key)
    - RouteID
    - Time
- Bus Stop
    - BusStopID (Primary Key)
    - Name
    - Longitude
    - Latitude
- Edge (Bus Stop Connection)
    - EdgeID (Primary Key)
    - FromBusStopID
    - ToBusStopID
    - RouteID
- Weight
    - WeightID (Primary Key)
    - EdgeID
    - Weight
    - Type
        - `1`: Distance
        - `2`: Duration

<u>Pengangkutan Awam Johor (PAJ) API</u><br>
The API provided by Malaysia's (Johor) public transportation provider, [PAJ](https://dataapi.paj.com.my/) is used during the initial population of data into the database, and the planning of routes (specifically live bus data).

<u>Google Maps API</u><br>
The [API](https://developers.google.com/maps) provided by Google Maps is used, specifically for the calculation of distances between bus stops, as well as general wayfinding to the starting bus stop and to the destination point during the last mile connectivity.


## Project Components
---
```
README.md (this file)

requirements.txt (program dependencies)

crawler/ (contains crawler programs)

flask_application/ (contains user interface programs)

docs/ (contains documentation images)

```
There are two main components/folders for this project:
1. Crawler
    - Used for getting initial Bus and Bus Stop information from various sources, including the dataset provided, [BusInterchange ](https://businterchange.net/johorbus.html) website, and the API provided by Malaysia's (Johor) public transportation provider, Perbadanan Pengangkutan Awam Johor ([PAJ](https://dataapi.paj.com.my/)).
    - Programs in this folder are generally not required to be executed as the necessary information have already been obtained, unless you are planning on setting up the database from scratch again. More instructions will be provided in the [program usage](#program-usage) section below.
2. Flask Application
    - Used to run the main user interface for the Journey Planner application.
    - This folder holds all necessary program components for getting the user's inputs, processing the path to a given destination, and outputting the results.

## Getting Started
---
1. Download all required [files and folders](#project-components) for this project.
2. Ensure that you have `python3` and `pip3` installed on your machine. Click [here](https://www.python.org/downloads/) for installation instructions if they are not already installed.
3. Install the necessary program dependencies for this project by running the following command on a terminal:
    ```
    pip3 install -r requirements.txt
    ```
    **Ensure that you are in the same working directory as the program files*


## Program Usage
---
### <u>Initial Project Setup</u>
This project utilises a Cloud MySQL database that have already been pre-configured for use. You can **skip this section** if you don't plan on re-crawling and setting up the database again from scratch.

If you plan on just setting up a local MySQL database, follow the instructions [here](#local-database-configurations). <br>
If you plan on setting up the entire database from scratch, follow the instructions [here](#full-database-setup). 

#### Local Database Configurations
---
Follow the instructions below to setup a local database for the application:
1. Ensure that you have installed MySQL on your machine. For installation instructions, click [here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/).
2. On a terminal, run the following command to import the pre-configured database:
    ```
    mysql -u<username> -p < crawler/sql/DB_24March2023.sql
    ```
3. Modify the configuration file in `flask_application` to connect to the local database instead of the cloud database. The following changes are required:
    ```
    db_host = "localhost"
    db_user = "username"
    db_password = "password"
    db_schema = "DSA_JP" (Generally unchanged, unless your schema has a different name)
    ```

#### Full Database Setup
---
Follow the instructions below to setup an empty database, and populate it with crawled data for the application:
1. Ensure that you have installed MySQL on your machine. For installation instructions, click [here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/).
2. On a terminal, run the following command to create the bare bone database (with no data):
    ```
    mysql -u<username> -p < crawler/sql/DB_NoData.sql
    ```
3. Ensure that the following program flags are set to `True` in the crawler's configuration file (`crawler/config.py`):
    ```
    # Program Flags
    LOCAL_DB = True
    CRAWL_API = True       
    CRAWL_WEB = True       
    UPDATE_DB = True       
    UPDATE_EDGES = True    
    UPDATE_WEIGHTS = True 
    ```
4. Create a copy of the `local_config_bak.py` local database configuration file
    ```
    cp crawler/local_config_bak.py crawler/local_config.py
    ```

5. Enter your local database's configurations into the `local_config.py` file. The following information should be included:
    ```
    db_host = "localhost"
    db_user = "username"
    db_password = "password"
    db_schema = "DSA_JP" (Generally unchanged, unless your schema has a different name)
    ```
6. Execute the crawler program (`crawl.py`) to obtain the required information using the following command on a terminal: <br>
    **Ensure that you are in the `crawler/` working directory*
    ```
    python3 crawl.py
    ```
    
    A sample output of the program's execution is provided below. You can ignore HTTP request warnings. 
    ![Crawler Program Sample Execution](docs/crawl_output.png)
7. Modify the configuration file in `flask_application` to connect to the local database instead of the cloud database. The following changes are required:
    ```
    db_host = "localhost"
    db_user = "username"
    db_password = "password"
    db_schema = "DSA_JP" (Generally unchanged, unless your schema has a different name)
    ```
### Program Execution
1. Run the Flask application using the following command on a terminal:
    <br>**Ensure that you are in the same working directory as the program files*
    ```
    python3 flask_application/run.py 
    ```
2. Navigate to [`localhost:8080`](http://localhost:8080) on your browser, and start journey planning!