import os
import logging

from typing import Tuple
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox
from functools import partial


class SEAQTGui():
    '''
    GUI class for SEAQT handler.
    '''

    # Class ('global') constants
    FRAME_PAD_X = 5
    FRAME_PAD_Y = 5
    ENTRY_PAD_X = 5
    ENTRY_PAD_Y = 2
    INPUT_FRAME_PAD_X = 15
    INPUT_FRAME_PAD_Y = 7
    INPUT_DATA_BUTTON_TEXT = 'Browse'
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
    DATA_VIEW_FRAME_WIDTH = 600
    DATA_VIEW_FRAME_HEIGHT = 350
    TIMER_FRAME_WIDTH = 105
    TIMER_FRAME_HEIGHT = 60
    MENU_FRAME_PAD_Y = 5
    MENU_BUTTON_WIDTH = 10
    MENU_BUTTON_PAD_X = 5
    MENU_BUTTON_PAD_Y = 6
    

    def __init__(self):
        '''
        Class constructor; create a SEAQTGui object, instantiate global variables, and starts the main menu.
        '''
        logging.info('Starting SEAQT GUI')

        # Create the Tkinter root window
        self.tkinter_root = Tk()
        self.tkinter_root.title('SEAQT GUI')
        self.tkinter_root.resizable(False, False)

        # Class ('global') variables
        self.electron_ev_file_path = StringVar(self.tkinter_root)
        self.electron_dos_file_path = StringVar(self.tkinter_root)
        self.phonon_ev_file_path = StringVar(self.tkinter_root)
        self.phonon_dos_file_path = StringVar(self.tkinter_root)
        
        self.fermi_energy = DoubleVar(self.tkinter_root, 6)                         # eV * 1.60218 * (10**-19) Joules
        self.phonon_group_velocities = DoubleVar(self.tkinter_root, 6000)           # m/s
        self.phonon_relaxation_time = DoubleVar(self.tkinter_root, 50 * (10**-12))  # seconds
        self.number_of_subsystems = IntVar(self.tkinter_root, 12)                   # amount
        self.subsystems_size = DoubleVar(self.tkinter_root, 1 * (10**-7))           # meters
        self.subsystem_temperatures_string = StringVar(self.tkinter_root, '295, 295, 295, 295, 295, 295, 300, 300, 300, 300, 300, 300')   # Kelvin    
        self.subsystem_temperatures_list = []                                       # Kelvin
        self.time = DoubleVar(self.tkinter_root, 20)                                # ??? (TODO)

        # Run the GUI
        self.activate_main_window()
        self.tkinter_root.mainloop()


    def activate_main_window(self) -> None:
        '''
        Create the 'main menu' of the GUI, including the data view, timer, and menu buttons.
        '''
        logging.info('Main Window Activated')

        #############################
        # Start frame for data view #
        #############################

        # Create data view frame
        data_view_frame = ttk.Frame(
            self.tkinter_root,
            padding=10,
            width=self.DATA_VIEW_FRAME_WIDTH,
            height=self.DATA_VIEW_FRAME_HEIGHT,
            relief=SOLID
        )
        data_view_frame.grid(padx=30, pady=20)
        data_view_frame.grid_propagate(False)

        # Create data message
        ttk.Label(
            data_view_frame,
            text='No Data Loaded\nClick "Load" to Import',
            justify=CENTER,
            padding=10
        ).place(relx=0.5, rely=0.5, anchor=CENTER)

        #############################
        # Start frame for menu view #
        #############################

        # Create outer menu frame
        outer_menu_frame = ttk.Frame(
            self.tkinter_root,
            padding=10
        )
        outer_menu_frame.grid(column=1, row=0)

        # Create timer frame
        timer_frame = ttk.LabelFrame(
            outer_menu_frame,
            text='Time Remaining',
            width=self.TIMER_FRAME_WIDTH,
            height=self.TIMER_FRAME_HEIGHT,
            padding=10,
            relief=SOLID
        )
        timer_frame.grid(column=0, row=0, pady=self.MENU_FRAME_PAD_Y)
        timer_frame.grid_propagate(False)

        # Timer label
        ttk.Label(
            timer_frame,
            text='00:00:00'
        ).place(relx=0.5, rely=0.5, anchor=CENTER)

        # Create menu option frame
        menu_option_frame = ttk.LabelFrame(
            outer_menu_frame,
            text='Menu',
            padding=10,
            relief=SOLID
        )
        menu_option_frame.grid(column=0, row=1, pady=self.MENU_FRAME_PAD_Y)

        # Load data button
        ttk.Button(
            menu_option_frame,
            text='Load',
            command=self.activate_input_data_window,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=0, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Start run button
        ttk.Button(
            menu_option_frame,
            text='Start',
            command=self.start_data_process,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=1, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Stop run button
        ttk.Button(
            menu_option_frame,
            text='Stop',
            command=self.stop_data_process,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=2, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Reset run button
        ttk.Button(
            menu_option_frame,
            text='Reset',
            command=self.reset_data_process,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=3, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Export run button
        ttk.Button(
            menu_option_frame,
            text='Export',
            command=self.export_data,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=4, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Help button
        ttk.Button(
            menu_option_frame,
            text='Help',
            command=self.activate_help_window,
            width=self.MENU_BUTTON_WIDTH
        ).grid(column=0, row=5, padx=self.MENU_BUTTON_PAD_X, pady=self.MENU_BUTTON_PAD_Y)

        # Copyright
        ttk.Label(
            self.tkinter_root,
            text='© 2023'
        ).grid(column=1, row=1)


    def activate_input_data_window(self) -> None:
        '''
        Collect input data files and important parameters from the user.
        '''       
        logging.info('Data Input Window Activated')

        # Create a new pop-up window and take control of input
        input_window = Toplevel(self.tkinter_root)
        input_window.title('Load Data and Set Parameters')
        input_window.grab_set()
        input_window.grid_columnconfigure(0, weight=1)
        input_window.grid_columnconfigure(1, weight=1)

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
        file_input_frame.grid(column=0, row=1, padx=self.INPUT_FRAME_PAD_X, pady=self.INPUT_FRAME_PAD_Y)

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
            text=self.INPUT_DATA_BUTTON_TEXT, 
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
            text=self.INPUT_DATA_BUTTON_TEXT, 
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
            text=self.INPUT_DATA_BUTTON_TEXT, 
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
            text=self.INPUT_DATA_BUTTON_TEXT, 
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

        # Select time ??? (TODO)
        ttk.Label(
            parameter_input_frame,
            text='Time (max(tau))',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=6)

        ttk.Entry(
            parameter_input_frame,
            textvariable=self.time,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=6)

        ##################################
        # Start frame for bottom buttons #
        ##################################

        # Create frame for bottom buttons
        data_input_button_frame = ttk.Frame(
            input_window,
            padding=10
        )
        data_input_button_frame.grid(column=0, row=3, padx=self.INPUT_FRAME_PAD_X, pady=self.INPUT_FRAME_PAD_Y)

        # Cancel button
        ttk.Button(
            data_input_button_frame,
            text='Cancel',
            command=input_window.destroy
        ).grid(column=0, row=0, padx=self.INPUT_BOTTOM_BUTTON_PAD_X)

        # Confirm button (all fields must be filled to confirm)
        ttk.Button(
            data_input_button_frame, 
            text='Confirm', 
            command=partial(self.confirm_data_input, input_window)
        ).grid(column=1, row=0, padx=self.INPUT_BOTTOM_BUTTON_PAD_X)


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


    def confirm_data_input(self, window: Toplevel) -> None:
        '''
        Ensures all data fields are filled out and the data is formatted correctly.
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
                not self.time.get()):

            messagebox.showerror(
                title='ERROR',
                message='Please Complete All Fields'
            )
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
        subsystem_temps_list = [x.strip() for x in subsystem_temps_string.split(',')]   # Split string by commas and strip any whitespace
        if len(subsystem_temps_list) != self.number_of_subsystems.get():
            self.pop_up_error('Number of Subsystems Does Not Match Number of Supplied Temperatures')
            return

        # Give back input control and close the window
        window.grab_release()
        window.destroy()


    def start_data_process(self) -> None:
        '''
        TODO
        '''
        self.feature_not_implemented_error()

    
    def stop_data_process(self) -> None:
        '''
        TODO
        '''
        self.feature_not_implemented_error()


    def reset_data_process(self) -> None:
        '''
        TODO
        '''
        self.feature_not_implemented_error()


    def export_data(self) -> None:
        '''
        TODO
        '''
        self.feature_not_implemented_error()


    def activate_help_window(self) -> None:
        '''
        TODO
        '''
        self.feature_not_implemented_error()

    
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
