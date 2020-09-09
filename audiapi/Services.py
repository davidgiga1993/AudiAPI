from abc import ABCMeta

from audiapi.API import API
from audiapi.model.BatteryChargeResponse import BatteryChargeResponse
from audiapi.model.ClimaRequest import ClimaRequestFactory
from audiapi.model.CurrentVehicleDataResponse import CurrentVehicleDataResponse
from audiapi.model.HonkFlash import HonkFlashAction, RemoteHonkFlashActionStatus
from audiapi.model.RequestStatus import RequestStatus
from audiapi.model.Vehicle import Vehicle
from audiapi.model.VehicleDataResponse import VehicleDataResponse
from services.Service import Service, MbbService, MbbMalService


class VehicleService(MbbService, metaclass=ABCMeta):
    def __init__(self, api: API, brand: str, country: str, vehicle: Vehicle):
        super().__init__(api, brand, country)
        self._vehicle = vehicle
        """
        Current vehicle

        :type _vehicle: Vehicle
        """

    def url(self, part, **format_data):
        return super().url(part, **format_data, vin=self._vehicle.vin)

    def _get_scope(self) -> str:
        return 'vehicle'


class CarFinderService(VehicleService):
    """
    Requires special permissions - might be for rental car companies
    """

    def find(self):
        """
        Returns the position of the car
        """
        return self._api.get(self.url('/vehicles/{vin}/position'))

    def _get_path(self):
        return 'bs/cf/v1'


class ClimateService(Service):
    def _get_path(self):
        return 'bs/rs/v1'

    def _get_scope(self):
        return 'vehicle'


class DiebstahlwarnanlageService(Service):
    def _get_path(self):
        return 'bs/dwap/v1'

    def _get_scope(self):
        return 'vehicle'


class GeofenceService(Service):
    """
    USA only - Restrict car area
    """

    def _get_path(self):
        return 'bs/geofencing/v1'

    def _get_scope(self):
        return 'vehicle'


class LockUnlockService(VehicleService):
    """
    Locks and unlocks the car
    """

    def get_actions(self):
        """
        Returns all available actions
        """
        return self._api.get(self.url("/vehicles/{vin}/actions"))

    # TODO: Lock and unlock request

    def _get_path(self):
        return 'bs/rlu/v1'


class MobileKeyService(Service):
    """
    Manages keyless access for the car
    """

    def _get_path(self):
        return '// Not implemented in MMI app'

    def _get_scope(self):
        return 'vehicle'


class OperationListService(MbbMalService):
    """
    Provides access to all permissions one can set for telemetrics and MMI (connect).
    This will also tell you how long your licences are valid,
    and when the service reaches it's final EOL date
    """

    def get_operations(self, vehicle: Vehicle):
        """
        Returns all services available and their license status
        """
        return self.get('/vehicles/{vin}/operations', vin=vehicle.vin)

    def get_api_list(self):
        """
        Returns all API operations
        """
        return self.get('')

    def _get_path(self):
        return super()._get_path() + '/rolesrights/operationlist/v3'


class PictureNavigationService(VehicleService):
    def get_all(self):
        # Returns 404 for some reason - might need to wireshark the correct path
        return self._api.get(self.url('/vehicles/{vin}/all'))

    def _get_path(self):
        return 'audi/b2c/picturenav/v1'

    def _get_scope(self):
        return 'vehicle'


class PoiNavigationService(Service):
    def _get_path(self):
        return 'audi/b2c/poinav/v1'

    def _get_scope(self):
        return 'vehicle'


class OnlineDestinationsService(VehicleService):
    def get_pois(self):
        return self._api.get(self.url('/vehicles/{vin}/pois'))

    def _get_path(self):
        return ''  # TODO


class PreTripClimaService(VehicleService):
    """
    Access to clima control - (EV only?)
    """

    def get_status(self):
        return self._api.get(self.url('/vehicles/{vin}/climater'))

    def get_request_status(self, action_id: str):
        return self._api.get(self.url('/vehicles/{vin}/climater/actions/{action_id}', action_id=action_id))

    def perform_action(self, request_factory: ClimaRequestFactory):
        self._api.post(self.url('/vehicles/{vin}/climater/actions'), data=request_factory.build())

    def _get_path(self):
        return 'bs/climatisation/v1'


class PushNotificationService(Service):
    """
    Registers push notifications (of some sort)
    """

    PLATFORM_GOOGLE = 'google'
    APP_ID = 'de.audi.mmiapp'

    def register(self, platform: str, app_id: str, token: str):
        """
        Registers a push notification service
        :param platform: Platform
        :param app_id: App ID
        :param token: Google messaging service token
        :return:
        """
        self._api.post(self.url('/subscriptions/{platform}/{app_id}/{token}', platform=platform, app_id=app_id,
                                token=token), data={})

    def _get_path(self):
        return 'fns/subscription/v1'

    def _get_scope(self):
        return 'vehicle'


class RemoteBatteryChargeService(VehicleService):
    """
    For EV only - battery status and charge management
    """

    def get_status(self):
        """
        Returns battery charge status

        :return: BatteryChargeResponse
        :rtype: BatteryChargeResponse
        """

        data = self._api.get(self.url('/vehicles/{vin}/charger'))
        response = BatteryChargeResponse()
        response.parse(data)
        return response

    def _get_path(self):
        return 'bs/batterycharge/v1'

    def _get_scope(self):
        return 'vehicle'


