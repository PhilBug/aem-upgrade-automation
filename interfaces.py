from abc import ABCMeta, abstractmethod

class IExecutable:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def execute(self):
        raise NotImplementedError
