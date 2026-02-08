
from app import app, db, Membro

with app.app_context():
    admins = Membro.query.filter(Membro.tipo.in_(['Admin', 'Lider', 'LiderRede', 'LiderGeracao'])).all()
    print(f"Encontrados {len(admins)} usuários com permissão de acesso ao painel admin:")
    for a in admins:
        print(f"ID: {a.id} | Nome: {a.nome} | Email: {a.email} | Senha: {a.senha} | Tipo: {a.tipo}")
