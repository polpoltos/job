import http.client
import json
import time

start = time.time()
conn = http.client.HTTPSConnection("agdyapi.huidatech.cn")
payload = json.dumps({
   "ident": "",
   "commandCode": "SetFieldlineAp",
   "param": {
      "id": "1742202890505",
      "name": "Кур",
      "ACoor": [
         73.10336796571079,
         49.80947977286718
      ],
      "vec": 35
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