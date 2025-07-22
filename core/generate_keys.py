import bcrypt

password = b"sua_senha" # Use a sua senha aqui
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed_password.decode())