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
	return render_template('login.html')



@app.route('/login', methods=['POST', ])
def login():
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
    return render_template('login.html', error=error)

@app.route('/SearchNR' , methods=['POST', ])
def searchNR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  
    


@app.route('/SearchRangeNR')
def searchRangeNR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    #return "You asked for sub number  in account : " 
    return render_template('searchRangeNR.html') 

@app.route('/performSearchRangeNR', methods=['POST', ])
def performSearchRangeNR():
    debug.p('FUNC:::::: app.route.sub')
    if request.method == 'POST':
        sub = str(request.form['sub'])
        c_sub = ims.IMSSubscriber
    else:
        return render_template('/', error=error)
    return "You asked for sub number  in account : {0}   \n\n and the details are: \n".format(sub,result.text) 

@app.route('/CreateNR')
def createNR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  

@app.route('/CreateRangeNR')
def createRangeNR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  


@app.route('/DeleteNR')
def deleteNR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "

@app.route('/DeleteRangeNR')  
def deleteRangeNR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  


#########################################################

@app.route('/SearchR' , methods=['POST', ])
def searchR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  
    


@app.route('/SearchRangeR')
def searchRangeR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    #return "You asked for sub number  in account : " 
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
            session['subType'] = 'registeredRangeSubscriber'
            return render_template('subscriberResult.html', sub = sub, details = subdetails, cSub = c_sub)
            #return redirect(url_for 'subscriberResult')
    else:
        return render_template('/', error=error)
    return render_template('/', error=error)


@app.route('/CreateR/<sub>')
def createR(sub):
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : %s" %(sub)

@app.route('/CreateRangeR')
def createRangeR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  


@app.route('/DeleteR')
def deleteR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "

@app.route('/DeleteRangeR')  
def deleteRangeR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  


####################################################



@app.route('/subscriberResult', methods=['POST',])
def subscriberResult():
    debug.p('FUNC:::::: app.route.subscriberResult')    
    if request.method == 'POST':
        for k,v in request.method.items():
            print k, v
    return "You asked for sub number %s in account : %s " %((sub_no), (account))


 
@app.route('/delete', methods=['POST',])
def delete():
    # 
    # 
    template = ''
    debug.p('FUNC::::::: app.route.delete')   
    if request.method == 'POST':
        cSub = session_calls.checkSessionSubType(session)

        result = cSub.subscriberDelete(session['emaSession'])

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
    return render_template(template)

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
    return render_template(template)


# Below this point the filters are stored    

@app.template_filter('rsplit')
def get_id_filter(data):
    if data:
        return data.rsplit('/')[-1]
    else:
        return



if __name__ == "__main__":
    app.run(debug =True, port= 4500)

