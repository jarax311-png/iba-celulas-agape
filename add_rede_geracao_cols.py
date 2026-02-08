from app import app, db
from sqlalchemy import text

with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE membro ADD COLUMN rede_id INTEGER REFERENCES rede(id)"))
            print("Coluna rede_id adicionada.")
        except Exception as e:
            print(f"Erro ao adicionar rede_id (pode já existir): {e}")

        try:
            conn.execute(text("ALTER TABLE membro ADD COLUMN geracao_id INTEGER REFERENCES geracao(id)"))
            print("Coluna geracao_id adicionada.")
        except Exception as e:
            print(f"Erro ao adicionar geracao_id (pode já existir): {e}")
            
        conn.commit()
