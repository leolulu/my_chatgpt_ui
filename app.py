import os

from dash import Dash, Input, Output, State, callback, dcc, html

from llms.openai_engine import OpenAIEngine
from utils.element_util import gen_bubble_content

app = Dash(__name__)
chatGPT = OpenAIEngine()

app.layout = html.Div(
    className="main-area",
    children=[
        html.Div(id="chat_display", className="left-area"),
        html.Div(
            className="right-area",
            children=[
                # Upper input area
                html.Div(
                    className="right-upper",
                    children=[
                        dcc.Textarea(id="input-box", className="input-box"),
                        html.Button(
                            "Submit", id="submit-button", className="whole-line-input"
                        ),
                        html.Button(
                            "Reset", id="reset-button", className="whole-line-input"
                        ),
                    ],
                ),
                # Lower parameter area
                html.Div(
                    className="right-lower",
                    children=[
                        dcc.Input(
                            id="api_key",
                            type="password",
                            value=os.getenv("api_key", default=""),
                            placeholder="API KEY here",
                            className="whole-line-input",
                        ),
                        dcc.Input(
                            id="proxy_address",
                            type="text",
                            value="http://127.0.0.1:10809",
                        ),
                        dcc.Checklist(
                            id="enable_proxy",
                            options=["enable"],
                        ),
                        html.Button(
                            "初始化引擎", id="init_engine", className="whole-line-input red"
                        ),
                        dcc.Input(
                            id="parameter-3",
                            type="text",
                            placeholder="Parameter 2",
                            className="whole-line-input",
                        ),
                        html.Button(
                            "Submit Parameters",
                            id="submit-parameters-button",
                            className="whole-line-input",
                        ),
                    ],
                ),
            ],
        ),
    ],
)


@callback(
    Output("chat_display", "children", allow_duplicate=True),
    Output("input-box", "value"),
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_history(n_clicks):
    return ([], "")


@callback(
    Output("chat_display", "children"),
    Input("submit-button", "n_clicks"),
    State("input-box", "value"),
    State("chat_display", "children"),
    prevent_initial_call=True,
)
def ask_for_chat(n_clicks, question, children):
    if not children:
        children = []
    if question:
        print(f"开始问问题...")
        (answer, usage) = chatGPT.ask(question)
        children.append(
            html.Div(gen_bubble_content(question), className="chat-record user-bubble")
        )
        children.append(
            html.Div(
                gen_bubble_content(answer), className="chat-record assistant-bubble"
            )
        )
        print(f"答案回来了，开销：{usage}")
    return children


@callback(
    Output("init_engine", "className"),
    Input("init_engine", "n_clicks"),
    State("api_key", "value"),
    State("proxy_address", "value"),
    State("init_engine", "className"),
    State("enable_proxy", "value"),
    prevent_initial_call=True,
)
def init_engine(n_clicks, api_key, proxy, class_name, if_enable_proxy):
    if api_key:
        if if_enable_proxy is None:
            proxy = ""
        print("初始化引擎中...")
        chatGPT.init_engine(api_key, proxy)
        print("引擎初始化完毕...")
        return class_name.replace("red", "green")
    else:
        return class_name


if __name__ == "__main__":
    app.run_server(debug=False, port=os.getenv("PORT", default=8050), host="0.0.0.0")
