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

    DATA_VIEW_FRAME_WIDTH = 800
    DATA_VIEW_FRAME_HEIGHT = 628
    DATA_VIEW_FRAME_PAD_X = 5
    DATA_VIEW_FRAME_PAD_Y = 25

    MENU_FRAME_PAD_X = 10
    MENU_FRAME_PAD_Y = 10
    MENU_BUTTON_WIDTH = 10
    MENU_BUTTON_PAD_X = 5
    MENU_BUTTON_PAD_Y = 15

    PLOT_BUTTON_PAD_Y = 3

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    DEFAULT_NUM_BLOCKS = 20
    DEFAULT_TIME_DURATION = 100
    DEFAULT_TIME_TYPE = TimeType.MIN.value
    DEFAULT_RUN_TYPE = RunType.BOTH.value

    DEFAULT_BLOCK_SIZE = 1 * (10**-7)
    DEFAULT_BLOCK_TEMP_A = 295
    DEFAULT_BLOCK_TEMP_B = 300
    DEFAULT_FERMI = 6

    DEFAULT_ELECTRON_DOS_FILENAME = 'Electron_DOS.xlsx'
    DEFAULT_ELECTRON_EV_FILENAME = 'Electron_EV.xlsx'
    DEFAULT_ELECTRON_RELAXATION = 5 * (10**-15)
    DEFAULT_ELECTRON_EFFECTIVE_MASS = 1

    DEFAULT_PHONON_DOS_FILENAME = 'Phonon_DOS.xlsx'
    DEFAULT_PHONON_EV_FILENAME = 'Phonon_EV.xlsx'
    DEFAULT_PHONON_VELOCITIES = 6000
    DEFAULT_PHONON_RELAXATION = 5 * (10**-12)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

    TEMP_DIRECTORY_PATH = 'tmp'
    EXAMPLE_DATA_DIRECTORY_PATH = 'Example Data'
    PARAM_PREFERENCES_FILE_NAME = 'seaqt_prefs.json'

    PLOT_NAMES = [
        'Electron Temperature',
        'Electron Number',
        'Electron Energy',
        'Electrical Conductivity',
        'Seebeck Coefficient',
        'Phonon Temperature',
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
        # self.tkinter_root.resizable(False, False)

        # Data output directory (class variable)
        self.export_directory = StringVar()

        # Runtime parameters (class variables)
        self.number_of_blocks = IntVar(value=self.DEFAULT_NUM_BLOCKS)       # scalar
        self.time_duration = DoubleVar(value=self.DEFAULT_TIME_DURATION)    # scalar
        self.selected_time_type = IntVar(value=self.DEFAULT_TIME_TYPE)      # min or max
        self.selected_run_type = IntVar(value=self.DEFAULT_RUN_TYPE)        # electron, phonon, or both
        self.run_type_buttons = []

        self.block_to_copy_from = IntVar(value=1)   # scalar 

        self.block_sizes = []                       # DoubleVar
        self.block_temperatures = []                # DoubleVar
        self.fermi_energies = []                    # DoubleVar

        self.electron_ev_file_paths = []            # StringVar
        self.electron_dos_file_paths = []           # StringVar
        self.electron_tau_file_paths = []           # StringVar
        self.electron_group_velocities = []         # DoubleVar
        self.electron_relaxation_times = []         # DoubleVar
        self.electron_effective_masses = []         # DoubleVar

        self.phonon_ev_file_paths = []              # StringVar
        self.phonon_dos_file_paths = []             # StringVar
        self.phonon_tau_file_paths = []             # StringVar
        self.phonon_group_velocities = []           # DoubleVar
        self.phonon_relaxation_times = []           # DoubleVar
        
        # Various frames and etc.
        self.right_menu_frame = None
        self.radio_button_frame = None

        self.block_plot_selection_frame = None
        self.checkbox_frame = None

        self.block_master_frame = None
        self.block_parameter_frame = None
        self.block_input_selection_frame = None
        self.notebook = None

        # Selected blocks for plotting
        self.selected_blocks = None
        self.block_radio_buttons = None
        self.selected_block_input = IntVar(value=1)
        
        # JSON dictionary to be passed to the backend
        self.input_json_dict = {}

        # Menu buttons (class variables)
        self.new_run_button = None
        self.load_run_button = None
        self.reset_button = None
        self.save_button = None
        self.export_button = None

        # Plot radio buttons (class variables)
        self.plot_radio_buttons = None
        self.selected_plot = IntVar(value=PlotNumber.INVALID.value)
        self.data_frame_image_frame = None
        self.data_frame_image = None

        self.time_radio_buttons = []
        
        # Subsystem checkbuttons (class variables)
        self.block_variables = None
        self.block_check_buttons = None
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
        # Create menu option frame
        menu_option_frame = ttk.LabelFrame(
            self.tkinter_root,
            text='Menu',
            padding=5,
            relief=SOLID
        )
        menu_option_frame.grid(column=0, row=0, padx=10, pady=10, sticky=N)

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

        # # Copyright
        # ttk.Label(
        #     self.tkinter_root,
        #     text='© 2023'
        # ).grid(column=1, row=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create right panel
        self.right_menu_frame = ttk.Frame(
            self.tkinter_root,
            padding=5
        )
        self.right_menu_frame.grid(column=2, row=0, padx=10, pady=0, sticky=N)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create plot radio buttons
        self.update_plot_radio_buttons(False)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create subsystem selection frame
        self.block_plot_selection_frame = ttk.LabelFrame(
            self.right_menu_frame,
            text='Blocks to Plot',
            padding=5,
            relief=SOLID
        )
        self.block_plot_selection_frame.grid(column=0, row=1, pady=5)

        # Create block check buttons
        self.update_plot_check_buttons(False)

        # Button to replot given selected systems
        self.plot_button = ttk.Button(
            self.block_plot_selection_frame,
            text='Plot',
            command=self.replot,
            state=DISABLED
        )
        self.plot_button.grid(column=0, row=1, pady=5, sticky=N)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create data view frame
        s = ttk.Style()
        s.configure('white.TFrame', background='white')
        data_view_frame = ttk.Frame(
            self.tkinter_root,
            padding=5,
            width=self.DATA_VIEW_FRAME_WIDTH,
            height=self.DATA_VIEW_FRAME_HEIGHT,
            # relief=SOLID,
            style='white.TFrame'
        )
        data_view_frame.grid(column=1, row=0, padx=5, pady=5, sticky=N)
        data_view_frame.grid_propagate(False)

        # Create data image (default "no data loaded")
        self.data_frame_image_frame = ttk.Label(
            data_view_frame,
            borderwidth=0,
            justify=CENTER
        )
        self.data_frame_image_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        self.update_plot(PlotNumber.DATA_NOT_LOADED.value)

    
    def update_plot_radio_buttons(self, enable: bool) -> None:
        '''
        (Re) create the radio buttons for the plot to display.

        :param enable: Boolean for whether to enable or disable the buttons
        '''
        # Create radio button frame
        if self.radio_button_frame != None:
            self.radio_button_frame.destroy()

        self.radio_button_frame = ttk.LabelFrame(
            self.right_menu_frame,
            text='Select Plot',
            padding=5,
            relief=SOLID
        )
        self.radio_button_frame.grid(column=0, row=0, pady=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create radio buttons
        self.plot_radio_buttons = []
        for i in range(len(self.PLOT_NAMES)):
            rb = ttk.Radiobutton(
                self.radio_button_frame,
                text=self.PLOT_NAMES[i],
                variable=self.selected_plot,
                value=i + 1,
                command=partial(self.update_plot, i + 1),
                state=DISABLED
            )
            rb.grid(column=0, row=i, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
            self.plot_radio_buttons.append(rb)

        # Reset plot selector
        self.selected_plot.set(PlotNumber.INVALID.value)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Update button states based on enable status and run type
        if enable:
            run_type = self.selected_run_type.get()

            # Enable electron buttons
            if run_type == RunType.ELECTRON.value or run_type == RunType.BOTH.value:
                self.plot_radio_buttons[0]['state'] = NORMAL
                self.plot_radio_buttons[1]['state'] = NORMAL
                self.plot_radio_buttons[2]['state'] = NORMAL
                self.plot_radio_buttons[3]['state'] = NORMAL
                self.plot_radio_buttons[4]['state'] = NORMAL

            # Enable phonon buttons
            if run_type == RunType.PHONON.value or run_type == RunType.BOTH.value:
                self.plot_radio_buttons[5]['state'] = NORMAL
                self.plot_radio_buttons[6]['state'] = NORMAL

            # Enable combined buttons
            if run_type == RunType.BOTH.value:
                self.plot_radio_buttons[7]['state'] = NORMAL
                self.plot_radio_buttons[8]['state'] = NORMAL


    def update_plot_check_buttons(self, enable: bool) -> None:
        '''
        (Re) create the check buttons for which blocks to plot

        :param enable: Boolean for whether to enable or disable the buttons
        '''
        # Frame to hold the checkboxes
        if self.checkbox_frame != None:
            self.checkbox_frame.destroy()

        self.checkbox_frame = ttk.Frame(self.block_plot_selection_frame)
        self.checkbox_frame.grid(column=0, row=0, sticky=N)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create a subsystem button for the number of selected subsystems
        num_blocks = self.number_of_blocks.get()
        self.block_check_buttons = []
        self.block_variables = []
        for i in range(num_blocks):
            curr_block_variable = IntVar(value=0)
            self.block_variables.append(curr_block_variable)

            check_button = ttk.Checkbutton(
                self.checkbox_frame,
                text=f'{i + 1}',
                variable=curr_block_variable,
                onvalue=1,
                offvalue=0,
                state=NORMAL if enable else DISABLED
            )
            check_button.grid(column=(i // int((num_blocks / 2) + 0.5)) % 2, row=i % int((num_blocks / 2) + 0.5), padx=17, pady=self.PLOT_BUTTON_PAD_Y, sticky=W)
            self.block_check_buttons.append(check_button)


    def activate_input_data_window(self) -> None:
        '''
        Collect input data files and important parameters from the user.
        ''' 
        # Create a new pop-up window and take control of input
        input_window = Toplevel(self.tkinter_root)
        input_window.title('Load Data and Set Parameters')
        # input_window.resizable(False, False)
        input_window.grab_set()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create master frame for base parameters
        top_window = ttk.Frame(
            input_window,
            padding=10
        )
        top_window.grid(column=0, row=0)

        top_top_window = ttk.Frame(top_window)
        top_top_window.pack()

        # Create master frame for block parameters
        self.block_master_frame = ttk.Frame(
            input_window,
            padding=10
        )
        self.block_master_frame.grid(column=0, row=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create base parameter frame
        base_parameter_input = ttk.LabelFrame(
            top_top_window,
            text='Base Parameters',
            padding=10,
            relief=SOLID
        )
        base_parameter_input.grid(column=0, row=0, padx=5, pady=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Number of blocks label
        ttk.Label(
            base_parameter_input,
            text='Number of Blocks',
            width=17
        ).grid(column=0, row=0)

        # Number of blocks input (spinbox)
        ttk.Spinbox(
            base_parameter_input,
            from_=1,
            to=100,
            increment=1,
            textvariable=self.number_of_blocks,
            command=self.update_number_of_blocks,
            justify=CENTER,
            width=5
        ).grid(column=1, row=0, padx=12, sticky=W)

        # As a first run, update block selection and data window
        self.update_number_of_blocks()
        self.update_block_data_window()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Run length label
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

        # Run length text input
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

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Run type label
        ttk.Label(
            base_parameter_input,
            text='Run Type',
            width=17
        ).grid(column=0, row=2)

        # Run type frame
        run_type_frame = ttk.Frame(
            base_parameter_input
        )
        run_type_frame.grid(column=1, row=2)

        # Electron radio button
        electron_rb = ttk.Radiobutton(
            run_type_frame,
            text='Electron',
            variable=self.selected_run_type,
            command=self.update_block_data_window,
            value=RunType.ELECTRON.value
        )
        electron_rb.grid(column=0, row=0, padx=2)
        self.run_type_buttons.append(electron_rb)

        # Phonon radio button
        phonon_rb = ttk.Radiobutton(
            run_type_frame,
            text='Phonon',
            variable=self.selected_run_type,
            command=self.update_block_data_window,
            value=RunType.PHONON.value
        )
        phonon_rb.grid(column=1, row=0, padx=2)
        self.run_type_buttons.append(phonon_rb)

        # Both radio button
        both_rb = ttk.Radiobutton(
            run_type_frame,
            text='Both',
            variable=self.selected_run_type,
            command=self.update_block_data_window,
            value=RunType.BOTH.value
        )
        both_rb.grid(column=2, row=0, padx=2)
        self.run_type_buttons.append(both_rb)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ # 

        # Create info frame
        info_frame = ttk.LabelFrame(
            top_top_window, 
            text='Info',
            padding=10,
            relief=SOLID
        )
        info_frame.grid(column=1, row=0, padx=5, pady=5, sticky=N)

        # Info label
        ttk.Label(
            info_frame,
            text='Block: a pair of local systems (electron & phonon)\n\nTau: the relaxation parameter'
        ).grid(column=0, row=0, sticky=NW)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        ttk.Separator(top_window, orient=HORIZONTAL).pack(fill=X, pady=7)

        ttk.Button(
            top_window,
            padding=5,
            text='Import Default Data and Parameters',
            command=self.import_default_settings
        ).pack(pady=7)

        ttk.Separator(top_window, orient=HORIZONTAL).pack(fill=X, pady=7)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

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


    def import_default_settings(self) -> None:
        '''
        Use the default parameters for this run.
        '''
        # Update number of blocks
        self.number_of_blocks.set(self.DEFAULT_NUM_BLOCKS)
        self.update_number_of_blocks()

        # Update run length and type
        self.time_duration.set(self.DEFAULT_TIME_DURATION)
        self.selected_time_type.set(self.DEFAULT_TIME_TYPE)
        self.selected_run_type.set(self.DEFAULT_RUN_TYPE)
        self.update_block_data_window()

        # Prepare filepaths
        example_data_directory = os.path.join(os.getcwd(), self.EXAMPLE_DATA_DIRECTORY_PATH)
        
        electron_ev_path = os.path.join(example_data_directory, self.DEFAULT_ELECTRON_EV_FILENAME)
        if not os.path.isfile(electron_ev_path):
            self.pop_up_error(f'Could not import default settings\n\nFile {self.DEFAULT_ELECTRON_EV_FILENAME} is missing or corrupted.')
            return
        
        electron_dos_path = os.path.join(example_data_directory, self.DEFAULT_ELECTRON_DOS_FILENAME)
        if not os.path.isfile(electron_dos_path):
            self.pop_up_error(f'Could not import default settings\n\nFile {self.DEFAULT_ELECTRON_DOS_FILENAME} is missing or corrupted.')
            return
        
        phonon_ev_path = os.path.join(example_data_directory, self.DEFAULT_PHONON_EV_FILENAME)
        if not os.path.isfile(phonon_ev_path):
            self.pop_up_error(f'Could not import default settings\n\nFile {self.DEFAULT_PHONON_EV_FILENAME} is missing or corrupted.')
            return
        
        phonon_dos_path = os.path.join(example_data_directory, self.DEFAULT_PHONON_DOS_FILENAME)
        if not os.path.isfile(phonon_dos_path):
            self.pop_up_error(f'Could not import default settings\n\nFile {self.DEFAULT_PHONON_DOS_FILENAME} is missing or corrupted.')
            return
        
        # Update each block
        num_blocks = self.number_of_blocks.get()
        for i in range(num_blocks):

            # Update shared parameters
            self.block_sizes[i].set(self.DEFAULT_BLOCK_SIZE)
            self.fermi_energies[i].set(self.DEFAULT_FERMI)

            if i < (num_blocks / 2):
                self.block_temperatures[i].set(self.DEFAULT_BLOCK_TEMP_A)
            else:
                self.block_temperatures[i].set(self.DEFAULT_BLOCK_TEMP_B)

            # Update electron parameters
            self.electron_ev_file_paths[i].set(electron_ev_path)
            self.electron_dos_file_paths[i].set(electron_dos_path)
            self.electron_relaxation_times[i].set(self.DEFAULT_ELECTRON_RELAXATION)
            self.electron_effective_masses[i].set(self.DEFAULT_ELECTRON_EFFECTIVE_MASS)

            # Update phonon parameters
            self.phonon_ev_file_paths[i].set(phonon_ev_path)
            self.phonon_dos_file_paths[i].set(phonon_dos_path)
            self.phonon_group_velocities[i].set(self.DEFAULT_PHONON_VELOCITIES)
            self.phonon_relaxation_times[i].set(self.DEFAULT_PHONON_RELAXATION)


    def update_number_of_blocks(self) -> None:
        '''
        Remove or add one or more blocks to the existing ones.
        '''
        # Calculate the old and new sizes
        old_list_size = len(self.block_sizes)
        new_list_size = self.number_of_blocks.get()
        size_delta = abs(new_list_size - old_list_size)

        # Removing block(s)
        if (new_list_size < old_list_size):
            self.block_sizes = self.block_sizes[:new_list_size]
            self.block_temperatures = self.block_temperatures[:new_list_size]
            self.fermi_energies = self.fermi_energies[:new_list_size]

            self.electron_ev_file_paths = self.electron_ev_file_paths[:new_list_size]
            self.electron_dos_file_paths = self.electron_dos_file_paths[:new_list_size]
            self.electron_tau_file_paths = self.electron_tau_file_paths[:new_list_size]
            self.electron_group_velocities = self.electron_group_velocities[:new_list_size]
            self.electron_relaxation_times = self.electron_relaxation_times[:new_list_size]
            self.electron_effective_masses = self.electron_effective_masses[:new_list_size]

            self.phonon_ev_file_paths = self.phonon_ev_file_paths[:new_list_size]
            self.phonon_dos_file_paths = self.phonon_dos_file_paths[:new_list_size]
            self.phonon_tau_file_paths = self.phonon_tau_file_paths[:new_list_size]
            self.phonon_group_velocities = self.phonon_group_velocities[:new_list_size]
            self.phonon_relaxation_times = self.phonon_relaxation_times[:new_list_size]
        
        # Adding block(s)
        elif (new_list_size > old_list_size):
            self.block_sizes += [DoubleVar() for _ in range(size_delta)]
            self.block_temperatures += [DoubleVar() for _ in range(size_delta)]
            self.fermi_energies += [DoubleVar() for _ in range(size_delta)]

            self.electron_ev_file_paths += [StringVar() for _ in range(size_delta)]
            self.electron_dos_file_paths += [StringVar() for _ in range(size_delta)]
            self.electron_tau_file_paths += [StringVar() for _ in range(size_delta)]
            self.electron_group_velocities += [DoubleVar() for _ in range(size_delta)]
            self.electron_relaxation_times += [DoubleVar() for _ in range(size_delta)]
            self.electron_effective_masses += [DoubleVar() for _ in range(size_delta)]

            self.phonon_ev_file_paths += [StringVar() for _ in range(size_delta)]
            self.phonon_dos_file_paths += [StringVar() for _ in range(size_delta)]
            self.phonon_tau_file_paths += [StringVar() for _ in range(size_delta)]
            self.phonon_group_velocities += [DoubleVar() for _ in range(size_delta)]
            self.phonon_relaxation_times += [DoubleVar() for _ in range(size_delta)]

        # Update the UI
        self.update_block_selection()

    
    def update_block_selection(self) -> None:
        '''
        Update the number of blocks available for selection
        '''
        # Create selection frame
        if self.block_input_selection_frame != None:
            self.block_input_selection_frame.destroy()

        self.block_input_selection_frame = ttk.LabelFrame(
            self.block_master_frame,
            text='Select Block',
            padding=10,
            relief=SOLID
        )
        self.block_input_selection_frame.grid(column=0, row=0, padx=5, pady=5, sticky=N)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create radio buttons
        self.block_radio_buttons = []
        num_blocks = self.number_of_blocks.get()
        for i in range(num_blocks):
            rb = ttk.Radiobutton(
                self.block_input_selection_frame,
                text=f"{i + 1}",
                variable=self.selected_block_input,
                command=self.update_block_data_window,
                value=i + 1
            )
            rb.grid(column=(i // int((num_blocks / 2) + 0.5)) % 2, row=i % int((num_blocks / 2) + 0.5), padx=8, pady=4, sticky=W)
            self.block_radio_buttons.append(rb)

    
    def update_block_data_window(self) -> None:
        '''
        (Re) create the window containing the block parameters.
        '''
        # Create parameter frame
        if self.block_parameter_frame != None:
            self.block_parameter_frame.destroy()

        self.block_parameter_frame = ttk.LabelFrame(
            self.block_master_frame,
            text="Block Data and Parameters",
            padding=5,
            relief=SOLID
        )
        self.block_parameter_frame.grid(column=1, row=0, padx=5, pady=5)

        block_index = self.selected_block_input.get() - 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create a combined frame for inputs
        combined_input_frame = ttk.Frame(self.block_parameter_frame)
        combined_input_frame.pack(fill=X)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Give users the option to load preferences from other block
        copy_input_frame = ttk.Frame(
            combined_input_frame,
            padding=10
        )
        copy_input_frame.pack()

        ttk.Separator(combined_input_frame, orient=HORIZONTAL).pack(fill=X)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Copy inputs label
        ttk.Label(
            copy_input_frame,
            text='Copy Inputs from Block:',
        ).grid(column=0, row=0, padx=5, pady=5)

        # Copy inputs spinbox (selector)
        ttk.Spinbox(
            copy_input_frame,
            from_=1,
            to=self.number_of_blocks.get(),
            increment=1,
            textvariable=self.block_to_copy_from,
            justify=CENTER,
            width=5
        ).grid(column=1, row=0, padx=7, pady=5)

        # Copy inputs button
        ttk.Button(
            copy_input_frame,
            text='Copy',
            command=self.copy_block_input,
            width=10
        ).grid(column=2, row=0, padx=5, pady=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create frame for general parameter inputs
        param_input_frame = ttk.Frame(
            combined_input_frame,
            padding=10
        )
        param_input_frame.pack()

        ttk.Separator(combined_input_frame, orient=HORIZONTAL).pack(fill=X)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Block size label
        ttk.Label(
            param_input_frame,
            text='Block Size',
            width=20
        ).grid(column=0, row=0)

        # Block size text entry 
        ttk.Entry(
            param_input_frame,
            textvariable=self.block_sizes[block_index],
            width=15
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Block size units
        ttk.Label(
            param_input_frame,
            text='m',
            width=20
        ).grid(column=2, row=0)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Block temperatures label
        ttk.Label(
            param_input_frame,
            text='Block Temperature',
            width=20
        ).grid(column=0, row=1)

        # Block temperatures text input 
        ttk.Entry(
            param_input_frame,
            textvariable=self.block_temperatures[block_index],
            width=15
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)  

        # Block temperatures unit 
        ttk.Label(
            param_input_frame,
            text='K',
            width=20
        ).grid(column=2, row=1)    

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Fermi energy label
        ttk.Label(
            param_input_frame,
            text='Fermi Energy',
            width=20
        ).grid(column=0, row=2)

        # Fermi energy text 
        ttk.Entry(
            param_input_frame,
            textvariable=self.fermi_energies[block_index],
            width=15
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Fermi energy unit  
        ttk.Label(
            param_input_frame,
            text='eV  X  1.60218e-19 J',
            width=20
        ).grid(column=2, row=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create the notebook and necessary tabs for inputs
        self.notebook = ttk.Notebook(
            self.block_parameter_frame,
            padding=10
        )
        self.notebook.pack()

        if self.selected_run_type.get() == RunType.BOTH.value:
            self.update_electron_tab()
            self.update_phonon_tab()

        elif self.selected_run_type.get()  == RunType.ELECTRON.value:
            self.update_electron_tab()
            
        elif self.selected_run_type.get()  == RunType.PHONON.value:
            self.update_phonon_tab()

        else:
            self.pop_up_error('Failed to populate electron/phonon input; invalid run type')


    def update_electron_tab(self) -> None:
        '''
        (Re) create the tab for the electron local system inputs
        '''
        # Create master electron frame
        electron_frame = ttk.Frame(self.notebook)
        electron_frame.grid()

        block_index = self.selected_block_input.get() - 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create file input frame
        electron_file_input_frame = ttk.Frame(
            electron_frame,
            padding=10
        )
        electron_file_input_frame.grid(column=0, row=0)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Electron ev file label
        ttk.Label(
            electron_file_input_frame,
            text='Electron EV Data',
            width=25
        ).grid(column=0, row=0)

        # Electron ev file text entry 
        ttk.Entry(
            electron_file_input_frame, 
            textvariable=self.electron_ev_file_paths[block_index],
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Electron ev file browse button
        ttk.Button(
            electron_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_ev_file_paths[block_index]),
            width=self.INPUT_DATA_BUTTON_WIDTH,
        ).grid(column=2, row=0, padx=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Electron dos file label
        ttk.Label(
            electron_file_input_frame,
            text='Electron DOS Data',
            width=25
        ).grid(column=0, row=1)

        # Electron dos file text entry 
        ttk.Entry(
            electron_file_input_frame, 
            textvariable=self.electron_dos_file_paths[block_index],
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Electron dos file browse button 
        ttk.Button(
            electron_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_dos_file_paths[block_index]),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=1, padx=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Electron tau file label
        ttk.Label(
            electron_file_input_frame,
            text='Electron Tau Data (optional)',
            width=25
        ).grid(column=0, row=2)

        # Electron tau file text entry 
        ttk.Entry(
            electron_file_input_frame, 
            textvariable=self.electron_tau_file_paths[block_index],
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Electron tau file browse button
        ttk.Button(
            electron_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.electron_tau_file_paths[block_index]),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=2, padx=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create parameter input frame
        electron_parameter_input_frame = ttk.Frame(
            electron_frame,
            padding=10
        )
        electron_parameter_input_frame.grid(column=0, row=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Electron group velocities label
        ttk.Label(
            electron_parameter_input_frame,
            text='Electron Group Velocities (optional)',
            width=35
        ).grid(column=0, row=0)

        # Electron group velocities text entry 
        ttk.Entry(
            electron_parameter_input_frame,
            textvariable=self.electron_group_velocities[block_index],
            width=15
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Electron group velocities unit
        ttk.Label(
            electron_parameter_input_frame,
            text='m/s',
            width=20
        ).grid(column=2, row=0)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Electron relaxation time label
        ttk.Label(
            electron_parameter_input_frame,
            text='Electron Relaxation Time',
            width=35
        ).grid(column=0, row=1)

        # Electron relaxation time text entry 
        ttk.Entry(
            electron_parameter_input_frame,
            textvariable=self.electron_relaxation_times[block_index],
            width=15
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Electron relaxation time unit 
        ttk.Label(
            electron_parameter_input_frame,
            text='s',
            width=20
        ).grid(column=2, row=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Electron effective mass time label
        ttk.Label(
            electron_parameter_input_frame,
            text='Electron Effective Mass',
            width=35
        ).grid(column=0, row=2)

        # Electron effective mass time text entry 
        ttk.Entry(
            electron_parameter_input_frame,
            textvariable=self.electron_effective_masses[block_index],
            width=15
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Electron effective mass time unit 
        ttk.Label(
            electron_parameter_input_frame,
            text='X  9.109e-31 kg',
            width=20
        ).grid(column=2, row=2)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Add the electron master frame to the notebook
        self.notebook.add(electron_frame, text='Electron Local System')


    def update_phonon_tab(self) -> None:
        '''
        (Re) create the tab for the phonon local system inputs
        '''
        # Create the master phonon frame
        phonon_frame = ttk.Frame(self.notebook)
        phonon_frame.grid()

        block_index = self.selected_block_input.get() - 1

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create file input frame
        phonon_file_input_frame = ttk.Frame(
            phonon_frame,
            padding=10
        )
        phonon_file_input_frame.grid(column=0, row=0)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Phonon ev file label
        ttk.Label(
            phonon_file_input_frame,
            text='Phonon EV Data',
            width=25
        ).grid(column=0, row=0)

        # Phonon ev file text entry
        ttk.Entry(
            phonon_file_input_frame, 
            textvariable=self.phonon_ev_file_paths[block_index],
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Phonon ev file browse button
        ttk.Button(
            phonon_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_ev_file_paths[block_index]),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=0, padx=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Phonon dos file label
        ttk.Label(
            phonon_file_input_frame,
            text='Phonon DOS Data',
            width=25
        ).grid(column=0, row=1)

        # Phonon dos file text entry
        ttk.Entry(
            phonon_file_input_frame, 
            textvariable=self.phonon_dos_file_paths[block_index],
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Phonon dos file browse button
        ttk.Button(
            phonon_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_dos_file_paths[block_index]),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=1, padx=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Phonon tau file label
        ttk.Label(
            phonon_file_input_frame,
            text='Phonon Tau Data (optional)',
            width=25
        ).grid(column=0, row=2)

        # Phonon tau file text entry
        ttk.Entry(
            phonon_file_input_frame, 
            textvariable=self.phonon_tau_file_paths[block_index],
            width=self.INPUT_DATA_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Phonon tau file browse button
        ttk.Button(
            phonon_file_input_frame, 
            text='Browse', 
            command=partial(self.select_file, self.INPUT_DATA_FILETYPES, self.phonon_tau_file_paths[block_index]),
            width=self.INPUT_DATA_BUTTON_WIDTH
        ).grid(column=2, row=2, padx=5)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Create parameter input frame
        phonon_parameter_input_frame = ttk.Frame(
            phonon_frame,
            padding=10
        )
        phonon_parameter_input_frame.grid(column=0, row=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Phonon group velocities label
        ttk.Label(
            phonon_parameter_input_frame,
            text='Phonon Group Velocities',
            width=35
        ).grid(column=0, row=0)

        # Phonon group velocities text entry
        ttk.Entry(
            phonon_parameter_input_frame,
            textvariable=self.phonon_group_velocities[block_index],
            width=15
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Phonon group velocities unit
        ttk.Label(
            phonon_parameter_input_frame,
            text='m/s',
            width=20
        ).grid(column=2, row=0)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Phonon relaxation time label
        ttk.Label(
            phonon_parameter_input_frame,
            text='Phonon Relaxation Time',
            width=35
        ).grid(column=0, row=1)

        # Phonon relaxation time text entry
        ttk.Entry(
            phonon_parameter_input_frame,
            textvariable=self.phonon_relaxation_times[block_index],
            width=15
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Phonon relaxation time unit
        ttk.Label(
            phonon_parameter_input_frame,
            text='s',
            width=20
        ).grid(column=2, row=1)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Add the phonon master frame to the notebook
        self.notebook.add(phonon_frame, text='Phonon Local System')

    
    def copy_block_input(self) -> None:
        '''
        Copy block parameters from the block to copy from to the selected block
        '''
        to_block_index = self.selected_block_input.get() - 1
        from_block_index = self.block_to_copy_from.get() - 1

        self.block_sizes[to_block_index].set(self.block_sizes[from_block_index].get())
        self.block_temperatures[to_block_index].set(self.block_temperatures[from_block_index].get())
        self.fermi_energies[to_block_index].set(self.fermi_energies[from_block_index].get())

        self.electron_ev_file_paths[to_block_index].set(self.electron_ev_file_paths[from_block_index].get())
        self.electron_dos_file_paths[to_block_index].set(self.electron_dos_file_paths[from_block_index].get())
        self.electron_tau_file_paths[to_block_index].set(self.electron_tau_file_paths[from_block_index].get())
        self.electron_group_velocities[to_block_index].set(self.electron_group_velocities[from_block_index].get())
        self.electron_relaxation_times[to_block_index].set(self.electron_relaxation_times[from_block_index].get())
        self.electron_effective_masses[to_block_index].set(self.electron_effective_masses[from_block_index].get())

        self.phonon_ev_file_paths[to_block_index].set(self.phonon_ev_file_paths[from_block_index].get())
        self.phonon_dos_file_paths[to_block_index].set(self.phonon_dos_file_paths[from_block_index].get())
        self.phonon_tau_file_paths[to_block_index].set(self.phonon_tau_file_paths[from_block_index].get())
        self.phonon_group_velocities[to_block_index].set(self.phonon_group_velocities[from_block_index].get())
        self.phonon_relaxation_times[to_block_index].set(self.phonon_relaxation_times[from_block_index].get())

        self.update_block_data_window()


    def cancel_data_input(self, window: Toplevel) -> None:
        '''
        Resets all data fields and then closes the window.

        :param window: The window object for the data input screen
        '''
        self.number_of_blocks = IntVar(value=self.DEFAULT_NUM_BLOCKS)       # scalar
        self.time_duration = DoubleVar(value=self.DEFAULT_TIME_DURATION)    # scalar
        self.selected_time_type = IntVar(value=self.DEFAULT_TIME_TYPE)      # min or max
        self.selected_run_type = IntVar(value=self.DEFAULT_RUN_TYPE)        # electron, phonon, or both
        self.run_type_buttons = []

        self.block_to_copy_from = IntVar(value=1)   # scalar 

        self.block_sizes = []                       # DoubleVar
        self.block_temperatures = []                # DoubleVar
        self.fermi_energies = []                    # DoubleVar

        self.electron_ev_file_paths = []            # StringVar
        self.electron_dos_file_paths = []           # StringVar
        self.electron_tau_file_paths = []           # StringVar
        self.electron_group_velocities = []         # DoubleVar
        self.electron_relaxation_times = []         # DoubleVar
        self.electron_effective_masses = []         # DoubleVar

        self.phonon_ev_file_paths = []              # StringVar
        self.phonon_dos_file_paths = []             # StringVar
        self.phonon_tau_file_paths = []             # StringVar
        self.phonon_group_velocities = []           # DoubleVar
        self.phonon_relaxation_times = []           # DoubleVar

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Update the plotting buttons
        self.update_plot_radio_buttons(False)
        self.update_plot_check_buttons(False)

        # Give back input control and close the window
        window.grab_release()
        window.destroy()


    def confirm_data_input_and_run(self, window: Toplevel) -> None:
        '''
        Ensures all data fields are filled out and the data is formatted correctly.

        :param window: The window object for the data input screen
        '''
        # Check base parameters
        if not self.number_of_blocks.get() or not self.time_duration.get() or not self.selected_run_type.get():
            self.pop_up_error('Please Complete All Fields\n\nMissing One or More Base Parameter')
            return
        
        # Check block sizes
        for block_size in self.block_sizes:
            if not block_size or not block_size.get():
                self.pop_up_error('Please Complete All Fields\n\nMissing One or More Block Size')
                return
            
        # Check block temperatures
        for block_temp in self.block_temperatures:
            if not block_temp or not block_temp.get():
                self.pop_up_error('Please Complete All Fields\n\nMissing One or More Block Temperature')
                return
            
        # Check fermi energies
        for energy in self.fermi_energies:
            if not energy or not energy.get():
                self.pop_up_error('Please Complete All Fields\n\nMissing One or More Fermi Energy')
                return

        # Get the run type
        run_type = self.selected_run_type.get()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Check electron run parameters
        if (run_type == RunType.ELECTRON.value or run_type == RunType.BOTH.value):

            # Check electron ev filepaths
            for file_path in self.electron_ev_file_paths:
                if not file_path or not file_path.get() or file_path.get() == "":
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Electron EV File Path')
                    return
                
            # Check electron dos filepaths
            for file_path in self.electron_dos_file_paths:
                if not file_path or not file_path.get() or file_path.get() == "":
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Electron DOS File Path')
                    return
                
            # Check electron relaxation times
            for relax_time in self.electron_relaxation_times:
                if not relax_time or not relax_time.get():
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Electron Relaxation Time')
                    return
                
            # Check electron effective masses
            for effect_mass in self.electron_effective_masses:
                if not effect_mass or not effect_mass.get():
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Electron Effective Mass')
                    return
                
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
                
        # Check phonon run parameters
        if (run_type == RunType.PHONON.value or run_type == RunType.BOTH.value):

            # Check phonon ev filepaths
            for file_path in self.phonon_ev_file_paths:
                if not file_path or not file_path.get() or file_path.get() == "":
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Phonon EV File Path')
                    return
                
            # Check phonon dos filepaths
            for file_path in self.phonon_dos_file_paths:
                if not file_path or not file_path.get() or file_path.get() == "":
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Phonon DOS File Path')
                    return
                
            # Check phonon group velocities
            for velocity in self.phonon_group_velocities:
                if not velocity or not velocity.get():
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Phonon Group Velocities')
                    return
            
            # Check phonon relaxation times
            for relax_time in self.phonon_relaxation_times:
                if not relax_time or not relax_time.get():
                    self.pop_up_error('Please Complete All Fields\n\nMissing One or More Phonon Relaxation Time')
                    return
            
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Give back input control and close the window
        window.grab_release()
        window.destroy()

        # Run the SEAQT backend
        self.update_plot(PlotNumber.DATA_PROCESSING.value)
        self.start_data_process()


    def start_data_process(self) -> None:
        '''
        Run the SEAQT backend using the desired handler.
        '''
        # Add base parameters
        self.input_json_dict['number_of_blocks'] = self.number_of_blocks.get()
        self.input_json_dict['time_duration'] = self.time_duration.get()
        self.input_json_dict['time_type'] = self.selected_time_type.get()
        self.input_json_dict['run_type'] = self.selected_run_type.get()

        # Add shared parameters
        self.input_json_dict['block_sizes'] = [x.get() for x in self.block_sizes]
        self.input_json_dict['block_temperatures'] = [x.get() for x in self.block_temperatures]
        self.input_json_dict['fermi_energies'] = [x.get() for x in self.fermi_energies]

        # Get the run type
        run_type = self.selected_run_type.get()

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Add electron parameters
        if run_type == RunType.ELECTRON.value or run_type == RunType.BOTH.value:

            self.input_json_dict['electron_ev_paths'] = [x.get() for x in self.electron_ev_file_paths]
            self.input_json_dict['electron_dos_paths'] = [x.get() for x in self.electron_dos_file_paths]
            self.input_json_dict['electron_tau_paths'] = [x.get() for x in self.electron_tau_file_paths]

            self.input_json_dict['electron_group_velocities'] = [x.get() for x in self.electron_group_velocities]
            self.input_json_dict['electron_relaxation_times'] = [x.get() for x in self.electron_relaxation_times]
            self.input_json_dict['electron_effective_masses'] = [x.get() for x in self.electron_effective_masses]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Add phonon parameters
        if run_type == RunType.PHONON.value or run_type == RunType.BOTH.value:
            
            self.input_json_dict['phonon_ev_paths'] = [x.get() for x in self.phonon_ev_file_paths]
            self.input_json_dict['phonon_dos_paths'] = [x.get() for x in self.phonon_dos_file_paths]
            self.input_json_dict['phonon_tau_paths'] = [x.get() for x in self.phonon_tau_file_paths]

            self.input_json_dict['phonon_group_velocities'] = [x.get() for x in self.phonon_group_velocities]
            self.input_json_dict['phonon_relaxation_times'] = [x.get() for x in self.phonon_relaxation_times]

        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Write the JSON object to the prefs file
        with open(self.prefs_file_path, 'w') as prefs_file:
            json.dump(self.input_json_dict, prefs_file)

        # Run the backend (NOTE: blocking)
        try:
            if run_type == RunType.ELECTRON.value:
                self.backend.run_seaqt_electron_only()
            elif run_type == RunType.PHONON.value:
                self.backend.run_seaqt_phonon_only()
            elif run_type == RunType.BOTH.value:
                self.backend.run_seaqt()
            else:
                self.pop_up_error(f'Invalid Run Type: {run_type}.\n\nThis could be due to faulty input data or parameters; or due to an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
                self.update_plot(PlotNumber.ERROR.value)
                return
            
            self.update_plot(PlotNumber.DATA_PROCESSED_SUCCESSFULLY.value)
        except:
            self.pop_up_error('SEAQT Backend Encountered an Error.\n\nThis could be due to faulty input data or parameters; or due to an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
            self.update_plot(PlotNumber.ERROR.value)
            return
        
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

        # Block the new and load buttons
        self.new_run_button['state'] = DISABLED
        self.load_run_button['state'] = DISABLED

        # Unlock replot, reset, and save buttons
        self.plot_button['state'] = NORMAL
        self.reset_button['state'] = NORMAL
        self.save_button['state'] = NORMAL

        # Update the plotting buttons
        self.update_plot_check_buttons(True)

        
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
        
        # Copy relevant values from JSON file to class vairables
        try:
            with open(self.prefs_file_path, 'r') as prefs_file:

                # Load JSON file
                prefs_json = json.load(prefs_file)
                self.input_json_dict = prefs_json

                # Extract global variables
                num_blocks = prefs_json['number_of_blocks']
                run_type = prefs_json['run_type']

                self.number_of_blocks.set(num_blocks)
                self.selected_run_type.set(run_type)
                self.time_duration.set(prefs_json['time_duration'])
                self.selected_time_type.set(prefs_json['time_type'])

                # Reset global arrays
                self.block_sizes = []                       # DoubleVar
                self.block_temperatures = []                # DoubleVar
                self.fermi_energies = []                    # DoubleVar

                self.electron_ev_file_paths = []            # StringVar
                self.electron_dos_file_paths = []           # StringVar
                self.electron_tau_file_paths = []           # StringVar
                self.electron_group_velocities = []         # DoubleVar
                self.electron_relaxation_times = []         # DoubleVar
                self.electron_effective_masses = []         # DoubleVar

                self.phonon_ev_file_paths = []              # StringVar
                self.phonon_dos_file_paths = []             # StringVar
                self.phonon_tau_file_paths = []             # StringVar
                self.phonon_group_velocities = []           # DoubleVar
                self.phonon_relaxation_times = []           # DoubleVar

                # Load each block's parameters
                for i in range(num_blocks):

                    # Shared parameters
                    self.block_sizes.append(DoubleVar(value=prefs_json['block_sizes'][i]))
                    self.block_temperatures.append(DoubleVar(value=prefs_json['block_temperatures'][i]))
                    self.fermi_energies.append(DoubleVar(value=prefs_json['fermi_energies'][i]))

                    # Electron-only parameters
                    if run_type == RunType.ELECTRON.value or run_type == RunType.BOTH.value:

                        self.electron_ev_file_paths.append(StringVar(value=prefs_json['electron_ev_paths'][i]))
                        self.electron_dos_file_paths.append(StringVar(value=prefs_json['electron_dos_paths'][i]))
                        self.electron_tau_file_paths.append(StringVar(value=prefs_json['electron_tau_paths'][i]))

                        self.electron_group_velocities.append(DoubleVar(value=prefs_json['electron_group_velocities'][i]))
                        self.electron_relaxation_times.append(DoubleVar(value=prefs_json['electron_relaxation_times'][i]))
                        self.electron_effective_masses.append(DoubleVar(value=prefs_json['electron_effective_masses'][i]))

                    # Phonon-only parameters
                    if run_type == RunType.PHONON.value or run_type == RunType.BOTH.value:
                        
                        self.phonon_ev_file_paths.append(StringVar(value=prefs_json['phonon_ev_paths'][i]))
                        self.phonon_dos_file_paths.append(StringVar(value=prefs_json['phonon_dos_paths'][i]))
                        self.phonon_tau_file_paths.append(StringVar(value=prefs_json['phonon_tau_paths'][i]))

                        self.phonon_group_velocities.append(DoubleVar(value=prefs_json['phonon_group_velocities'][i]))
                        self.phonon_relaxation_times.append(DoubleVar(value=prefs_json['phonon_relaxation_times'][i]))
        except:
            self.pop_up_error('Failed to read parameters from preferences file; data may be missing or corrupted.')
            return

        # Disable new, load, and save buttons
        self.new_run_button['state'] = DISABLED
        self.load_run_button['state'] = DISABLED
        self.save_button['state'] = DISABLED

        # Enable reset and plot buttons
        self.reset_button['state'] = NORMAL
        self.plot_button['state'] = NORMAL

        # Update the plotting buttons
        self.update_plot_radio_buttons(True)
        self.update_plot_check_buttons(True)

        # Update plot image
        self.update_plot(PlotNumber.DATA_LOADED_SUCCESSFULLY.value)
    

    def update_plot(self, filenum: int) -> None:
        '''
        Update the central plot using the given file number.

        :param filenum: The number relating to the plot to show
        '''
        try:
            # Open the desired image
            loaded_image = Image.open(f'Figures/{filenum}.png')
            # loaded_image = loaded_image.resize((600, 600), Image.NEAREST)
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
        self.data_frame_image_frame.configure(image=self.data_frame_image, borderwidth=0)


    def replot(self) -> bool:
        '''
        Replot with the new selected subsystems.

        :return: True iff the plot was successful; false otherwise
        '''
        # Tally the selected subsystems
        self.selected_blocks = []
        for i in range(len(self.block_variables)):
            if self.block_variables[i].get():
                self.selected_blocks.append(i)

        if len(self.selected_blocks) == 0:
            self.pop_up_error('No Block(s) Selected. Please Choose at Least One.')
            return False
        
        self.input_json_dict['selected_subs'] = self.selected_blocks

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

            run_type = self.selected_run_type.get()
            if run_type == RunType.ELECTRON.value or run_type == RunType.BOTH.value:
                self.selected_plot.set(PlotNumber.ELECTRON_TEMPERATURE.value)
            elif run_type == RunType.PHONON.value:
                self.selected_plot.set(PlotNumber.PHONON_TEMPERATURE.value)
            else:
                self.pop_up_error(f'Invalid Run Type: {run_type}.\n\nThis could be due to faulty input data or parameters; or due to an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
                return False

            self.update_plot(self.selected_plot.get())
        except:
            self.pop_up_error('SEAQT Backend Encountered an Error.\n\nThis could be due to faulty input data or parameters; or due to an internal bug.\n\nPlease try again; if the problem persists, please open a ticket at https://github.com/azsprague/seaqt-gui/issues.')
            return False

        # Update plotting buttons
        self.update_plot_radio_buttons(True)

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

            self.number_of_blocks = IntVar(value=self.DEFAULT_NUM_BLOCKS)       # scalar
            self.time_duration = DoubleVar(value=self.DEFAULT_TIME_DURATION)    # scalar
            self.selected_time_type = IntVar(value=self.DEFAULT_TIME_TYPE)      # min or max
            self.selected_run_type = IntVar(value=self.DEFAULT_RUN_TYPE)        # electron, phonon, or both
            self.run_type_buttons = []

            self.block_to_copy_from = IntVar(value=1)   # scalar 

            self.block_sizes = []                       # DoubleVar
            self.block_temperatures = []                # DoubleVar
            self.fermi_energies = []                    # DoubleVar

            self.electron_ev_file_paths = []            # StringVar
            self.electron_dos_file_paths = []           # StringVar
            self.electron_tau_file_paths = []           # StringVar
            self.electron_group_velocities = []         # DoubleVar
            self.electron_relaxation_times = []         # DoubleVar
            self.electron_effective_masses = []         # DoubleVar

            self.phonon_ev_file_paths = []              # StringVar
            self.phonon_dos_file_paths = []             # StringVar
            self.phonon_tau_file_paths = []             # StringVar
            self.phonon_group_velocities = []           # DoubleVar
            self.phonon_relaxation_times = []           # DoubleVar

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

            # Update the plotting buttons
            self.update_plot_radio_buttons(False)
            self.update_plot_check_buttons(False)

            # Reset the displayed image (data not loaded)
            self.update_plot(PlotNumber.DATA_NOT_LOADED.value)

            # Enable new and load buttons, disable reset, save, and export buttons
            self.new_run_button['state'] = NORMAL
            self.load_run_button['state'] = NORMAL
            self.reset_button['state'] = DISABLED
            self.save_button['state'] = DISABLED
            self.export_button['state'] = DISABLED

            # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #

            # Remove any old plots
            clear_matlab_meta()
            clear_plots()


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
        # export_window.resizable(False, False)
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
