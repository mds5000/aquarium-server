from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCServer
import sqlite3

def lookup_device(db, host, name):
    res = db.execute("SELECT id FROM devices WHERE provider = ? AND provider_name = ?;",
                     host, name).fetchone()
    return None if res is None else res[0]

def register_device(db, host, name, description):
    if lookup_device(db, host, name) is None:
        db.execute("INSERT INTO devices(provider, provider_name, description) VALUES (?, ?, ?);",
                    (host, name, description)
        )
        db.commit()
        print "ADDED DEVICE"
    return lookup_device(db, host, name)


DB_LOCATION = '../db/database.db' # Get from env var
db = sqlite3.connect(DB_LOCATION)

led_device = register_device(db, "localhost:5000", "LED", "A Fake LED")

PORT = 5000
server = SimpleJSONRPCServer(('localhost', PORT))

led_state = 'Off'
def set_state(enabled):
    led_state = 'On' if enabled else 'Off'
    db.execute("INSERT INTO events(device_id, action) VALUES (?, ?)", led_device, led_state)
    return led_state

server.register_function(set_state)
print "Starting Server"
server.serve_forever()