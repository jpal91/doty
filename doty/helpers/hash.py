import hashlib
import json

def get_md5(object) -> str:
    return hashlib.md5(json.dumps(object, sort_keys=True).encode()).hexdigest()

def get_sha256(object) -> str:
    return hashlib.sha256(json.dumps(object, sort_keys=True).encode()).hexdigest()