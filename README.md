## Steepest Entropy Ascent Quantum Thermodynamics (SEAQT) Graphical User Interface (GUI)

SEAQT framework/code provides a general thermodynamically rigorous determination of the equation of motion for nonequilibrium system state evolution. Utilizing the development of hypoequilibrium states and the density of state method for electrons and phonons, SEAQT can be applied from a practical standpoint at all temporal and spatial scales. This allows for a comprehensive evaluation of material properties (electrical conductivity, thermal conductivity, etc.) that current alternative methods cannot fully address.

Further discussion can be found in `Introduction.pdf`.

---

### Changelog
| Version |   Date   |        Notes       |
| :-----: | :------: | :----------------: |
|   1.0   | 03.23.23 | First Full Release |

---

### Run SEAQT GUI from Source

#### Download via GitHub
Clone the repository using the following command:
```
git clone https://github.com/azsprague/seaqt-gui
```
Install the latest versions of git [here](https://git-scm.com/downloads).


#### Verify Python Version
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
