import glob
import os

PARAM_PREFERENCES_FILE_NAME = 'seaqt_prefs.json'

def clear_plots():
    '''
    Erase all plots from previous run(s).
    '''
    for i in range(1, 10):
        try:
            os.remove(f'Figures/{i}.png')
        except:
            pass

def clear_matlab_meta():
    '''
    Erase any files leftover from MATLAB run(s).
    '''
    for mat in glob.glob('tmp/*.mat'):
        try:
            os.remove(mat)
        except:
            pass

    for csv in glob.glob('tmp/*.csv'):
        try:
            os.remove(csv)
        except:
            pass

def clear_prefs():
    '''
    Erase the stored prefs from previous run(s)
    '''
    try:
        os.remove(PARAM_PREFERENCES_FILE_NAME)
    except:
        pass
