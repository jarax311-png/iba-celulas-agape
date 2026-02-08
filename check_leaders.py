from app import app, Membro

with app.app_context():
    print("-" * 80)
    print(f"{'ID':<5} | {'Nome':<20} | {'Tipo':<15} | {'Célula':<8} | {'Rede':<8} | {'Geração':<8}")
    print("-" * 80)
    
    # Busca todos os usuários, mas destaca os líderes
    membros = Membro.query.all()
    
    for m in membros:
        # Se for algum tipo de líder ou admin, ou se tiver rede/geração vinculada
        if 'Lider' in m.tipo or m.tipo == 'Admin' or m.rede_id or m.geracao_id:
            print(f"{m.id:<5} | {m.nome[:20]:<20} | {m.tipo:<15} | {str(m.celula_id):<8} | {str(m.rede_id):<8} | {str(m.geracao_id):<8}")
    
    print("-" * 80)
