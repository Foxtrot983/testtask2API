from fastapi import Depends, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.orm import Session


from .crud import get_packages, create_package, package_info, db_del_package, db_package_patch, db_truck_patch
from .schemas import TruckItem, PackageItem, LocationItem, PackageSchema, PackageCreate, PackageInfoSchema, InfoSchema, PackagePatch, TruckPatch
from .database import SessionLocal


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/create_delivery/', response_model=PackageCreate)
async def create_delivery(package: PackageCreate, db: Session = Depends(get_db)):
    pickup_zip = package.pickup_zip
    delivery_zip = package.delivery_zip
    weight = package.weight
    description = package.description
    result = create_package(
        db=db,
        pickup_zip=pickup_zip,
        delivery_zip=delivery_zip,
        weight=weight,
        description=description,
        )
    return result


@router.get('/packages_list', response_model=list[PackageSchema])
async def get_list_packages(
    weigth_ge:int|None=1, 
    weight_le:int|None=1000, 
    miles_le:int|None=450,
    db: Session = Depends(get_db)
    ):
    try:
        item = get_packages(db=db, weigth_ge=weigth_ge, weight_le=weight_le, miles_le=miles_le)
        return item
    except Exception as e:
        print(e)
        return {'error': 'No packages to show'}
    pass


@router.get('/packages_item/{package_id}', response_model=PackageInfoSchema)
async def get_package(package_id: int, db: Session = Depends(get_db)):
    result = package_info(package_id=package_id, db=db)
    return result
    pass


@router.patch('/patch_truck/{truck_id}', response_model=TruckPatch)
async def patch_truck(truck_id, truck:TruckPatch, db:Session = Depends(get_db)):
    zipcode = truck.zipcode
    result = db_truck_patch(db=db, truck_id=truck_id, zipcode=zipcode)
    return {'zipcode': result}


@router.patch('/patch_package/{package_id}', response_model=PackagePatch)
async def patch_package(package_id, package: PackagePatch, db:Session = Depends(get_db)):
    package: PackagePatch
    weight = package.weight
    description = package.description
    result = db_package_patch(db=db, package_id=package_id, weight=weight, description=description)
    return result


@router.delete('/delete_package/{package_id}')
async def delete_package(package_id, db: Session = Depends(get_db)):
    result = db_del_package(package_id=package_id, db=db)
    return {'info': result}
    pass