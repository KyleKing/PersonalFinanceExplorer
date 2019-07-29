"""Profile Settings Page."""

import dash_html_components as html
import dash_table
import pandas as pd
from dash.dependencies import Input, Output
from dash_charts import appUtils
from icecream import ic

from .plaidWrapper import PlaidDashWrapper


class TabProfile(appUtils.TabBase):
    """Profile Page."""

    NAME = 'Profile'

    df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

    def __init__(self, app):
        """Initialize the tab and verify data members.

        app -- Dash application instance

        """
        super().__init__(app)
        self.pdw = PlaidDashWrapper(app)

    def createLayout(self):
        """Return the Dash layout components."""
        return html.Div(className='section', children=[
            html.H1('Manage User Profile'),
            html.H2('Edit Linked Accounts'),
            # TODO: Add confirmation modal when deleting an account
            dash_table.DataTable(
                id='table',
                columns=[{"name": i, "id": i} for i in self.df.columns],
                data=self.df.to_dict('records'),
                row_deletable=True,
            ),
            self.pdw.createLayout(),
        ])

    def registerCallbacks(self):
        """Register callbacks necessary for this tab."""
        self._edits()
        self.pdw.registerCallbacks()

    def _edits(self):
        """Read changes to the data table."""
        @self.app.callback(
            Output('table', 'figure'),
            [Input('table', 'data'), Input('table', 'columns')])
        def readTableChanges(rows, columns):
            self.df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
            return {}  # Make no changes to table
