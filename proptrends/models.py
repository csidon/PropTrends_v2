from proptrends import db, loginManager
from flask_login import UserMixin


@loginManager.user_loader
def loadUser(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):                                                 
    id = db.Column(db.Integer, primary_key = True)
    user_first_name = db.Column(db.String(100), nullable=False)
    user_last_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(120), unique=True, nullable=False)
    # A hash will be generated for user_image to be 20 Char, and userPass as 60 Char
    user_image = db.Column(db.String(20), nullable=False, default='default.jpg')
    user_password = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"User('{self.user_email}', '{self.user_password}', '{self.user_image}')"


class Suburb_key(db.Model):     # Using snake_case because RDS does not like CamelCase
    id = db.Column(db.Integer, primary_key=True)
    suburb_name = db.Column(db.String)
    suburbkeys = db.relationship('Listing', backref='suburbs', lazy=True, uselist=False)


class Proptype_key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String)
    proptypekeys = db.relationship('Listing', backref='proptypes', lazy=True, uselist=False)


class City_key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String)
    citykeys = db.relationship('Listing', backref='cities', lazy=True, uselist=False)

class Region_key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region_name = db.Column(db.String)
    regionkeys = db.relationship('Listing', backref='regions', lazy=True, uselist=False)


class Listing(db.Model):
    # DECLARING VARIABLES TO COLLECT
    id = db.Column(db.Integer, primary_key=True)
    prop_url = db.Column(db.String, unique=True)
    list_date = db.Column(db.DateTime)
    address = db.Column(db.String)
    region = db.Column(db.Integer, db.ForeignKey('region_key.id'))
    city = db.Column(db.Integer, db.ForeignKey('city_key.id'))
    suburb = db.Column(db.Integer, db.ForeignKey('suburb_key.id'))      # This will be the suburb.id
    prop_type = db.Column(db.Integer, db.ForeignKey('proptype_key.id'))      # This will be the prop_type.id
    title_type = db.Column(db.String)  # Potentially change to id if there's a lot of listings with titletypes
    list_price = db.Column(db.BigInteger)
    beds = db.Column(db.Integer)
    baths = db.Column(db.Integer)
    size_m2 = db.Column(db.Integer)
    land_m2 = db.Column(db.Integer)
    floor_m2 = db.Column(db.Integer)
    garage = db.Column(db.Integer)
    other_parks = db.Column(db.Integer)
    nbs = db.Column(db.Integer)
    bodycorp = db.Column(db.Numeric)
    rates = db.Column(db.Numeric)
    ensuite = db.Column(db.Integer)

    def serialize(self):
        return {
            'id': self.id,
            'prop_url': self.prop_url,
            # 'list_date': self.list_date.strftime('%Y-%m-%d %H:%M:%S'),
            'address': self.address,
            'region': self.regions.region_name if self.regions else None,
            'city': self.cities.city_name if self.cities else None,
            'suburb': self.suburbs.suburb_name if self.suburbs else None,
            'prop_type': self.proptypes.type if self.proptypes else None,

            'title_type': self.title_type,
            'list_price': self.list_price,
            'beds': self.beds,
            'baths': self.baths,
            'size_m2': self.size_m2,
            'land_m2': self.land_m2,
            'floor_m2': self.floor_m2,
            'garage': self.garage,
            'other_parks': self.other_parks,
            'nbs': self.nbs,
            'bodycorp': self.bodycorp,
            'rates': self.rates,
            'ensuite': self.ensuite,
        }



class Last_scraped(db.Model):
    # This is an extremely "light" table that registers when the scraper was last run/
    # if it was run to completion
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String)
    last_scrape_start = db.Column(db.DateTime)
    last_scrape_end = db.Column(db.DateTime)
    still_running = db.Column(db.Boolean)


# For future expansion where it accepts more than just Wellington-city
class Regions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    region = db.Column(db.String)
    district = db.Column(db.String)
    suburb = db.Column(db.String)