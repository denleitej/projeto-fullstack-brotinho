# app/routes.py

from urllib.parse import urlsplit
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from app import app, db
from datetime import datetime, timezone, date
from app.forms import LoginForm, RegistrationForm, EditProfileForm, TrocaForm, TarefaForm
from app.models import User, Plant, Tarefa, Troca
from sqlalchemy.orm import joinedload


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.email == form.email.data)) # !!!!!!!
        
        if user is None or not user.check_password(form.password.data): 
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    plants = Plant.query.options(joinedload(Plant.tarefas)).filter_by(user_id=user.id).all()
    form_tarefa = TarefaForm()
    return render_template('user.html', user=user, plants=plants, form_tarefa=form_tarefa)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc)
        db.session.commit()
      
        
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.route('/plant/<int:plant_id>/add_tarefa', methods=['POST'])
@login_required
def add_tarefa(plant_id):
    plant = Plant.query.get_or_404(plant_id)

    if plant.dono != current_user:
        flash("Você não tem permissão para adicionar tarefas a esta planta.")
        return redirect(url_for('user', username=current_user.username))

    titulo = request.form.get('titulo')
    tipo = request.form.get('tipo')  # opcional
    data_programada_str = request.form.get('data_programada')

    if not titulo or not data_programada_str:
        flash("Todos os campos são obrigatórios.")
        return redirect(url_for('user', username=current_user.username))

    try:
        data_programada = datetime.strptime(data_programada_str, '%Y-%m-%d')
    except ValueError:
        flash("Formato de data inválido. Use AAAA-MM-DD")
        return redirect(url_for('user', username=current_user.username))

    tarefa = Tarefa(
        titulo=titulo,
        tipo=tipo if tipo else None,
        data_programada=data_programada,
        plant_id=plant.id
    )
    db.session.add(tarefa)
    db.session.commit()
    flash('Tarefa adicionada com sucesso!')

    return redirect(url_for('user', username=current_user.username))

@app.route('/add_plant', methods=['GET', 'POST'])
@login_required
def add_plant():
    if request.method == 'POST':
        planta_nome = request.form['planta']
        descricao = request.form.get('descricao')
        
        # Criar um novo objeto de Planta
        new_plant = Plant(planta=planta_nome, descricao=descricao, user_id=current_user.id)
        
        # Adicionar e comitar a planta no banco
        db.session.add(new_plant)
        db.session.commit()
        flash('Planta adicionada com sucesso!')
        return redirect(url_for('user', username=current_user.username))
    
    return render_template('add_plant.html')


# ADICIONADOS RECENTEMENTE
# criar um template add_troca
@app.route('/add_troca', methods=['GET', 'POST'])
@login_required
def add_troca():
    form = TrocaForm()
    if form.validate_on_submit():
        troca = Troca(
            titulo=form.titulo.data,
            local=form.local.data,
            descricao=form.descricao.data,
            user_id=current_user.id
        )
        db.session.add(troca)
        db.session.commit()
        flash('Troca adicionada com sucesso!')
        return redirect(url_for('user', username=current_user.username))
    return render_template('add_troca.html', title='Adicionar Troca', form=form)


@app.route('/delete_plant/<int:plant_id>', methods=['POST'])
@login_required
def delete_plant(plant_id):
    plant = db.session.query(Plant)\
        .options(joinedload(Plant.tarefas))\
        .get_or_404(plant_id)

    if plant.dono != current_user:
        flash('Você não tem permissão para deletar esta planta.')
        return redirect(url_for('user', username=current_user.username))

    db.session.delete(plant)
    db.session.commit()
    flash('Planta deletada com sucesso!')
    return redirect(url_for('user', username=current_user.username))

