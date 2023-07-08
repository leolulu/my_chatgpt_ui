import os
import traceback

import diskcache
from dash import Dash, DiskcacheManager, Input, Output, State, callback, dash_table, dcc, html

from llms.openai_engine import OpenAIEngine
from models.prompt import Prompt
from utils.concat_util import concat_webpage_content_and_question
from utils.mongo_util import MongoUtil
from utils.url_util import get_webpage_content

app = Dash(
    __name__,
    title="my GPT UI",
    background_callback_manager=DiskcacheManager(diskcache.Cache("./runtime_data/cache")),
)
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
                        dcc.Dropdown(
                            id="model_name_dropdown",
                            options=["gpt-3.5-turbo-16k-0613", "gpt-4-0613", "gpt-4-32k-0613"],
                            value="gpt-3.5-turbo-16k-0613",
                            clearable=False,
                        ),
                        dcc.Textarea(id="input-box", className="input-box"),
                        html.Button("Submit", id="submit-button", disabled=True),
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
                        dcc.Input(id="proxy_address", type="text", value="http://127.0.0.1:10809"),
                        dcc.Checklist(id="enable_proxy", options=["proxy"]),
                        html.Button("Init Engine", id="init_engine", className="whole-line-input red"),
                        dcc.Input(id="webpage_url_input", type="text", placeholder="Load content from URL"),
                        dcc.Checklist(id="enable_load_content_from_url", options=["url"]),
                        dash_table.DataTable(
                            id="prompt_table",
                            style_table={"overflowX": "auto"},
                            style_cell={"textAlign": "left"},
                            css=[
                                {
                                    "selector": "tr",
                                    "rule": "height:10px;line-height:10px;font-size:12px",
                                },
                                {
                                    "selector": "tr:first-child",
                                    "rule": "display: none",
                                },
                            ],
                        ),
                        dcc.Input(id="add_prompt_input", type="text", placeholder="add prompt", className="whole-line-input"),
                        html.Div(
                            [
                                html.Button("Put to query", id="put-prompt-button"),
                                html.Button("add", id="add-prompt-button"),
                                html.Button("del", id="del-prompt-button"),
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
    Input("reset-button", "n_clicks"),
    prevent_initial_call=True,
)
def clear_history(n_clicks):
    chatGPT.reset_messages()
    return []


@callback(
    Output("chat_display", "children"),
    Output("input-box", "value", allow_duplicate=True),
    Output("enable_load_content_from_url", "value"),
    Input("submit-button", "n_clicks"),
    State("input-box", "value"),
    State("chat_display", "children"),
    State("enable_load_content_from_url", "value"),
    State("webpage_url_input", "value"),
    State("model_name_dropdown", "value"),
    prevent_initial_call=True,
    background=True,
    running=[
        (Output("submit-button", "disabled"), True, False),
        (Output("submit-button", "children"), "Querying...", "Submit"),
    ],
)
def ask_for_chat(n_clicks, question, children, if_enable_load_from_url, url, model):
    if not children:
        children = []
    if question:
        try:
            if if_enable_load_from_url and url:
                webpage_content = get_webpage_content(url)
                question = concat_webpage_content_and_question(webpage_content, question)
            print(f"开始问问题...")
            (answer, usage) = chatGPT.ask(question, model)
            children.append(html.Div(dcc.Markdown(question), className="chat-record user-bubble"))
            children.append(html.Div(dcc.Markdown(answer), className="chat-record assistant-bubble"))
            print(f"答案回来了，开销：{usage}")
            question = f"{question}\n\n\n[系统信息]\n{usage}"
        except:
            question = "\n\n\n".join([question, traceback.format_exc()])
    return (children, question, [])


@callback(
    Output("init_engine", "className"),
    Output("submit-button", "disabled"),
    Input("init_engine", "n_clicks"),
    State("api_key", "value"),
    State("proxy_address", "value"),
    State("init_engine", "className"),
    State("enable_proxy", "value"),
    prevent_initial_call=True,
)
def init_engine(n_clicks, api_key, proxy, class_name, if_enable_proxy):
    if api_key:
        if not if_enable_proxy:
            proxy = ""
        print("初始化引擎中...")
        chatGPT.init_engine(api_key, proxy)
        print("引擎初始化完毕...")
        chatGPT.reset_messages()
        return (class_name.replace("red", "green"), False)
    else:
        return (class_name, True)


@callback(
    Output("input-box", "value", allow_duplicate=True),
    Input("put-prompt-button", "n_clicks"),
    State("prompt_table", "active_cell"),
    State("prompt_table", "data"),
    State("input-box", "value"),
    State("enable_hyphen", "value"),
    prevent_initial_call=True,
)
def put_prompt(n_clicks, active_cell, prompt_table_data, input_box_content, if_enable_hyphen):
    if active_cell is not None:
        selected_prompt = prompt_table_data[active_cell["row"]]["prompt"]
        if not if_enable_hyphen:
            connector = "\n"
        else:
            connector = "\n\n" + "-" * 50 + "\n"
        if input_box_content:
            return input_box_content + connector + selected_prompt
        else:
            return selected_prompt
    else:
        return input_box_content


@callback(
    Output("prompt_table", "data"),
    Output("add_prompt_input", "value"),
    Input("add-prompt-button", "n_clicks"),
    State("add_prompt_input", "value"),
    State("prompt_table", "data"),
)
def add_prompt(n_clicks, prompt, data):
    if prompt:
        new_prompt_dict = Prompt(max([i["id"] for i in (data or [{"id": 0}])]) + 1, prompt).value
        mongo_util.insert_one(new_prompt_dict)
    data = [{Prompt.PROMPT: i[Prompt.PROMPT], Prompt.ID: i[Prompt.ID]} for i in mongo_util.find_many()]
    return (data, "")


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
    app.run_server(debug=False, port=os.getenv("PORT", default=8050), host="0.0.0.0")
