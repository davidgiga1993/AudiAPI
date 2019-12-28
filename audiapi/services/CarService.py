from dev.CodeGenerator import CodeGenerator
from model.Vehicle import Vehicle
from services.Service import MsgService


class CarService(MsgService):

    def get_vehicle(self, vin: str):
        """
        Returns a list of all vehicles
        :return:
        """
        reply = self._api.get(self.url('/vehicles/{vin}', vin=vin))
        print(str(reply))

    def _get_path(self):
        return super()._get_path() + '/msg/myaudi/carservice/v3'


class VehicleManagementService(MsgService):

    def get_vehicles(self):
        """
        Returns a list of all vehicles

        :return: List of vehicles
        :rtype: List[Vehicle]
        """
        reply = self._api.get(self.url('/vehicles'))
        vehicles = []
        for data in reply['vehicles']:
            vehicles.append(self._to_dto(data, Vehicle()))
        return vehicles

    def _get_path(self):
        return super()._get_path() + '/myaudi/vehicle-management/v1'
