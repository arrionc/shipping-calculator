from sqlalchemy import Column, ForeignKey, Integer, String, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class States(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    name = Column(String(5), nullable=False)
    transit = Column(String(80), nullable=False)
    carrier = Column(String(30), nullable=False)
    zone = Column(Integer, nullable=False)

class RegPrices(Base):
    __tablename__ = 'regprices'

    id = Column(Integer, primary_key=True)
    zone = Column(Integer, nullable=False)
    bottles = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)

class MagPrices(Base):
    __tablename__ = 'magprices'

    id = Column(Integer, primary_key=True)
    zone = Column(Integer, nullable=False)
    bottles = Column(Integer, nullable=False)
    price = Column(Numeric, nullable=False)


engine = create_engine('sqlite:///vingo.db')
# engine = create_engine('postgresql://vingo:somepassword@localhost/vingo')
Base.metadata.create_all(engine)