class RemoteDepartureTimeService(Service):
    """
    For EV only - timer for choosing when the battery  should be fully charged
    """

    def _get_path(self):
        return 'bs/departuretimer/v1'

    def _get_scope(self):
        return 'vehicle'


class RemoteHonkFlashService(VehicleService):
    """
    Note: This service requires special auth from vw/audi :(
    """

    FLASH_ONLY = "FLASH_ONLY"
    HONK_AND_FLASH = "HONK_AND_FLASH"
    HONK_ONLY = "HONK_ONLY"

    def flash(self, seconds: int):
        """
        Flashes the car for the given amount

        :param seconds: Seconds
        :return: HonkFlashAction
        :rtype: HonkFlashAction
        """
        data = {'honkAndFlashRequest': {
            'userPosition': {'latitude': 0,
                             'longitude': 0
                             },
            'serviceDuration': seconds,
            'serviceOperationCode': self.FLASH_ONLY
        }}
        data = self._api.post(self.url('/vehicles/{vin}/honkAndFlash'),
                              data=data)
        return HonkFlashAction(data)

    def get_status(self, action: HonkFlashAction):
        """
        Returns the status of the given action

        :param action: Action
        :return: RemoteHonkFlashActionStatus
        :rtype: RemoteHonkFlashActionStatus
        """
        data = self._api.get(self.url('/vehicles/{vin}/honkAndFlash/{action_id}/status', action_id=action.id))
        return RemoteHonkFlashActionStatus(data)

    def _get_path(self):
        return 'bs/rhf/v1'


class RemoteTripStatisticsService(VehicleService):
    """
    Trip statistics (like range, fuel consumption, ...)
    """
    LONG_TERM = 'longTerm'
    SHORT_TERM = 'shortTerm'

    def get_latest(self, trip_type: str):
        """
        Returns the latest trip statistic
        """
        return self._api.get(self.url('/vehicles/{vin}/tripdata/{trip_type}?newest', trip_type=trip_type))

    def _get_path(self):
        return 'bs/tripstatistics/v1'


class SpeedAlertService(VehicleService):
    """
    USA only - monitors if the car has been driven too fast
    """

    def get_list(self):
        return self._api.get(self.url('/vehicles/{vin}/speedAlerts'))

    def _get_path(self):
        return 'bs/speedalert/v1'


class UserManagementService(VehicleService):
    """
    Manages car pairing stuff
    """

    def get_paring_status(self):
        return self._api.get(self.url('/vehicles/{vin}/pairing'))

    def _get_path(self):
        return 'usermanagement/users/v1'


class ValetAlertService(Service):
    """
    USA only - Alerting for invalid car usage
    """

    def get_alerts(self):
        return self._api.get(self.url('/vehicles/{vin}/valetAlerts'))

    def get_definition(self):
        return self._api.get(self.url('/vehicles/{vin}/valetAlertDefinition'))

    def get_request_status(self, request_id: str):
        return self._api.get(self.url('/vehicles/{vin}/valetAlertDefinition/{id}/status', id=request_id))

    def set_definition(self, definition):
        # TODO: Implement definition
        return self._api.post(self.url('/vehicles/{vin}/valetAlertDefinition', data={}))

    def _get_path(self):
        return 'bs/valetalert/v1'

    def _get_scope(self):
        return 'vehicle'


class VehicleManagementService(VehicleService):
    """
    Information about the vehicle management system
    """

    def get_information(self):
        """
        Returns information about the connection system of the vehicle
        (such as embedded sim)
        """
        return self._api.get(self.url('/vehicles/{vin}'))

    def _get_path(self):
        return 'vehicleMgmt/vehicledata/v2'


class VehicleStatusReportService(VehicleService):
    """
    General status of the vehicle
    """

    def get_request_status(self, request_id: str):
        """
        Returns the status of the request with the given ID

        :param request_id: Request ID
        :return: RequestStatus
        :rtype: RequestStatus
        """
        data = self._api.get(self.url('/vehicles/{vin}/requests/{request_id}/jobstatus', request_id=request_id))
        return RequestStatus(data)

    def get_requested_current_vehicle_data(self, request_id: str):
        """
        Returns the vehicle report of the request with the given ID

        :param request_id: Request ID
        :return: VehicleDataResponse
        :rtype: VehicleDataResponse
        """
        data = self._api.get(self.url('/vehicles/{vin}/requests/{request_id}/status', request_id=request_id))
        return VehicleDataResponse(data)

    def request_current_vehicle_data(self):
        """
        Requests the latest report data from the vehicle

        :return: CurrentVehicleDataResponse
        :rtype: CurrentVehicleDataResponse
        """
        data = self.post('/vehicles/{vin}/requests')
        return CurrentVehicleDataResponse(data)

    def get_stored_vehicle_data(self):
        """
        Returns the last vehicle data received

        :return: VehicleDataResponse
        :rtype: VehicleDataResponse
        """
        data = self._api.get(self.url('/vehicles/{vin}/status'))
        return VehicleDataResponse(data)

    def _get_path(self):
        return super()._get_path() + '/bs/vsr/v1/{brand}/{country}'
