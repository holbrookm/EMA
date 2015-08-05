import sys, os
from flask import request,  Flask, render_template, url_for, redirect, flash, session, g
from flask.ext.sqlalchemy import SQLAlchemy

import config

#from cie_connect import cie_connect, perform_cie_logon
import debug, logging_config
import class_ims_ema as ims
import ema_functions as ema
import session_calls


#create the application
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    DEBUG=True,
    SECRET_KEY='developmentkey',
    #USERNAME='holbrookm',
    #PASSWORD='manu16'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

logger = logging_config.logger

@app.route('/')
def index():
    """ Index Page.
    """
    logger.debug('FUNC::::::: app.route.login')
    logger.debug('** Leaving FUNC::::::: app.route.login')
    return render_template('login.html')



@app.route('/login', methods=['POST', 'GET',])
def login(error = None):
    logger.debug('FUNC::::::: app.route.login')

    if request.method == 'POST':
        logger.debug ('Performing logon')
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        #return_code = perform_cie_logon(session['username'], session['password'])
        return_code = 1
        logger.debug(session['username'])
        if return_code == 100:
             error = 'Invalid password'
             flash(u'Invalid password provided', 'error')

        else:
            session['logged_in'] = True
            logger.debug(session['username'] + ': Logged In')
            if debug.mac():
                pass
            else:
                session['emaSession'] = ema.emaLogin()
                session['transaction_id'] = '2222222'
            return redirect(url_for(('subscribers')))
    logger.debug('** Leaving FUNC::::::: app.route.login')
    return render_template('login.html', error=error)


#############################
#### SEARCH #########
#############################

@app.route('/searchRangeR')
def searchRangeR():
    logger.debug('FUNC:::::: app.route.searchRangeR')
    logger.debug('** Leaving FUNC:::::: app.route.searchRangeR')
    return render_template('searchRangeR.html')

@app.route('/performSearchRangeR', methods=['POST', ])
def performSearchRangeR():
    logger.debug('FUNC:::::: app.route.performSearchRangeR')
    debug.p(request.method)
    if request.method == 'POST':
        sub = str(request.form['sub'])
        session['sub'] = sub   # subscriber number in text
        c_sub = ims.registeredRangeSubscriber(sub)
        transaction_id = session['transaction_id']
        result = c_sub.subscriberGet(session['emaSession'])
        logger.debug (result.status_code)
        logger.debug (result.text)

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session') != -1:
                logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Invalid Session'))
                return redirect(url_for('login', error='Invalid Session'))
            elif result.text.find('No such object') != -1:
                logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Subscriber not provisioned: redirecting to subscribers.html'))
                session['mesg'] = 'NotProvisioned'
                return redirect(url_for('subscribers'))
            else:
                pass
        if result.status_code == 200:
            subdetails = ema.prepareXmlToClass(result.text)
            session['subType'] = subdetails['pubData']['publicIdState'] # Current Subscriber State in text
            session['details'] = subdetails  # Current Subscriber SOAP XML structure

            del c_sub # Remove Subscriber Class instance

            logger.debug('**Leaving FUNC:::::: app.route.performSearchRangeR: Status = 200')
            return redirect(url_for('subscriberResult'))
            
    else:
        return render_template('/login.html')
        logger.error('Unexpected error occurred in app.route.performSearchRangeR ')
    logger.debug('** Leaving FUNC::::::: app.route.performSearchRangeR: End of Func error')
    return render_template('/login.html')


#############################
#### CREATE
#############################
@app.route('/subscriberCreate')
def subscriberCreate():
    logger.debug('FUNC:::::: app.route.subscriberCreate')
    logger.debug('** Leaving FUNC::::::: app.route.subscriberCreate')
    return render_template('searchRangeR.html', createmesg= 'True')

@app.route('/CreateNR/<sub>')
def createNR(sub):
    logger.debug('FUNC:::::: app.route.createNR')
    cSub = ims.nonRegisteredSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    logger.debug('** Leaving FUNC::::::: app.route.createNR')
    return redirect('subscribers.html', createmesg = sub)

@app.route('/CreateRangeNR/<sub>')
def createRangeNR(sub):
    logger.debug('FUNC:::::: app.route.createRangeNR')
    cSub = ims.nonRegisteredRangeSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    logger.debug('** Leaving FUNC::::::: app.route.createRangeNR')
    return redirect('subscribers.html', createmesg = sub)



