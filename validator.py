import re

def phone(phone):
    pat = re.compile(r"(\+\d{1,3})?\s?\(?\d{1,4}\)?[\s.-]?\d{3}[\s.-]?\d{4}")
    if re.match(pat, phone):
        return True
    return False
