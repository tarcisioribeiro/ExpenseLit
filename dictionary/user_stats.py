from functions.login import User

user_name, user_document, user_phone = User().get_user_doc_name()
not_used_name, user_sex = User().check_user()
