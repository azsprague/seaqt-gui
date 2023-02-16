import argparse
import logging
import sys

from SEAQT_GUI import SEAQTGui


### Entry point ###
if __name__ == '__main__':
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Run SEAQT code.')
    parser.add_argument('-v', '--verbose', action='store_true', help='output debug messages to console')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] %(message)s')
    else:
        logging.basicConfig(stream=sys.stderr, level=logging.CRITICAL, format='[%(asctime)s] [%(levelname)s] %(message)s')

    # Build and run the GUI
    logging.info('Execution Beginning')

    seaqt_gui = SEAQTGui()
    seaqt_gui.run()

    logging.info('Execution Complete')
