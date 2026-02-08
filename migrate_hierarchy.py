from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        # Create new tables
        db.create_all()
        print("Tabelas Rede e Geracao verificadas/criadas.")

        # Add columns to Celula if they don't exist
        with db.engine.connect() as conn:
            # Check if columns exist
            columns = conn.execute(text("PRAGMA table_info(celula)")).fetchall()
            col_names = [c[1] for c in columns]
            
            if 'rede_id' not in col_names:
                print("Adicionando coluna rede_id em Celula...")
                conn.execute(text("ALTER TABLE celula ADD COLUMN rede_id INTEGER REFERENCES rede(id)"))
            
            if 'geracao_id' not in col_names:
                print("Adicionando coluna geracao_id em Celula...")
                conn.execute(text("ALTER TABLE celula ADD COLUMN geracao_id INTEGER REFERENCES geracao(id)"))

            if 'lider_treinamento' not in col_names:
                print("Adicionando coluna lider_treinamento em Celula...")
                conn.execute(text("ALTER TABLE celula ADD COLUMN lider_treinamento VARCHAR(100)"))

            # Rename old rede column to rede_legacy/rede_str is harder in SQLite
            # We will just ignore the old column or rely on the mapping in the model
            
            conn.commit()
            print("Migração concluída.")

if __name__ == '__main__':
    migrate()
