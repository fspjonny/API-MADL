import secrets

# Gera uma chave de vários comprimentos: 32, 64, 256, etc...
secret_key = secrets.token_hex(64)
print(f'COPIE E COLE SUA CHAVE(sem os colchetes):\n[{secret_key}]')
