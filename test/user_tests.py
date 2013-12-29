import os, sys
sys.path.append(os.path.abspath('../lib/userapp/'))

import userapp

def normal_user(app_id, login, password):
    """
    Example #1: A normal user logging in.  You can tell because the API
                token isn't set until we get it back from user_login().
    """

    api = userapp.API(app_id=app_id, debug=True)

    # Login our user
    results = api.user.login(login=login, password=password)

    token = results.token
    user_id = results.user_id
    lock_type = results.lock_type

    api.get_logger().debug("token={t}, user_id={u}, lock_type={l}".format(t=token, u=user_id, l=lock_type))

    # Retrieve the details for the logged in user.
    myself = api.user.get()

    # This will result in a count of 0, because a normal user doesn't
    # have access to see this sort of thing.
    count = api.user.count()

    api.user.logout()

def admin_user(app_id, token):
    """
    Example #2: An admin logging in.  You can tell because we set the
                API token when we create the instance.
    """

    api = userapp.API(app_id=app_id, token=token, debug=True)

    # Get a count of all the users registered under this app ID.
    count = api.user.count()

    # Retrieve a list of all the users under this app ID.
    results = api.user.search()
    user_list = results.items
 
    # Retrieve the details for three users from the user list.
    results = api.user.get(user_id = [
        user_list[0].user_id,
        user_list[1].user_id,
        user_list[2].user_id
    ])

    # Test the nested Services
    results = api.user.invoice.search()
    results = api.user.paymentMethod.search()

normal_user(app_id='APP ID', login='MY USERNAME', password='MY PASSWORD')
admin_user(app_id='APP ID', token='GENERATED USER TOKEN')