def concat_webpage_content_and_question(webpage_content, question):
    result = webpage_content + "\n\n"
    result += "-" * 50
    result += "\n"
    result += "根据上面的内容回答以下问题，如果提供的材料中没有相关内容的话，就回答不知道:"
    result += "\n"
    result += question
    return result
