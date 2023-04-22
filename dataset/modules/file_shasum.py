def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as file:
        while True:
            chunk = file.read(h.block_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()[0:6]

