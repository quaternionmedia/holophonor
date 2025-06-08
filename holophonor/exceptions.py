class HolophonorException(Exception):
    """Base class for all exceptions raised by the Holophonor package."""

    pass


class LoopNotFoundException(HolophonorException):
    """Exception raised when a loop is not found."""

    ...


class SceneNotFoundException(HolophonorException):
    """Exception raised when a scene is not found."""

    pass


class ProcessNotFoundException(HolophonorException):
    """Exception raised when a running process is not found."""

    pass
