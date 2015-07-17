import sys
from flask import request,  Flask, render_template, url_for, redirect, flash, session
import os
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
            return render_template('subscribers.html')
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
        c_sub = ims.registeredRangeSubscriber(sub)
        transaction_id = session['transaction_id']
        result = c_sub.subscriberGet(session['emaSession'])
        logger.debug (result.status_code)
        logger.debug (result.text)

        if result.status_code == 500: #Successful EMA connection but there is an error.        
            if result.text.find('Invalid Session') != -1:
                logger.debug(('Invalid Session'))
                return render_template('/login.html', error = 'Invalid Session')
            elif result.text.find('No such object') != -1:
                return render_template('subscribers.html', mesg ='Your subscriber is not provisioned', sub = sub)
            else: 
                pass
        if result.status_code == 200:
            subdetails = ema.prepareXmlToClass(result.text)
            session['sub'] = sub
            session['subType'] = subdetails['pubData']['publicIdState']
            return render_template('subscriberResult.html', sub = sub, details = subdetails, cSub = c_sub)
            #return redirect(url_for 'subscriberResult')
    else:
        return render_template('/login.html')
        logger.error('Unexpected error occurred in app.route.performSearchRangeR ')
    logger.debug('** Leaving FUNC::::::: app.route.performSearchRangeR')
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
    return render_template('subscribers.html', createmesg = sub)

@app.route('/CreateRangeNR/<sub>')
def createRangeNR(sub):
    logger.debug('FUNC:::::: app.route.createRangeNR')
    cSub = ims.nonRegisteredRangeSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    logger.debug('** Leaving FUNC::::::: app.route.createRangeNR')
    return render_template('subscribers.html', createmesg = sub)



@app.route('/CreateR/<sub>')
def createR(sub):
    logger.debug('FUNC:::::: app.route.createR')
    cSub = ims.registeredSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    logger.debug('** Leaving FUNC::::::: app.route.createR')
    return render_template('subscribers.html', createmesg = 'Successful Creation', newsub = sub)

@app.route('/CreateRangeR/<sub>')
def createRangeR(sub):
    logger.debug('FUNC:::::: app.route.createRangeR')
    cSub = ims.registeredRangeSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    logger.debug('** Leaving FUNC::::::: app.route.createRangeR')
    return render_template('subscribers.html', createmesg = sub)



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
                return render_template ('/login.html', error = 'Invalid Session')
            elif result.text.find('No such object'):
                template = ('searchRangeR.html')
            else: 
                pass
        elif result.status_code == 200:
            render_template('/subscribers.html', mesg = 'Successful Delete')
    else:
        template = ('login.html')
    logger.debug('** Leaving FUNC::::::: app.route.create')
    return render_template(template)



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
                return render_template('/login.html', error = 'Invalid Session : Please login again.')
            elif result.text.find('No such object'):
                logger.debug('******** No Such object')
                return render_template('searchRangeR.html')
            else: 
                pass
        elif result.status_code == 200:
            logger.debug('** Leaving FUNC::::::: app.route.delete')
            return render_template('subscribers.html', deletemesg = 'Successful Delete')
    else:
        logger.debug('** Leaving FUNC::::::: app.route.delete')
        return render_template('searchRangeR.html', deletemesg = "True")
    return


####################################
### MISC
####################################


@app.route('/subscriberResult', methods=['POST',])
def subscriberResult():
    logger.debug('FUNC:::::: app.route.subscriberResult')    
    if request.method == 'POST':
        for k,v in request.method.items():
            print k, v
    return "You asked for sub number %s in account : %s " %((sub_no), (account))



# Below this point the filters are stored    

@app.template_filter('rsplit')
def get_id_filter(data):
    if data:
        return data.rsplit('/')[-1]
    else:
        return



if __name__ == "__main__":
    app.run(debug =True, port= 4500)

