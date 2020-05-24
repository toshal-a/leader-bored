

# LeaderBored

## Requirements

* Python 3.7
* [Poetry](https://python-poetry.org/) for Python package and environment management.

### Python3.7 Installation
Installing Python 3.7 on Ubuntu with apt is a relatively straightforward process and will only take a few minutes:
1. Start by updating the packages list and installing the prerequisites:
```console
$ sudo apt update
$ sudo apt install software-properties-common
```
2.  Next, add the deadsnakes PPA to your sources list:
```console
$ sudo add-apt-repository ppa:deadsnakes/ppa
```
When prompted press  `Enter`  to continue:
```output
Output:-
Press [ENTER] to continue or Ctrl-c to cancel adding it.
```
3. Once the repository is enabled, install Python 3.7 with:
```console
$ sudo apt install python3.7
```
4.  At this point, Python 3.7 is installed on your Ubuntu system and ready to be used. You can verify it by typing:
```console
$ python3.7 --version
```
```output
Output:-
Python 3.7.3
```
5. Additional Python 3.7 virtual environments packages which must be installed in order to make **poetry** work:
```console
$ sudo apt install python3.7-venv
```
### Poetry Installation
Poetry is a tool for dependency management and packaging in Python. It allows you to declare the libraries your project depends on and it will manage (install/update) them for you.

```console
$ curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3.7
```
>Note:- There might be a issue of poetry creating a virtual environment based on python 2.7 version.
>There is a work around as stated below:-
* Add an alias to your ``.bashrc`` or similar at the end of the file and save it, like this:
```bash
alias poetry="python3.7 $HOME/.poetry/bin/poetry"
```

## Backend local development, additional details
By default, the dependencies are managed with [Poetry](https://python-poetry.org/), go there and install it.
``pyproject.toml`` file contains all the project dependencies present in the root directory of the project.

 One of the dependencies ``psycopg2`` requires additional packages: You can install it with:
```console
 $ sudo apt install libpq-dev python3.7-dev
 ```

 You can install all the dependencies with:
 ```console
 $ poetry install
 ```
 Then you can start a shell session with the new environment with:
 ```console 
 $ poetry shell
 ```
To run the app:
```console 
$ poetry run uvicorn leader_bored.asgi:app --reload
```
To test the APIs, head on to [localhost:8000/docs](localhost:8000/docs)
