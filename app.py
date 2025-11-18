from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime, date
import os
from dotenv import load_dotenv

# Importar db e modelos
from models import db, Categoria, Transacao

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua-chave-secreta-aqui-2024'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///controle_despesas.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar db com app
db.init_app(app)

# Rotas
@app.route('/')
def index():
    mes_atual = date.today().month
    ano_atual = date.today().year
    
    transacoes = Transacao.query.filter(
        db.extract('month', Transacao.data) == mes_atual,
        db.extract('year', Transacao.data) == ano_atual
    ).order_by(Transacao.data.desc()).all()
    
    total_receitas = sum(t.valor for t in transacoes if t.tipo == 'receita')
    total_despesas = sum(t.valor for t in transacoes if t.tipo == 'despesa')
    saldo = total_receitas - total_despesas
    
    return render_template('index.html', 
                         transacoes=transacoes,
                         total_receitas=total_receitas,
                         total_despesas=total_despesas,
                         saldo=saldo)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar_transacao():
    categorias = Categoria.query.all()
    
    if request.method == 'POST':
        try:
            nova_transacao = Transacao(
                descricao=request.form['descricao'],
                valor=float(request.form['valor']),
                tipo=request.form['tipo'],
                categoria_id=int(request.form['categoria_id']),
                data=datetime.strptime(request.form['data'], '%Y-%m-%d')
            )
            
            db.session.add(nova_transacao)
            db.session.commit()
            flash('Transação adicionada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao adicionar transação: {str(e)}', 'error')
    
    return render_template('adicionar_transacao.html', categorias=categorias)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    categorias = Categoria.query.all()
    
    if request.method == 'POST':
        try:
            transacao.descricao = request.form['descricao']
            transacao.valor = float(request.form['valor'])
            transacao.tipo = request.form['tipo']
            transacao.categoria_id = int(request.form['categoria_id'])
            transacao.data = datetime.strptime(request.form['data'], '%Y-%m-%d')
            
            db.session.commit()
            flash('Transação atualizada com sucesso!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Erro ao atualizar transação: {str(e)}', 'error')
    
    return render_template('editar_transacao.html', 
                         transacao=transacao, 
                         categorias=categorias)

@app.route('/excluir/<int:id>')
def excluir_transacao(id):
    transacao = Transacao.query.get_or_404(id)
    db.session.delete(transacao)
    db.session.commit()
    flash('Transação excluída com sucesso!', 'success')
    return redirect(url_for('index'))

@app.route('/relatorios')
def relatorios():
    mes = request.args.get('mes', date.today().month, type=int)
    ano = request.args.get('ano', date.today().year, type=int)
    
    transacoes = Transacao.query.filter(
        db.extract('month', Transacao.data) == mes,
        db.extract('year', Transacao.data) == ano
    ).all()
    
    despesas_por_categoria = {}
    receitas_por_categoria = {}
    
    for transacao in transacoes:
        categoria_nome = transacao.categoria.nome
        if transacao.tipo == 'despesa':
            despesas_por_categoria[categoria_nome] = despesas_por_categoria.get(categoria_nome, 0) + transacao.valor
        else:
            receitas_por_categoria[categoria_nome] = receitas_por_categoria.get(categoria_nome, 0) + transacao.valor
    
    total_receitas = sum(receitas_por_categoria.values())
    total_despesas = sum(despesas_por_categoria.values())
    saldo = total_receitas - total_despesas
    
    return render_template('relatorios.html',
                         despesas_por_categoria=despesas_por_categoria,
                         receitas_por_categoria=receitas_por_categoria,
                         total_receitas=total_receitas,
                         total_despesas=total_despesas,
                         saldo=saldo,
                         mes=mes,
                         ano=ano)

# Inicializar banco de dados
def init_db():
    with app.app_context():
        db.create_all()
        
        # Criar categorias iniciais se não existirem
        if Categoria.query.count() == 0:
            categorias = [
                Categoria(nome='Salário', tipo='receita'),
                Categoria(nome='Investimentos', tipo='receita'),
                Categoria(nome='Freelance', tipo='receita'),
                Categoria(nome='Alimentação', tipo='despesa'),
                Categoria(nome='Moradia', tipo='despesa'),
                Categoria(nome='Transporte', tipo='despesa'),
                Categoria(nome='Saúde', tipo='despesa'),
                Categoria(nome='Lazer', tipo='despesa'),
                Categoria(nome='Educação', tipo='despesa'),
                Categoria(nome='Outros', tipo='ambos')
            ]
            db.session.bulk_save_objects(categorias)
            db.session.commit()
            print("✅ Categorias iniciais criadas!")

if __name__ == '__main__':
    init_db()
    print("✅ Servidor iniciando... Acesse: http://localhost:5000")
    app.run(debug=True)