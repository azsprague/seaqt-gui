from abc import ABC, abstractmethod


class BackendHandler(ABC):
    '''
    Abstract class to represent a SEAQT backend handler. Implement all methods with decorator '@abstractmethod'.
    Use 'SEAQT_Wrapper_MATLAB.py' as an example.
    '''

    def __init__(self, input_file_path: str):
        '''
        Class constructor; create a backend handler object.

        :param input_file: A JSON file containing the filenames and inputs to be run
        '''
        self.input_file_path = input_file_path
        super().__init__()
    

    @abstractmethod
    def run_seaqt(self) -> bool:
        '''
        Start the SEAQT backend process(es).
        To be implemented in child class.

        :return: True iff the SEAQT backend was successfully started; False otherwise
        '''
        pass


    @abstractmethod
    def reset_seaqt(self) -> bool:
        '''
        Reset the SEAQT backend process(es).
        To be implemented in child class.

        :return: True iff the SEAQT backend was successfully reset; False otherwise
        '''
        pass


    @abstractmethod
    def get_results(self) -> str:
        '''
        Retrieve the results from the SEAQT backend process(es).
        To be implemented in child class.

        :return: The filename (str) of the SEAQT backend output
        '''
        pass
