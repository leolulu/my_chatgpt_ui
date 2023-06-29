from dash import html


def gen_bubble_content(content):
    lines = content.split('\n')
    lines = [html.Div(i) for i in lines]
    return lines
