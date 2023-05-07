import openai
from mtranslate import translate
from flask import current_app, g
from flask_login import current_user
from .auth_filter import check_for_cyrillic_string

async def get_imgmodel_request(content):

    openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
    openai.api_key = current_user.openai_api
    
    if check_for_cyrillic_string(content):
        # content = content.replace()
        # print(content)
        content = translate(content)
        content = content.replace('puss in boots', 'cat in boots')

    try:

        completion = await openai.Image.acreate(
            prompt=content,
            n=3,
            size="1024x1024"
        )

        g.img_output = completion['data']
        g.img_success = True

    except Exception as ex:
        g.img_output = str(ex)
        g.img_success = False


async def get_chatmodel_request(content):

    # print(os.system('pwd'))
    openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
    openai.api_key = current_user.openai_api

    try:

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": content}
            ],
        )

        # print(content)
        g.chat_output = completion.choices[0]['message']['content']
        g.chat_success = True

        # print(g.chat_output.encode('unicode_escape').decode())

    except Exception as ex:
        g.chat_output = str(ex)
        g.chat_success = False