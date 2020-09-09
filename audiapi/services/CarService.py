from model.Vehicle import Vehicle
from services.Service import MsgService


class CarService(MsgService):

    def get_vehicle(self, vin: str) -> Vehicle:
        """
        Returns details about the given VIN
        """
        reply = self.get('/vehicles/{vin}', vin=vin)
        return self._to_dto(reply, Vehicle())

    def _get_path(self):
        return super()._get_path() + '/myaudi/carservice/v3'

    def _get_scope(self):
        return 'vehicle'


class VehicleManagementService(MsgService):

    def get_vehicles(self):
        """
        Returns a list of all vehicles

        :return: List of vehicles
        :rtype: List[Vehicle]
        """
        reply = self.get('/vehicles', scope='vehicle')
        vehicles = []
        for data in reply['vehicles']:
            vehicles.append(self._to_dto(data, Vehicle()))
        return vehicles

    def _get_path(self):
        return super()._get_path() + '/myaudi/vehicle-management/v2'

    def _get_scope(self):
        return 'vehicle'
