import zipfile, re
import glob
f = glob.glob('sdk/fyers_apiv3-*.whl')
print('wheel:', f)
z = zipfile.ZipFile(f[0])
src = ''
for n in z.namelist():
    if n.endswith('.py'):
        src += u'//===== ' + n + u'=====//' + z.read(n).decode('utf-8', 'ignore')
open('sdk/stable_source.py', 'w', encoding='utf-8').write(src)
i = src.find('class Config')
print(src[i:i+1200])
print('#####')
m = re.search(r'def optionchain.*?(?=\n    def |\nclass |\Z)', src, re.S)
print(m.group(0)[:1200] if m else 'no optionchain' )
m2 = re.search(r'def get_quotes.*?(?=\n    def |\nclass |\Z)', src, re.S)
print('#####')
print(m2.group(0)[:800] if m2 else 'no quotes')
