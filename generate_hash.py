import bcrypt
mot_de_passe = "123456789"
hash = bcrypt.hashpw(mot_de_passe.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
print(hash)