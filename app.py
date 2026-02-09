import os
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Habilita CORS para qualquer origem (necessário para rodar client.html localmente)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configuração de Upload
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database Config - Supports SQLite (local) and PostgreSQL (production)
database_url = os.environ.get('DATABASE_URL', 'sqlite:///igreja.db')
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Auto-create tables if they don't exist (Production Friendly)
with app.app_context():
    db.create_all()

# Rota para servir imagens de upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rota para servir imagens estáticas gerais (logo, etc)
@app.route('/imagens/<path:filename>')
def serve_imagens(filename):
    return send_from_directory(os.path.join(os.getcwd(), 'imagens'), filename)

# Rotas do Frontend
@app.route('/')
def serve_client():
    return send_from_directory(os.getcwd(), 'client.html')

@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.getcwd(), 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.getcwd(), 'sw.js')

@app.route('/app_icon.png')
def serve_app_icon():
    return send_from_directory(os.getcwd(), 'app_icon.png')

@app.route('/admin')
def serve_admin():
    return send_from_directory(os.getcwd(), 'admin.html')

# --- MODELOS DO BANCO DE DADOS ---

class Rede(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    lider_nome = db.Column(db.String(100))
    lider_telefone = db.Column(db.String(20))
    
    # Relacionamento com Gerações
    geracoes = db.relationship('Geracao', backref='rede', lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "lider_nome": self.lider_nome,
            "lider_telefone": self.lider_telefone
        }

class Geracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    rede_id = db.Column(db.Integer, db.ForeignKey('rede.id'), nullable=True)
    lider_nome = db.Column(db.String(100))
    lider_telefone = db.Column(db.String(20))
    
    # Relacionamento com Células
    celulas = db.relationship('Celula', backref='geracao', lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "rede_id": self.rede_id,
            "lider_nome": self.lider_nome,
            "lider_telefone": self.lider_telefone,
            "rede_nome": self.rede.nome if self.rede else None,
            "celulas": [{
                "id": c.id,
                "nome": c.nome,
                "lider": c.lider,
                "total_membros": len(c.membros)
            } for c in self.celulas]
        }

class Celula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    lider = db.Column(db.String(100))
    lider_treinamento = db.Column(db.String(100)) # Novo campo
    
    # Hierarquia
    rede_id = db.Column(db.Integer, db.ForeignKey('rede.id'), nullable=True)
    geracao_id = db.Column(db.Integer, db.ForeignKey('geracao.id'), nullable=True)
    rede_str = db.Column("rede", db.String(100)) 
    
    # Relacionamento explícito com Rede (para evitar conflito com coluna 'rede')
    rede_obj = db.relationship('Rede', backref='celulas_da_rede', lazy=True)

    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))     # UF
    cep = db.Column(db.String(10))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    dia_reuniao = db.Column(db.String(50))
    horario_reuniao = db.Column(db.String(50))
    
    # Relacionamentos
    membros = db.relationship('Membro', backref='celula', lazy=True)
    reunioes = db.relationship('Reuniao', backref='celula', lazy=True)

    def to_json(self):
        membros_objs = Membro.query.filter_by(celula_id=self.id).all()
        return {
            "id": self.id, 
            "nome": self.nome, 
            "lider": self.lider,
            "lider_treinamento": self.lider_treinamento,
            "rede": self.rede_obj.nome if self.rede_obj else (self.rede_str or "Sem Rede"),
            "rede_id": self.rede_id,
            "geracao": self.geracao.nome if self.geracao else "Sem Geração",
            "geracao_id": self.geracao_id,
            "endereco": self.endereco,
            "numero": self.numero,
            "bairro": self.bairro,
            "cidade": self.cidade,
            "estado": self.estado,
            "cep": self.cep,
            "formatted_address": f"{self.endereco}, {self.numero} - {self.bairro}, {self.cidade}/{self.estado}",
            "latitude": self.latitude,
            "longitude": self.longitude,
            "dia_reuniao": self.dia_reuniao,
            "horario_reuniao": self.horario_reuniao,
            "membros": [m.to_json() for m in membros_objs]
        }

class Membro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    # Permite membro sem célula (nullable=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celula.id'), nullable=True)
    
    # Campos expandidos para gestão de pessoas
    telefone = db.Column(db.String(20))
    data_nascimento = db.Column(db.Date) # YYYY-MM-DD
    endereco = db.Column(db.String(200))
    numero = db.Column(db.String(20))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    tipo = db.Column(db.String(20), default='Membro') # Membro, Visitante
    
    # Hierarquia (Para LiderRede e LiderGeracao)
    rede_id = db.Column(db.Integer, db.ForeignKey('rede.id'), nullable=True)
    geracao_id = db.Column(db.Integer, db.ForeignKey('geracao.id'), nullable=True)
    data_conversao = db.Column(db.Date)
    
    # Autenticação
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(100)) # Em produção, usar hash!
    
    # Campo novo: Encontro com Deus
    fez_encontro = db.Column(db.Boolean, default=False)

    # Novos Campos: Biografia e Foto
    biografia = db.Column(db.String(500))
    foto_url = db.Column(db.String(200))
    
    def to_json(self):
        return {
            "id": self.id, 
            "nome": self.nome, 
            "celula_id": self.celula_id,
            "rede_id": self.rede_id,
            "geracao_id": self.geracao_id,
            "telefone": self.telefone,
            "data_nascimento": self.data_nascimento.isoformat() if self.data_nascimento else None,
            "endereco": self.endereco,
            "tipo": self.tipo,
            "data_conversao": self.data_conversao.isoformat() if self.data_conversao else None,
            "email": self.email,
            "fez_encontro": self.fez_encontro,
            "biografia": self.biografia,
            "foto_url": self.foto_url
        }

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    data_evento = db.Column(db.DateTime) 
    local = db.Column(db.String(200))
    foto_url = db.Column(db.String(200))

    # Relacionamentos
    curtidas = db.relationship('Curtida', backref='evento', lazy=True)
    comentarios = db.relationship('Comentario', backref='evento', lazy=True)

    def to_json(self, current_user_id=None):
        data = {
            "id": self.id,
            "titulo": self.titulo,
            "descricao": self.descricao,
            "data_evento": self.data_evento.isoformat() if self.data_evento else None,
            "local": self.local,
            "foto_url": self.foto_url,
            "total_curtidas": len(self.curtidas),
            "total_comentarios": len(self.comentarios)
        }
        if current_user_id:
            msg_curtida = next((c for c in self.curtidas if c.membro_id == current_user_id), None)
            data["curtido_por_mim"] = True if msg_curtida else False
        return data

