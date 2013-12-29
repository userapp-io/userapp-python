import config, userapp

api = userapp.API(app_id=config.USERAPP_APP_ID)

try:
	user_result = api.user.save(login="epicrawbot", email="epicrobot@userapp.io", password="play_withBitz!")
	print("Saved new user {l} with user id {i}.".format(l=user_result.login, i=user_result.user_id))
except userapp.UserAppServiceException as e:
	print("An error occurred: {m} ({c}).".format(m=e.message, c=e.error_code))