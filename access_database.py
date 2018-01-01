import json
# Lock for resetting the database
from threading import Lock

filename = "database.json"

def store(data, lock):
    with lock:
        with open(filename, 'w') as fp:
            json.dump(data, fp, indent=3)


def load(lock):
    with lock:
        with open(filename, 'r') as fp:
            data = json.load(fp)
    return data


# Run this program to reset the database
if __name__ == "__main__":
    dic = {"server": ["password", ["server", "message"]]}
    store(dic, Lock())
    print("Database has been reset")
