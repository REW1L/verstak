# verstak 0.0.12
Program for creation of html document from docx.

### Usage
Script `verstak` will be available after installation.

Help for it is provided below. 
```
$ verstak --help
usage: verstak [-h] [-t] [-ah] in [out]

Make html from docx.

positional arguments:
  in          Input file/directory
  out         Output directory

optional arguments:
  -h, --help  show this help message and exit
  -t          Disable tipograf
  -ah         Allow links in headers/titles
```

### How to install
For MacOS installation could be done with [Homebrew](https://brew.sh/)
```shell script
brew install rew1l/verstak/verstak
```
For other OS it could be done from sources.

### How to install from sources using virtualenv

Requirements:
- python3.8

All commands should be executed from the root of the project.

Linux:
```
python3 -m venv venv
./venv/bin/activate
python3 setup.py install
```

Windows:
```
python -m venv venv
.\env\Scripts\activate.bat
python setup.py install
```

The same actions can be performed without virtualenv.
