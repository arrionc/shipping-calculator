from flask import Flask, render_template, request, redirect, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from database_setup import Base, States, RegPrices, MagPrices
import string
import httplib2
import json
from flask import make_response, flash, url_for
import requests
import locale
locale.setlocale( locale.LC_ALL, '' )

app = Flask(__name__)

# Connect to the Database to create sessions
engine = create_engine('sqlite:///vingo.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

noShippingStates = ['AR', 'DE', 'KY', 'MS', 'OK', 'RI', 'UT']

@app.route('/', methods=['GET', 'POST'])
@app.route('/calculator', methods=['GET', 'POST'])
def enterValues():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    if request.method == 'POST':
        state = request.form['state']
        regBottles = request.form['750s']
        magBottles = request.form['magnums']
        if state in noShippingStates:
            flash('''NO SHIPMENTS TO: AR, DE, KY, MS, OK, RI, UT''')
            return render_template('input.html')
        try:
            validState = session.query(States).filter_by(name=state).one()
        except NoResultFound:
            flash('''Invalid State Entered''')
            return render_template('input.html')
        if regBottles == '':
            flash('''Please Enter a value for Regular Size or Less''')
            return render_template('input.html')
        if magBottles == '':
            flash('''Please Enter a value for Magnums ''')
            return render_template('input.html')
        
        if int(regBottles) <= 12 and int(magBottles) <= 6:
            return redirect(url_for('firstCalculation', state=state, regBottles=regBottles, magBottles=magBottles))
        if int(regBottles) > 12 and int(magBottles) > 6: 
            return redirect(url_for('secondCalculation', state=state, regBottles=regBottles, magBottles=magBottles))
        if int(regBottles) > 12 and int(magBottles) <= 6: 
            return redirect(url_for('thirdCalculation', state=state, regBottles=regBottles, magBottles=magBottles))
        if int(regBottles) <= 12 and int(magBottles) > 6:
            return redirect(url_for('fourthCalculation', state=state, regBottles=regBottles, magBottles=magBottles))
        
    else:
        return render_template('input.html') 


# Calculation for <= 12 regular bottles and <= 6 magnum bottles
@app.route('/firstcalculation/<state>/<int:regBottles>/<int:magBottles>/')
def firstCalculation(state, regBottles, magBottles):

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    
    OneState = session.query(States).filter_by(name=state).one()
    regShipPrices = session.query(RegPrices).filter_by(zone=OneState.zone, bottles=regBottles).one()
    magShipPrices = session.query(MagPrices).filter_by(zone=OneState.zone, bottles=magBottles).one()
    totalRegPrices = locale.currency(regShipPrices.price)
    totalMagPrices = locale.currency(magShipPrices.price)
    totalShipPrice = locale.currency(regShipPrices.price + magShipPrices.price)
    return render_template('first.html', target=OneState, regPrices=totalRegPrices, magPrices=totalMagPrices, 
                           totalPrice=totalShipPrice, regBottles=regBottles, magBottles=magBottles)

# Calculation for > 12 regular bottles and > 6 magnum bottles
@app.route('/secondcalculation/<state>/<int:regBottles>/<int:magBottles>/')
def secondCalculation(state, regBottles, magBottles):

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    OneState = session.query(States).filter_by(name=state).one()
    looseBottles = regBottles % 12
    regCases = (regBottles - looseBottles) / 12
    twelveCasePrice = session.query(RegPrices).filter_by(zone=OneState.zone, bottles=12).one()
    twelveCasePriceDollar = locale.currency(twelveCasePrice.price)
    casePriceDollar = regCases * twelveCasePrice.price
    casePrice = locale.currency(casePriceDollar)
    looseBottlePrice = session.query(RegPrices).filter_by(zone=OneState.zone, bottles=looseBottles).one()
    looseRegPriceDollar = looseBottlePrice.price
    looseRegPrice = locale.currency(looseRegPriceDollar)
    magLooseBottles = magBottles % 6
    magCases = (magBottles - magLooseBottles) / 6
    magCasePrice = session.query(MagPrices).filter_by(zone=OneState.zone, bottles=6).one()
    magCasePriceDollar = locale.currency(magCasePrice.price)
    magPriceDollar = magCases * magCasePrice.price
    magPrice = locale.currency(magPriceDollar)
    looseMagnumPrice = session.query(MagPrices).filter_by(zone=OneState.zone, bottles=magLooseBottles).one()
    looseMagPriceDollar = looseMagnumPrice.price
    looseMagPrice = locale.currency(looseMagPriceDollar)
    totalPrice = locale.currency(casePriceDollar + looseRegPriceDollar + magPriceDollar + looseMagPriceDollar)

    return render_template('second.html', target=OneState, regBottles=regBottles, magBottles=magBottles,
                            looseBottles=looseBottles, regCases=regCases, magLooseBottles=magLooseBottles,
                            magCases=magCases, casePrice=casePrice, twelveCasePriceDollar=twelveCasePriceDollar, looseRegPrice=looseRegPrice,
                            magPrice=magPrice, magCasePriceDollar=magCasePriceDollar, looseMagPrice=looseMagPrice, totalPrice=totalPrice)

# Calculation for >12 reg bottles and <= 6 magnum bottles 
@app.route('/thirdcalculation/<state>/<int:regBottles>/<int:magBottles>')
def thirdCalculation(state, regBottles, magBottles):

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    OneState = session.query(States).filter_by(name=state).one()
    looseBottles = regBottles % 12
    regCases = (regBottles - looseBottles) / 12
    twelveCasePrice = session.query(RegPrices).filter_by(zone=OneState.zone, bottles=12).one()
    twelveCasePriceDollar = locale.currency(twelveCasePrice.price)
    casePriceDollar = regCases * twelveCasePrice.price
    casePrice = locale.currency(casePriceDollar)
    looseBottlePrice = session.query(RegPrices).filter_by(zone=OneState.zone, bottles=looseBottles).one()
    looseRegPriceDollar = looseBottlePrice.price
    looseRegPrice = locale.currency(looseRegPriceDollar)
    magShipPrices = session.query(MagPrices).filter_by(zone=OneState.zone, bottles=magBottles).one()
    magPriceDollar = magShipPrices.price
    magPrice = locale.currency(magPriceDollar)
    totalPrice = locale.currency(casePriceDollar + looseRegPriceDollar + magPriceDollar)

    return render_template('third.html', target=OneState, regBottles=regBottles, magBottles=magBottles,
                            looseBottles=looseBottles, regCases=regCases, twelveCasePriceDollar=twelveCasePriceDollar, casePrice=casePrice, 
                            looseRegPrice=looseRegPrice, magPrice=magPrice, totalPrice=totalPrice)

# Calculation for <=12 reg bottles and > 6 magnum bottles
@app.route('/fourthcalculation/<state>/<int:regBottles>/<int:magBottles>')
def fourthCalculation(state, regBottles, magBottles):

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    OneState = session.query(States).filter_by(name=state).one()
    regShipPrices = session.query(RegPrices).filter_by(zone=OneState.zone, bottles=regBottles).one()
    casePriceDollar = regShipPrices.price
    casePrice = locale.currency(casePriceDollar)
    magLooseBottles = magBottles % 6
    magCases = (magBottles - magLooseBottles) / 6
    magCasePrice = session.query(MagPrices).filter_by(zone=OneState.zone, bottles=6).one()
    magCasePriceDollar = locale.currency(magCasePrice)
    magPriceDollar = magCases * magCasePrice.price
    magPrice = locale.currency(magPriceDollar)
    looseMagnumPrice = session.query(MagPrices).filter_by(zone=OneState.zone, bottles=magLooseBottles).one()
    looseMagPriceDollar = looseMagnumPrice.price
    looseMagPrice = locale.currency(looseMagPriceDollar)
    totalPrice = locale.currency(casePriceDollar + magPriceDollar + looseMagPriceDollar)
    

    return render_template('fourth.html', target=OneState, regBottles=regBottles, magBottles=magBottles,
                            casePrice=casePrice, magCases=magCases, magLooseBottles=magLooseBottles, magCasePriceDollar=magCasePriceDollar, 
                            magPrice=magPrice, looseMagPrice=looseMagPrice, totalPrice=totalPrice)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)