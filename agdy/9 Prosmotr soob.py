import http.client
import json

conn = http.client.HTTPSConnection("agdyapi.huidatech.cn")


conn.request("Get", "/navdata/message/list/2890041c")
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))