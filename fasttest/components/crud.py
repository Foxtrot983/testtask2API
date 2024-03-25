import random
import logging
from string import ascii_uppercase
from fastapi import HTTPException

from sqlalchemy.orm import Session as sql_session
from geopy.distance import geodesic

from .models import Location, Truck, Package
from .schemas import LocationItem, TruckItem, PackageItem
from .database import Session
from .utils import read_csv


def check_and_prepare_db():
    with Session() as session:
        current_data = session.query(Location).first()
        trucks = session.query(Truck).first()
        if current_data and trucks:
            return True
        if not current_data:
            locations = read_csv()
            for i in locations:
                city = i[3]
                state = i[5]
                postcode = i[0]
                latitude = i[1]
                longitude = i[2]
                new_location = Location(
                    city = city,
                    state = state,
                    postcode = postcode,
                    latitude = latitude,
                    longitude = longitude,
                )
                session.add(new_location)
            session.commit()
        if not trucks:
            for i in range(20):
                truck = Truck(number=f"{random.randint(1000, 9999)}{random.choice(ascii_uppercase)}", capacity=random.randint(1, 1000))
                session.add(truck)
            session.commit()


def change_locations():
    with Session() as session:
        locations = session.query(Location).all()
        trucks = session.query(Truck).all()
        for truck in trucks:
            truck.current_location = random.choice(locations)
        session.commit()



def get_packages(db: sql_session, weigth_ge:int, weight_le:int, miles_le:int):
    """
    [
        {
            pickup_location,
            delivery_location,
            cars_count,
        },
    ]
    """
    done_list = []
    packages = db.query(Package).all()
    trucks = db.query(Truck).all()
    for package in packages:
        if package.weight>weight_le or package.weight<weigth_ge:
            continue
        p_loc = package.pickup_location
        d_loc = package.delivery_location
        prepare_dict = {
            "pickup_location": f"{p_loc.state}/{p_loc.city}",
            "delivery_location": f"{d_loc.state}/{d_loc.city}",
            "cars_count": 0,
        }
        p_location = (p_loc.latitude, p_loc.longitude)
        for truck in trucks:
            t_loc = truck.current_location
            t_location = (t_loc.latitude, t_loc.longitude)
            miles = geodesic(p_location, t_location).miles
            #calculating cars with distance<=450
            #if miles<=450:
            #    prepare_dict["cars_count"]+=1
            if miles<=miles_le:
                prepare_dict["cars_count"]+=1
        
        done_list.append(prepare_dict)
    if not packages:
        done_list.append({
            "pickup_location": "",
            "delivery_location": "",
            "cars_count": 0,
        })
    return done_list


def db_del_package(db: sql_session, package_id:int):
    print('test')
    data = db.get(Package, package_id)
    if not data:
        raise HTTPException(status_code=404, detail="Package not found")
    db.delete(data)
    db.commit()
    return 'Success'
    


def create_package(db: sql_session, pickup_zip:int, delivery_zip:int, weight:int, description:str):
    if weight>1000 or weight<1:
        raise HTTPException(status_code=422, detail="Weight must be in range from 1 to 1000")
    p_location = db.get(Location, pickup_zip)
    d_location = db.get(Location, delivery_zip)
    if not p_location or not d_location:
        raise HTTPException(status_code=422, detail='Error with locations')
    package = Package(weight=weight, description=description, pickup_location=p_location, delivery_location=d_location)
    db.add(package)
    db.commit()
    return {
        'pickup_zip':pickup_zip, 
        'delivery_zip':delivery_zip, 
        'weight':weight, 
        'description':description, 
    }
    

def package_info(db: sql_session, package_id):
    '''
    {
        p_location: str
        d_location: str
        weight: int
        description: str
        trucks: []
    }
    '''
    
    package = db.get(Package, package_id)
    p_location = package.pickup_location
    d_location = package.delivery_location
    weight = package.weight
    description = package.description
    trucks = db.query(Truck).all()
    trucks_dict = {}
    p_la = p_location.latitude
    p_lo = p_location.longitude
    for truck in trucks:
        cur = truck.current_location
        la = cur.latitude
        lo = cur.longitude
        trucks_dict[truck.number] = geodesic((la,lo), (p_la, p_lo)).miles
    ordered_trucks = dict(sorted(trucks_dict.items(), key=lambda tr: tr[1]))
    return {
        "p_location": f"{p_location.state}/{p_location.city}",
        "d_location": f"{d_location.state}/{d_location.city}",
        "weight":weight,
        "description":description,
        "trucks":ordered_trucks,
    }


def db_package_patch(db: sql_session, package_id:int, weight:int, description:str):
    package = db.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404, detail="Package not found")
    package.weight = weight
    package.description = description
    db.commit()
    return {
        'weight': weight,
        'description': description,
    }


def db_truck_patch(db: sql_session, truck_id: int, zipcode: int):
    truck = db.get(Truck, truck_id)
    location = db.query(Location).filter(Location.postcode==zipcode).first()
    if not truck:
        raise HTTPException(status_code=404, detail='Truck not found')
    if not location:
        raise HTTPException(status_code=404, detail='Location not found')
    truck.current_location=location
    db.commit()
    return location.postcode
    