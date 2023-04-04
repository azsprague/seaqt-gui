import json
import os

from enum import IntEnum
from shutil import copyfile
import time
from typing import Tuple
from functools import partial
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from PIL import Image, ImageTk
from zipfile import ZipFile

from Frontend.MATLAB_Backend_Handler import MATLABBackendHandler
from Frontend.Utils import clear_matlab_meta, clear_plots


class PlotNumber(IntEnum):
    '''
    Enum to map plot name to a number for faster acquisition.
    '''
    INVALID = -1,
    UNKNOWN = 0,
    ELECTRON_TEMPERATURE = 1,
    ELECTRON_NUMBER = 2,
    ELECTRON_ENERGY = 3,
    ELECTRICAL_CONDUCTIVITY = 4,
    SEEBECK_COEFFICIENT = 5,
    PHONON_TEMPERATURE = 6,
    PHONON_ENERGY = 7,
    THERMAL_CONDUCTIVITY = 8,
    ZT_FACTOR = 9,
    DATA_NOT_LOADED = 400,
    DATA_PROCESSING = 401,
    DATA_PROCESSED_SUCCESSFULLY = 402,
    DATA_LOADED_SUCCESSFULLY = 403,
    ERROR = 999


class TimeType(IntEnum):
    '''
    Enum to map time type to a number for faster acquisition.
    '''
    INVALID = -1,
    UNKNOWN = 0,
    MIN = 1,
    MAX = 2,


class RunType(IntEnum):
    '''
    Enum to map run type to a number for faster acquisition.
    '''
    INVALID = -1,
    UNKNOWN = 0,
    ELECTRON = 1,
    PHONON = 2,
    BOTH = 3


