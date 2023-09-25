from flask_login import current_user, login_required, login_user, logout_user
from app import app, db, cocktailRecommender
from flask import current_app, flash, redirect, render_template, url_for, request, session
from flask_paginate import Pagination, get_page_args 
from app.forms import LoginForm, RegistrationForm, SimpleForm, MessageForm, EvalForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import CocktailDTO, User, Message
from datetime import datetime
from app.email import send_password_reset_email


@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html', title='homepage')

@app.route('/language=<language>')
def set_language(language=None):
    session['language'] = language
    return redirect(url_for('index'))

@app.context_processor
def inject_conf_var():
    return dict(AVAILABLE_LANGUAGES=app.config['LANGUAGES'], CURRENT_LANGUAGE=session.get('language', request.accept_languages.best_match(app.config['LANGUAGES'].keys())))


@app.route('/base')
def base():
    return render_template('base.html', title='Layout')


@app.route('/no_recommendation')
def no_recommendation():
    return render_template('no_recommendation.html', title='Norec')


@app.route('/messages')
@login_required
def messages():
    '''current_user.last_message_read_time = datetime.utcnow
    db.session.commit()''' ## no se puede visualizar los mensajes si se pone estas lineas
    page = request.args.get('page1', 1, type=int)
    messages = current_user.messages_received.order_by(Message.timestamp.desc())\
        .paginate(page, current_app.config['MESSAGES_PER_PAGE'], True)
    next_url = url_for('messages', page=messages.next_num) if messages.has_next else None
    prev_url = url_for('messages', page=messages.prev_num) if messages.has_prev else None
    id = current_user.id 
    if id == 1:
        return render_template('messages.html', messages=messages.items, next_url=next_url, prev_url=prev_url)
    else:
        flash('Sorry you must be logged in as admin to access this page')
        return render_template('index.html', title='Homepage')
    
    
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return render_template('index.html', title='Homepage')
            else:
                error = 'Wrong Password'
                return render_template('login.html', form=form, error=error)
        else:
            return redirect(url_for('register'))
    return render_template('login.html', form=form, error='')

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
        flash('Congratulations you have registered successfully!')
        return redirect(url_for('register'))
    return render_template('register.html', title='Register', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


def get_cocktail_pagination(cocktail_list, per_page=10, offset=0):
    return cocktail_list[offset: offset + per_page]

@app.route('/recommender', methods=['GET', 'POST'])
def recommender():
    form = SimpleForm()
    error = ""
    if form.validate_on_submit():
        if len(form.fruits_cb.data) + len(form.alco_cb.data) + len(form.nonalco_cb.data) + len(form.others_cb.data) < 2:
            error = "You must select at least two ingredients"
            return render_template('recommender.html', form=form, error=error)
        else:
            response = [form.fruits_cb.data, form.alco_cb.data, form.nonalco_cb.data, form.others_cb.data]
            user_query = [val.lower() for sublist in response for val in sublist]
            print('USER QUERY', user_query)

            cocktail = cocktailRecommender.get_recommendation(user_query)

            if cocktail.name is None:
                return render_template("no_recommendation.html", user_query=user_query)
            else:
                return redirect(url_for("cocktail", name=cocktail.name, ask_eval=True))
    return render_template('recommender.html', form=form, error=error)


@app.route('/cocktail/<name>?<ask_eval>', methods=["GET", "POST"])
def cocktail(name, ask_eval):
    for c in cocktailRecommender.case_base.get_all_cocktails():
        print(c.ingredient_quantity_unit)
        print('----------')


    form = EvalForm()
    cocktail = cocktailRecommender.get_recommended_cocktail() if ask_eval == 'True' else cocktailRecommender.get_cocktail(name)
    if cocktail is not None:
        print(cocktail.ingredient_quantity_unit)
        cocktailDTO = CocktailDTO(cocktail)
        if form.validate_on_submit():
            value = request.form.getlist('options')
            if len(value) == 0:
                error = 'You must select an opinion.'
                return render_template('cocktail.html', cocktail=cocktailDTO, ask_eval=str(ask_eval), form=form, error=error)
            cocktailRecommender.set_user_evaluation(value[0])  # Process user evaluation
            flash('Thanks for your opinion! we are going to keep improving :)')
            return render_template('cocktail.html', cocktail=cocktailDTO, ask_eval=str(False), form=form)
        else:
            return render_template('cocktail.html', cocktail=cocktailDTO, ask_eval=str(ask_eval), form=form)
    else:
        return render_template('404.html', name=name)


@app.route('/cocktails')
def cocktails():
    cocktail_list = cocktailRecommender.get_all_cocktails()

    cocktail_list = [CocktailDTO(c) for c in cocktail_list]
    cocktail_list = sorted(cocktail_list, key=lambda x: x.name)

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page')
    total = len(cocktail_list)
    pagination_cocktails = get_cocktail_pagination(cocktail_list, offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total,
                            css_framework='bootstrap4')

    return render_template('cocktails.html',
                           cocktails=pagination_cocktails,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           )

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html', name=''), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html', name=''), 500

@app.route('/contactus', methods=['GET', 'POST'])
def contactus():
    form = MessageForm()
    user = User.query.filter_by(username="Maurice").first_or_404()
    print(user.username)
    if form.validate_on_submit():
        print(form.message.data)
        msg= Message(author=current_user, recipient=user, body=form.message.data)
        db.session.add(msg)
        db.session.commit()
        flash(('Your message has been sent.'))
        return redirect(url_for('contactus'))
    return render_template('contactus.html', title='Send Message', form=form)

@app.route('/request_reset_password', methods=['GET', 'POST'])
def request_reset_password():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('request_reset_password.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

if __name__ == "__main__":
    app.run(debug=True,)

