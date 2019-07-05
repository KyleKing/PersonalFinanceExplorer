"""Example Implementation of plaidash.

Source: https://github.com/SterlingButters/plaidash#usage

"""

import datetime
import json
import os

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plaid
import plaidash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from flask import jsonify
from icecream import ic

# # Fill in your Plaid API keys - https://dashboard.plaid.com/account/keys
# PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
# PLAID_SECRET = os.getenv('PLAID_SECRET')
# PLAID_PUBLIC_KEY = os.getenv('PLAID_PUBLIC_KEY')
# # Use 'sandbox' to test with Plaid's Sandbox environment (username: user_good,
# # password: pass_good)
# # Use `development` to test with live users and credentials and `production`
# # to go live
# PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
# # PLAID_PRODUCTS is a comma-separated list of products to use when initializing
# # Link. Note that this list must contain 'assets' in order for the app to be
# # able to create and retrieve asset reports.
# PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'transactions')

# # PLAID_COUNTRY_CODES is a comma-separated list of countries for which users
# # will be able to select institutions from.
# PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US,CA,GB,FR,ES')

stylesheet = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=stylesheet)
app.config['suppress_callback_exceptions'] = True

with open('.credentials.json') as CREDENTIALS:
    KEYS = json.load(CREDENTIALS)
    PLAID_CLIENT_ID = KEYS['client_id']
    PLAID_PUBLIC_KEY = KEYS['public_key']
    PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
    if PLAID_ENV == 'sandbox':
        PLAID_SECRET = KEYS['sandbox_secret']
    else:
        PLAID_SECRET = KEYS['development_secret']
    PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', ['auth', 'transactions'])


def pretty_response(response):
    return json.dumps(response, indent=2, sort_keys=True)


def format_error(e):
    # 'error_message': e.message } }
    return {'error': {'display_message': e.display_message, 'error_code': e.code, 'error_type': e.type, }}


app.layout = html.Div([
    # Will lose the data when browser/tab closes.
    dcc.Store(id='public-tokens', storage_type='session', data={'tokens': []}),
    html.Button('Store current token', id='store-button'),
    html.Div(id='display-tokens'),

    plaidash.LoginForm(
        id='plaid-link',
        clientName='Butters',
        env=PLAID_ENV,
        publicKey=PLAID_PUBLIC_KEY,
        product=PLAID_PRODUCTS,
        # institution=
    ),
    html.Div(id='transaction-table'),
])


client = plaid.Client(client_id=PLAID_CLIENT_ID,
                      secret=PLAID_SECRET,
                      public_key=PLAID_PUBLIC_KEY,
                      environment=PLAID_ENV,
                      api_version='2019-05-29')


@app.callback(Output('public-tokens', 'data'),
              [Input('store-button', 'n_clicks')],
              [State('plaid-link', 'public_token'),
               State('public-tokens', 'data')])
def onClickStoreTokenBtn(clicks, public_token, data):
    """Read and store token to browser's memory."""
    if clicks is None:
        raise PreventUpdate()
    stored_tokens = data['tokens'] or []
    stored_tokens.append(public_token)
    data = {'tokens': stored_tokens}
    return data


# Display from Memory
@app.callback(Output('transaction-table', 'children'),
              [Input('public-tokens', 'modified_timestamp')],
              [State('public-tokens', 'data')])
def display_output(timestamp, data):
    if timestamp is None:
        raise PreventUpdate()

    if data is not None:
        STORED_TOKENS = list(data.get('tokens'))
        if len(STORED_TOKENS) > 0 and STORED_TOKENS[-1] is not None:
            public_token = STORED_TOKENS[-1]
            response = client.Item.public_token.exchange(public_token)
            access_token = response['access_token']
            ic("Public Token '{}' was exchanged for Access Token '{}'".format(public_token, access_token))

            start_date = '{:%Y-%m-%d}'.format(datetime.datetime.now() + datetime.timedelta(-30))
            end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())
            try:
                transactions_response = client.Transactions.get(
                    access_token=access_token, start_date=start_date, end_date=end_date)
            except plaid.errors.PlaidError as e:
                return html.P(jsonify(format_error(e)))

            transactions = transactions_response.get('transactions')

            names = [transaction['name'] for transaction in transactions]
            categories = [transaction['category'] for transaction in transactions]
            locations = [transaction['location'] for transaction in transactions]
            statuses = [transaction['pending'] for transaction in transactions]
            amounts = [transaction['amount'] for transaction in transactions]
            # Payment Method: payment_meta
            dates = [transaction['date'] for transaction in transactions]
            trans_ids = [transaction['transaction_id'] for transaction in transactions]

            TOKEN_MEAT = []
            for a in range(len(STORED_TOKENS)):
                if a is not None:
                    TOKEN_MEAT.append(html.Tr([html.Td(STORED_TOKENS[a]), '']))

            INFO_MEAT = []
            for b in range(len(transactions)):
                INFO_MEAT.append(html.Tr([html.Td(names[b]), html.Td(amounts[b]), html.Td(dates[b])]))

            return html.Div([
                html.Table([
                    html.Thead([
                        html.Tr([html.Th('Stored Public Tokens')]),
                        html.Tbody([*TOKEN_MEAT]),
                    ]),
                    html.Table([
                        html.Thead([
                            html.Tr([html.Th('Name'), html.Th('Amount'), html.Th('Date')])
                        ]),
                        html.Tbody([*INFO_MEAT]),
                    ]),
                ]),
            ])
    return 'Navigate Plaid Link to Obtain Token'


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_hot_reload=False)
