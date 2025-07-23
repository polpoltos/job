import http.client
import json
import time

start = time.time()
conn = http.client.HTTPSConnection("agdyapi.huidatech.cn")
payload = json.dumps({
   "ident": "",
   "commandCode": "SetFieldlineCircle",
   "param": {
      "id": "1742202896669",
      "name": "Пичаево",
      "ACoor": [
         42.20731558285246,
         53.23557418855387
      ],
      "stepLength": 13
   }
})
headers = {
   'Content-Type': 'application/json'
}
conn.request("POST", "/navdata/newtask", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
print(f'Время выполнения: {time.time() - start}')