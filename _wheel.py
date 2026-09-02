import zipfile, re
z = zipfile.ZipFile('sdk/fyers_apiv3_beta-1.0.0-py3-none-any.whl')
print(z.namelist())
src = ''
for n in z.namelist():
    if n.endswith('.py'):
        src += u'//===== ' + n + u'=====//' + z.read(n).decode('utf-8', 'ignore')
open('sdk/all_source.py', 'w', encoding='utf-8').write(src)
for pat in [r'BASE_URL[^\n]*', r'generate-authcode[^\n]*', r'validate-authcode[^\n]*', r'validate-refresh-token[^\n]*', r'def optionchain.*?(?=\n    def |\nclass |\Z)', r'data/option-chain[^\n]*', r'def generate_token.*?(?=\n    def |\nclass |\Z)']:
    ms = re.findall(pat, src, re.S)
    print('#### ' + pat + ' => ' + str(len(ms)))
    for m in ms[:3]:
        print(m[:800])
        print('----')
