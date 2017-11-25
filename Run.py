import json

from audiapi.API import API
from audiapi.Services import LogonService, CarService


def main():
    api = API()
    logon_service = LogonService(api)
    if not logon_service.restore_token():
        # We need to login
        with open('credentials.json') as data_file:
            data = json.load(data_file)
        logon_service.login(data['user'], data['pass'])

    car_service = CarService(api)
    vehicles_response = car_service.get_vehicles()
    for vehicle in vehicles_response.vehicles:
        print(str(vehicle))


if __name__ == '__main__':
    main()
