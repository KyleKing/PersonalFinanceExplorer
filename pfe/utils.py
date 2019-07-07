"""Base utility functions."""

class TabBase:
    """Base class for each tab (page) of the application."""

    NAME = None

    def __init__(self, app):
        """Initialize the tab and verify data members.

        app -- Dash application instance

        """
        assert self.NAME is not None, 'The tab must be assigned a unique NAME'

        self.app = app

    def createLayout(self):
        """Return the Dash layout components."""
        raise NotImplementedError('self.createLayout has not been implemented for "{}"'.format(self.NAME))
