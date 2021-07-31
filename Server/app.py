from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import sqlite3

db = SQLAlchemy()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "./"
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 16MB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"

db.init_app(app)
migrate = Migrate(app, db)


class Device(db.Model):
    uid = db.Column(db.Text, primary_key=True)
    key = db.Column(db.Text, unique=True, nullable=False)

    def __init__(self, uid, key):
        self.uid = uid
        self.key = key


@app.route('/add', methods=['POST'])
def add():
    device = Device(request.json['uid'], request.json['key'])
    db.session.add(device)
    db.session.commit()
    return jsonify({
        'status': 'ok'
    })


@app.route('/get', methods=['POST'])
def get():
    # TODO: Add Check
    query = Device.query.filter_by(uid=request.json['uid']).first()
    # print(query)
    return jsonify({
        'key': query.key
    })


@app.route('/')
def index():
    return jsonify({
        'status': 'ok'
    })


if __name__ == "__main__":
    app.run(debug=True)
