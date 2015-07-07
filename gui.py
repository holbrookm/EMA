import sys
from flask import request,  Flask, render_template, url_for, redirect, flash, session
import os
#from cie_connect import cie_connect, perform_cie_logon
import debug
import class_ims_ema as ims
import emaConnect


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
	return render_template('mylogin.html')



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
            if debug.mac :
                pass
            else:
                session['emaSession'] = emaConnect.emaLogin()
                session['transaction_id'] = '2222222'
            return render_template('subscribers.html')
            #return redirect(url_for('suscribers'))
    return render_template('mylogin.html', error=error)

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
    return "You asked for sub number  in account : {0}".format(sub) 

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
    debug.p('FUNC:::::: app.route.sub')
    if request.method == 'POST':
        sub = str(request.form['sub'])
        c_sub = ims.registeredRangeSubscriber(sub)
        transaction_id = session['transaction_id']
        result = c_sub.subscriberGet(session['emaSession'])

        print result0.status_code

    else:
        return render_template('/', error=error)
    return "You asked for sub number  in account : {0}".format(sub) 

@app.route('/CreateR')
def createR():
    debug.p('FUNC:::::: app.route.show_sub_account')
    return "You asked for sub number  in account : "  

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



@app.route('/accounts/<account>/subscriptions/<sub_no>')
def show_sub_details(account, sub_no):
    debug.p('FUNC:::::: app.route.show_sub_details')    
    return "You asked for sub number %s in account : %s " %((sub_no), (account))




 
@app.route('/subscribers', methods=['POST',])
def subscribers():
    # accounts list will be a list of accounts under the HOME account
    # it contains parent, id, uid and href of the accounts
    debug.p('FUNC:::::: app.route.subscribers')
    flash(u'You were logged in', 'success')   
 
    return render_template('subscribers.html')



# Below this point the filters are stored    

@app.template_filter('rsplit')
def get_id_filter(data):
    if data:
        return data.rsplit('/')[-1]
    else:
        return



if __name__ == "__main__":
    app.run(debug =True, port= 4500)

