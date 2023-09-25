from flask import Flask, session, request
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_babel import Babel
from config import Config
from recommender import CocktailRecommender




app = Flask(__name__, static_url_path='/static')
app.config.from_object(Config)
app.config['RECIPES_PER_PAGE'] = 15
app.config['MESSAGES_PER_PAGE'] = 6
app.config['LANGUAGES'] =  {
    'en': 'English',
    'es': 'Español',
}
app.secret_key = "Mixologist Extra Spicy"

mail = Mail(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

bootstrap = Bootstrap(app)

login = LoginManager(app)
login.login_view = 'login'

babel = Babel(app)

cocktailRecommender = CocktailRecommender(taxonomy_file='data/taxonomy_taste.csv',
                                          cocktail_file='data/ccc_cocktails.xml',
                                          general_taxonomy_file='data/general_taxonomy.csv')


@babel.localeselector
def get_locale():
    try:
        language = session['language']
    except KeyError:
        language = None
    if language is not None:
        return language
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys())


from app import routes

