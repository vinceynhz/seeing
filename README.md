![Stage](https://img.shields.io/badge/Stage-Proof%20of%20Concept-purple?style=flat)
![Language](https://img.shields.io/badge/Language-Python%203.8-green?style=flat)
![Language](https://img.shields.io/badge/Language-HTML%205-green?style=flat)
![Language](https://img.shields.io/badge/Language-Javascript%20ES6-green?style=flat)

## Seeing is believing...

This project involves generating 3D graph visualizations from domain-specific data, utilizing a general graph model that
can be expanded to include simplified visual properties, and using an interactive web-based render tool. 

The goal is to facilitate exploration of complex structured data.

## Architecture

<img src="https://github.com/vinceynhz/seeing/blob/a92b283312e549c391d49eb93e55ff143fa0e042/seeing-arch.draw.io.drawio.png" alt="architecture" width="800"/>

## Tech stack and installation

In the current stage this is a Python 3.8 application for the backend and HTML 5/CSS 3/JS ES 6 for the frontend.


Make sure the following is installed before setting up this in your local environment

### Python 3.8

Make sure the following python packages are installed as they are needed to install everything else.

* python3.8
* python3.8-venv
* python3.8-dev

See Python's official documentation for instructions on your own dev system. 

For Linux Mint (and other deb based OS)

```bash
sudo apt-get install python3.8 python3.8-venv python3.8-dev
```

### Upgrade pip

This is needed to avoid issues installing versions of libraries that might not be available if your pip is not up to date.

```bash
pip3 install --upgrade pip
```

### Graphviz

  * [Graphviz](https://pygraphviz.github.io/documentation/stable/install.html)

This might need to be installed as an application, including the pygraphviz package.
 
### Create a virtual environment
 
This is heavily recommended to avoid issues with other applications.
 
From the root of the project, where you cloned this repository.

```bash
python -m venv ./venv
source ./venv/bin/activate
```

### Install requirements

The project provides a list of all the dependencies for the backend that can be installed with pip

```bash
pip install -r requirements.txt
```

### Run the application

```bash
python main.py
```

Please note that the application needs to load the domain-specific data as well as prepare the taxonomy and domain 
compounds, this may take a couple of minutes before the service is fully stood up.

After this is complete, you should be able to access the frontend at http://localhost:5000/
