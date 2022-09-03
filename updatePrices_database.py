from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import States, Base, RegPrices, MagPrices
from decimal import *

# engine = create_engine('postgresql://vingo:somepassword@localhost/vingo')
engine = create_engine('sqlite:///vingo.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

for i in session.query(RegPrices).all():
    i.price = i.price * Decimal(1.10)
session.commit()

for e in session.query(MagPrices).all():
    e.price = e.price * Decimal(1.10)
session.commit()
    
