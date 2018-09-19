from driver import Driver

from schema import Event, Measurement

global led, temp

with Driver.app.app_context():
    led = Driver.register_device("localhost:5000", "fake_led", "My fake LED.")
    temp = Driver.register_device("localhost:5000", "fake_temp", "A fake temperature.")

@Driver.app.route("/")
def index():
    return "HI"

@Driver.rpc.method('set_state')
def set_state(enabled):
    led_state = enabled
    return enabled

def periodic():
    with Driver.app.app_context():
        Driver.db.session.add(Measurement(device=temp.id, value=4))
        Driver.db.session.commit()
    return 0.05

Driver.periodic(periodic)

Driver.serve("localhost", 5000)
