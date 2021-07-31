import codecs
import json
import os
import pickle
from os import walk
from os.path import join

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA


def decrypt(file):
    """data = pickle.loads(codecs.decode(open('./database', 'rb').read(), "base64"))
    private_key = RSA.import_key(open("priv.pem").read())
    enc_session_key, nonce, tag, ciphertext = data
    cipher_rsa = PKCS1_OAEP.new(private_key)
    session_key = cipher_rsa.decrypt(enc_session_key)
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    key = cipher_aes.decrypt_and_verify(ciphertext, tag)"""

    with open('key.json','r') as f:
        key = codecs.decode((json.load(f)['key']).encode('utf-8'), "base64")

    base = os.path.splitext(file)[0]

    with open(base + '.e2eiv', "rb") as iv:
        cipher = AES.new(key, AES.MODE_CFB, iv=iv.read())
        iv.close()

    os.remove(base + '.e2eiv')

    with open(file, 'rb') as f:
        data = f.read()
        cipheredData = cipher.decrypt(data)
        f.close()

    with open(base + '.e2eext', "r+") as fn:
        with open(base + fn.read(), "wb+") as f:
            f.write(cipheredData)
            f.close()
        fn.close()
    os.remove(base + '.e2eext')
    os.remove(base + '.e2e')


if __name__ == '__main__':
    # print(codecs.decode(open('./database', 'rb').read(), "base64"))
    for root, dirs, files in walk('./data'):
        for f in files:
            if f.endswith('.e2eiv') or f.endswith('.e2eext'):
                continue
            #print(f)

            decrypt(join(root, f))
