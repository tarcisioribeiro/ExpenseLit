from functions.login import User

call_user = User()

user_name, user_document, user_phone = call_user.get_doc_name()
not_used_name, user_sex = call_user.check_user()