from grid2op.Exceptions.Grid2OpException import Grid2OpException


# Exception bad environment configured
class EnvError(Grid2OpException):
    """
    This exception indicate that the :class:`grid2op.Environment.Environment` is poorly configured.

    It is for example thrown when assessing if a backend is properly set up with
    :func:`grid2op.Backend.Backend.assert_grid_correct`
    """
    pass


class IncorrectNumberOfLoads(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the total number of
    loads of the powergrid.
    """
    pass


class IncorrectNumberOfGenerators(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the total number of
    generators of the powergrid.
    """
    pass


class IncorrectNumberOfLines(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the total number of
     powerlines of the powergrid.
    """
    pass


class IncorrectNumberOfSubstation(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the total
    number of substation of the powergrid.
    """
    pass


class IncorrectNumberOfElements(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the total number
    of elements of the powergrid.
    """
    pass

class IncorrectPositionOfLoads(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the number of
    loads at a substation.
    """
    pass


class IncorrectPositionOfGenerators(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the number of
    generators at a substation.
    """
    pass
class IncorrectPositionOfLines(EnvError):
    """
    This is a more precise exception than :class:`EnvError` indicating that there is a mismatch in the number of
    power lines at a substation.
    """
    pass

# Unknown environment at creating
class UnknownEnv(Grid2OpException):
    """
    This exception indicate that a bad argument has been sent to the :func:`grid2op.make` function.

    It does not recognize the name of the :class:`grid2op.Environment.Environment`.
    """
    pass

# multi environment
class MultiEnvException(Grid2OpException):
    """General exception raised by :class:`grid2Op.MultiEnv.MultiEnvironment` """
    pass

