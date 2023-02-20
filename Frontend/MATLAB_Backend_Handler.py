import matlab.engine


class MATLABBackendHandler():
    '''
    SEAQT backend handler implementation for original MATLAB scripts.
    '''

    def __init__(self, input_file_path: str):
        '''
        Class constructor; starts the backend handler by starting the matlab engine (must be preconfigured).

        :param input_file_path: Path to prefs file containing all SEAQT inputs and parameters
        '''
        self.input_file_path = input_file_path
        self.matlab_engine = matlab.engine.start_matlab()
        self.matlab_engine.addpath('../Backend/MATLAB')


    def start_seaqt(self) -> bool:
        '''
        Start the SEAQT backend process(es).

        :return: True iff the SEAQT backend was successfully started; False otherwise
        '''
        # self.matlab_engine.Phase1()
        pass


    def stop_seaqt(self) -> bool:
        '''
        Pause (but don't reset) the SEAQT backend process(es).

        :return: True iff the SEAQT backend was successfully stopped; False otherwise
        '''
        pass


    def reset_seaqt(self) -> bool:
        '''
        Reset the SEAQT backend process(es).

        :return: True iff the SEAQT backend was successfully reset; False otherwise
        '''
        pass


    def get_results(self) -> str:
        '''
        Retrieve the results from the SEAQT backend process(es).

        :return: The filename (str) of the SEAQT backend output
        '''
        pass
