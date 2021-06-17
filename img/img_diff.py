from PIL import Image
from imagehash import dhash
from binascii import a2b_hex
from io import BytesIO
from base14 import get_base14

def get_dhash_b14(datas: bytes) -> str:
    b14_dhash = "0" * 16
    with BytesIO(datas) as dataio:
        with Image.open(dataio) as img:
            b14_dhash = get_base14(a2b_hex(str(dhash(img))))[:-1]
    return b14_dhash
