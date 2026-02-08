from app import app, db, Membro

with app.app_context():
    user = Membro.query.get(1) # Jakson William
    if user:
        print(f"Atualizando usuário: {user.nome}")
        print(f"Antes: Tipo={user.tipo}, Geracao={user.geracao_id}")
        
        user.tipo = 'LiderGeracao'
        user.geracao_id = 1
        
        db.session.commit()
        print(f"Depois: Tipo={user.tipo}, Geracao={user.geracao_id}")
        print("Sucesso!")
    else:
        print("Usuário ID 1 não encontrado.")
