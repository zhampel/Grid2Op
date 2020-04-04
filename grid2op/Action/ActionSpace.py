import warnings

from grid2op.Exceptions import *
from grid2op.Action.BaseAction import BaseAction
from grid2op.Action.SerializableActionSpace import SerializableActionSpace


class ActionSpace(SerializableActionSpace):
    """
    :class:`ActionSpace` should be created by an :class:`grid2op.Environment.Environment`
    with its parameters coming from a properly
    set up :class:`grid2op.Backend.Backend` (ie a Backend instance with a loaded powergrid.
    See :func:`grid2op.Backend.Backend.load_grid` for
    more information).

    It will allow, thanks to its :func:`ActionSpace.__call__` method to create valid :class:`BaseAction`. It is the
    the preferred way to create an object of class :class:`BaseAction` in this package.

    On the contrary to the :class:`BaseAction`, it is NOT recommended to overload this helper. If more flexibility is
    needed on the type of :class:`BaseAction` created, it is recommended to pass a different "*actionClass*" argument
    when it's built. Note that it's mandatory that the class used in the "*actionClass*" argument derived from the
    :class:`BaseAction`.

    Attributes
    ----------
    game_rules: :class:`grid2op.RulesChecker.RulesChecker`
        Class specifying the rules of the game used to check the legality of the actions.


    """
    
    def __init__(self, gridobj, legal_action, actionClass=BaseAction):
        """
        All parameters (name_gen, name_load, name_line, sub_info, etc.) are used to fill the attributes having the
        same name. See :class:`ActionSpace` for more information.

        Parameters
        ----------

        gridobj: :class:`grid2op.Space.GridObjects`
            The representation of the powergrid.

        actionClass: ``type``
            Note that this parameter expected a class and not an object of the class. It is used to return the
            appropriate action type.

        legal_action: :class:`grid2op.RulesChecker.BaseRules`
            Class specifying the rules of the game used to check the legality of the actions.

        """
        SerializableActionSpace.__init__(self, gridobj, actionClass=actionClass)
        self.legal_action = legal_action

    def __call__(self, dict_=None, check_legal=False, env=None):
        """
        This utility allows you to build a valid action, with the proper sizes if you provide it with a valid
        dictionnary.

        More information about this dictionnary can be found in the :func:`Action.update` help. This dictionnary
        is not changed in this method.

        **NB** This is the only recommended way to make a valid, with proper dimension :class:`Action` object:

        Examples
        --------
        Here is a short example on how to make a action. For more detailed examples see :func:`Action.update`

        .. code-block:: python

            import grid2op
            # create a simple environment
            env = grid2op.make()
            act = env.action_space({})
            # act is now the "do nothing" action, that doesn't modify the grid.

        Parameters
        ----------
        dict_ : :class:`dict`
            see :func:`Action.__call__` documentation for an extensive help about this parameter

        check_legal: :class:`bool`
            is there a test performed on the legality of the action. **NB** When an object of class :class:`Action` is
            used, it is automatically tested for ambiguity. If this parameter is set to ``True`` then a legality test
            is performed. An action can be illegal if the environment doesn't allow it, for example if an agent tries
            to reconnect a powerline during a maintenance.

        env: :class:`grid2op.Environment`, optional
            An environment used to perform a legality check.

        Returns
        -------
        res: :class:`BaseAction`
            An action that is valid and corresponds to what the agent want to do with the formalism defined in
            see :func:`Action.udpate`.

        """

        res = self.actionClass(gridobj=self)
        # update the action
        res.update(dict_)
        if check_legal:
            if not self._is_legal(res, env):
                raise IllegalAction("Impossible to perform action {}".format(res))

        return res

    def _is_legal(self, action, env):
        """

        Parameters
        ----------
        action
        env

        Returns
        -------
        res: ``bool``
            ``True`` if the action is legal, ie is allowed to be performed by the rules of the game. ``False``
            otherwise.
        """
        if env is None:
            warnings.warn("Cannot performed legality check because no environment is provided.")
            return True
        return self.legal_action(action, env)
