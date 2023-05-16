import openai
from mtranslate import translate
from flask import g, current_app
from flask_login import current_user
from .key_cryptograpy import decrypt_cipher
from openai.error import AuthenticationError

async def get_imgmodel_request(content):

    decrypted_apikey = decrypt_cipher(current_user.openai_api)

    openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
    openai.api_key = decrypted_apikey

    if any([ch for ch in content if 'а' <= ch <= 'я' or 'А' <= ch <= 'Я']):
        
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

    decrypted_apikey = decrypt_cipher(current_user.openai_api)

    openai.organization = "org-MB9HPIF9vvXS6JqcEosUqMxM"
    openai.api_key = decrypted_apikey

    try:

        completion = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", 
                 "content": content,
                 "name": current_user.login,}
            ],
        )

        g.chat_output = completion.choices[0]['message']['content']
        g.chat_success = True
        # current_app.logger.info(completion.choices) 

    except AuthenticationError:
        g.chat_output = 'API ключ недействительный или неверный'
        g.chat_success = False

    except Exception as ex:
        g.chat_output = str(ex)
        g.chat_success = False