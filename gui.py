import sys
from flask import request,  Flask, render_template, url_for, redirect, flash, session
import os
#from cie_connect import cie_connect, perform_cie_logon
import debug
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

@app.route('/')
def index():
    """ Index Page.
    """
    debug.p('FUNC::::::: app.route.login')
    debug.p('** Leaving FUNC::::::: app.route.login')
    return render_template('login.html')



@app.route('/login', methods=['POST', ])
def login():
    debug.p('FUNC::::::: app.route.login')
    error = None
    if request.method == 'POST':
        debug.p ('Performing logon')
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        #return_code = perform_cie_logon(session['username'], session['password']) 
        return_code = 1
        debug.p(session['username'])
        if return_code == 100:
             error = 'Invalid password'
             flash(u'Invalid password provided', 'error')
             
        else:
            session['logged_in'] = True
            debug.p('####################')
            if debug.mac():
                pass
            else:
                session['emaSession'] = ema.emaLogin()
                session['transaction_id'] = '2222222'
            return render_template('subscribers.html')
    debug.p('** Leaving FUNC::::::: app.route.login')
    return render_template('login.html', error=error)
    

#############################
#### SEARCH #########
#############################

@app.route('/searchRangeR')
def searchRangeR():
    debug.p('FUNC:::::: app.route.searchRangeR')
    debug.p('** Leaving FUNC:::::: app.route.searchRangeR')
    return render_template('searchRangeR.html') 

@app.route('/performSearchRangeR', methods=['POST', ])
def performSearchRangeR():
    debug.p('FUNC:::::: app.route.performSearchRangeR')
    if request.method == 'POST':
        sub = str(request.form['sub'])
        c_sub = ims.registeredRangeSubscriber(sub)
        transaction_id = session['transaction_id']
        result = c_sub.subscriberGet(session['emaSession'])
        debug.p (result.status_code)
        debug.p (result.text)

        if result.status_code == 500: #Successful EMA connection but there is an error.
            debug.p(result.text.find('35000'))
            debug.p(result.text.find('Invalid Session1001'))
            debug.p(result.text.find('No such object'))
            debug.p('##########')
            if result.text.find('Invalid Session1001') != -1:
                return render_template('/login')
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
        return render_template('/', error=error)
    debug.p('** Leaving FUNC::::::: app.route.performSearchRangeR')
    return render_template('/', error=error)


#############################
#### CREATE
#############################
@app.route('/subscriberCreate')
def subscriberCreate():
    debug.p('FUNC:::::: app.route.subscriberCreate')
    debug.p('** Leaving FUNC::::::: app.route.subscriberCreate')
    return render_template('searchRangeR.html', createmesg= 'True')

@app.route('/CreateNR/<sub>')
def createNR(sub):
    debug.p('FUNC:::::: app.route.createNR')
    cSub = ims.nonRegisteredSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    debug.p('** Leaving FUNC::::::: app.route.createNR')
    return render_template('subscribers.html', createmesg = sub)

@app.route('/CreateRangeNR/<sub>')
def createRangeNR(sub):
    debug.p('FUNC:::::: app.route.createRangeNR')
    cSub = ims.nonRegisteredRangeSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    debug.p('** Leaving FUNC::::::: app.route.createRangeNR')
    return render_template('subscribers.html', createmesg = sub)



@app.route('/CreateR/<sub>')
def createR(sub):
    debug.p('FUNC:::::: app.route.createR')
    cSub = ims.registeredSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    debug.p('** Leaving FUNC::::::: app.route.createR')
    return render_template('subscribers.html', createmesg = 'Successful Creation', newsub = sub)

@app.route('/CreateRangeR/<sub>')
def createRangeR(sub):
    debug.p('FUNC:::::: app.route.createRangeR')
    cSub = ims.registeredRangeSubscriber(sub)
    result = cSub.subscriberCreate(session['emaSession'])
    debug.p('** Leaving FUNC::::::: app.route.createRangeR')
    return render_template('subscribers.html', createmesg = sub)



@app.route('/create', methods=['POST',])
def create(subType, sub):
    # 
    # 
    template = ''
    debug.p('FUNC::::::: app.route.create')   
    if request.method == 'POST':
        cSub = session_calls.setSessionSubType(subType)

        result = cSub.subscriberCreate(session['emaSession'])

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session1001'):
                template = ('/')
            elif result.text.find('No such object'):
                template = ('searchRangeR.html')
            else: 
                pass
        elif result.status_code == 200:
            render_template('/subscribers.html', mesg = 'Successful Delete')
    else:
        template = ('error.html')
    debug.p('** Leaving FUNC::::::: app.route.create')
    return render_template(template)



#########################################################
##### DELETE
####################################################
 
@app.route('/delete', methods=['POST','GET',])
def delete():
    # 
    # 
    template = ''
    debug.p('FUNC::::::: app.route.delete')   
    if request.method == 'POST':
        debug.p(request.form['submit'])
        sub = request.form['submit']
        cSub = ims.registeredSubscriber(sub) # For a delete any Class Type can work

        result = cSub.subscriberDelete(session['emaSession'])

        if result.status_code == 500: #Successful EMA connection but there is an error.
            if result.text.find('Invalid Session1001'):
                debug.p('********Invalid Session')
                template = ('/')
            elif result.text.find('No such object'):
                debug.p('******** No Such object')
                template = ('searchRangeR.html')
            else: 
                pass
        elif result.status_code == 200:
            debug.p('** Leaving FUNC::::::: app.route.delete')
            return render_template('subscribers.html', deletemesg = 'Successful Delete')
    else:
        debug.p('** Leaving FUNC::::::: app.route.delete')
        return render_template('searchRangeR.html', deletemesg = "True")
    return


####################################
### MISC
####################################


@app.route('/subscriberResult', methods=['POST',])
def subscriberResult():
    debug.p('FUNC:::::: app.route.subscriberResult')    
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
