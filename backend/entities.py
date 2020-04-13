import dataclasses

MIN_LATITUDE = -90
MAX_LATITUDE = 90
MIN_LONGITUDE = -180
MAX_LONGITUDE = 180


@dataclasses.dataclass()
class Bus:
    busId: str
    lat: float
    lng: float
    route: str

    def to_dict(self):
        return dataclasses.asdict(self)


@dataclasses.dataclass()
class WindowBounds:
    east_lng: float = MIN_LONGITUDE
    north_lat: float = MAX_LATITUDE
    south_lat: float = MIN_LATITUDE
    west_lng: float = MAX_LONGITUDE

    def update(self, east_lng, north_lat, south_lat,  west_lng):
        self.east_lng = east_lng
        self.north_lat = north_lat
        self.south_lat = south_lat
        self.west_lng = west_lng

    def is_inside(self, lat, lng):
        return self.south_lat < lat < self.north_lat and \
               self.west_lng < lng < self.east_lng
