import json
import os

from enum import IntEnum
from typing import Tuple
from functools import partial
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from PIL import Image, ImageTk
from zipfile import ZipFile

from Frontend.MATLAB_Backend_Handler import MATLABBackendHandler
from Frontend.Utils import clear_plots


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
    Enum to map type type to a number for faster acquisition.
    '''
    INVALID = -1,
    UNKNOWN = 0,
    MIN = 1,
    MAX = 2,


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
    INPUT_DATA_ENTRY_WIDTH = 70
    INPUT_DATA_FILETYPES = (
        ('Excel Spreadsheet', '*.xlsx'),
        ('Comma-Separated Values', '*.csv')
    )

    INPUT_PARAMETER_LABEL_WIDTH = 33
    INPUT_PARAMETER_ENTRY_WIDTH = 70
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

    DEFAULT_FERMI = 6
    DEFAULT_VELOCITIES = 6000
    DEFAULT_RELAXATION = 50 * (10**-12)
    DEFAULT_NUM_SUBSYSTEMS = 20
    DEFAULT_SUBS_SIZE = 1 * (10**-7)
    DEFAULT_SUBS_TEMPS = '295, 295, 295, 295, 295, 295, 295, 295, 295, 295, 300, 300, 300, 300, 300, 300, 300, 300, 300, 300'
    DEFAULT_TIME_DURATION = 100
    DEFAULT_TIME_TYPE = 1

    TEMP_DIRECTORY_PATH = 'tmp'
    PARAM_PREFERENCES_FILE_NAME = 'seaqt_prefs.json'


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
        self.electron_ev_file_path = StringVar(self.tkinter_root)
        self.electron_dos_file_path = StringVar(self.tkinter_root)
        self.phonon_ev_file_path = StringVar(self.tkinter_root)
        self.phonon_dos_file_path = StringVar(self.tkinter_root)
        
        # Runtime parameters (class variables)
        self.fermi_energy = DoubleVar(self.tkinter_root, self.DEFAULT_FERMI)                        # eV * 1.60218 * (10**-19) Joules
        self.phonon_group_velocities = DoubleVar(self.tkinter_root, self.DEFAULT_VELOCITIES)        # m/s
        self.phonon_relaxation_time = DoubleVar(self.tkinter_root, self.DEFAULT_RELAXATION)         # seconds
        self.number_of_subsystems = IntVar(self.tkinter_root, self.DEFAULT_NUM_SUBSYSTEMS)          # amount
        self.selected_subsystems = []                                                               # list of scalars
        self.subsystems_size = DoubleVar(self.tkinter_root, self.DEFAULT_SUBS_SIZE)                 # meters
        self.subsystem_temperatures_string = StringVar(self.tkinter_root, self.DEFAULT_SUBS_TEMPS)  # Kelvin    
        self.subsystem_temperatures_list = []                                                       # list of Kelvin
        self.time_duration = DoubleVar(self.tkinter_root, self.DEFAULT_TIME_DURATION)               # scalar
        self.selected_time_type = DoubleVar(self.tkinter_root, self.DEFAULT_TIME_TYPE)              # 'min'

        self.input_json_dict = {}

        # Menu buttons (class variables)
        self.new_run_button = None
        self.load_run_button = None
        self.reset_button = None
        self.save_button = None
        self.export_button = None

        # Plot radio buttons (class variables)
        self.plot_radio_buttons = []
        self.selected_plot = None
        self.data_frame_image_frame = None
        self.data_frame_image = None

        self.time_radio_buttons = []
        
        # Subsystem checkbuttons (class variables)
        self.subsystem_variables = []
        self.subsystem_checkbuttons = []
        self.plot_button = None

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

        # Variable to store button choice
        self.selected_plot = IntVar(radio_button_frame, PlotNumber.ELECTRON_TEMPERATURE.value)

        # Radio button for electron temperature vs time
        rb1 = ttk.Radiobutton(
            radio_button_frame,
            text='Electron Temperature',
            variable=self.selected_plot,
            value=PlotNumber.ELECTRON_TEMPERATURE.value,
            command=partial(self.update_plot, PlotNumber.ELECTRON_TEMPERATURE.value),
            state=DISABLED
        )
        rb1.grid(column=0, row=0, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb1)

        # Radio button for electron number vs time
        rb2 = ttk.Radiobutton(
            radio_button_frame,
            text='Electron Number',
            variable=self.selected_plot,
            value=PlotNumber.ELECTRON_NUMBER.value,
            command=partial(self.update_plot, PlotNumber.ELECTRON_NUMBER.value),
            state=DISABLED
        )
        rb2.grid(column=0, row=1, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb2)

        # Radio button for electron energy vs time
        rb3 = ttk.Radiobutton(
            radio_button_frame,
            text='Electron Energy',
            variable=self.selected_plot,
            value=PlotNumber.ELECTRON_ENERGY.value,
            command=partial(self.update_plot, PlotNumber.ELECTRON_ENERGY.value),
            state=DISABLED
        )
        rb3.grid(column=0, row=2, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb3)

        # Radio button for electrical conductivity vs time
        rb4 = ttk.Radiobutton(
            radio_button_frame,
            text='Electrical Conductivity',
            variable=self.selected_plot,
            value=PlotNumber.ELECTRICAL_CONDUCTIVITY.value,
            command=partial(self.update_plot, PlotNumber.ELECTRICAL_CONDUCTIVITY.value),
            state=DISABLED
        )
        rb4.grid(column=0, row=3, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb4)

        # Radio button for seebeck coefficient vs time
        rb5 = ttk.Radiobutton(
            radio_button_frame,
            text='Seebeck Coefficient',
            variable=self.selected_plot,
            value=PlotNumber.SEEBECK_COEFFICIENT.value,
            command=partial(self.update_plot, PlotNumber.SEEBECK_COEFFICIENT.value),
            state=DISABLED
        )
        rb5.grid(column=0, row=4, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb5)

        # Radio button for phonon temperature vs time
        rb6 = ttk.Radiobutton(
            radio_button_frame,
            text='Phonon Temperature',
            variable=self.selected_plot,
            value=PlotNumber.PHONON_TEMPERATURE.value,
            command=partial(self.update_plot, PlotNumber.PHONON_TEMPERATURE.value),
            state=DISABLED
        )
        rb6.grid(column=0, row=5, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb6)

        # Radio button for phonon energy vs time
        rb7 = ttk.Radiobutton(
            radio_button_frame,
            text='Phonon Energy',
            variable=self.selected_plot,
            value=PlotNumber.PHONON_ENERGY.value,
            command=partial(self.update_plot, PlotNumber.PHONON_ENERGY.value),
            state=DISABLED
        )
        rb7.grid(column=0, row=6, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb7)

        # Radio button for thermal conductivity vs time
        rb8 = ttk.Radiobutton(
            radio_button_frame,
            text='Thermal Conductivity',
            variable=self.selected_plot,
            value=PlotNumber.THERMAL_CONDUCTIVITY.value,
            command=partial(self.update_plot, PlotNumber.THERMAL_CONDUCTIVITY.value),
            state=DISABLED
        )
        rb8.grid(column=0, row=7, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb8)

        # Radio button for ZT factor vs time
        rb9 = ttk.Radiobutton(
            radio_button_frame,
            text='ZT Factor',
            variable=self.selected_plot,
            value=PlotNumber.ZT_FACTOR.value,
            command=partial(self.update_plot, PlotNumber.ZT_FACTOR.value),
            state=DISABLED
        )
        rb9.grid(column=0, row=8, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
        self.plot_radio_buttons.append(rb9)

        #######################################
        # Start frame for subsystem selection #
        #######################################

        # Create subsystem selection frame
        subsystem_selection_frame = ttk.LabelFrame(
            right_menu_frame,
            text='Select Subsystem(s)',
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
        num_subsystems = self.number_of_subsystems.get()
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
        input_window.grid_columnconfigure(0, weight=1)
        input_window.grid_columnconfigure(1, weight=1)

        # Give users the option to load preferences from last run
        ttk.Button(
            input_window,
            text='Import Settings From Last Run',
            command=self.import_settings_from_last_run,
            state=NORMAL if os.path.isfile(self.prefs_file_path) else DISABLED,
            width=self.LOAD_LAST_RUN_BUTTON_WIDTH
        ).grid(column=0, row=0, padx=5, pady=15)

        ###############################
        # Start frame for file inputs #
        ###############################

        # Create file input frame
        file_input_frame = ttk.LabelFrame(
            input_window, 
            text='Input Data',
            padding=10, 
            relief=SOLID
        )
        file_input_frame.grid(column=0, row=1, padx=self.INPUT_FRAME_PAD_X)

        # Select electron ev file (label, entry, button)
        ttk.Label(
            file_input_frame,
            text='Electron EV Data',
            width=self.INPUT_DATA_LABEL_WIDTH
        ).grid(column=0, row=0)

        ttk.Entry(
            file_input_frame, 
            textvariable=self.electron_ev_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_ev_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH,
        ).grid(column=2, row=0, padx=5)

        # Select electron dos file (label, entry, button)
        ttk.Label(
            file_input_frame,
            text='Electron DOS Data',
            width=self.INPUT_DATA_LABEL_WIDTH
        ).grid(column=0, row=1)

        ttk.Entry(
            file_input_frame, 
            textvariable=self.electron_dos_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_dos_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=1, padx=5)
        
        # Select phonon ev file (label, entry, button)
        ttk.Label(
            file_input_frame,
            text='Phonon EV Data',
            width=self.INPUT_DATA_LABEL_WIDTH
        ).grid(column=0, row=2)

        ttk.Entry(
            file_input_frame, 
            textvariable=self.phonon_ev_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_ev_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=2, padx=5)

        # Select phonon dos file (label, entry, button)
        ttk.Label(
            file_input_frame,
            text='Phonon DOS Data',
            width=self.INPUT_DATA_LABEL_WIDTH
        ).grid(column=0, row=3)

        ttk.Entry(
            file_input_frame, 
            textvariable=self.phonon_dos_file_path,
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=3, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ttk.Button(
            file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_dos_file_path),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=3, padx=5)

        ####################################
        # Start frame for parameter inputs #
        ####################################

        # Create parent parameter input frame
        parameter_input_frame = ttk.LabelFrame(
            input_window, 
            text='SEAQT Parameters',
            padding=10, 
            relief=SOLID
        )
        parameter_input_frame.grid(column=0, row=2, padx=self.INPUT_FRAME_PAD_X, pady=self.INPUT_FRAME_PAD_Y)

        # Select Fermi energy (label, entry)
        ttk.Label(
            parameter_input_frame,
            text='Fermi Energy (eV)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=0)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.fermi_energy,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select phonon group velocities
        ttk.Label(
            parameter_input_frame,
            text='Phonon Group Velocities (m/s)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=1)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.phonon_group_velocities,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select phonon relaxation time
        ttk.Label(
            parameter_input_frame,
            text='Phonon Relaxation Time (s)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=2)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.phonon_relaxation_time,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select number of subsystems
        ttk.Label(
            parameter_input_frame,
            text='Number of Subsystems',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=3)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.number_of_subsystems,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=3, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select subsystems size
        ttk.Label(
            parameter_input_frame,
            text='Subsystems Size (m)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=4)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.subsystems_size,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=4, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select subsystem temperatures
        ttk.Label(
            parameter_input_frame,
            text='Subsystem Temperatures (K)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=5)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.subsystem_temperatures_string,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=5, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        ##################################
        # Start frame for time selection #
        ##################################

        # Create frame for time selection
        time_selection_frame = ttk.LabelFrame(
            input_window,
            text='Time',
            padding=10,
            relief=SOLID
        )
        time_selection_frame.grid(column=0, row=3, padx=self.INPUT_FRAME_PAD_X, pady=self.INPUT_FRAME_PAD_Y)

        # Select time duration
        ttk.Label(
            time_selection_frame,
            text='Run Duration',
            width=15
        ).grid(column=0, row=0)

        ttk.Entry(
            time_selection_frame,
            textvariable=self.time_duration,
            width=15
        ).grid(column=1, row=0)

        # Variable to store button choice
        self.selected_time_type = IntVar(time_selection_frame, TimeType.MIN.value)

        # Radio button for min time
        rb1 = ttk.Radiobutton(
            time_selection_frame,
            text='Min(tau)',
            variable=self.selected_time_type,
            value=TimeType.MIN.value
        )
        rb1.grid(column=0, row=1, padx=5, pady=5)
        self.time_radio_buttons.append(rb1)

        # Radio button for max time
        rb2 = ttk.Radiobutton(
            time_selection_frame,
            text='Max(tau)',
            variable=self.selected_time_type,
            value=TimeType.MAX.value
        )
        rb2.grid(column=1, row=1, padx=5, pady=5)
        self.time_radio_buttons.append(rb2)        

        ##################################
        # Start frame for bottom buttons #
        ##################################

        # Create frame for bottom buttons
        data_input_button_frame = ttk.Frame(
            input_window,
            padding=10
        )
        data_input_button_frame.grid(column=0, row=4, padx=self.INPUT_FRAME_PAD_X, pady=self.INPUT_FRAME_PAD_Y)

        # Cancel button
        ttk.Button(
            data_input_button_frame,
            text='Cancel',
            command=partial(self.cancel_data_input, input_window)
        ).grid(column=1, row=0, padx=self.INPUT_BOTTOM_BUTTON_PAD_X)

        # Run button (all fields must be filled to confirm)
        ttk.Button(
            data_input_button_frame, 
            text='Run', 
            command=partial(self.confirm_data_input_and_run, input_window)
        ).grid(column=0, row=0, padx=self.INPUT_BOTTOM_BUTTON_PAD_X)


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
                self.number_of_subsystems.set(subsystems)
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
        self.phonon_group_velocities.set(self.DEFAULT_VELOCITIES)
        self.phonon_relaxation_time.set(self.DEFAULT_RELAXATION)
        self.subsystems_size.set(self.DEFAULT_SUBS_SIZE)
        self.number_of_subsystems.set(self.DEFAULT_NUM_SUBSYSTEMS)
        self.selected_subsystems = []
        self.subsystem_temperatures_string.set(self.DEFAULT_SUBS_TEMPS)
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
                not self.phonon_group_velocities.get() or
                not self.phonon_relaxation_time.get() or
                not self.subsystems_size.get() or
                not self.number_of_subsystems.get() or
                not self.subsystem_temperatures_string.get() or
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
        if len(self.subsystem_temperatures_list) != self.number_of_subsystems.get():
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
        self.input_json_dict['subsystems'] = self.number_of_subsystems.get()
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
            self.number_of_subsystems.set(self.DEFAULT_NUM_SUBSYSTEMS)
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
        TODO
        '''
        self.feature_not_implemented_error()


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

        if user_choice:
            self.tkinter_root.destroy()
        else:
            return

    
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
