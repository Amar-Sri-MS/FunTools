# Data analysis

This foler includes modules for analyzing data from FunOS.

## Environment setup

Conda (or pipenv, future work) is recommended for managing the environment.

To use the conda environment, run the following commands:

```bash 
# create conda env
conda env create -f ./environment.yml

# switch to conda env
conda activate data_analysis
```

Required modules are described in `requirements.txt`

To update the environment, run the following command to update `requirements.txt`:

```bash

pipreqsnb .

```

## Currently availble analysis

### FunOS module init time line analysis

Tools to analyze FunOS module initilization orders and durations.

This module contains utility functions for funos module init time analysis.
It parses the log files or dpcsh output json file and extract the module init time data.
It also contains utility functions to plot the data.

To run `PYTHONPATH` needs to be set to point where `dpcsh_interactive_client` modules are located.

```bash
export PYTHONPATH=$WORKSPACE/FunTools/data_analysis:$PYTHONPATH
```

- Example:
The following test example runs the module init time analysis on the log file and plots the data:

```bash
python3 funos_module_init_time_test.py

```

### FunOS memory cache (`mcache`)

## TODO

- move mcache analysis from dpcsh dir to here

### SDK API test code coverage analysis


## Tests

```bash

# run test
pytest

# show stdout
pytest -s

# run selected test
pytest tests/test_gen_func_cov.py -o log_cli=true

# generate coverage report
pytest --cov=gen_func_cov --cov-report html 
```
