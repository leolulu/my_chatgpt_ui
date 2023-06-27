from dash import Dash, html, dcc, Input, Output, State, callback

from llms.openai_engine import OpenAIEngine

app = Dash(__name__)
chatGPT = OpenAIEngine()

app.layout = html.Div(
    className='main-area',
    children=[
        html.Div(
            id='chat_display',
            className='left-area'
        ),
        html.Div(
            className='right-area',
            children=[
                # Upper input area
                html.Div(
                    className='right-upper',
                    children=[
                        dcc.Textarea(id='input-box', className='input-box'),
                        html.Button('Submit', id='submit-button', className='whole-line-input'),
                    ]
                ),

                # Lower parameter area
                html.Div(
                    className='right-lower',
                    children=[
                        dcc.Input(id='api_key', type='text', placeholder='api key', className='whole-line-input'),
                        dcc.Input(id='proxy_address', type='text', value='http://127.0.0.1:10809', className='whole-line-input'),
                        html.Button('初始化引擎', id='init_engine', className='whole-line-input red'),
                        dcc.Input(id='parameter-3', type='text', placeholder='Parameter 2', className='whole-line-input'),
                        html.Button('Submit Parameters', id='submit-parameters-button', className='whole-line-input'),
                    ]
                ),
            ]
        )
    ])


@callback(
    Output('chat_display', 'children'),
    Input('submit-button', 'n_clicks'),
    State('input-box', 'value'),
    State('chat_display', 'children')
)
def ask_for_chat(n_clicks, question, children):
    if not children:
        children = []
    if question:
        print(f"开始问问题...")
        (answer, usage) = chatGPT.ask(question)
        children.append(html.Div(question, className='chat-record user-bubble'))
        children.append(html.Div(answer, className='chat-record assistant-bubble'))
        print(f'答案回来了，开销：{usage}')
    return children


@callback(
    Output('init_engine', 'className'),
    Input('init_engine', 'n_clicks'),
    State('api_key', 'value'),
    State('proxy_address', 'value'),
    State('init_engine', 'className')
)
def init_engine(n_clicks, api_key, proxy, class_name):
    if api_key:
        print('初始化引擎中...')
        chatGPT.init_engine(api_key, proxy)
        print('引擎初始化完毕...')
        return class_name.replace('red', 'green')
    else:
        return class_name


if __name__ == '__main__':
    app.run_server(debug=True)
