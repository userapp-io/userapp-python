import config, userapp

api = userapp.API(app_id=config.USERAPP_APP_ID, debug=True, throw_errors=False)

user_result = api.user.login(login="epicrawbot", password="play_withBitz!")