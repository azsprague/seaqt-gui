## Steepest Entropy Ascent Quantum Thermodynamics (SEAQT) Graphical User Interface (GUI)

The SEAQT GUI is a tool designed to ...

### Run SEAQT GUI from Source

#### Download via GitHub
```
git clone https://github.com/azsprague/seaqt-gui
```

#### Python Version
Python >= 3.6 is required. You can check your python version using the following command:
```
python --version
```
Install the latest versions of python [here](https://www.python.org/downloads/).

#### Install Dependencies
Install required python packages using the following command:
```
pip install -r requirements.txt
```

#### Install MATLAB Engine for Python
To use SEAQT GUI with the MATLAB backend, you must first install the MATLAB engine for Python:
```
# Find your MATLAB root directory. This can be done in MATLAB using the command 'matlabroot'
# Default MATLAB directory: "\Program Files\MATLAB\<version>\"

# Change directories to the MATLAB engine for python
cd "\path\to\matlab\root\extern\engines\python"

# Install the engine
python setup.py install
```
Official installation instructions from MATLAB can be found [here](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).

#### Usage
The following command will start a standard interactive session:
```
python SEAQT.py
```
Use the `--help` flag for more usage information.
