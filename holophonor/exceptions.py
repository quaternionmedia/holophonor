class HolophonorException(Exception):
    """Base class for all exceptions raised by the Holophonor package."""
    pass

class LoopNotFoundException(HolophonorException):
    """Exception raised when a loop is not found."""
    pass

class SceneNotFoundException(HolophonorException):
    """Exception raised when a scene is not found."""
    pass