class SEAQTGui():
    '''
    GUI class for SEAQT handler.
    '''

    # Class ('global') constants
    FRAME_PAD_X = 5
    FRAME_PAD_Y = 5

    ENTRY_PAD_X = 5
    ENTRY_PAD_Y = 2

    LOAD_LAST_RUN_BUTTON_WIDTH = 50

    SEAQT_RUN_FILETYPE = (
        ('SEAQT Run Archive', '*.seaqt'),
    )

    SEAQT_RUN_FILENAMES = [
        'Time_Evolution.mat',
        'System_description.mat',
        'seaqt_prefs.json'
    ]

    INPUT_FRAME_PAD_X = 15
    INPUT_FRAME_PAD_Y = 7
    INPUT_DATA_BUTTON_WIDTH = 10
    INPUT_DATA_LABEL_WIDTH = 20
    INPUT_DATA_ENTRY_WIDTH = 50
    INPUT_DATA_FILETYPES = (
        ('Excel Spreadsheet', '*.xlsx'),
        ('Comma-Separated Values', '*.csv')
    )

    INPUT_PARAMETER_LABEL_WIDTH = 33
    INPUT_PARAMETER_ENTRY_WIDTH = 50
    INPUT_PARAMETER_INNER_FRAME_PAD_Y = 5
    INPUT_BOTTOM_BUTTON_PAD_X = 5

    DATA_VIEW_FRAME_WIDTH = 850
    DATA_VIEW_FRAME_HEIGHT = 700
    DATA_VIEW_FRAME_PAD_X = 5
    DATA_VIEW_FRAME_PAD_Y = 25

    MENU_FRAME_PAD_X = 10
    MENU_FRAME_PAD_Y = 10
    MENU_BUTTON_WIDTH = 10
    MENU_BUTTON_PAD_X = 5
    MENU_BUTTON_PAD_Y = 15

    PLOT_BUTTON_PAD_Y = 3

    DEFAULT_NUM_BLOCKS = 10
    DEFAULT_SUB_SIZE = 1 * (10**-7)
    DEFAULT_SUB_TEMP = 300
    DEFAULT_FERMI = 6

    DEFAULT_ELECTRON_VELOCITIES = 6000
    DEFAULT_ELECTRON_RELAXATION = 50 * (10**-16)
    DEFAULT_ELECTRON_EFFECTIVE_MASS = 1

    DEFAULT_PHONON_VELOCITIES = 6000
    DEFAULT_PHONON_RELAXATION = 5 * (10**-12)
    
    DEFAULT_TIME_DURATION = 100
    DEFAULT_TIME_TYPE = TimeType.MIN.value
    DEFAULT_RUN_TYPE = RunType.BOTH.value

    TEMP_DIRECTORY_PATH = 'tmp'
    PARAM_PREFERENCES_FILE_NAME = 'seaqt_prefs.json'

    PLOT_NAMES = [
        'Electron Temperature',
        'Electron Number',
        'Electron Energy',
        'Electrical Conductivity',
        'Seebeck Coefficient',
        'Phonon Tempertaure',
        'Phonon Energy',
        'Thermal Conductivity',
        'ZT Factor'
    ]


    def __init__(self):
        '''
        Class constructor; create a SEAQTGui object, instantiate global variables, and start the main menu.
        '''
        # Initialize the backend handler
        try:
            self.prefs_file_path = os.path.join(self.TEMP_DIRECTORY_PATH, self.PARAM_PREFERENCES_FILE_NAME)
            self.backend = MATLABBackendHandler(self.prefs_file_path)
        except:
            self.pop_up_error('SEAQT Backend Encountered an Error.\n\nThis is likely due to a faulty or corrupted installation, but could also be an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
            return

        # Create the Tkinter root window
        self.tkinter_root = Tk()
        self.tkinter_root.title('SEAQT GUI')
        self.tkinter_root.resizable(False, False)

        # Data input files (class variables)
        self.electron_ev_file_path = StringVar()
        self.electron_dos_file_path = StringVar()
        self.electron_tau_file_path = StringVar()

        self.phonon_ev_file_path = StringVar()
        self.phonon_dos_file_path = StringVar()
        self.phonon_tau_file_path = StringVar()

        # Data output directory (class variable)
        self.export_directory = StringVar()
        
        # Runtime parameters (class variables)
        self.number_of_blocks = IntVar(value=self.DEFAULT_NUM_BLOCKS)               # scalar
        self.time_duration = DoubleVar(value=self.DEFAULT_TIME_DURATION)                    # scalar
        self.selected_time_type = IntVar(value=self.DEFAULT_TIME_TYPE)                      # 'min' or 'max'
        self.fermi_energy = DoubleVar(value=self.DEFAULT_FERMI)                             # eV * 1.60218 * (10**-19) Joules
        self.electron_group_velocities = DoubleVar(value=self.DEFAULT_ELECTRON_VELOCITIES)  # m/s
        self.electron_relaxation_time = DoubleVar(value=self.DEFAULT_ELECTRON_RELAXATION)   # seconds
        self.electron_effective_mass = DoubleVar(value=self.DEFAULT_ELECTRON_EFFECTIVE_MASS)
        self.phonon_group_velocities = DoubleVar(value=self.DEFAULT_PHONON_VELOCITIES)      # m/s
        self.phonon_relaxation_time = DoubleVar(value=self.DEFAULT_PHONON_RELAXATION)       # seconds
        self.subsystem_size = DoubleVar(value=self.DEFAULT_SUB_SIZE)                        # meters
        self.subsystem_temperature = DoubleVar(value=self.DEFAULT_SUB_TEMP)                # Kelvin    
        
        self.selected_subsystems = []                                                   

        self.selected_subsystem_input = IntVar(value=1)
        self.subsystem_radio_buttons = []

        self.block_to_copy_from = IntVar(value=1)
        self.selected_run_type = IntVar(value=self.DEFAULT_RUN_TYPE)
        self.run_type_buttons = []

        self.input_json_dict = {}

        # Menu buttons (class variables)
        self.new_run_button = None
        self.load_run_button = None
        self.reset_button = None
        self.save_button = None
        self.export_button = None

        # Plot radio buttons (class variables)
        self.plot_radio_buttons = []
        self.selected_plot = IntVar(value=PlotNumber.ELECTRON_TEMPERATURE.value)
        self.data_frame_image_frame = None
        self.data_frame_image = None

        self.time_radio_buttons = []
        
        # Subsystem checkbuttons (class variables)
        self.subsystem_variables = []
        self.subsystem_checkbuttons = []
        self.plot_button = None

        # Export variables
        self.plot_variables = []
        self.plot_checkbuttons = []
        self.selected_plots = []

        # Run the GUI
        self.activate_main_window()
        self.tkinter_root.mainloop()


    def activate_main_window(self) -> None:
        '''
        Create the 'main menu' of the GUI, including the data view, plot, and menu buttons.
        '''
        #############################
        # Start frame for menu view #
        #############################

        # Create menu option frame
        menu_option_frame = ttk.LabelFrame(
            self.tkinter_root,
            text='Menu',
            padding=10,
            relief=SOLID
        )
        menu_option_frame.grid(column=0, row=0, padx=self.MENU_FRAME_PAD_X, pady=self.DATA_VIEW_FRAME_PAD_Y, sticky=N)

        # New run button
        self.new_run_button = ttk.Button(
            menu_option_frame,
            text='New',
            command=self.activate_input_data_window,
            width=self.MENU_BUTTON_WIDTH
        )
        self.new_run_button.grid(column=0, row=0, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Load run button
        self.load_run_button = ttk.Button(
            menu_option_frame,
            text='Load',
            command=self.load_previous_run,
            width=self.MENU_BUTTON_WIDTH
        )
        self.load_run_button.grid(column=0, row=1, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Reset run button
        self.reset_button = ttk.Button(
            menu_option_frame,
            text='Reset',
            command=self.reset_data_process,
            state=DISABLED,
            width=self.MENU_BUTTON_WIDTH
        )
        self.reset_button.grid(column=0, row=2, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Save run button
        self.save_button = ttk.Button(
            menu_option_frame,
            text='Save',
            command=self.save_data,
            state=DISABLED,
            width=self.MENU_BUTTON_WIDTH
        )
        self.save_button.grid(column=0, row=3, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Export graphs button
        self.export_button = ttk.Button(
            menu_option_frame,
            text='Export',
            command=self.export_data,
            state=DISABLED,
            width=self.MENU_BUTTON_WIDTH
        )
        self.export_button.grid(column=0, row=4, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Help button
        ttk.Button(
            menu_option_frame,
            text='Help',
            command=self.activate_help_window,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=5, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Exit Button
        ttk.Button(
            menu_option_frame,
            text='Exit',
            command=self.exit_button,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=6, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Copyright
        ttk.Label(
            self.tkinter_root,
            text='© 2023'
        ).grid(column=1, row=1)

        ###############################
        # Start frame for Right Panel #
        ###############################

        # Create right panel
        right_menu_frame = ttk.Frame(
            self.tkinter_root,
            padding=10
        )
        right_menu_frame.grid(column=2, row=0, padx=10, pady=15, sticky=N)

        #################################
        # Start frame for Radio Buttons #
        #################################

        # Create radio button frame
        radio_button_frame = ttk.LabelFrame(
            right_menu_frame,
            text='Select Plot',
            padding=10,
            relief=SOLID
        )
        radio_button_frame.grid(column=0, row=0, pady=5)

        # Create radio buttons
        for i in range(len(self.PLOT_NAMES)):
            rb = ttk.Radiobutton(
                radio_button_frame,
                text=self.PLOT_NAMES[i],
                variable=self.selected_plot,
                value=i + 1,
                command=partial(self.update_plot, i + 1),
                state=DISABLED
            )
            rb.grid(column=0, row=i, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
            self.plot_radio_buttons.append(rb)

        #######################################
        # Start frame for subsystem selection #
        #######################################

        # Create subsystem selection frame
        subsystem_selection_frame = ttk.LabelFrame(
            right_menu_frame,
            text='Blocks to Plot',
            padding=10,
            relief=SOLID
        )
        subsystem_selection_frame.grid(column=0, row=1, pady=5)

        # Frame to hold the checkboxes
        checkbox_frame = ttk.Frame(
            subsystem_selection_frame
        )
        checkbox_frame.grid(column=0, row=0, sticky=N)

        # Create a subsystem button for the number of selected subsystems
        num_subsystems = self.number_of_blocks.get()
        for i in range(num_subsystems):
            subsystem_variable = IntVar(checkbox_frame, 0)
            self.subsystem_variables.append(subsystem_variable)

            check_btn = ttk.Checkbutton(
                checkbox_frame,
                text=f'{i + 1}',
                variable=subsystem_variable,
                onvalue=1,
                offvalue=0,
                state=DISABLED
            )
            check_btn.grid(column=(i // (num_subsystems // 2)) % 2, row=i % (num_subsystems // 2), padx=17, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
            self.subsystem_checkbuttons.append(check_btn)

        # Button to replot given selected systems
        self.plot_button = ttk.Button(
            subsystem_selection_frame,
            text='Plot',
            command=self.replot,
            state=DISABLED
        )
        self.plot_button.grid(column=0, row=1, pady=5, sticky=N)

        #############################
        # Start frame for data view #
        #############################

        # Create data view frame
        s = ttk.Style()
        s.configure('white.TFrame', background='white')
        data_view_frame = ttk.Frame(
            self.tkinter_root,
            padding=10,
            width=self.DATA_VIEW_FRAME_WIDTH,
            height=self.DATA_VIEW_FRAME_HEIGHT,
            relief=SOLID,
            style='white.TFrame'
        )
        data_view_frame.grid(column=1, row=0, padx=self.DATA_VIEW_FRAME_PAD_X, pady=self.DATA_VIEW_FRAME_PAD_Y, sticky=N)
        data_view_frame.grid_propagate(False)

        # Create data image (default "no data loaded")
        self.data_frame_image_frame = ttk.Label(
            data_view_frame,
            justify=CENTER
        )
        self.data_frame_image_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.update_plot(PlotNumber.DATA_NOT_LOADED.value)


    def activate_input_data_window(self) -> None:
        '''
        Collect input data files and important parameters from the user.
        ''' 
        # Create a new pop-up window and take control of input
        input_window = Toplevel(self.tkinter_root)
        input_window.title('Load Data and Set Parameters')
        input_window.resizable(False, False)
        input_window.grab_set()
        # input_window.grid_columnconfigure(0, weight=1)
        # input_window.grid_columnconfigure(1, weight=1)

        ###################################
        # Start frame for Base Parameters #
        ###################################

        top_window = ttk.Frame(
            input_window,
            padding=10
        )
        top_window.grid(column=0, row=0)

        # Create base parameter frame
        base_parameter_input = ttk.LabelFrame(
            top_window,
            text='Base Parameters',
            padding=10,
            relief=SOLID
        )
        base_parameter_input.grid(column=0, row=0, padx=5, pady=5)

        # Number of subsystems label
        ttk.Label(
            base_parameter_input,
            text='Number of Blocks',
            width=17
        ).grid(column=0, row=0)

        # Number of subsystems input (spinbox)
        ttk.Spinbox(
            base_parameter_input,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.number_of_blocks,
            justify=CENTER,
            width=5
        ).grid(column=1, row=0, padx=12, sticky=W)

        # Run length Label
        ttk.Label(
            base_parameter_input,
            text='Run Length',
            width=17
        ).grid(column=0, row=1)

        # Create time parameter frame
        time_parameter_frame = ttk.Frame(
            base_parameter_input,
            padding=10
        )
        time_parameter_frame.grid(column=1, row=1);

        # Run length input
        ttk.Entry(
            time_parameter_frame,
            textvariable=self.time_duration,
            justify=CENTER,
            width=5
        ).grid(column=0, row=0, padx=2, sticky=W)

        # Times sign
        ttk.Label(
            time_parameter_frame,
            text="X",
            justify=CENTER,
        ).grid(column=1, row=0)

        # Radio button for min time
        rb1 = ttk.Radiobutton(
            time_parameter_frame,
            text='Min(tau)',
            variable=self.selected_time_type,
            value=TimeType.MIN.value
        )
        rb1.grid(column=2, row=0, padx=2)
        self.time_radio_buttons.append(rb1)

        # Radio button for max time
        rb2 = ttk.Radiobutton(
            time_parameter_frame,
            text='Max(tau)',
            variable=self.selected_time_type,
            value=TimeType.MAX.value
        )
        rb2.grid(column=3, row=0, padx=2)
        self.time_radio_buttons.append(rb2) 

        ttk.Label(
            base_parameter_input,
            text='Run Type',
            width=17
        ).grid(column=0, row=2)

        run_type_frame = ttk.Frame(
            base_parameter_input
        )
        run_type_frame.grid(column=1, row=2)

        electron_rb = ttk.Radiobutton(
            run_type_frame,
            text='Electron',
            variable=self.selected_run_type,
            value=RunType.ELECTRON.value
        )
        electron_rb.grid(column=0, row=0, padx=2)
        self.run_type_buttons.append(electron_rb)

        phonon_rb = ttk.Radiobutton(
            run_type_frame,
            text='Phonon',
            variable=self.selected_run_type,
            value=RunType.PHONON.value
        )
        phonon_rb.grid(column=1, row=0, padx=2)
        self.run_type_buttons.append(phonon_rb)

        both_rb = ttk.Radiobutton(
            run_type_frame,
            text='Both',
            variable=self.selected_run_type,
            value=RunType.BOTH.value
        )
        both_rb.grid(column=2, row=0, padx=2)
        self.run_type_buttons.append(both_rb)

        ########################
        # Start frame for info #
        ########################   

        # Create frame
        info_frame = ttk.LabelFrame(
            top_window, 
            text='Info',
            padding=10,
            relief=SOLID
        )
        info_frame.grid(column=1, row=0, padx=5, pady=5, sticky=N)

        # Create info
        ttk.Label(
            info_frame,
            text='Block: a pair of local systems (electron & phonon)\n\nTau: the relaxation parameter'
        ).grid(column=0, row=0, sticky=NW)

        ##########################################
        # Start frame for subsystem master frame #
        ##########################################

        # Create master frame for subsystem data
        subsystem_master_frame = ttk.Frame(
            input_window,
            padding=10
        )
        subsystem_master_frame.grid(column=0, row=2)

        #############################################
        # Start frame for subsystem selection frame #
        #############################################

        # Create selection frame
        subsystem_selection_frame = ttk.LabelFrame(
            subsystem_master_frame,
            text='Block Selection',
            padding=10,
            relief=SOLID
        )
        subsystem_selection_frame.grid(column=0, row=0, padx=5, pady=5, sticky=N)

        # Radio buttons
        for i in range(self.number_of_blocks.get()):
            rb = ttk.Radiobutton(
                subsystem_selection_frame,
                text=f"Block {i + 1}",
                variable=self.selected_subsystem_input,
                value=i + 1
            )
            rb.grid(column=0, row=i, padx=3, pady=3, sticky=W)
            self.subsystem_radio_buttons.append(rb)

        #############################################
        # Start frame for subsystem parameter frame #
        #############################################

        # Create parameter frame
        subsystem_parameter_frame = ttk.LabelFrame(
            subsystem_master_frame,
            text="Block Data and Parameters",
            padding=10,
            relief=SOLID
        )
        subsystem_parameter_frame.grid(column=1, row=0, padx=5, pady=5)

        ########################################
        # Start frame for combined input frame #
        ########################################

        combined_input_frame = ttk.Frame(
            subsystem_parameter_frame
        )
        combined_input_frame.grid(column=0, row=0)

        # Give users the option to load preferences from last subsystem
        copy_input_frame = ttk.Frame(
            combined_input_frame,
            padding=10,
            relief=SOLID
        )
        copy_input_frame.grid(column=0, row=0, padx=5, pady=5)

        ttk.Label(
            copy_input_frame,
            text='Copy Inputs from Block:',
        ).grid(column=0, row=0, padx=5, pady=5)

        # 
        ttk.Spinbox(
            copy_input_frame,
            from_=1,
            to=self.number_of_blocks.get(),
            increment=1,
            textvariable=self.block_to_copy_from,
            justify=CENTER,
            width=5
        ).grid(column=1, row=0, padx=7, pady=5)

        ttk.Button(
            copy_input_frame,
            text='Copy',
            width=10
        ).grid(column=2, row=0, padx=5, pady=5)

        ###
        param_input_frame = ttk.Frame(
            combined_input_frame,
            padding=10,
            relief=SOLID
        )
        param_input_frame.grid(column=0, row=1, padx=5, pady=5)

        # Select subsystem size
        ttk.Label(
            param_input_frame,
            text='Block Size',
            width=20
        ).grid(column=0, row=0)

        ttk.Entry(
            param_input_frame,
            textvariable=self.subsystem_size,
            width=15
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            param_input_frame,
            text='m',
            width=20
        ).grid(column=2, row=0)

        # Select subsystem temperatures
        ttk.Label(
            param_input_frame,
            text='Block Temperature',
            width=20
        ).grid(column=0, row=1)

        ttk.Entry(
            param_input_frame,
            textvariable=self.subsystem_temperature,
            width=15
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)  

        ttk.Label(
            param_input_frame,
            text='K',
            width=20
        ).grid(column=2, row=1)    

        # Select Fermi energy (label, entry)
        ttk.Label(
            param_input_frame,
            text='Fermi Energy',
            width=20
        ).grid(column=0, row=2)

        ttk.Entry(
            param_input_frame,
            textvariable=self.fermi_energy,
            width=15
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            param_input_frame,
            text='eV  X  1.60218e-19 J',
            width=20
        ).grid(column=2, row=2)

        ############################
        # Start frame for notebook #
        ############################

        notebook = ttk.Notebook(
            subsystem_parameter_frame,
            padding=10
        )
        notebook.grid(column=0, row=1, padx=5, pady=5)

        ############################
        # Start frame for electron #
        ############################

        electron_frame = ttk.Frame(
            notebook
        )
        electron_frame.grid()

        ###############################
        # Start frame for file inputs #
        ###############################

        # Create file input frame
        electron_file_input_frame = ttk.Frame(
            electron_frame,
            padding=10
        )
        electron_file_input_frame.grid(column=0, row=0)

        # Select electron ev file (label, entry, button)
        ttk.Label(
            electron_file_input_frame,
            text='Electron EV Data',
            width=25
        ).grid(column=0, row=0)

        ttk.Entry(
            electron_file_input_frame, 
            textvariable=self.electron_ev_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            electron_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_ev_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH,
        ).grid(column=2, row=0, padx=5)

        # Select electron dos file (label, entry, button)
        ttk.Label(
            electron_file_input_frame,
            text='Electron DOS Data',
            width=25
        ).grid(column=0, row=1)

        ttk.Entry(
            electron_file_input_frame, 
            textvariable=self.electron_dos_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            electron_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_dos_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=1, padx=5)

        # Select electron tau file (label, entry, button)
        ttk.Label(
            electron_file_input_frame,
            text='Electron Tau Data (optional)',
            width=25
        ).grid(column=0, row=2)

        ttk.Entry(
            electron_file_input_frame, 
            textvariable=self.electron_tau_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            electron_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_tau_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=2, padx=5)

        ####################################
        # Start frame for parameter inputs #
        ####################################

        # Create parameter input frame
        electron_parameter_input_frame = ttk.Frame(
            electron_frame,
            padding=10
        )
        electron_parameter_input_frame.grid(column=0, row=1)

        # Select electron group velocities
        ttk.Label(
            electron_parameter_input_frame,
            text='Electron Group Velocities (optional)',
            width=35
        ).grid(column=0, row=0)

        ttk.Entry(
            electron_parameter_input_frame,
            textvariable=self.electron_group_velocities,
            width=15
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            electron_parameter_input_frame,
            text='m/s',
            width=20
        ).grid(column=2, row=0)

        # Select electron relaxation time
        ttk.Label(
            electron_parameter_input_frame,
            text='Electron Relaxation Time',
            width=35
        ).grid(column=0, row=1)

        ttk.Entry(
            electron_parameter_input_frame,
            textvariable=self.electron_relaxation_time,
            width=15
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            electron_parameter_input_frame,
            text='s',
            width=20
        ).grid(column=2, row=1)

        # Select electron effective mass time
        ttk.Label(
            electron_parameter_input_frame,
            text='Electron Effective Mass',
            width=35
        ).grid(column=0, row=2)

        ttk.Entry(
            electron_parameter_input_frame,
            textvariable=self.electron_effective_mass,
            width=15
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            electron_parameter_input_frame,
            text='X  9.109e-31 kg',
            width=20
        ).grid(column=2, row=2)

        ############################
        # Start frame for phonon #
        ############################

        phonon_frame = ttk.Frame(
            notebook
        )
        phonon_frame.grid()

        ###############################
        # Start frame for file inputs #
        ###############################

        # Create file input frame
        phonon_file_input_frame = ttk.Frame(
            phonon_frame,
            padding=10
        )
        phonon_file_input_frame.grid(column=0, row=0)

        # Select phonon ev file (label, entry, button)
        ttk.Label(
            phonon_file_input_frame,
            text='Phonon EV Data',
            width=25
        ).grid(column=0, row=0)

        ttk.Entry(
            phonon_file_input_frame, 
            textvariable=self.phonon_ev_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            phonon_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_ev_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=0, padx=5)

        # Select phonon dos file (label, entry, button)
        ttk.Label(
            phonon_file_input_frame,
            text='Phonon DOS Data',
            width=25
        ).grid(column=0, row=1)

        ttk.Entry(
            phonon_file_input_frame, 
            textvariable=self.phonon_dos_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            phonon_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_dos_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=1, padx=5)

        # Select phonon tau file (label, entry, button)
        ttk.Label(
            phonon_file_input_frame,
            text='Phonon Tau Data (optional)',
            width=25
        ).grid(column=0, row=2)

        ttk.Entry(
            phonon_file_input_frame, 
            textvariable=self.phonon_tau_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            phonon_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_tau_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=2, padx=5)

        ####################################
        # Start frame for parameter inputs #
        ####################################

        # Create parameter input frame
        phonon_parameter_input_frame = ttk.Frame(
            phonon_frame,
            padding=10
        )
        phonon_parameter_input_frame.grid(column=0, row=1)

        # Select phonon group velocities
        ttk.Label(
            phonon_parameter_input_frame,
            text='Phonon Group Velocities',
            width=35
        ).grid(column=0, row=0)

        ttk.Entry(
            phonon_parameter_input_frame,
            textvariable=self.phonon_group_velocities,
            width=15
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            phonon_parameter_input_frame,
            text='m/s',
            width=20
        ).grid(column=2, row=0)

        # Select phonon relaxation time
        ttk.Label(
            phonon_parameter_input_frame,
            text='Phonon Relaxation Time',
            width=35
        ).grid(column=0, row=1)

        ttk.Entry(
            phonon_parameter_input_frame,
            textvariable=self.phonon_relaxation_time,
            width=15
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Label(
            phonon_parameter_input_frame,
            text='s',
            width=20
        ).grid(column=2, row=1)

        ####
        notebook.add(electron_frame, text='Electron Local System')
        notebook.add(phonon_frame, text='Phonon Local System')

        ##################################
        # Start frame for bottom buttons #
        ##################################

        # Create frame for bottom buttons
        data_input_button_frame = ttk.Frame(
            input_window,
            padding=10
        )
        data_input_button_frame.grid(column=0, row=3, padx=5, pady=5)

        # Run button (all fields must be filled to confirm)
        ttk.Button(
            data_input_button_frame, 
            text='Run', 
            command=partial(self.confirm_data_input_and_run, input_window)
        ).grid(column=0, row=0, padx=5)

        # Cancel button
        ttk.Button(
            data_input_button_frame,
            text='Cancel',
            command=partial(self.cancel_data_input, input_window)
        ).grid(column=1, row=0, padx=5)


    def import_settings_from_last_run(self) -> None:
        '''
        Load the existing prefs file to speed up runtime.
        '''
        if not os.path.isfile(self.prefs_file_path):
            self.pop_up_error('Could Not Import Prefs; No Previous Run Data Found')
            return

        with open(self.prefs_file_path, 'r') as prefs_file:
            try:
                prefs_json_dict = json.load(prefs_file)
            except:
                self.pop_up_error('Could Not Import Prefs; File Corrupted / Modified')
                return

            failed_imports = []

            e_ev_path = prefs_json_dict.get('e_ev_path')
            if e_ev_path and isinstance(e_ev_path, str):
                self.electron_ev_file_path.set(e_ev_path)
            else:
                failed_imports.append('Electron EV Path')

            e_dos_path = prefs_json_dict.get('e_dos_path')
            if e_dos_path and isinstance(e_dos_path, str):
                self.electron_dos_file_path.set(e_dos_path)
            else:
                failed_imports.append('Electron DOS Path')

            p_ev_path = prefs_json_dict.get('p_ev_path')
            if p_ev_path and isinstance(p_ev_path, str):
                self.phonon_ev_file_path.set(p_ev_path)
            else:
                failed_imports.append('Phonon EV Path')

            p_dos_path = prefs_json_dict.get('p_dos_path')
            if p_dos_path and isinstance(p_dos_path, str):
                self.phonon_dos_file_path.set(p_dos_path)
            else:
                failed_imports.append('Phonon DOS Path')

            fermi_energy = prefs_json_dict.get('fermi_energy')
            if fermi_energy and isinstance(fermi_energy, float):
                self.fermi_energy.set(fermi_energy)
            else:
                failed_imports.append('Fermi Energy')

            velocities = prefs_json_dict.get('velocities')
            if velocities and isinstance(velocities, float):
                self.phonon_group_velocities.set(velocities)
            else:
                failed_imports.append('Velocities')

            relaxation = prefs_json_dict.get('relaxation')
            if relaxation and isinstance(relaxation, float):
                self.phonon_relaxation_time.set(relaxation)
            else:
                failed_imports.append('Relaxation Period')

            subsystems = prefs_json_dict.get('subsystems')
            if subsystems and isinstance(subsystems, int):
                self.number_of_blocks.set(subsystems)
            else:
                failed_imports.append('Number of Subsystems')

            sub_size = prefs_json_dict.get('sub_size')
            if sub_size and isinstance(sub_size, float):
                self.subsystems_size.set(sub_size)
            else:
                failed_imports.append('Subsystems Size')

            temps = prefs_json_dict.get('temps')
            if temps and isinstance(temps, list):
                self.subsystem_temperatures_string.set(', '.join(temps))
                self.subsystem_temperatures_list = temps
            else:
                failed_imports.append('Temperatures')

            time = prefs_json_dict.get('time_duration')
            if time and isinstance(time, float):
                self.time_duration.set(time)
            else:
                failed_imports.append('Time Duration')

            num_failed = len(failed_imports)
            if num_failed > 0:
                self.pop_up_error(f"Failed to Import {num_failed} Preference{'s' if num_failed > 1 else ''}:\n\n{', '.join(failed_imports)}")


    def load_previous_run(self) -> None:
        '''
        Have the user select a previous run file to load into memory.
        '''
        # Have the user select a file
        archive_file_path = StringVar()
        self.select_file(self.SEAQT_RUN_FILETYPE, archive_file_path)

        # If no file was selected, return
        if not archive_file_path or not archive_file_path.get() or archive_file_path.get() == '':
            self.pop_up_error('No Archive File Selected')
            return
        
        # Unpack and check the files
        try:
            with ZipFile(archive_file_path.get(), 'r') as zf:
                for filename in self.SEAQT_RUN_FILENAMES:
                    zf.extract(filename, self.TEMP_DIRECTORY_PATH)
        except:
            self.pop_up_error('Failed to unpack SEAQT archive; data may be missing or corrupt.')
            return    
        
        # Copy all values from JSON file to class vairables
        try:
            with open(self.prefs_file_path, 'r') as prefs_file:
                prefs_json = json.load(prefs_file)
                
                self.input_json_dict['e_ev_path'] = prefs_json['e_ev_path']
                self.input_json_dict['e_dos_path'] = prefs_json['e_dos_path']
                self.input_json_dict['p_ev_path'] = prefs_json['p_ev_path']
                self.input_json_dict['p_dos_path'] = prefs_json['p_dos_path']
                self.input_json_dict['fermi_energy'] = prefs_json['fermi_energy']
                self.input_json_dict['velocities'] = prefs_json['velocities']
                self.input_json_dict['relaxation'] = prefs_json['relaxation']
                self.input_json_dict['subsystems'] = prefs_json['subsystems']
                self.input_json_dict['sub_size'] = prefs_json['sub_size']
                self.input_json_dict['temps'] = prefs_json['temps']
                self.input_json_dict['time_duration'] = prefs_json['time_duration']
                self.input_json_dict['time_type'] = prefs_json['time_type']
                self.input_json_dict['selected_subs'] = prefs_json['selected_subs']
        except:
            self.pop_up_error('Failed to read parameters from preferences file; data may be missing or corrupted.')
            return

        # Disable new and load buttons, enable reset, save, and plot buttons
        self.new_run_button['state'] = DISABLED
        self.load_run_button['state'] = DISABLED
        self.reset_button['state'] = NORMAL
        self.save_button['state'] = NORMAL
        self.plot_button['state'] = NORMAL

        # Unlock the subsystem checkbuttons
        for chk in self.subsystem_checkbuttons:
            chk['state'] = NORMAL

        # Update plot image
        self.update_plot(PlotNumber.DATA_LOADED_SUCCESSFULLY.value)


    def cancel_data_input(self, window: Toplevel) -> None:
        '''
        Resets all data fields and then closes the window.

        :param window: The window object for the data input screen
        '''
        # Erase data input paths
        self.electron_ev_file_path.set('')
        self.electron_dos_file_path.set('')
        self.phonon_ev_file_path.set('')
        self.phonon_dos_file_path.set('')

        # Set params to default
        self.fermi_energy.set(self.DEFAULT_FERMI)
        self.electron_group_velocities.set(self.DEFAULT_ELECTRON_VELOCITIES)
        self.electron_relaxation_time.set(self.DEFAULT_ELECTRON_RELAXATION)
        self.phonon_group_velocities.set(self.DEFAULT_PHONON_VELOCITIES)
        self.phonon_relaxation_time.set(self.DEFAULT_PHONON_RELAXATION)
        self.subsystem_size.set(self.DEFAULT_SUB_SIZE)
        self.number_of_blocks.set(self.DEFAULT_NUM_BLOCKS)
        self.selected_subsystems = []
        self.subsystem_temperature.set(self.DEFAULT_SUB_TEMP)
        self.time_duration.set(self.DEFAULT_TIME_DURATION)
        self.selected_time_type.set(self.DEFAULT_TIME_TYPE)

        # Give back input control and close the window
        window.grab_release()
        window.destroy()


    def confirm_data_input_and_run(self, window: Toplevel) -> None:
        '''
        Ensures all data fields are filled out and the data is formatted correctly.

        :param window: The window object for the data input screen
        '''
        # Check all data fields
        if (not self.electron_dos_file_path.get() or
                not self.electron_ev_file_path.get() or 
                not self.phonon_dos_file_path.get() or
                not self.phonon_ev_file_path.get() or
                not self.fermi_energy.get() or
                not self.electron_group_velocities.get() or
                not self.electron_relaxation_time.get() or
                not self.phonon_group_velocities.get() or
                not self.phonon_relaxation_time.get() or
                not self.subsystem_size.get() or
                not self.number_of_blocks.get() or
                not self.subsystem_temperature.get() or
                not self.time_duration.get()):

            self.pop_up_error('Please Complete All Fields')
            return

        # Ensure data files exist
        if not os.path.isfile(self.electron_ev_file_path.get()):
            self.file_not_found_error(self.electron_ev_file_path.get())
            return
        elif not os.path.isfile(self.electron_dos_file_path.get()):
            self.file_not_found_error(self.electron_dos_file_path.get())
            return
        elif not os.path.isfile(self.phonon_ev_file_path.get()):
            self.file_not_found_error(self.phonon_ev_file_path.get())
            return
        elif not os.path.isfile(self.phonon_dos_file_path.get()):
            self.file_not_found_error(self.phonon_dos_file_path.get())
            return
        
        # Convert temperature string to array
        subsystem_temps_string = self.subsystem_temperatures_string.get()
        self.subsystem_temperatures_list = [x.strip() for x in subsystem_temps_string.split(',')]   # Split string by commas and strip any whitespace
        if len(self.subsystem_temperatures_list) != self.number_of_blocks.get():
            self.pop_up_error('Number of Subsystems Does Not Match Number of Supplied Temperatures')
            return

        # Give back input control and close the window
        window.grab_release()
        window.destroy()

        # Run the SEAQT backend
        self.update_plot(PlotNumber.DATA_PROCESSING.value)
        self.start_data_process()
    

    def update_plot(self, filenum: int) -> None:
        '''
        Update the central plot using the given file number.

        :param filenum: The number relating to the plot to show
        '''
        try:
            # Open the desired image
            loaded_image = Image.open(f'Figures/{filenum}.png')
            self.data_frame_image = ImageTk.PhotoImage(loaded_image)

            if filenum > 0 and filenum < 10:
                self.export_button['state'] = NORMAL
        except:
            try:
                # An error occurred; try to open the error image
                loaded_image = Image.open(f'Figures/{PlotNumber.ERROR.value}.png')
                self.data_frame_image = ImageTk.PhotoImage(loaded_image)
            except:
                # Error image could not be opened; display pop up error
                self.pop_up_error('Failed to open image/plot. Data may be missing or corrupted.')

        # Set the image in the frame
        self.data_frame_image_frame.configure(image=self.data_frame_image)


    def start_data_process(self) -> None:
        '''
        Run the SEAQT backend using the desired handler.
        '''
        # Aggregate the input data into a JSON object
        self.input_json_dict['e_ev_path'] = self.electron_ev_file_path.get()
        self.input_json_dict['e_dos_path'] = self.electron_dos_file_path.get()
        self.input_json_dict['p_ev_path'] = self.phonon_ev_file_path.get()
        self.input_json_dict['p_dos_path'] = self.phonon_dos_file_path.get()
        self.input_json_dict['fermi_energy'] = self.fermi_energy.get()
        self.input_json_dict['velocities'] = self.phonon_group_velocities.get()
        self.input_json_dict['relaxation'] = self.phonon_relaxation_time.get()
        self.input_json_dict['subsystems'] = self.number_of_blocks.get()
        self.input_json_dict['sub_size'] = self.subsystems_size.get()
        self.input_json_dict['temps'] = self.subsystem_temperatures_list
        self.input_json_dict['time_duration'] = self.time_duration.get()
        self.input_json_dict['time_type'] = self.selected_time_type.get()
        self.input_json_dict['selected_subs'] = self.selected_subsystems

        # Write the JSON object to the prefs file
        with open(self.prefs_file_path, 'w') as prefs_file:
            json.dump(self.input_json_dict, prefs_file)

        # Run the backend (NOTE: blocking)
        try:
            self.backend.run_seaqt()
            self.update_plot(PlotNumber.DATA_PROCESSED_SUCCESSFULLY.value)
        except:
            self.pop_up_error('SEAQT Backend Encountered an Error.\n\nThis could be due to faulty input data or parameters; or due to an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
            self.update_plot(PlotNumber.ERROR.value)
            return

        # Block the new and load buttons
        self.new_run_button['state'] = DISABLED
        self.load_run_button['state'] = DISABLED

        # Unlock replot, reset, and save buttons
        self.plot_button['state'] = NORMAL
        self.reset_button['state'] = NORMAL
        self.save_button['state'] = NORMAL

        # Unlock the subsystem checkbuttons
        for chk in self.subsystem_checkbuttons:
            chk['state'] = NORMAL


    def replot(self) -> bool:
        '''
        Replot with the new selected subsystems.

        :return: True iff the plot was successful; false otherwise
        '''
        # Tally the selected subsystems
        self.selected_subsystems = []
        for i in range(len(self.subsystem_variables)):
            if self.subsystem_variables[i].get():
                self.selected_subsystems.append(i)

        if len(self.selected_subsystems) == 0:
            self.pop_up_error('No Subsystem(s) Selected. Please Choose at Least One.')
            return False
        
        self.input_json_dict['selected_subs'] = self.selected_subsystems

        # Write the JSON object to the prefs file
        try:
            with open(self.prefs_file_path, 'w') as prefs_file:
                json.dump(self.input_json_dict, prefs_file)
        except:
            self.pop_up_error('Failed to modify preferences file; data may be missing or corrupted.')
            return False

        # Replot
        try:
            self.backend.generate_plot()
            self.update_plot(self.selected_plot.get())
        except:
            self.pop_up_error('SEAQT Backend Encountered an Error.\n\nThis could be due to faulty input data or parameters; or due to an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
            return False

        # Unlock radio buttons for plot selection
        for btn in self.plot_radio_buttons:
            btn['state'] = NORMAL

        return True


    def reset_data_process(self) -> None:
        '''
        Resets all stored / calculated data.
        '''
        user_choice = messagebox.askyesno(
            title='WARNING',
            message='You are about to erase all data and reset inputs to defaults. Do you wish to proceed?'
        )

        # If user selects 'YES', reset all values
        if user_choice:

            # Reset file paths
            self.electron_ev_file_path.set('')
            self.electron_dos_file_path.set('')
            self.phonon_ev_file_path.set('')
            self.phonon_dos_file_path.set('')
            
            # Reset parameters to defaults
            self.fermi_energy.set(self.DEFAULT_FERMI)
            self.phonon_group_velocities.set(self.DEFAULT_VELOCITIES)
            self.phonon_relaxation_time.set(self.DEFAULT_RELAXATION)
            self.number_of_blocks.set(self.DEFAULT_NUM_BLOCKS)
            self.selected_subsystems = []
            self.subsystems_size.set(self.DEFAULT_SUBS_SIZE)
            self.subsystem_temperatures_string.set(self.DEFAULT_SUBS_TEMPS)
            self.subsystem_temperatures_list = []
            self.time_duration.set(self.DEFAULT_TIME_DURATION)
            self.selected_time_type.set(self.DEFAULT_TIME_TYPE)   

            # Enable new and load buttons, disable reset, save, and export buttons
            self.new_run_button['state'] = NORMAL
            self.load_run_button['state'] = NORMAL
            self.reset_button['state'] = DISABLED
            self.save_button['state'] = DISABLED
            self.export_button['state'] = DISABLED

            # Disable all radio buttons and reset the selected one to default
            self.selected_plot.set(PlotNumber.ELECTRON_TEMPERATURE.value)
            for btn in self.plot_radio_buttons:
                btn['state'] = DISABLED

            # Disable checkbuttons and replot button
            self.plot_button['state'] = DISABLED
            for chk in self.subsystem_checkbuttons:
                chk['state'] = DISABLED

            # Remove any old plots
            clear_matlab_meta()
            clear_plots()

            # Reset the displayed image (data not loaded)
            self.update_plot(PlotNumber.DATA_NOT_LOADED.value)


    def save_data(self) -> None:
        '''
        Save the run data (.mat files and .json file) to be used for later plotting.
        '''
        # Have the user select a filename to save as
        filename = fd.asksaveasfilename(
            title='Save SEAQT Data',
            defaultextension='.seaqt',
            filetypes=self.SEAQT_RUN_FILETYPE,
            confirmoverwrite=True
        )

        # If no file was selected, return
        if not filename or filename == '':
            self.pop_up_error('No Archive File Selected')
            return
        
        # Create the archive file and save
        temp_dir = os.path.join(os.getcwd(), self.TEMP_DIRECTORY_PATH)
        try:
            with ZipFile(filename, 'w') as zf:
                for filename in self.SEAQT_RUN_FILENAMES:
                    zf.write(os.path.join(temp_dir, filename), filename)
        except Exception as e:
            self.pop_up_error('Failed to create SEAQT archive')
            print(e)
            return
        
        # Inform the user the data has been saved
        self.pop_up_info('SEAQT Run Saved Successfully.')
        

    def export_data(self) -> None:
        '''
        Allow the user to export the generated plots.
        '''
        export_window = Toplevel(self.tkinter_root)
        export_window.title('Export Generated Plots')
        export_window.resizable(False, False)
        export_window.grab_set()

        ###################################
        # Start frame for directory input #
        ###################################
        directory_frame = ttk.LabelFrame(
            export_window,
            text='Destination',
            padding=10
        )
        directory_frame.grid(column=0, row=0, padx=10, pady=5)

        ttk.Label(
            directory_frame,
            text='Destination Folder',
            padding=10
        ).grid(column=0, row=0)

        ttk.Entry(
            directory_frame,
            textvariable=self.export_directory,
            width=45
        ).grid(column=1, row=0)

        ttk.Button(
            directory_frame,
            text='Browse',
            command=partial(self.select_directory, self.export_directory),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=0, padx=5)

        #################################
        # Start frame for options input #
        #################################

        # Create frame for plot selection
        plot_select_frame = ttk.LabelFrame(
            export_window,
            text='Select Plot(s) to Export',
            padding=15
        )
        plot_select_frame.grid(column=0, row=1, padx=5, pady=5)

        # Create checkbuttons for each plot
        num_of_plots = len(self.PLOT_NAMES)
        for i in range(num_of_plots):
            plot_variable = IntVar(plot_select_frame, 0)
            self.plot_variables.append(plot_variable)

            check_btn = ttk.Checkbutton(
                plot_select_frame,
                text=self.PLOT_NAMES[i],
                variable=plot_variable,
                onvalue=1,
                offvalue=0
            )
            check_btn.grid(column=(i // (num_of_plots // 3)) % 3, row=i % (num_of_plots // 3), padx=7, pady=5, sticky=W)
            self.plot_checkbuttons.append(check_btn)

        ##################################
        # Start frame for bottom buttons #
        ##################################
        button_frame = ttk.Frame(
            export_window,
            padding=10
        )
        button_frame.grid(column=0, row=2, padx=5, pady=5)

        ttk.Button(
            button_frame,
            text='Export',
            command=partial(self.confirm_data_export, export_window)
        ).grid(column=0, row=0, padx=5)

        ttk.Button(
            button_frame,
            text='Cancel',
            command=partial(self.cancel_data_export, export_window)
        ).grid(column=1, row=0, padx=5)


    def confirm_data_export(self, export_window: Toplevel) -> None:
        '''
        Confirm all data export parameters, then save plots.

        :param export_window: Toplevel object to destroy upon confirming
        '''
        # Ensure destination path has been set
        if not self.export_directory or not self.export_directory.get() or self.export_directory.get() == '':
            self.pop_up_error('No Destination Directory Specified. Please Select One.')
            return

        # Tally the selected plots
        self.selected_plots = []
        for i in range(len(self.PLOT_NAMES)):
            if self.plot_variables[i].get():
                self.selected_plots.append(i)

        num_selected_plots = len(self.selected_plots)
        if num_selected_plots == 0:
            self.pop_up_error('No Plot(s) Selected. Please Choose at Least One.')
            return

        curr_time = time.time()
        failed_plots = []
        for plot_number in self.selected_plots:
            try:
                copyfile(f'Figures/{plot_number + 1}.png', os.path.join(self.export_directory.get(), f'{self.PLOT_NAMES[plot_number]}_{curr_time}.png'))
            except Exception as e:
                print(e)
                failed_plots.append(plot_number)

        num_failed_plots = len(failed_plots)
        if num_failed_plots > 0:
            self.pop_up_error(f"Failed to save {num_failed_plots} plot{'s' if num_failed_plots > 1 else ''}\n\nData may be missing or corrupted, or there may be an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.")
            return

        # Release control and close the window
        self.pop_up_info(f"{num_selected_plots} plot{'s' if num_selected_plots > 1 else ''} successfully saved.")
        export_window.grab_release()
        export_window.destroy()


    def cancel_data_export(self, export_window: Toplevel) -> None:
        '''
        Cancel and reset all data export parameters, then close the window.

        :param export_window: Toplevel object to destroy upon cancelling
        '''
        # Reset choices
        self.export_directory.set('')

        # Release control and close the winow
        export_window.grab_release()
        export_window.destroy()


    def activate_help_window(self) -> None:
        '''
        Inform the user to post a ticket to the github (for now). Eventually, should show FAQ.
        '''
        self.pop_up_info('Please visit https://github.com/azsprague/seaqt-gui for more info on the system.\n\nIf you have an issue or find a bug, view or open a ticket at https://github.com/azsprague/seaqt-gui/issues.')


    def exit_button(self) -> None:
        '''
        Ask the user if they are sure, then exit.
        '''
        user_choice = messagebox.askyesno(
            title='WARNING',
            message='Are you sure you want to exit? Any unsaved data will be lost.'
        )

        # If the user chooses "yes", destroy the main window (closing the program)
        if user_choice:
            clear_matlab_meta()
            clear_plots()
            self.tkinter_root.destroy()
        else:
            return
        

    def select_file(self, filetypes: Tuple[Tuple[str, str]], global_file_path: StringVar) -> None:
        '''
        Open a filesystem window to allow the user to choose a file.

        :param filetypes: A tuple of tuples containing (description, filetype)'s, e.g., ('text files', '*.txt')
        :param global_file_path: StringVar to contain the chosen file path
        '''
        filename = fd.askopenfilename(
            title='Select a File',
            filetypes=filetypes
        )
        global_file_path.set(filename)


    def select_directory(self, global_directory_path: StringVar) -> None:
        '''
        Open a filesystem window to allow the user to choose a directory.

        :param global_directory_path: StringVar to contain the chosen directory path
        '''
        directory = fd.askdirectory(
            title='Select a Directory / Folder'
        )
        global_directory_path.set(directory)

    
    def feature_not_implemented_error(self) -> None:
        '''
        Create a pop-up warning dialog that the feature has not been implemented.
        '''
        self.pop_up_error('Feature Not Implemented')

    
    def file_not_found_error(self, filename) -> None:
        '''
        Create a pop-up warning dialog that the supplied filename does not have an associated file.

        :param filename: The bad filename
        '''
        self.pop_up_error(f"File '{filename}' Could Not Be Found")


    def pop_up_error(self, error_message: str) -> None:
        '''
        Create a pop-up warning dialog containing the supplied message.

        :param message: The message to present the user
        '''
        messagebox.showerror(
            title='ERROR',
            message=error_message
        )


    def pop_up_info(self, info_message: str) -> None:
        '''
        Create a pop-up info dialog containing the supplied message.

        :param message: The message to present the user
        '''
        messagebox.showinfo(
            title='INFO',
            message=info_message
        )
