import re

def extract_first_json(s):
    match = re.findall(r"{.+[:,].+}|\[.+[,:].+\]", s)
    return match[0] if match else s