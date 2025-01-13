from cryptography.fernet import Fernet

f = Fernet('pe5crkWiPHzJ1EeVRtRSZscLF5bRsHBXCfKxLCsEnfI=')

print(f.encrypt(b'Programmer_smlg').decode())
print(f.encrypt(b'I3uta5r12X').decode())
print(f.encrypt(b'Programmer_msk').decode())
print(f.encrypt(b'9q5yRnEq93').decode())

