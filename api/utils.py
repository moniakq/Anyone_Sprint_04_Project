import hashlib
import os
import numpy as np


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    nombre, extension=os.path.splitext(filename)
    for ext in [".png", ".jpg", ".jpeg", ".gif",'.JPG','.JPEG','.GIF','.PNG']:
        if ext==extension:
            return True
    return False


def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """

    data = file.read()
    md5hash = hashlib.md5(data).hexdigest()
    nombre, extension=os.path.splitext(file.filename)
    md5hash=md5hash+extension
    # This was a test to get a better performance in the stress test. If the system uses a different filename everytime the ml_model didn't crash at all
    # And could perform at 15 RPS with only one model container
    #md5hash=md5hash+str(np.random.randint(200))+extension
    file.seek(0) 
    return md5hash
    #os.path.basename(md5hash)
