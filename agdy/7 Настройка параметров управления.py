import http.client
import json
import time

start = time.time()
conn = http.client.HTTPSConnection("agdyapi.huidatech.cn")
payload = json.dumps({
   "ident": "289072ec",
   "commandCode": "vehicleParamSet",
   "data": {
      "vehicleAntHeight": 1.2,
      "vehicleAntAxisDist": 1,
      "vehicleAntFrontAxisDist": 2,
      "vehicleHitchDist": 0.9,
      "vehicleGyroDir": 0,
      "vehicleRoll": 0,
      "vehiclePitch": 0,
      "motorType": 5,
      "lineInSensitivity": 1,
      "lateralSensitivity": 1,
      "headingSensitivity": 1,
      "terrainComp": 0.5,
      "steeringGain": 6
   }
})
headers = {
   'Content-Type': 'application/json'
}
conn.request("POST", "/navdata/setparameter", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
print(f'Время выполнения: {time.time() - start}')