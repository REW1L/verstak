# verstak 0.0.15
Program for creation of html document from docx.

### Usage
Script `verstak` will be available after installation.

Help for it is provided below. 
```
$ verstak --help
usage: verstak [-h] [-t] [-ah] [-st] [--config] [in] [out]

Make html from docx.

positional arguments:
  in          Input file/directory
  out         Output directory

optional arguments:
  -h, --help  show this help message and exit
  -t          Disable tipograf
  -st         Print stub instead of parsed tables
  -ah         Allow links in headers/titles
  --config    Show configs paths of tipograph currently in use
              VERSTAK_CONFIG environment variable can include path
              for additional configure file for tipograf
```

### How to install
For MacOS installation could be done with [Homebrew](https://brew.sh/)
```shell script
brew install rew1l/verstak/verstak
```
For other OS it could be done from sources.

### Patterns for tipograf
All default patterns are stored in .ini file which location
can be found by providing --config flag for verstak command.

Additional configuration file can be added with environment
variable VERSTAK_CONFIG
```
export VERSTAK_CONFIG=/home/user/tipograf_config.ini
verstak --config
Paths to configure files:
/.../verstak_parser/default_tipograf.ini
/home/user/tipograf_config.ini
```
Structure of file with configuration:

Configuration files have 2 types of sections:
1. [DEFAULT] section has NBSP definition and located
in default_tipograf.ini
2. [NBSP_*] [NOBR_*] [SPAN_*] sections:
    1. must have group and pattern fields
    2. group field defines number of the search group
    3. pattern field defines pattern to find
    4. must have unique name

Important! Tipograf works this way:
1. Adds NOBR
2. Replaces NBSP
3. Adds SPAN

Examples of patterns you can find in default_tipograf.ini 

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
