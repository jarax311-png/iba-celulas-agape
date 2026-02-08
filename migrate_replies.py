from app import app, db
from sqlalchemy import text

with app.app_context():
    # 1. Cria tabela CurtidaComentario se não existir
    db.create_all()
    print("Tabelas base verificadas.")

    # 2. Tenta adicionar coluna parent_id na tabela comentario (se não existir)
    # SQLite não tem "IF NOT EXISTS" para colunas em versões antigas, mas vamos tentar
    try:
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE comentario ADD COLUMN parent_id INTEGER REFERENCES comentario(id)"))
            conn.commit()
        print("Coluna parent_id adicionada com sucesso!")
    except Exception as e:
        print(f"Nota: Coluna parent_id provavelmente já existe ou erro: {e}")