class Curtida(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=True)
    aviso_id = db.Column(db.Integer, db.ForeignKey('aviso.id'), nullable=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(500), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=True)
    aviso_id = db.Column(db.Integer, db.ForeignKey('aviso.id'), nullable=True)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)
    
    # Campo para respostas (aninhamento)
    parent_id = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=True)
    respostas = db.relationship('Comentario', backref=db.backref('parent', remote_side=[id]), lazy=True)

    # Relacionamento para acessar dados do autor
    autor = db.relationship('Membro', backref='meus_comentarios', lazy=True)
    curtidas = db.relationship('CurtidaComentario', backref='comentario', lazy=True)

    def to_json(self, current_user_id=None):
        data = {
            "id": self.id,
            "texto": self.texto,
            "data": self.data_criacao.strftime('%d/%m %H:%M'),
            "autor_nome": self.autor.nome,
            "autor_foto": self.autor.foto_url,
            "total_curtidas": len(self.curtidas),
            "respostas": [r.to_json(current_user_id) for r in self.respostas]
        }
        if current_user_id:
             msg_curtida = next((c for c in self.curtidas if c.membro_id == current_user_id), None)
             data["curtido_por_mim"] = True if msg_curtida else False
        return data

class CurtidaComentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comentario_id = db.Column(db.Integer, db.ForeignKey('comentario.id'), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    foto_url = db.Column(db.String(200), nullable=False)
    legenda = db.Column(db.String(100))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    expira_em = db.Column(db.DateTime) 
    
    # Novos campos para gestão
    autor_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celula.id'), nullable=True)
    rede_id = db.Column(db.Integer, db.ForeignKey('rede.id'), nullable=True)
    geracao_id = db.Column(db.Integer, db.ForeignKey('geracao.id'), nullable=True)
    
    autor = db.relationship('Membro', backref='meus_stories')

    def to_json(self):
        return {
            "id": self.id,
            "foto_url": self.foto_url,
            "legenda": self.legenda,
            "criado_em": self.criado_em.isoformat(),
            "autor_id": self.autor_id,
            "autor_nome": self.autor.nome if self.autor else "Admin",
            "celula_id": self.celula_id,
            "rede_id": self.rede_id,
            "geracao_id": self.geracao_id
        }

class Aviso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celula.id'), nullable=True) # Agora opcional
    rede_id = db.Column(db.Integer, db.ForeignKey('rede.id'), nullable=True)     # Novo
    geracao_id = db.Column(db.Integer, db.ForeignKey('geracao.id'), nullable=True) # Novo
    
    titulo = db.Column(db.String(100), nullable=False)
    mensagem = db.Column(db.String(500), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    autor_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)
    
    autor = db.relationship('Membro', backref='avisos_criados')
    curtidas = db.relationship('Curtida', backref='aviso', lazy=True)
    comentarios = db.relationship('Comentario', backref='aviso', lazy=True)

    def to_json(self, current_user_id=None):
        data = {
            "id": self.id,
            "titulo": self.titulo,
            "mensagem": self.mensagem,
            "data": self.data_criacao.strftime('%d/%m %H:%M'),
            "autor_id": self.autor_id,
            "autor_nome": self.autor.nome,
            "celula_id": self.celula_id,
            "rede_id": self.rede_id,
            "geracao_id": self.geracao_id,
            "total_curtidas": len(self.curtidas),
            "total_comentarios": len(self.comentarios)
        }
        if current_user_id:
            msg_curtida = next((c for c in self.curtidas if c.membro_id == current_user_id), None)
            data["curtido_por_mim"] = True if msg_curtida else False
        return data

class PedidoOracao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celula.id'), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)
    pedido = db.Column(db.String(500), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    resolvido = db.Column(db.Boolean, default=False)
    
    autor = db.relationship('Membro', backref='meus_pedidos')

    def to_json(self):
        return {
            "id": self.id,
            "pedido": self.pedido,
            "data": self.data_criacao.strftime('%d/%m %H:%M'),
            "autor_nome": self.autor.nome,
            "autor_foto": self.autor.foto_url,
            "resolvido": self.resolvido
        }

class Testemunho(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celula.id'), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)
    texto = db.Column(db.String(1000), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    autor = db.relationship('Membro', backref='meus_testemunhos')
    
    def to_json(self):
        return {
            "id": self.id,
            "texto": self.texto,
            "data": self.data_criacao.strftime('%d/%m %H:%M'),
            "autor_nome": self.autor.nome,
            "autor_foto": self.autor.foto_url
        }
class Escola(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(500))
    foto_url = db.Column(db.String(200))
    dia_horario = db.Column(db.String(100))
    
    def to_json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "descricao": self.descricao,
            "foto_url": self.foto_url,
            "dia_horario": self.dia_horario
        }

class Reuniao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    celula_id = db.Column(db.Integer, db.ForeignKey('celula.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    tema = db.Column(db.String(100))
    observacoes = db.Column(db.Text)
    
    # Relacionamento com frequencia
    frequencias = db.relationship('Frequencia', backref='reuniao', lazy=True)

    def to_json(self):
        return {
            "id": self.id,
            "celula_id": self.celula_id,
            "data": self.data.isoformat(),
            "tema": self.tema,
            "observacoes": self.observacoes
        }

class Frequencia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reuniao_id = db.Column(db.Integer, db.ForeignKey('reuniao.id'), nullable=False)
    membro_id = db.Column(db.Integer, db.ForeignKey('membro.id'), nullable=False)
    presente = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            "reuniao_id": self.reuniao_id,
            "membro_id": self.membro_id,
            "presente": self.presente
        }

class Estudo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    conteudo_link = db.Column(db.String(200)) # Link para PDF ou texto
    data_publicacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_json(self):
        return {
            "id": self.id,
            "titulo": self.titulo,
            "conteudo_link": self.conteudo_link,
            "data_publicacao": self.data_publicacao.isoformat()
        }

# --- ROTAS DA API ---

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')
    
    user = Membro.query.filter_by(email=email).first()
    
    if user and user.senha == senha:
        return jsonify({
            "mensagem": "Login realizado com sucesso",
            "usuario": user.to_json()
        })
        
    return jsonify({"erro": "Credenciais invalidas"}), 401

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        print(f"Tentativa de cadastro: {data}") # Debug output

        if Membro.query.filter_by(email=data['email']).first():
            return jsonify({"erro": "Email ja cadastrado"}), 400

        # Tratamento de data
        dt_nasc = None
        if data.get('data_nascimento'):
            try:
                dt_nasc = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            except ValueError:
                pass # Mantém None se data inválida

        cel_id = None
        cel_input = data.get('celula_id')
        
        if cel_input and str(cel_input).strip():
             if str(cel_input).isdigit():
                 cel_id = int(cel_input)
                 # Verifica se célula existe
                 if not Celula.query.get(cel_id):
                      return jsonify({"erro": f"Célula {cel_id} não encontrada. Deixe em branco se não tiver."}), 400
             else:
                 return jsonify({"erro": "ID da Célula deve ser numérico"}), 400
            
        # Determina tipo de usuario pelo codigo VIP
        tipo_usuario = 'Membro'
        codigo = data.get('codigo_vip', '').upper().strip()
        
        if codigo == 'LIDER12':
            tipo_usuario = 'Lider'
        elif codigo == 'REDE12':
            tipo_usuario = 'LiderRede'
        elif codigo == 'GERACAO12':
            tipo_usuario = 'LiderGeracao'
        elif codigo == 'ADMIN12': # Backdoor de conveniencia
            tipo_usuario = 'Admin'

        # Tratamento de Rede e Geração (opcional)
        rede_id = None
        if data.get('rede_id') and str(data.get('rede_id')).isdigit():
            rede_id = int(data['rede_id'])
            
        geracao_id = None
        if data.get('geracao_id') and str(data.get('geracao_id')).isdigit():
            geracao_id = int(data['geracao_id'])

        novo = Membro(
            nome=data['nome'], 
            celula_id=cel_id, # Pode ser None
            rede_id=rede_id,
            geracao_id=geracao_id,
            telefone=data.get('telefone'),
            data_nascimento=dt_nasc,
            email=data['email'],
            senha=data['senha'],
            tipo=tipo_usuario,
            fez_encontro=data.get('fez_encontro', False),
            endereco=data.get('endereco'),
            numero=data.get('numero'),
            bairro=data.get('bairro'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            cep=data.get('cep')
        )
        db.session.add(novo)
        db.session.commit()
        
        return jsonify(novo.to_json()), 201
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/api/meus-dados/<int:id>')
def menus_dados(id):
    user = Membro.query.get(id)
    if not user:
        return jsonify({"erro": "Usuario nao encontrado"}), 404
        
    # Busca dados da célula, rede ou geração do usuário
    celula = Celula.query.get(user.celula_id) if user.celula_id else None
    rede = Rede.query.get(user.rede_id) if user.rede_id else None
    geracao = Geracao.query.get(user.geracao_id) if user.geracao_id else None
    
    return jsonify({
        "usuario": user.to_json(),
        "celula": celula.to_json() if celula else None,
        "rede": rede.to_json() if rede else None,
        "geracao": geracao.to_json() if geracao else None
    })

@app.route('/api/eventos', methods=['GET'])
def get_eventos():
    eventos = Evento.query.order_by(Evento.data_evento).all()
    # Tenta pegar ID do usuário do header para checar likes
    user_id = request.headers.get('User-Id')
    try:
        user_id = int(user_id) if user_id else None
    except:
        user_id = None
        
    return jsonify([e.to_json(current_user_id=user_id) for e in eventos])

@app.route('/api/eventos/<int:evento_id>/curtir', methods=['POST'])
def curtir_evento(evento_id):
    data = request.json
    membro_id = data.get('membro_id')
    
    if not membro_id:
        return jsonify({"error": "Membro ID obrigatório"}), 400

    curtida = Curtida.query.filter_by(evento_id=evento_id, membro_id=membro_id).first()
    
    if curtida:
        db.session.delete(curtida)
        action = "descurtiu"
    else:
        nova_curtida = Curtida(evento_id=evento_id, membro_id=membro_id)
        db.session.add(nova_curtida)
        action = "curtiu"
    
    db.session.commit()
    
    # Retorna contagem atualizada
    total = Curtida.query.filter_by(evento_id=evento_id).count()
    return jsonify({"action": action, "total": total})

@app.route('/api/eventos/<int:evento_id>/comentar', methods=['POST'])
def comentar_evento(evento_id):
    data = request.json
    membro_id = data.get('membro_id')
    texto = data.get('texto')
    
    if not membro_id or not texto:
        return jsonify({"error": "Dados incompletos"}), 400
        
    novo_comentario = Comentario(evento_id=evento_id, membro_id=membro_id, texto=texto)
    db.session.add(novo_comentario)
    db.session.commit()
    
    return jsonify(novo_comentario.to_json())

@app.route('/api/eventos/<int:evento_id>/comentarios', methods=['GET'])
def get_comentarios(evento_id):
    # Retorna apenas comentários RAIZ (sem pai)
    comentarios = Comentario.query.filter_by(evento_id=evento_id, parent_id=None).order_by(Comentario.data_criacao.desc()).all()
    
    user_id = request.headers.get('User-Id')
    try: user_id = int(user_id) if user_id else None
    except: user_id = None

    return jsonify([c.to_json(current_user_id=user_id) for c in comentarios])

    db.session.commit()
    
    # Retorna contagem atualizada
    total = CurtidaComentario.query.filter_by(comentario_id=comentario_id).count()
    return jsonify({"action": action, "total": total})

# --- INTERAÇÕES NO MURAL (AVISOS) ---

@app.route('/api/avisos/<int:aviso_id>/curtir', methods=['POST'])
def curtir_aviso(aviso_id):
    data = request.json
    membro_id = data.get('membro_id')
    
    if not membro_id:
        return jsonify({"error": "Membro ID obrigatório"}), 400

    curtida = Curtida.query.filter_by(aviso_id=aviso_id, membro_id=membro_id).first()
    
    if curtida:
        db.session.delete(curtida)
        action = "descurtiu"
    else:
        nova_curtida = Curtida(aviso_id=aviso_id, membro_id=membro_id)
        db.session.add(nova_curtida)
        action = "curtiu"
    
    db.session.commit()
    
    total = Curtida.query.filter_by(aviso_id=aviso_id).count()
    return jsonify({"action": action, "total": total})

@app.route('/api/avisos/<int:aviso_id>/comentar', methods=['POST'])
def comentar_aviso(aviso_id):
    data = request.json
    membro_id = data.get('membro_id')
    texto = data.get('texto')
    
    if not membro_id or not texto:
        return jsonify({"error": "Dados incompletos"}), 400
        
    novo_comentario = Comentario(aviso_id=aviso_id, membro_id=membro_id, texto=texto)
    db.session.add(novo_comentario)
    db.session.commit()
    
    return jsonify(novo_comentario.to_json())

@app.route('/api/avisos/<int:aviso_id>/comentarios', methods=['GET'])
def get_comentarios_aviso(aviso_id):
    comentarios = Comentario.query.filter_by(aviso_id=aviso_id, parent_id=None).order_by(Comentario.data_criacao.desc()).all()
    
    user_id = request.headers.get('User-Id')
    try: user_id = int(user_id) if user_id else None
    except: user_id = None

    return jsonify([c.to_json(current_user_id=user_id) for c in comentarios])

@app.route('/api/comentarios/<int:comentario_id>/curtir', methods=['POST'])
def curtir_comentario(comentario_id):
    data = request.json
    membro_id = data.get('membro_id')
    
    if not membro_id:
        return jsonify({"error": "Membro ID obrigatório"}), 400

    curtida = CurtidaComentario.query.filter_by(comentario_id=comentario_id, membro_id=membro_id).first()
    
    if curtida:
        db.session.delete(curtida)
        action = "descurtiu"
    else:
        nova_curtida = CurtidaComentario(comentario_id=comentario_id, membro_id=membro_id)
        db.session.add(nova_curtida)
        action = "curtiu"
    
    db.session.commit()
    
    # Retorna contagem atualizada
    total = CurtidaComentario.query.filter_by(comentario_id=comentario_id).count()
    return jsonify({"action": action, "total": total})
    return jsonify({"action": action, "total": total})

@app.route('/api/comentarios/<int:comentario_id>/responder', methods=['POST'])
def responder_comentario(comentario_id):
    data = request.json
    membro_id = data.get('membro_id')
    texto = data.get('texto')
    
    if not membro_id or not texto:
        return jsonify({"error": "Dados incompletos"}), 400

    parent = Comentario.query.get(comentario_id)
    if not parent:
        return jsonify({"error": "Comentario pai nao encontrado"}), 404

    nova_resposta = Comentario(
        evento_id=parent.evento_id, # Mesmo evento do pai
        membro_id=membro_id, 
        texto=texto,
        parent_id=comentario_id
    )
    db.session.add(nova_resposta)
    db.session.commit()
    
    return jsonify(nova_resposta.to_json())



@app.route('/api/membros/sem-celula', methods=['GET'])
def get_sem_celula():
    membros = Membro.query.filter_by(celula_id=None).all()
    return jsonify([m.to_json() for m in membros])

@app.route('/api/membros', methods=['GET', 'POST'])
def handle_membros():
    if request.method == 'GET':
        membros = Membro.query.all()
        return jsonify([m.to_json() for m in membros])
    
    if request.method == 'POST':
        # Mantendo para compatibilidade, mas ideal usar /api/register
        data = request.json
        dt_nasc = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if 'data_nascimento' in data else None
        
        # Lógica de Código de Honra / VIP
        tipo_usuario = 'Membro'
        codigo = data.get('codigo_vip', '').upper().strip()
        
        if codigo == 'LIDER12':
            tipo_usuario = 'Lider'
        elif codigo == 'REDE12':
            tipo_usuario = 'LiderRede'
        
        novo = Membro(
            nome=data['nome'], 
            celula_id=data['celula_id'],
            telefone=data.get('telefone'),
            data_nascimento=dt_nasc,
            endereco=data.get('endereco'),
            tipo=data.get('tipo', tipo_usuario), # Prioriza o calculado via código, mas mantém fallback
            email=data.get('email'),
            senha=data.get('senha'),
            fez_encontro=data.get('fez_encontro', False)
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_json()), 201

@app.route('/api/membros/<int:id>', methods=['PUT'])
def update_membro(id):
    membro = Membro.query.get(id)
    if not membro:
        return jsonify({"erro": "Membro nao encontrado"}), 404
    
    data = request.json
    if 'celula_id' in data:
        membro.celula_id = data['celula_id']
    
    if 'tipo_usuario' in data:
        membro.tipo_usuario = data['tipo_usuario']
        
    db.session.commit()
    return jsonify(membro.to_json())

@app.route('/api/membros/<int:id>', methods=['DELETE'])
def delete_membro(id):
    membro = Membro.query.get(id)
    if not membro:
        return jsonify({"erro": "Membro nao encontrado"}), 404
    
    try:
        # Remover dependências para evitar erro de integridade
        # 1. Curtidas em eventos
        Curtida.query.filter_by(membro_id=id).delete()
        
        # 2. Curtidas em comentários
        CurtidaComentario.query.filter_by(membro_id=id).delete()
        
        # 3. Comentários (e suas dependências: respostas e curtidas neles)
        user_comments = Comentario.query.filter_by(membro_id=id).all()
        for c in user_comments:
            # Deleta curtidas neste comentário
            CurtidaComentario.query.filter_by(comentario_id=c.id).delete()
            # Deleta respostas a este comentário (recursivo simples)
            Comentario.query.filter_by(parent_id=c.id).delete()
            # Deleta o próprio comentário
            db.session.delete(c)
            
        # 4. Frequencias
        Frequencia.query.filter_by(membro_id=id).delete()

        # 5. Avisos (se for líder)
        Aviso.query.filter_by(autor_id=id).delete()

        # 6. Pedidos de Oração
        PedidoOracao.query.filter_by(membro_id=id).delete()

        # 7. Testemunhos
        Testemunho.query.filter_by(membro_id=id).delete()

        # 8. Finalmente, deleta o membro
        db.session.delete(membro)
        db.session.commit()
        return jsonify({"mensagem": "Membro excluído com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir membro: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/api/redes', methods=['GET', 'POST'])
def handle_redes():
    if request.method == 'GET':
        redes = Rede.query.all()
        return jsonify([r.to_json() for r in redes])
    
    if request.method == 'POST':
        data = request.json
        nova = Rede(
            nome=data['nome'],
            lider_nome=data.get('lider_nome'),
            lider_telefone=data.get('lider_telefone')
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify(nova.to_json()), 201

@app.route('/api/geracoes', methods=['GET', 'POST'])
def handle_geracoes():
    if request.method == 'GET':
        rede_id = request.args.get('rede_id')
        if rede_id:
            geracoes = Geracao.query.filter_by(rede_id=rede_id).all()
        else:
            geracoes = Geracao.query.all()
        return jsonify([g.to_json() for g in geracoes])
    
    if request.method == 'POST':
        data = request.json
        nova = Geracao(
            nome=data['nome'],
            rede_id=data.get('rede_id'),
            lider_nome=data.get('lider_nome'),
            lider_telefone=data.get('lider_telefone')
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify(nova.to_json()), 201

@app.route('/api/celulas', methods=['GET', 'POST'])
def handle_celulas():
    if request.method == 'GET':
        celulas = Celula.query.all()
        celulas.sort(key=lambda x: x.nome)
        return jsonify([c.to_json() for c in celulas])
    
    if request.method == 'POST':
        data = request.json
        
        def safe_float(val):
            if not val or val == '': return None
            try: return float(val)
            except: return None

        nova_celula = Celula(
            nome=data['nome'],
            lider=data.get('lider'),
            lider_treinamento=data.get('lider_treinamento'),
            rede_id=data.get('rede_id'),
            geracao_id=data.get('geracao_id'),
            rede_str=data.get('rede'), # Compatibilidade
            endereco=data.get('endereco'),
            numero=data.get('numero'),
            bairro=data.get('bairro'),
            cidade=data.get('cidade'),
            estado=data.get('estado'),
            cep=data.get('cep'),
            latitude=safe_float(data.get('latitude')),
            longitude=safe_float(data.get('longitude'))
        )
        db.session.add(nova_celula)
        db.session.commit()
        return jsonify(nova_celula.to_json()), 201

@app.route('/api/celulas/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_celula_id(id):
    celula = Celula.query.get(id)
    if not celula:
        return jsonify({"erro": "Celula nao encontrada"}), 404

    if request.method == 'GET':
        return jsonify(celula.to_json())

    if request.method == 'PUT':
        data = request.json
        
        def safe_int(val):
            if not val or val == '': return None
            try: return int(val)
            except: return None
            
        def safe_float(val):
            if not val or val == '': return None
            try: return float(val)
            except: return None

        if 'nome' in data: celula.nome = data['nome']
        if 'lider' in data: celula.lider = data['lider']
        if 'lider_treinamento' in data: celula.lider_treinamento = data['lider_treinamento']
        if 'rede_id' in data: celula.rede_id = safe_int(data['rede_id'])
        if 'geracao_id' in data: celula.geracao_id = safe_int(data['geracao_id'])
        if 'rede' in data: celula.rede_str = data['rede'] # Compatibilidade
        
        # Endereço
        if 'endereco' in data: celula.endereco = data['endereco']
        if 'numero' in data: celula.numero = data['numero']
        if 'bairro' in data: celula.bairro = data['bairro']
        if 'cidade' in data: celula.cidade = data['cidade']
        if 'estado' in data: celula.estado = data['estado']
        if 'cep' in data: celula.cep = data['cep']
        if 'latitude' in data: celula.latitude = safe_float(data['latitude'])
        if 'longitude' in data: celula.longitude = safe_float(data['longitude'])
        if 'dia_reuniao' in data: celula.dia_reuniao = data['dia_reuniao']
        if 'horario_reuniao' in data: celula.horario_reuniao = data['horario_reuniao']

        db.session.commit()
        return jsonify(celula.to_json())

    if request.method == 'DELETE':
        db.session.delete(celula)
        db.session.commit()
        return jsonify({"mensagem": "Celula removida"}), 200

@app.route('/api/reunioes', methods=['GET', 'POST'])
def handle_reunioes():
    if request.method == 'GET':
        reunioes = Reuniao.query.all()
        return jsonify([r.to_json() for r in reunioes])
    
    if request.method == 'POST':
        data = request.json
        dt_reuniao = datetime.strptime(data['data'], '%Y-%m-%d %H:%M') if 'data' in data else datetime.utcnow()
        
        nova = Reuniao(
            celula_id=data['celula_id'],
            data=dt_reuniao,
            tema=data.get('tema'),
            observacoes=data.get('observacoes')
        )
        db.session.add(nova)
        db.session.commit()
        return jsonify(nova.to_json()), 201

@app.route('/api/frequencia', methods=['POST'])
def handle_frequencia():
    # Espera { "reuniao_id": 1, "membros_presentes": [1, 2, 5] }
    data = request.json
    reuniao_id = data['reuniao_id']
    presentes_ids = data['membros_presentes']
    
    # Primeiro, limpa frequencias anteriores dessa reunião (simples) ou atualiza
    # Aqui vamos assumir que enviamos a lista completa de presentes
    reuniao = Reuniao.query.get(reuniao_id)
    if not reuniao:
        return jsonify({"erro": "Reuniao nao encontrada"}), 404
        
    # Remove frequencias existentes desta reuniao
    Frequencia.query.filter_by(reuniao_id=reuniao_id).delete()
    
    for mid in presentes_ids:
        freq = Frequencia(reuniao_id=reuniao_id, membro_id=mid, presente=True)
        db.session.add(freq)
    
    db.session.commit()
    return jsonify({"mensagem": "Frequencia salva com sucesso"}), 201

@app.route('/api/estudos', methods=['GET'])
def get_estudos():
    estudos = Estudo.query.all()
    return jsonify([e.to_json() for e in estudos])

@app.route('/api/relatorio/celula/<int:celula_id>')
def get_relatorio_celula(celula_id):
    # Exemplo simples de estatísticas
    total_membros = Membro.query.filter_by(celula_id=celula_id, tipo='Membro').count()
    total_visitantes = Membro.query.filter_by(celula_id=celula_id, tipo='Visitante').count()
    
    # Média de presença nas últimas 4 reuniões (exemplo simplificado)
    reunioes_ids = [r.id for r in Reuniao.query.filter_by(celula_id=celula_id).order_by(Reuniao.data.desc()).limit(4).all()]
    media_frequencia = 0
    if reunioes_ids:
        total_presencas = Frequencia.query.filter(Frequencia.reuniao_id.in_(reunioes_ids), Frequencia.presente==True).count()
        media_frequencia = total_presencas / len(reunioes_ids)

    return jsonify({
        "total_membros": total_membros,
        "total_visitantes": total_visitantes,
        "media_frequencia_ultimas_4": round(media_frequencia, 1)
    })

# Rota para setup inicial rápido
@app.route('/api/update_profile/<int:user_id>', methods=['PUT'])
def update_profile(user_id):
    try:
        data = request.json
        membro = Membro.query.get(user_id)
        if not membro:
            return jsonify({"erro": "Usuario nao encontrado"}), 404
        
        # Atualiza campos permitidos
        if 'nome' in data: membro.nome = data['nome']
        if 'telefone' in data: membro.telefone = data['telefone']
        if 'email' in data: membro.email = data['email']
        
        # Atualiza data de nascimento se fornecida
        if 'data_nascimento' in data and data['data_nascimento']:
            try:
                membro.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
            except ValueError:
                pass

        # Atualiza biografia
        if 'biografia' in data: membro.biografia = data['biografia']

        # Atualiza endereço se fornecido
        if 'endereco' in data: membro.endereco = data['endereco']
        if 'numero' in data: membro.numero = data['numero']
        if 'bairro' in data: membro.bairro = data['bairro']
        if 'cidade' in data: membro.cidade = data['cidade']
        if 'estado' in data: membro.estado = data['estado']
        if 'cep' in data: membro.cep = data['cep']

        db.session.commit()
        return jsonify(membro.to_json()), 200
    except Exception as e:
        print(f"Erro update perfil: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/api/change_password/<int:user_id>', methods=['PUT'])
def change_password(user_id):
    try:
        data = request.json
        membro = Membro.query.get(user_id)
        if not membro:
            return jsonify({"erro": "Usuario nao encontrado"}), 404
            
        senha_atual = data.get('senha_atual')
        nova_senha = data.get('nova_senha')
        
        # Verificação simples (em produção usar hash!)
        if membro.senha != senha_atual:
            return jsonify({"erro": "Senha atual incorreta"}), 400
            
        membro.senha = nova_senha
        db.session.commit()
        return jsonify({"mensagem": "Senha alterada com sucesso"}), 200
    except Exception as e:
        print(f"Erro troca senha: {e}")
        return jsonify({"erro": str(e)}), 500

@app.route('/api/upload_foto/<int:user_id>', methods=['POST'])
def upload_foto(user_id):
    if 'foto' not in request.files:
        return jsonify({"erro": "Nenhum arquivo enviado"}), 400
        
    file = request.files['foto']
    if file.filename == '':
        return jsonify({"erro": "Nenhum arquivo selecionado"}), 400
        
    if file:
        filename = secure_filename(f"user_{user_id}_{int(datetime.now().timestamp())}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Atualiza usuario
        membro = Membro.query.get(user_id)
        if membro:
            # Remove foto antiga se existir (opcional, bom para economizar espaço)
            membro.foto_url = f"/uploads/{filename}"
            db.session.commit()
            return jsonify({"mensagem": "Foto atualizada", "foto_url": membro.foto_url}), 200
            
    return jsonify({"erro": "Erro ao salvar"}), 500

# --- ROTAS NOVAS: EVENTOS, STORIES, ESCOLAS ---

# 1. EVENTOS
@app.route('/api/eventos', methods=['GET', 'POST'])
def handle_eventos():
    if request.method == 'GET':
        # Ordena por data (mais próximo primeiro)
        eventos = Evento.query.order_by(Evento.data_evento.asc()).all()
        return jsonify([e.to_json() for e in eventos])

    if request.method == 'POST':
        data = request.json # Esperamos JSON, mas upload de imagem precisa ser separado ou base64?
        # Simples: Admin envia url da foto já uploadada ou null. Vamos assumir JSON puro aqui.
        novo = Evento(
            titulo=data['titulo'],
            descricao=data.get('descricao'),
            data_evento=datetime.fromisoformat(data['data_evento']) if data.get('data_evento') else None,
            local=data.get('local'),
            foto_url=data.get('foto_url')
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_json()), 201

@app.route('/api/eventos/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def handle_evento_id(id):
    evento = Evento.query.get(id)
    if not evento:
        return jsonify({"erro": "Evento nao encontrado"}), 404

    if request.method == 'GET':
        return jsonify(evento.to_json())

    if request.method == 'PUT':
        data = request.json
        if 'titulo' in data: evento.titulo = data['titulo']
        if 'descricao' in data: evento.descricao = data['descricao']
        if 'local' in data: evento.local = data['local']
        if 'foto_url' in data: evento.foto_url = data['foto_url']
        if 'data_evento' in data and data['data_evento']:
            try:
                evento.data_evento = datetime.fromisoformat(data['data_evento'])
            except: pass
            
        db.session.commit()
        return jsonify(evento.to_json())

    if request.method == 'DELETE':
        # Remove dependencias
        Curtida.query.filter_by(evento_id=id).delete()
        Comentario.query.filter_by(evento_id=id).delete()
        db.session.delete(evento)
        db.session.commit()
        return jsonify({"mensagem": "Evento removido"}), 200

# 2. STORIES
@app.route('/api/stories', methods=['GET', 'POST'])
def handle_stories():
    if request.method == 'GET':
        # Pega stories das ultimas 24h
        hoje = datetime.utcnow()
        ontem = hoje - timedelta(hours=24)
        
        rede_id = request.args.get('rede_id')
        geracao_id = request.args.get('geracao_id')
        autor_id = request.args.get('autor_id')
        
        query = Story.query.filter(Story.criado_em >= ontem)
        if rede_id: query = query.filter_by(rede_id=rede_id)
        if geracao_id: query = query.filter_by(geracao_id=geracao_id)
        if autor_id: query = query.filter_by(autor_id=autor_id)
        
        stories = query.order_by(Story.criado_em.desc()).all()
        return jsonify([s.to_json() for s in stories])

    if request.method == 'POST':
        data = request.json
        novo = Story(
            foto_url=data['foto_url'],
            legenda=data.get('legenda'),
            autor_id=data.get('autor_id'),
            celula_id=data.get('celula_id'),
            rede_id=data.get('rede_id'),
            geracao_id=data.get('geracao_id')
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_json()), 201

@app.route('/api/stories/<int:story_id>', methods=['DELETE'])
def handle_story_id(story_id):
    story = Story.query.get(story_id)
    if not story:
        return jsonify({"erro": "Story nao encontrado"}), 404
        
    db.session.delete(story)
    db.session.commit()
    return jsonify({"mensagem": "Story removido"}), 200

# 3. ESCOLAS
@app.route('/api/escolas', methods=['GET', 'POST', 'PUT'])
def handle_escolas():
    if request.method == 'GET':
        escolas = Escola.query.all()
        return jsonify([e.to_json() for e in escolas])
    
    # POST/PUT para admin editar (implementaremos o básico GET primeiro)
    return jsonify({"msg": "Admin only"}), 403

# Upload Genérico (para banners de eventos e stories)
@app.route('/api/upload', methods=['POST'])
def upload_general():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No filename'}), 400
        
    filename = secure_filename(f"upload_{int(datetime.now().timestamp())}_{file.filename}")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    
    return jsonify({'url': f"/uploads/{filename}"}), 200

@app.route('/setup_test')
def setup_test():
    # Cria uma celula e um membro se não existirem
    if not Celula.query.first():
        c = Celula(nome="Célula Matriz", lider="Pastor", latitude=-23.5505, longitude=-46.6333)
        db.session.add(c)
        db.session.commit()
        
        m1 = Membro(nome="João", celula_id=c.id, tipo="Lider")
        m2 = Membro(nome="Maria", celula_id=c.id, tipo="Membro")
        db.session.add_all([m1, m2])
        db.session.commit()
        
        r = Reuniao(celula_id=c.id, tema="Fé", observacoes="Reunião abençoada")
        db.session.add(r)
        db.session.commit()
        
        est = Estudo(titulo="A Importância da Oração", conteudo_link="http://link.com/pdf")
        db.session.add(est)
        db.session.commit()
        
    return jsonify({"message": "Dados de teste criados!"})

@app.route('/api/celulas/<int:celula_id>/avisos', methods=['GET', 'POST'])
def handle_avisos(celula_id):
    if request.method == 'GET':
        # Mural da Célula deve mostrar avisos da própria célula + rede + geração dela
        celula = Celula.query.get(celula_id)
        if not celula:
             return jsonify([]), 404
             
        avisos = Aviso.query.filter(
            (Aviso.celula_id == celula_id) | 
            (Aviso.rede_id == celula.rede_id) | 
            (Aviso.geracao_id == celula.geracao_id)
        ).order_by(Aviso.data_criacao.desc()).all()
        
        user_id = request.headers.get('User-Id')
        try: user_id = int(user_id) if user_id else None
        except: user_id = None

        return jsonify([a.to_json(current_user_id=user_id) for a in avisos])
    
    if request.method == 'POST':
        data = request.json
        membro = Membro.query.get(data.get('autor_id'))
        if not membro or membro.tipo not in ['Lider', 'LiderRede', 'LiderGeracao', 'Admin']:
             return jsonify({"error": "Apenas lideres podem postar avisos"}), 403
             
        novo = Aviso(
            celula_id=celula_id if celula_id != 0 else None,
            rede_id=data.get('rede_id'),
            geracao_id=data.get('geracao_id'),
            titulo=data['titulo'],
            mensagem=data['mensagem'],
            autor_id=data['autor_id']
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_json()), 201

# Rota genérica para avisos (Feed Global/Rede)
@app.route('/api/avisos', methods=['GET'])
def get_all_avisos():
    rede_id = request.args.get('rede_id')
    geracao_id = request.args.get('geracao_id')
    autor_id = request.args.get('autor_id')
    
    query = Aviso.query
    if rede_id:
        # Pega gerações e células dessa rede
        gens = Geracao.query.filter_by(rede_id=rede_id).all()
        g_ids = [g.id for g in gens]
        cells = Celula.query.filter_by(rede_id=rede_id).all()
        c_ids = [c.id for c in cells]
        
        query = query.filter(
            (Aviso.rede_id == rede_id) | 
            (Aviso.geracao_id.in_(g_ids)) |
            (Aviso.celula_id.in_(c_ids))
        )
    elif geracao_id:
        # Pega células dessa geração
        cells = Celula.query.filter_by(geracao_id=geracao_id).all()
        c_ids = [c.id for c in cells]

        query = query.filter(
            (Aviso.geracao_id == geracao_id) |
            (Aviso.celula_id.in_(c_ids))
        )
    
    if autor_id: query = query.filter_by(autor_id=autor_id)
    
    avisos = query.order_by(Aviso.data_criacao.desc()).all()
    
    user_id = request.headers.get('User-Id')
    try: user_id = int(user_id) if user_id else None
    except: user_id = None

    return jsonify([a.to_json(current_user_id=user_id) for a in avisos])

@app.route('/api/avisos/<int:aviso_id>', methods=['DELETE', 'PUT'])
def handle_aviso_id(aviso_id):
    aviso = Aviso.query.get(aviso_id)
    if not aviso:
        return jsonify({"erro": "Aviso nao encontrado"}), 404
        
    if request.method == 'DELETE':
        db.session.delete(aviso)
        db.session.commit()
        return jsonify({"mensagem": "Aviso removido"}), 200
        
    elif request.method == 'PUT':
        data = request.json
        if 'titulo' in data: aviso.titulo = data['titulo']
        if 'mensagem' in data: aviso.mensagem = data['mensagem']
        
        db.session.commit()
        return jsonify({"mensagem": "Aviso atualizado", "aviso": aviso.to_json()}), 200

@app.route('/api/celulas/<int:celula_id>/pedidos', methods=['GET', 'POST'])
def handle_pedidos(celula_id):
    if request.method == 'GET':
        pedidos = PedidoOracao.query.filter_by(celula_id=celula_id).order_by(PedidoOracao.data_criacao.desc()).all()
        return jsonify([p.to_json() for p in pedidos])
    
    if request.method == 'POST':
        data = request.json
        novo = PedidoOracao(
            celula_id=celula_id,
            membro_id=data['membro_id'],
            pedido=data['pedido']
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_json()), 201

# Rota genérica para pedidos (Para Líderes verem tudo da Rede/Geração)
@app.route('/api/pedidos', methods=['GET'])
def get_all_pedidos():
    rede_id = request.args.get('rede_id')
    geracao_id = request.args.get('geracao_id')
    
    query = PedidoOracao.query
    if rede_id:
        cells = Celula.query.filter_by(rede_id=rede_id).all()
        c_ids = [c.id for c in cells]
        query = query.filter(PedidoOracao.celula_id.in_(c_ids))
    elif geracao_id:
        cells = Celula.query.filter_by(geracao_id=geracao_id).all()
        c_ids = [c.id for c in cells]
        query = query.filter(PedidoOracao.celula_id.in_(c_ids))
        
    pedidos = query.order_by(PedidoOracao.data_criacao.desc()).all()
    return jsonify([p.to_json() for p in pedidos])

@app.route('/api/pedidos/<int:pedido_id>/resolver', methods=['PUT'])
def resolver_pedido(pedido_id):
    pedido = PedidoOracao.query.get(pedido_id)
    if not pedido: return jsonify({"error": "Nao encontrado"}), 404
    
    pedido.resolvido = not pedido.resolvido
    db.session.commit()
    return jsonify(pedido.to_json())

@app.route('/api/celulas/<int:celula_id>/testemunhos', methods=['GET', 'POST'])
def handle_testemunhos(celula_id):
    if request.method == 'GET':
        testemunhos = Testemunho.query.filter_by(celula_id=celula_id).order_by(Testemunho.data_criacao.desc()).all()
        return jsonify([t.to_json() for t in testemunhos])
    
    if request.method == 'POST':
        data = request.json
        novo = Testemunho(
            celula_id=celula_id,
            membro_id=data['membro_id'],
            texto=data['texto']
        )
        db.session.add(novo)
        db.session.commit()
        return jsonify(novo.to_json()), 201

# Rota genérica para testemunhos
@app.route('/api/testemunhos', methods=['GET'])
def get_all_testemunhos():
    rede_id = request.args.get('rede_id')
    geracao_id = request.args.get('geracao_id')
    
    query = Testemunho.query
    if rede_id:
        cells = Celula.query.filter_by(rede_id=rede_id).all()
        c_ids = [c.id for c in cells]
        query = query.filter(Testemunho.celula_id.in_(c_ids))
    elif geracao_id:
        cells = Celula.query.filter_by(geracao_id=geracao_id).all()
        c_ids = [c.id for c in cells]
        query = query.filter(Testemunho.celula_id.in_(c_ids))
        
    testemunhos = query.order_by(Testemunho.data_criacao.desc()).all()
    return jsonify([t.to_json() for t in testemunhos])

if __name__ == '__main__':
    with app.app_context():
        # ATENÇÃO: Em produção, usar Flask-Migrate. Aqui dropamos tudo para facilitar dev.
        # db.drop_all() 
        db.create_all()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
