import os
import hmac
import uuid
import secrets
import zipfile
import io
from io import BytesIO
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.core.signing import Signer

from mycloud import settings


# global unique identifier
def get_uuid():
    return memoryview(uuid.uuid1().bytes)[:32].hex()


# random key and signature
def get_key_signature():
    secret_key = secrets.token_hex(3)
    signature = Signer().sign(secret_key)
    return secret_key, signature


# get signal address
def get_secret_path(msg):
    h = hmac.new(secrets.token_bytes(3), msg, 'sha1')
    return h.hexdigest()


# get unique file name
def get_unique_filename(instance, filename):
    return f"uploads/{instance.user.id}/{get_uuid()}{Path(filename).suffix}"


# get directory size
def get_dir_size(path):
    return sum(f.stat().st_size for f in path.glob('**/*') if f.is_file())


# Compress the folder and return the byte object
def make_archive_bytes(dir_path, encrypt=False):
    buffer = BytesIO()
    dl = len(str(dir_path.parent)) + 1

    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zipper:
        for basedir, subdir, files in os.walk(dir_path):
            base = Path(basedir)
            parent = Path(basedir[dl:])
            zipper.writestr(str(parent) + '/', '')
            for file in files:
                file_path = base / file
                if encrypt:
                    with open(file_path, 'rb') as f:
                        file_content = f.read()
                    try:
                        if len(file_content) > 16:  # Make sure the file is long enough to include IV
                            iv = file_content[:16]
                            encrypted_content = file_content[16:]
                            cipher = AES.new(settings.ENCRYPTION_KEY, AES.MODE_CBC, iv)
                            decrypted_content = unpad(cipher.decrypt(encrypted_content), AES.block_size)
                        else:
                            # File is too short and may not be encrypted
                            decrypted_content = file_content
                    except ValueError:
                        # If decryption fails, it is assumed that the file is not encrypted and the original content is used directly
                        decrypted_content = file_content
                    # Write content to a zip file
                    zipper.writestr(str(parent / file), decrypted_content)
                else:
                    zipper.write(file_path, parent / file)
            for folder in subdir:
                zipper.writestr(str(parent / folder) + '/', '')

    buffer.seek(0)
    return buffer


# format file size
def file_size_format(value, fixed=2):
    if value < 1024:
        size = f'{value} B'
    elif value < 1048576:
        size = f'{round(value / 1024, fixed)} KB'
    elif value < 1073741824:
        size = f'{round(value / 1024 / 1024, fixed)} MB'
    else:
        size = f'{round(value / 1024 / 1024 / 1024, fixed)} GB'
    return size


class AjaxData(dict):

    def __init__(self, code=200, msg='', data=None, errors=None):
        assert isinstance(code, int)
        assert isinstance(msg, str)
        if data is not None:
            assert isinstance(data, dict)
        if errors is not None:
            assert isinstance(errors, dict)
        super().__init__(code=code, msg=msg, data=data, errors=errors)
