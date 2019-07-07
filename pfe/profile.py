"""Profile Settings Page."""

import dash_html_components as html

from .utils import TabBase


class TabProfile(TabBase):
    """Profile Page."""

    NAME = 'Profile'

    def createLayout(self):
        """Return the Dash layout components."""
        return html.Div(className='section', children=[
            html.H1('Manage User Profile'),
        ])
