import requests
import json

url = "https://agdyapi.huidatech.cn/navdata/newtask"

payload = json.dumps({
   "ident": "2890041c",
   "commandCode": "SetFieldlineAB",
   "param": {
      "id": "1742182092791",
      "name": "На БЕРЛИН",
      "ACoor": [
         41.454856895395125,
         52.719419307744744
      ],
      "BCoor": [
         13.38667602804847,
         52.517106614886416
      ]
   }
})
headers = {
   'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)