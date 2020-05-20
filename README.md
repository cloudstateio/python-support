# Python User Language Support
Python User Language Support for [Cloudstate](https://github.com/cloudstateio/cloudstate).

## Installation via source

```
> git clone https://github.com/cloudstateio/python-support.git
Cloning into 'python-support'...

> cd python-support
> python3 -m venv ./venv 
> source ./venv/bin/activate
> python --version     
Python 3.7.3
> pip --version 
> pip install -r requirements.txt
```

### generate installer
```
./venv/bin/python3 setup.py bdist_wheel
```

### local install
```
./venv/bin/python3 -m pip install dist/cloudstate-0.5.0-py3-none-any.whl
```