import argparse

from Frontend.Utils import clear_matlab_meta, clear_plots
from Frontend.SEAQT_GUI import SEAQTGui


### Entry point ###
if __name__ == '__main__':
    
    # Erase old plots and metadata from previous run(s)
    clear_plots()
    clear_matlab_meta()

    # Parse command-line arguments (none yet. TODO: pipeline?)
    parser = argparse.ArgumentParser(description='Run SEAQT code.')
    args = parser.parse_args()

    # Build and run the GUI
    SEAQTGui()
