from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Tenta adicionar a coluna. Se der erro, provavelmente já existe.
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE celula ADD COLUMN rede VARCHAR(50)"))
            conn.commit()
            print("Coluna 'rede' adicionada com sucesso!")
    except Exception as e:
        print(f"Erro (talvez a coluna ja exista): {e}")
