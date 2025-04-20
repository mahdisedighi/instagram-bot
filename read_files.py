import json

with open('text-instructions.txt' , 'r' ,encoding="utf-8") as file:
    r = file.read()

with open('story-text-instructions.txt' ,'r' ,encoding='utf-8') as s_file:
    sr = s_file.read()

with open('values.json') as file:
    content = file.read().strip()
    limit = json.loads(content)['Limit']
