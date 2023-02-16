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
    INPUT_DATA_BUTTON_TEXT = 'Browse'
    INPUT_DATA_BUTTON_WIDTH = 10
    INPUT_DATA_LABEL_WIDTH = 20
    INPUT_DATA_ENTRY_WIDTH = 50
    INPUT_DATA_FILETYPES = (
        ('Excel Spreadsheet', '*.xlsx'),
        ('Comma-Separated Values', '*.csv')
    )
    INPUT_PARAMETER_LABEL_WIDTH = 27
    INPUT_PARAMETER_ENTRY_WIDTH = 30
    INPUT_PARAMETER_INNER_FRAME_PAD_Y = 5


    def __init__(self):
        '''
        Class constructor; create a SEAQTGui object and instantiate global variables.
        '''
        logging.info('Starting SEAQT GUI')

        # Create the Tkinter root window and frame
        self.tkinter_root = Tk()
        self.tkinter_root.title('SEAQT GUI')
        self.tkinter_root.resizable(False, False)
        self.gui_frame = ttk.Frame(self.tkinter_root, padding=10)
        self.gui_frame.grid()

        # Class ('global') variables
        self.electron_ev_file_path = StringVar(self.tkinter_root)
        self.electron_dos_file_path = StringVar(self.tkinter_root)
        self.phonon_ev_file_path = StringVar(self.tkinter_root)
        self.phonon_dos_file_path = StringVar(self.tkinter_root)
        
        self.fermi_energy = DoubleVar(self.tkinter_root, 6)                         # eV * 1.60218 * (10**-19) Joules
        self.phonon_group_velocities = DoubleVar(self.tkinter_root, 6000)           # m/s
        self.phonon_relaxation_time = DoubleVar(self.tkinter_root, 50 * (10**-12))  # seconds
        self.number_of_subsystems = IntVar(self.tkinter_root, 12)
        self.subsystems_size = DoubleVar(self.tkinter_root, 1 * (10**-7))           # meters
        self.subsystem_temperatures_string = StringVar(self.tkinter_root, '295,295,295,295,295,295,300,300,300,300,300,300')   # Kelvin    
        self.subsystem_temperatures_list = []                                       # Kelvin
        self.time = DoubleVar(self.tkinter_root, 20)                                # ??? (TODO)


    def run(self):
        '''
        Run the main loop of the GUI. Gets input from user, passes to the backend, then displays results.
        '''
        # Get input data and parameters from user
        self.get_input_data()

        # Create the window (GUI)
        self.tkinter_root.mainloop()


    def get_input_data(self) -> None:
        '''
        Collect input data files and important parameters from the user.
        '''
        ###############################
        # Start frame for file inputs #
        ###############################

        # Create file input frame
        file_input_frame = ttk.LabelFrame(
            self.gui_frame, 
            text='Input Data',
            padding=10, 
            relief=SOLID
        )
        file_input_frame.grid(column=0, row=1, padx=self.FRAME_PAD_X, pady=self.FRAME_PAD_Y)

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

        #############################
        # End frame for file inputs #
        #############################


        ####################################
        # Start frame for parameter inputs #
        ####################################

        # Create parent parameter input frame
        parameter_input_frame = ttk.LabelFrame(
            self.gui_frame, 
            text='SEAQT Parameters',
            padding=10, 
            relief=SOLID
        )
        parameter_input_frame.grid(column=0, row=2, padx=self.FRAME_PAD_X, pady=self.FRAME_PAD_Y)

        # Create upper parameter input frame
        upper_parameter_input_frame = ttk.Frame(parameter_input_frame)
        upper_parameter_input_frame.grid(column=0, row=0, pady=self.INPUT_PARAMETER_INNER_FRAME_PAD_Y)

        # Select Fermi energy (label, entry)
        ttk.Label(
            upper_parameter_input_frame,
            text='Fermi Energy (eV)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=0)

        ttk.Entry(
            upper_parameter_input_frame,
            textvariable=self.fermi_energy,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select phonon group velocities
        ttk.Label(
            upper_parameter_input_frame,
            text='Phonon Group Velocities (m/s)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=1)

        ttk.Entry(
            upper_parameter_input_frame,
            textvariable=self.phonon_group_velocities,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select phonon relaxation time
        ttk.Label(
            upper_parameter_input_frame,
            text='Phonon Relaxation Time (s)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=0, row=2)

        ttk.Entry(
            upper_parameter_input_frame,
            textvariable=self.phonon_relaxation_time,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=1, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select number of subsystems
        ttk.Label(
            upper_parameter_input_frame,
            text='Number of Subsystems',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=2, row=0)

        ttk.Entry(
            upper_parameter_input_frame,
            textvariable=self.number_of_subsystems,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=3, row=0, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select subsystems size
        ttk.Label(
            upper_parameter_input_frame,
            text='Subsystems Size (m)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=2, row=1)

        ttk.Entry(
            upper_parameter_input_frame,
            textvariable=self.subsystems_size,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=3, row=1, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Select subsystem temperatures
        ttk.Label(
            upper_parameter_input_frame,
            text='Subsystem Temperatures (K)',
            width=self.INPUT_PARAMETER_LABEL_WIDTH
        ).grid(column=2, row=2)

        ttk.Entry(
            upper_parameter_input_frame,
            textvariable=self.subsystem_temperatures_string,
            width=self.INPUT_PARAMETER_ENTRY_WIDTH
        ).grid(column=3, row=2, padx=self.ENTRY_PAD_X, pady=self.ENTRY_PAD_Y)

        # Create lower parameter input frame
        lower_parameter_input_frame = ttk.Frame(parameter_input_frame)
        lower_parameter_input_frame.grid(column=0, row=1, pady=self.INPUT_PARAMETER_INNER_FRAME_PAD_Y)

        # Select time ??? (TODO)
        ttk.Label(
            lower_parameter_input_frame,
            text='Time (max(tau))',
            width=15
        ).grid(column=2, row=3)

        ttk.Entry(
            lower_parameter_input_frame,
            textvariable=self.time,
            width=5
        ).grid(column=3, row=3)

        ##################################
        # End frame for parameter inputs #
        ##################################


        # Confirm button (all fields must be filled to confirm)
        ttk.Button(
            self.gui_frame, 
            text='Confirm', 
            command=self.confirm_data_input
        ).grid(column=0, row=3)


    def select_file(self, filetypes: Tuple[Tuple[str, str]], global_file_path: StringVar) -> None:
        '''
        Comment

        :param filetypes: A tuple of tuples containing (description, filetype)'s, e.g., ('text files', '*.txt')
        :param global_file_path: StringVar to contain the chosen file path
        '''
        filename = fd.askopenfilename(
            title='Select a File',
            filetypes=filetypes
        )

        global_file_path.set(filename)


    def confirm_data_input(self) -> None:
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
                message='Please Complete all Fields'
            )
        
        # Convert temperature string to array
        subsystem_temps_string = self.subsystem_temperatures_string.get()
        subsystem_temps_list = subsystem_temps_string.split(',')
        if len(subsystem_temps_list) != self.number_of_subsystems.get():
            messagebox.showerror(
                title='ERROR',
                message='Number of Subsystems Does Not Match Number of Supplied Temperatures'
            )
        
        # Close the window
        self.tkinter_root.destroy
