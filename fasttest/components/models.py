import random
from typing import List

from sqlalchemy import func, JSON, UniqueConstraint, create_engine, ForeignKey, BigInteger, Float, Integer, select
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped, MappedAsDataclass, sessionmaker

from .database import Base, Session, engine


class Package(Base, MappedAsDataclass):
    __tablename__ = 'package'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    weight: Mapped[int] = mapped_column()
    description: Mapped[str]
    
    pickup_location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    pickup_location: Mapped["Location"] = relationship(foreign_keys=[pickup_location_id]) 
    
    delivery_location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    delivery_location: Mapped["Location"] = relationship(foreign_keys=[delivery_location_id])
    

class Location(Base, MappedAsDataclass):
    __tablename__ = 'location'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    city: Mapped[str] = mapped_column(nullable=False)
    state: Mapped[str] = mapped_column(nullable=False)
    postcode: Mapped[int] = mapped_column(nullable=False)
    latitude: Mapped[float] = mapped_column(type_=Float(precision=8), nullable=False)
    longitude: Mapped[float] = mapped_column(type_=Float(precision=8), nullable=False)
    
    trucks: Mapped[List["Truck"]] = relationship(back_populates='current_location')
    
    packages_pickup: Mapped[List['Package']] = relationship(back_populates='pickup_location', foreign_keys=[Package.pickup_location_id])
    packages_delivery: Mapped[List['Package']] = relationship(back_populates='delivery_location', foreign_keys=[Package.delivery_location_id])



class Truck(Base, MappedAsDataclass):
    __tablename__ = 'truck'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str]
    capacity: Mapped[int]
    current_location: Mapped[Location] = relationship(back_populates='trucks')
    current_location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    
    def __init__(self, number: str, capacity: int):
        self.number = number
        self.capacity = capacity
        self.current_location = self._get_random_location()
        self.current_location_id = self.current_location.id
        pass
    
    
    def _get_random_location(self) -> Location:
        with Session() as session:
            #locations = session.execute(select(Location)).scalars().all()
            id = random.randint(1, 33000)
            location = session.get(Location, id)
        return location

Base.metadata.create_all(engine)