@app.route('/CreateR/<sub>')
def createR(sub):
    logger.debug('FUNC:::::: app.route.createR')
    c_sub = ims.registeredSubscriber(sub)# Create Registered Subscriber Class instance
    result = c_sub.subscriberCreate(session['emaSession'])
   
    if result.status_code == 500: #Successful EMA connection but there is an error.
        if result.text.find('Invalid Session') != -1:
            logger.debug(('** Leaving FUNC:::: app.route.performSearchrangeR:  Invalid Session'))
            return redirect(url_for('login', error='Invalid Session'))
        else:
            logger.debug('Unknown Error in createR func')
            pass
    if result.status_code == 200:
        session['mesg'] = 'Created'
        session['sub'] = sub
        del c_sub # Remove Subscriber Class instance
    
    logger.debug('** Leaving FUNC::::::: app.route.createR')
    return redirect(url_for('subscribers'))

@app.route('/CreateRangeR/<sub>')
def createRangeR(sub):
    logger.debug('FUNC:::::: app.route.createRangeR')
    cSub = ims.registeredRangeSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    logger.debug('** Leaving FUNC::::::: app.route.createRangeR')
    return redirect('subscribers.html', createmesg = sub)



@app.route('/create', methods=['POST',])
def create(subType, sub):
    #
    #
    template = ''
    logger.debug('FUNC::::::: app.route.create')
    if request.method == 'POST':
        cSub = session_calls.setSessionSubType(subType)

        result = cSub.subscriberCreate(session['emaSession'])

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session'):
                return redirect(url_for('login', error='Invalid Session'))
            elif result.text.find('No such object'):
                return redirect ('searchRangeR.html')
            else:
                pass
        elif result.status_code == 200:
            return redirect('/subscribers.html', mesg = 'Successful Delete')
    else:
        return render_template ('login.html')
    logger.debug('** Leaving FUNC::::::: app.route.create')
    return render_template(url_for('login'))



#########################################################
##### DELETE
####################################################

@app.route('/delete', methods=['POST','GET',])
def delete():
    #
    #
    template = ''
    logger.debug('FUNC::::::: app.route.delete')
    if request.method == 'POST':
        logger.debug(request.form['submit'])
        sub = request.form['submit']
        cSub = ims.registeredSubscriber(sub) # For a delete any Class Type can work

        result = cSub.subscriberDelete(session['emaSession'])

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session'):
                logger.debug('********Invalid Session')
                return redirect(url_for('login', error='Invalid Session : Please login again.'))
            elif result.text.find('No such object'):
                logger.debug('******** No Such object')
                return redirect(url_for('searchRangeR'))
            else:
                pass
        elif result.status_code == 200:
            logger.debug('** Leaving FUNC::::::: app.route.delete')
            session['mesg'] = 'Deleted'
            return redirect(url_for('subscribers'))
    else: #GET Method
        logger.debug('** Leaving FUNC::::::: app.route.delete')
        return render_template('searchRangeR.html', deletemesg = "True")
    return


####################################
### MISC
####################################


@app.route('/subscriberResult', methods=['POST','GET',])
def subscriberResult():
    logger.debug('FUNC:::::: app.route.subscriberResult')
    logger.debug(request.method)
    if request.method == 'POST':
        logger.debug('** Leaving FUNC:::::: app.route.subscriberResult')
        return redirect(url_for ('subscriberResult'))
    else:
        logger.debug('** Leaving FUNC:::::: app.route.subscriberResult')
        return render_template('subscriberResult.html', sub = session.get('sub'), details = session.get('details')) # Correct format to use Session Variables


@app.route('/subscribers', methods=['POST','GET',])
def subscribers(mesg = None):
    logger.debug('FUNC:::::: app.route.subscribers')
    if session.get('mesg'):        
        if session.get('mesg') == 'Deleted':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers     ::  Subscriber Deleted')
            return render_template('subscribers.html', deletemesg = 'Successful Delete')
        elif session.get('mesg') == 'NotProvisioned':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers   ::  Subscriber not Provisioned')
            return render_template('subscribers.html', sub = session.get('sub'), mesg = 'Your Subscriber is not Provisioned')
        elif session.get('mesg') == 'Created':
            logger.debug('** Leaving FUNC:::::: app.route.subscribers    ::  Subscriber created')
            return render_template('subscribers.html', newsub = session.get('sub'), createmesg = 'Your Subscriber has been Created')
        else:
            logger.debug('** Leaving FUNC:::::: app.route.subscribers')
            return render_template('subscribers.html', mesg = mesg)
    else:
        logger.debug('** Leaving FUNC:::::: app.route.subscribers')
        return render_template('subscribers.html', mesg = mesg)

# Below this point the filters are stored

@app.template_filter('rsplit')
def get_id_filter(data):
    if data:
        return data.rsplit('/')[-1]
    else:
        return



if __name__ == "__main__":
    app.run(debug =True, host = '0.0.0.0', port= 4500)
