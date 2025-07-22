import bcrypt

password = b"forms123" # Use a sua senha aqui
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
print(hashed_password.decode())