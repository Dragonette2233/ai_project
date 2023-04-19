import re
from dataclasses import dataclass

@dataclass
class UserInfo:

    email: str
    login: str
    pass_main: str
    pass_confirm: str

def check_for_cyrillic(user: UserInfo):

    cyrillic_fileds = {}

    for i in user.__dict__.items():
        if re.search('[а-яА-Я]', i[1]):
            cyrillic_fileds[i[0]] = True
    
    return cyrillic_fileds if cyrillic_fileds != {} else False

def get_flash_message_for_cyrillic(cyrillic_check: dict):

    flash_fields = [k for k, v in cyrillic_check.items() if v]
    flash_message = f"Cyrillic symbols in {','.join(flash_fields)}"
    return flash_message





