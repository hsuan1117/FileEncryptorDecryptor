from Crypto.PublicKey import RSA


def generate():
    key = RSA.generate(2048)

    # Private Key
    priv = key.export_key()
    f = open('./Server/priv.pem', 'wb')
    f.write(priv)
    f.close()

    # Public Key
    pub = key.export_key()
    f = open('./Client/pub.pem', 'wb')
    f.write(pub)
    f.close()


generate()
