import json
with open('/tmp/hermes-results/call_03_mdSIXGwJiDm4r2HQcyq73107.txt') as f:
    raw = f.read()
outer = json.loads(raw)
inner = json.loads(outer['result'])
data = inner['result']['data']
top10 = []
for item in data[:15]:
    name = item.get('name','')
    price = item.get('price','')
    percent = item.get('percent','')
    sw2hy = item.get('sw2hy','')
    fdAmount = item.get('fdAmount','')
    top10.append({'name':name,'price':price,'percent':percent,'sector':sw2hy,'fdAmount':fdAmount})
    print(f'{name} | {price} | {percent}% | {sw2hy}')
with open('/home/hermes_agent/digest/zt_pool_top.json','w') as f:
    json.dump(top10, f, ensure_ascii=False, indent=2)
