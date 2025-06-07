from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    address: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[str] = mapped_column(String(120), nullable=False)

    favorite_character: Mapped[list['Fav_character']]= relationship(back_populates= 'user')
    favorite_planet: Mapped[list['Fav_planet']]= relationship(back_populates= 'user')
    favorite_vehicle: Mapped[list['Fav_vehicle']]= relationship(back_populates= 'user')


    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "address": self.address,
            "country": self.country
            # do not serialize the password, its a security breach
        }

class Character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    height: Mapped[str] = mapped_column(String(120), nullable=False)
    gender: Mapped[str] = mapped_column(String(120), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(120), nullable=False)

    favorite_by_links: Mapped[list['Fav_character']]= relationship(back_populates= 'character')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "gender": self.gender,
            "eye_color": self.eye_color
        }
    
class Planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    climate: Mapped[str] = mapped_column(String(120), nullable=False)
    population: Mapped[int] = mapped_column(Integer, nullable=False)
    gravity: Mapped[str] = mapped_column(String(120), nullable=False)

    favorite_by_links: Mapped[list['Fav_planet']]= relationship(back_populates= 'planet')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "climate": self.climate,
            "population": self.population,
            "gravity": self.gravity
        }

class Vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    model: Mapped[str] = mapped_column(String(120), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(120), nullable=False)
    passengers: Mapped[int] = mapped_column(Integer, nullable=False)
    max_speed: Mapped[int] = mapped_column(Integer, nullable=False)

    favorite_by_links: Mapped[list['Fav_vehicle']]= relationship(back_populates= 'vehicle')

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "model": self.model,
            "manufacturer": self.manufacturer,
            "passengers": self.passengers,
            "max_speed": self.max_speed
        }
    
class Fav_character(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    character_id: Mapped[int] = mapped_column(ForeignKey('character.id'))
    user: Mapped['User'] = relationship(back_populates= 'favorite_character')
    character: Mapped['Character'] = relationship(back_populates= 'favorite_by_links')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id
        }

class Fav_planet(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    planet_id: Mapped[int] = mapped_column(ForeignKey('planet.id'))
    user: Mapped['User'] = relationship(back_populates= 'favorite_planet')
    planet: Mapped['Planet'] = relationship(back_populates= 'favorite_by_links')

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "planet_id": self.planet_id
        }
    
class Fav_vehicle(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey('vehicle.id'))
    user: Mapped['User'] = relationship(back_populates= 'favorite_vehicle')
    vehicle: Mapped['Vehicle'] = relationship(back_populates= 'favorite_by_links')