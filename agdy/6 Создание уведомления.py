import http.client
import json

conn = http.client.HTTPSConnection("agdyapi.huidatech.cn")
payload = json.dumps({
   "ident": "2890041c",
   "type": 1,
   "notifyType": 2,
   "plainText": "Hello test from Python",
   "coordinates": [
          52.7079,
          41.3890
        ],
})
headers = {
   'Content-Type': 'application/json'
}
conn.request("POST", "/navdata/message/new", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))