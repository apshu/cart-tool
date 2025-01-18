import argparse


class AliasedSubParsersAction(argparse._SubParsersAction):
    old_init = staticmethod(argparse._ActionsContainer.__init__)

    @staticmethod
    def _containerInit(self, description, prefix_chars, argument_default, conflict_handler):
        AliasedSubParsersAction.old_init(self, description, prefix_chars, argument_default, conflict_handler)
        self.register('action', 'parsers', AliasedSubParsersAction)

    class _AliasedPseudoAction(argparse.Action):
        def __init__(self, name, aliases, help):
            dest = name
            if aliases:
                dest += ' (%s)' % ','.join(aliases)
            sup = super(AliasedSubParsersAction._AliasedPseudoAction, self)
            sup.__init__(option_strings=[], dest=dest, help=help)

    def add_parser(self, name, **kwargs):
        aliases = kwargs.pop('aliases', [])
        parser = super(AliasedSubParsersAction, self).add_parser(name, **kwargs)

        # Make the aliases work.
        for alias in aliases:
            self._name_parser_map[alias] = parser
        # Make the help text reflect them, first removing old help entry.
        if 'help' in kwargs:
            help = kwargs.pop('help')
            self._choices_actions.pop()
            pseudo_action = self._AliasedPseudoAction(name, aliases, help)
            self._choices_actions.append(pseudo_action)

        return parser


# override argparse to register new subparser action by default
argparse._ActionsContainer.__init__ = AliasedSubParsersAction._containerInit