"""Example using Plotly Express with tabbed interface.

Examples: https://www.plotly.express/
Docs: https://www.plotly.express/plotly_express/

"""

import copy
from collections import OrderedDict

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly_express as px
from dash.dependencies import Input, Output
from dash_charts.helpers import MinGraph, ddOpts, initApp


class Tab1:
    title = 'Placeholder'
    takesArgs = True
    data = px.data.tips()
    funcMap = OrderedDict([
        ('density_contour', px.density_contour),
    ])
    dims = ('x')
    dimsDict = OrderedDict([])

    def __init__(self):
        """Resolve higher-order data members."""
        self.colOpts = tuple([ddOpts(_c, _c) for _c in self.data.columns])
        self.funcOpts = tuple([ddOpts(lbl, lbl) for idx, lbl in enumerate(self.funcMap.keys())])


class PFEApp:
    """Personal Finance Explorer Application."""

    def __init__(self):
        """Initialize app."""
        self.app = initApp()

    def run(self, *, debug=True, **kwargs):
        """Run the application passing any kwargs to dash."""
        # Suppress callback verification as tab content is rendered later
        self.app.config['suppress_callback_exceptions'] = True

        # FIXME: Remove...
        self.TABS = [Tab1()]
        self.TAB_LOOKUP = {_tab.title: _tab for _tab in self.TABS}

        self.createLayout()

        # FIXME: Remove...
        self._registerTabCB()
        for tab in self.TABS:
            self._registerChartCB(tab)

        self.app.run_server(debug=debug, **kwargs)

    def createLayout(self):
        """Create application layout."""
        # Configure each tab
        self.__createTabMap()
        # Assign app layour
        self.app.layout = html.Div(children=[
            self.__sideMenu(),
            html.Div(style={'margin-left': '10%', 'width': '90%'}, children=[
                self.__content()
            ]),
        ])

    def __sideMenu(self):
        """Return the HTML elements for the tab side-menu."""
        tabStyle = {'padding': '10px 20px 10px 20px'}
        tabSelect = copy.copy(tabStyle)
        tabSelect['border-left'] = '3px solid #119DFF'
        return html.Div(children=[
            dcc.Tabs(
                id='tabs-select', value=self.TABS[0].title, vertical=True,
                children=[
                    dcc.Tab(label=_tab.title, value=_tab.title, style=tabStyle, selected_style=tabSelect) for _tab in self.TABS
                ],
                style={'width': '100%'},
                parent_style={'width': '100%'},
            ),
        ], style={
            'background-color': '#F9F9F9',
            'bottom': '0',
            'left': '0',
            'padding': '15px 0 0 5px',
            'position': 'fixed',
            'top': '0',
            'width': '9%',
        })

    def __content(self):
        """Return HTML elements for the main content."""
        return html.Div(className='section', children=[
            html.H1('Dash/Plotly Express Data Exploration Demo'),
            html.Div(id='tabs-content'),
        ])

    def __createTabMap(self):
        """Create TAB_MAP to store the tab individual tab layouts."""
        self.TAB_MAP = {
            tab.title: html.Div([
                html.Div([
                    html.P([
                        'Plot Type:',
                        dcc.Dropdown(
                            id='{}-func'.format(tab.title), options=tab.funcOpts, value=tab.funcOpts[0]['label']
                        ),
                    ])
                ] + [
                    html.P([
                        _d + ':', dcc.Dropdown(id='{}-{}'.format(tab.title, _d), options=tab.colOpts)
                    ]) for _d in tab.dims
                ] + [
                    html.P([
                        _d + ':',
                        dcc.Dropdown(id='{}-{}'.format(tab.title, _d),
                                     options=[ddOpts(_l, _l) for _l in _list]),
                    ]) for _d, _list in tab.dimsDict.items()
                ], style={'width': '25%', 'float': 'left'},
                ),
                MinGraph(id='{}-graph'.format(tab.title), style={'width': '75%', 'display': 'inline-block'}),
            ])
            for tab in self.TABS
        }

    def _registerTabCB(self):
        """Register callback to handle tab rendering."""
        @self.app.callback(
            Output('tabs-content', 'children'),
            [Input('tabs-select', 'value')],
        )
        def renderTabs(tabName):
            """Render tabs when switched."""
            return self.TAB_MAP[tabName]

    def _registerChartCB(self, tab):
        """Register the callbacks for handling the user input panel and chart rendering.

        tab -- tab dictionary.

        """
        inputs = [Input('tabs-select', 'value'), Input('{}-func'.format(tab.title), 'value')]
        inputs.extend([Input('{}-{}'.format(tab.title, _d), 'value') for _d in tab.dims])
        inputs.extend([Input('{}-{}'.format(tab.title, _k), 'value') for _k in tab.dimsDict.keys()])

        # Register callbacks for each tab
        @self.app.callback(
            Output('{}-graph'.format(tab.title), 'figure'),
            inputs,
        )
        def renderFigure(tabName, nameFunc, *args):
            """Create the figure."""
            # Check if the trigger event is a tab change. If so, return an empty chart
            ctx = dash.callback_context
            if 'tabs-select.value' in [_t['prop_id'] for _t in ctx.triggered]:
                return {}
            # Otherwise, parse the arguments to generate a new plot
            _tab = self.TAB_LOOKUP[tabName]
            if tab.takesArgs:
                keys = list(_tab.dims) + list(_tab.dimsDict.keys())
                kwargs = OrderedDict(zip(keys, args))
                return _tab.funcMap[nameFunc](_tab.data, height=650, **kwargs)
            return _tab.funcMap[nameFunc]()
