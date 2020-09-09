import json

from audiapi.API import API
from audiapi.Services import VehicleStatusReportService, OperationListService
from audiapi.model.RequestStatus import RequestStatus
from services.CarService import CarService, VehicleManagementService
from services.LogonService import LogonService


def main():
    api = API()
    api.set_market('DE', 'de')
    logon_service = LogonService(api)
    if not logon_service.restore_token():
        # We need to login
        with open('credentials.json') as data_file:
            data = json.load(data_file)
        logon_service.login(data['user'], data['pass'])

    user_info = logon_service.get_user_info()
    print('Current user: ' + user_info.email)

    car_service = VehicleManagementService(api)
    vehicles = car_service.get_vehicles()
    for vehicle in vehicles:
        # Get more details about the vehicle
        print('Found vehicle ' + vehicle.vin)
        vehicle = CarService(api).get_vehicle(vehicle.vin)

        operations = OperationListService(api).get_operations(vehicle)
        print(str(operations))

        # TODO: Fix calls below..
        report_service = VehicleStatusReportService(api, 'Audi', 'DE', vehicle)
        response = report_service.get_stored_vehicle_data()
        response = report_service.request_current_vehicle_data()

        request_status = report_service.get_request_status(response.request_id)
        while request_status.status == RequestStatus.IN_PROGRESS:
            request_status = report_service.get_request_status(response.request_id)

        print(str(report_service.get_requested_current_vehicle_data(response.request_id)))


if __name__ == '__main__':
    main()
