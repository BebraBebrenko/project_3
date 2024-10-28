
from flask import Flask, render_template
from .routes import weather
from .routes import test
def create_app():
    app = Flask(__name__)

    # Регистрация маршрутов
    app.register_blueprint(weather.bp)
    app.register_blueprint(test.bp)

    return app


app = create_app()

@app.route('/')
def index():
    return render_template('index.html')