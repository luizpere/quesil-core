import bcrypt

# Assumindo que 'senha' é a string bruta do usuário
senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pessoa_id INTEGER NOT NULL,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0,
        notificacoes INTEGER DEFAULT 1,
        FOREIGN KEY (pessoa_id) REFERENCES pessoas(id)
    )
''')

# Adicionar índice para pessoa_id se não existir
cursor.execute('CREATE INDEX IF NOT EXISTS idx_usuarios_pessoa_id ON usuarios(pessoa_id)')

# Exemplo de inserção segura com placeholder
cursor.execute('''
    INSERT INTO usuarios (pessoa_id, email, senha, is_admin, notificacoes)
    VALUES (?, ?, ?, ?, ?)
''', (pessoa_id, email, senha_hash.decode('utf-8'), is_admin, notificacoes))