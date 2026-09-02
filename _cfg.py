import re
src = open('sdk/all_source.py', encoding='utf-8').read()
i = src.find('class Config')
print(src[i:i+1400])
