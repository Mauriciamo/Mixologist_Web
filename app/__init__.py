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

def create_app(config_class=Config):
    # ...
    if not app.debug and not app.testing:
        # ...

        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/microblog.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')

    return app

from app import routes

