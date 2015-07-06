import emaConnect
import class_ims_ema as ims
import debug

session = emaConnect.emaLogin()


e1 = ims.nonRegisteredSubscriber('353766875262')


transaction_id = 24424424424


result0 = e1.subscriberGet(session)

print result0.status_code


result = e1.subscriberCreate(session)
print result.status_code

result2 = e1.subscriberDelete(session)
print result2.status_code


emaConnect.emaLogout(session)
