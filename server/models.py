from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)


class Mission(db.Model, SerializerMixin):
    __tablename__ = 'missions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    scientist_id = db.Column(db.Integer, db.ForeignKey('scientists.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    @validates('name')
    def validate_name(self, key, name):
        if not name:
            raise ValueError('Name is required.')
        return name
    
    @validates('scientist_id')
    def validate_scientist_id(self, key, scientist_id):
        scientists = Scientist.query.all()
        ids = [scientist.id for scientist in scientists]
        if not scientist_id:
            raise ValueError('Scientist must be assign to as mission.')
        elif not scientist_id in ids:
            raise ValueError('Scientist must exist')
        # if Mission.query.filter_by(scientist_id=scientist_id, planet_id=self.planet_id).count() > 0:
        #     raise ValueError('Scientist already assigned to this mission')
        return scientist_id
    
    @validates('planet_id')
    def validate_planet_id(self, key, planet_id):
        planets = Planet.query.all()
        ids = [planet.id for planet in planets]
        if not planet_id:
            raise ValueError('Planet must be assigned to a mission.')
        elif not planet_id in ids:
            raise ValueError('Planet must exist.')
        return planet_id
    
    def __repr__(self):
        return f'<Mission id: {self.id}, scientist_id: {self.scientist_id}, planet_id: {self.planet_id}, name: {self.name}>'
    
    planet = db.relationship('Planet', back_populates='missions')
    scientist = db.relationship('Scientist', back_populates='missions')

    # serialize_rules = ('-planet.missions', '-scientist.missions',
    #                    '-planet.scientists', '-scientist.planets', '-created_at', '-updated_at')
    serialize_rules = ('-planet', '-scientist',)
    


class Scientist(db.Model, SerializerMixin):
    __tablename__ = 'scientists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    field_of_study = db.Column(db.String, nullable=False)
    avatar = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    @validates('name')
    def validate_name(self, key, name):
        scientists = Scientist.query.all()
        names = [scientist.name for scientist in scientists]
        if not name:
            raise ValueError('Name is required.')
        elif name in names:
            raise ValueError('Name already exists.')
        return name
    
    @validates('field_of_study')
    def validate_field_of_study(self, key, field_of_study):
        if not field_of_study:
            raise ValueError('Field of study is required.')
        return field_of_study
    
    missions = db.relationship(
        'Mission', back_populates='scientist', cascade="all,delete, delete-orphan")
    # missions = db.relationship('Mission', backref='scientist') other option, cross ref in Mission class not needed like it is for back_populates
    planets = association_proxy('missions', 'planet')
    serialize_rules = ('-missions', '-created_at', '-updated_at')
    
    


class Planet(db.Model, SerializerMixin):
    __tablename__ = 'planets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    distance_from_earth = db.Column(db.String)
    nearest_star = db.Column(db.String)
    image = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    missions = db.relationship('Mission', back_populates='planet', cascade="all,delete, delete-orphan")
    # missions = db.relationship('Mission', backref='planet')
    scientists = association_proxy('missions', 'scientist')
    serialize_rules = ('-missions', '-created_at', '-updated_at')