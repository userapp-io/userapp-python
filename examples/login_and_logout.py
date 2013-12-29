import config, userapp

api = userapp.API(app_id=config.USERAPP_APP_ID)

try:
	login_result = api.user.login(login="jdoe81", password="joelikesfishi_g")

	print("Authenticated using token {t} and user id {i}.".format(t=login_result.token, i=login_result.user_id))

	user = api.user.get()[0]

	print("Authenticated as user {u}, first name = {f}, last name = {l}, email = {e}.".format(u=user.login, f=user.first_name, l=user.last_name, e=user.email))

	api.user.logout()

	user_result = api.user.save(login="epicrawbot", email="epicrobot@userapp.io", password="play_withBitz!")

	print("Saved new user {l} with user id {i}.".format(l=user_result.login, i=user_result.user_id))
except userapp.UserAppServiceException as e:
	print("An error occurred: {m} ({c}).".format(m=e.message, c=e.error_code))