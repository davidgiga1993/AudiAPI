# Audi Connect API
This library provides access to the Audi Connect API.
It allows easy access to all vehicle relevant data.

The API does automatic session caching and tries to keep the 
original service names as found in the audi connect app.

Some services require special permissions or certain origin countries of the car
to be accessible.

Note: Not all services are fully implemented due to missing permissions as mentioned above. 

# Examples
## Login
Login using cached token and use plain credentials as fallback
```python
api = API()
logon_service = LogonService(api)
if not logon_service.restore_token():
	with open('credentials.json') as data_file:
		data = json.load(data_file)
	logon_service.login(data['user'], data['pass'])
```

## List all vehicles under your account
```python
api = API()
car_service = CarService(api)
car_service.get_vehicles()
```
```json
{
	"csid": "-----",
	"vin": "-----",
	"registered": "2017-02-15T18:06:39.000+01:00"
}
```

## Get details about the embedded SIM
```python
mgmt_service = VehicleManagementService(api, vehicle)
mgmt_service.get_information()
```
```json
{
  "vehicleData": {
	"requestId": "--",
	"vin": "--",
	"country": "DE",
	"isConnect": "true",
	"brand": "Audi",
	"vehicleDevices": {
	  "vehicleDevice": [
		{
		  "ecuGeneration": "MIB2high",
		  "deviceType": "INFOTAINMENT"
		},
		{
		  "deviceId": "----",
		  "embeddedSim": {
			"identification": {
			  "content": "----",
			  "type": "ICCID"
			},
			"imei": "----",
			"mno": "vodafone"
		  },
		  "ecuGeneration": "cGW",
		  "deviceType": "TELEMATICS"
		}
	  ]
	},
	"isConnectSorglosReady": "true",
	"systemId": "XID_APP_AUDI"
  }
}
```

# Dependencies
- Python 3
- Requests library