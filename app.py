import os

from dash import Dash, Input, Output, State, callback, dash_table, dcc, html

from llms.openai_engine import OpenAIEngine
from models.prompt import Prompt
from utils.element_util import gen_bubble_content
from utils.mongo_util import MongoUtil

app = Dash(__name__)
chatGPT = OpenAIEngine()
mongo_util = MongoUtil(
    host=os.getenv("MONGODB_HOST"),
    port=int(os.getenv("MONGODB_PORT", 0)),
    username=os.getenv("MONGODB_USERNAME"),
    password=os.getenv("MONGODB_PASSWORD"),
)
mongo_util.set_collection("prompt")

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
                        html.Button("Submit", id="submit-button"),
                        html.Button("Reset", id="reset-button"),
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
                        dcc.Checklist(id="enable_proxy", options=["enable"]),
                        html.Button("初始化引擎", id="init_engine", className="whole-line-input red"),
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
                        dash_table.DataTable(
                            id="prompt_table",
                            style_table={"overflowX": "auto"},
                            style_cell={"textAlign": "left"},
                            css=[
                                {
                                    "selector": "tr",
                                    "rule": "height:10px;line-height:10px;font-size:15px",
                                },
                                {
                                    "selector": "tr:first-child",
                                    "rule": "display: none",
                                },
                            ],
                        ),
                        html.Div(
                            [
                                html.Button("Put", id="put-prompt-button"),
                                html.Button("Add", id="add-prompt-button"),
                                html.Button("Del", id="del-prompt-button"),
                                dcc.Checklist(id="enable_hyphen", options=["hyphen"]),
                            ]
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
    chatGPT.reset_messages()
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
        children.append(html.Div(gen_bubble_content(question), className="chat-record user-bubble"))
        children.append(html.Div(gen_bubble_content(answer), className="chat-record assistant-bubble"))
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
        chatGPT.reset_messages()
        return class_name.replace("red", "green")
    else:
        return class_name


@callback(
    Output("input-box", "value", allow_duplicate=True),
    Input("put-prompt-button", "n_clicks"),
    State("prompt_table", "active_cell"),
    State("prompt_table", "data"),
    State("input-box", "value"),
    State("enable_hyphen", "value"),
    prevent_initial_call=True,
)
def put_prompt(n_clicks, active_cell, prompt_table_data, input_data, if_enable_hyphen):
    if active_cell is not None:
        if if_enable_hyphen is None:
            connector = "\n"
        else:
            connector = "\n" + "-" * 50 + "\n"
        return input_data + connector + prompt_table_data[active_cell["row"]]["prompt"]
    else:
        return input_data


@callback(
    Output("prompt_table", "data"),
    Input("add-prompt-button", "n_clicks"),
    State("input-box", "value"),
    State("prompt_table", "data"),
)
def add_prompt(n_clicks, prompt, data):
    if prompt:
        new_prompt_dict = Prompt(max([i["id"] for i in (data or [{"id": 0}])]) + 1, prompt).value
        mongo_util.insert_one(new_prompt_dict)
    data = [{Prompt.PROMPT: i[Prompt.PROMPT], Prompt.ID: i[Prompt.ID]} for i in mongo_util.find_many()]
    return data


@callback(
    Output("prompt_table", "data", allow_duplicate=True),
    Input("del-prompt-button", "n_clicks"),
    State("prompt_table", "data"),
    State("prompt_table", "active_cell"),
    prevent_initial_call=True,
)
def del_prompt(n_clicks, data, active_cell):
    if active_cell is not None:
        mongo_util.delete_one({Prompt.ID: data[active_cell["row"]][Prompt.ID]})
    data = [{Prompt.PROMPT: i[Prompt.PROMPT], Prompt.ID: i[Prompt.ID]} for i in mongo_util.find_many()]
    return data


if __name__ == "__main__":
    app.run_server(debug=True, port=os.getenv("PORT", default=8050), host="0.0.0.0")
