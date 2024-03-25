from pydantic import BaseModel, Field


class PackageItem(BaseModel):
    weight: int = Field(ge=1, le=1000)
    description: str | None
    pickup_location: "LocationItem"
    delivery_location: "LocationItem"
    pass


class PackageSchema(BaseModel):
    pickup_location: str
    delivery_location: str
    cars_count: int
    

class PackageInfoSchema(BaseModel):
    p_location: str
    d_location: str
    weight: int = Field(ge=1, le=1000)
    description: str
    trucks: dict


class PackageCreate(BaseModel):
    pickup_zip: int
    delivery_zip: int
    weight: int = Field(ge=1, le=1000)
    description: str


class PackagePatch(BaseModel):
    weight: int = Field(ge=1, le=1000)
    description: str


class TruckItem(BaseModel):
    number: str
    capacity: int
    current_location: "LocationItem"
    current_location_id: int
    

class TruckPatch(BaseModel):
    zipcode: int


class LocationItem(BaseModel):
    city: str
    state: str
    postcode: int
    latitude: float
    longitude: float
    
    
class InfoSchema(BaseModel):
    info: str