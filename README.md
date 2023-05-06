## Steepest Entropy Ascent Quantum Thermodynamics (SEAQT) Graphical User Interface (GUI)

SEAQT framework/code provides a general thermodynamically rigorous determination of the equation of motion for nonequilibrium system state evolution. Utilizing the development of hypoequilibrium states and the density of state method for electrons and phonons, SEAQT can be applied from a practical standpoint at all temporal and spatial scales. This allows for a comprehensive evaluation of material properties (electrical conductivity, thermal conductivity, etc.) that current alternative methods cannot fully address.

Further discussion can be found in the file `Introduction.pdf`.


---

### Table of Contents

- [Changelog](#changelog)
- [Setup & Installation](#setup--installation)
    - [1. Download via Github](#1-download-via-github)
    - [2. Verify Python Version](#2-verify-python-version)
    - [3. Install Dependencies](#3-install-dependencies)
    - [4. Install MATLAB Engine for Python](#4-install-matlab-engine-for-python)
    - [5. Invocation](#5-invocation)
- [Running & Example Data](#running--example-data)
    - [Home Screen](#home-screen)
    - [New Runs](#new-runs)
    - [Plotting](#plotting)
    - [Export Plots](#export-plots)
    - [Save & Load Runs](#save--load-runs)
    - [Other Functionality](#other-functionality)
- [Frequently Asked Questions (FAQs)](#frequently-asked-questions-faqs)

---

### Changelog
| Version |   Date   |        Notes       |
| :-----: | :------: | :----------------: |
|   1.0   | 05.05.23 | First Full Release |

---


### Setup & Installation

#### 1. Download via GitHub
If needed, install the latest versions of git [here](https://git-scm.com/downloads). Clone the repository using the following command:
```
git clone https://github.com/azsprague/seaqt-gui
```
Alternatively, the code can be downloaded as a `zip` file by selecting `Code -> Download ZIP` or by clicking [here](https://github.com/azsprague/seaqt-gui/archive/refs/heads/main.zip).


#### 2. Verify Python Version
Python >= 3.6 is required. You can check your python version using the following command:
```
python --version
```
Install the latest versions of python [here](https://www.python.org/downloads/).


#### 3. Install Dependencies
Ensure you are in the directory containing the SEAQT GUI code (i.e., `cd seaqt-gui`). Install the required python packages using the following command:
```
pip install -r requirements.txt
```


#### 4. Install MATLAB Engine for Python
To use SEAQT GUI with the MATLAB backend, you must first install the MATLAB engine for Python:
```
# Find your MATLAB root directory. This can be done in MATLAB using the command 'matlabroot'
# - Default Windows MATLAB directory: "\Program Files\MATLAB\<version>\"
# - Default MacOS MATLAB directory: "/Applications/MATLAB_<version>/"
# - Default Linux MATLAB directory: "/usr/local/MATLAB_<version>/"

# Change directories to the MATLAB engine for python
cd "\<path>\<to>\<matlab>\<root>\extern\engines\python"

# Install the engine
python setup.py install
```
Official installation instructions from MATLAB can be found [here](https://www.mathworks.com/help/matlab/matlab_external/install-the-matlab-engine-for-python.html).


#### 5. Invocation
The following command will start a standard interactive session:
```
python SEAQT.py
```
Use the `--help` flag for more usage information.


---

### Running & Example Data

#### Home Screen
After invoking SEAQT GUI, you will be greeted by the home screen. Here you have the option to perform a new run or load data from a previous run.

![Home Screen](Figures/Home%20Screen.png)


#### New Runs
When inputting data for a new run, make sure all fields not labeled "optional" are filled. The directory `Example Data` contains both sample input files and parameters; these can be automatically imported by clicking the `Import Default Data and Parameters` button.

After clicking "Run", the SEAQT backend will begin processing all data files and parameters. **During this time the GUI may seem unresponsive, but it *is* working**. Depending on you run length and type, this process may take a long time (and significant system resources).

![New Run](Figures/New%20Run.png)


#### Plotting
After processing (or loading, discussed later) data, several graphs can be generated. The specific blocks to be plotted must be selected on the bottom right side, then clicking the `Plot` button will generate the plots (**this may take a few seconds**).

![Plotting 1](Figures/Plotting%201.png)

When the plotting is complete, you can select which plot to display by clicking on the radio buttons on the top right side. If you'd like to replot using different blocks, simply select the blocks you'd like to plot and click the `Plot` button again.

![Plotting 2](Figures/Plotting%202.png)


#### Export Plots
If you would like to save the plots you've generated, click the `Export` button to open a window to select a destination and which plots to export. Plots will be named as "PlotName_Timestamp.png" by default.

![Save Plots](Figures/Save%20Plots.png)


#### Save & Load Runs
SEAQT runs can be saved and loaded by using the `Save` and `Load` buttons, respectively. This was created to save time for subsequent runs. The file format is a `.zip` archive containing data produced from the backend along with the parameters inputted to the GUI.


#### Other Functionality
The `Reset` button will delete any generated data and return all input parameters to their default value. The `Help` button will direct you to this Git repo. The `Exit` button will close the GUI.


---

### Frequently Asked Questions (FAQs)
Q. *The GUI is not responding to inputs and says "Not Responding" at the top?*
A. This is likely because the SEAQT backend is currently running. Depending on your inputted run length and type, this process may take a while.

Q. *The SEAQT backend completed but states the data may be corrupted / the plots are empty?*
A. Many times this can occur when the run length is not sufficiently long enough. Try running with a longer run length or switch to `Max(tau)` instead of `Min(tau)`. If the problem persists, please create a ticket at [here](https://github.com/azsprague/seaqt-gui/issues).

Q. *When I run the SEAQT backend with a large run length, my system slows down significantly?*
A. The longer the run length, the more RAM / memory the SEAQT backend will require, which can lead to a slowing-down of your system.
