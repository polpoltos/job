import http.client
import json
import time

start = time.time()
conn = http.client.HTTPSConnection("agdyapi.huidatech.cn")
payload = json.dumps()
headers = {
   'Content-Type': 'application/json'
}
conn.request("POST", "/navdata/setparameter", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
print(f'Время выполнения: {time.time() - start}')