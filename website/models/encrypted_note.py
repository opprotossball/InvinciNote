from .. import db
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512
from Crypto.Cipher import AES
from ..action_result import ActionResult
from sqlalchemy.sql import func
from Crypto.Random import get_random_bytes

class EncryptedNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    tag = db.Column(db.String)
    salt = db.Column(db.String)
    nonce = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, data, title, user_id, password):
        self.data = data
        self.title = title
        self.user_id = user_id
        salt = get_random_bytes(16)
        self.salt = salt
        key = PBKDF2(password.encode('utf-8'), salt, 32, count=1000000, hmac_hash_module=SHA512)
        cipher = AES.new(key, AES.MODE_GCM)
        self.nonce = cipher.nonce
        encrypted, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
        self.data = encrypted
        self.tag = tag

    def decrypt(self, password):
        key = PBKDF2(password.encode('utf-8'), self.salt, 32, count=1000000, hmac_hash_module=SHA512)
        cipher = AES.new(key, AES.MODE_GCM, nonce=self.nonce)
        decrypted = cipher.decrypt(self.data)
        try:
            cipher.verify(self.tag)
            return ActionResult(True, decrypted.decode('utf-8'))
        except ValueError:
            return ActionResult(False, 'Wrong password.')
        