import zenoh
import time

config = zenoh.Config()
config.insert_json5("connect/endpoints", '["tcp/zenoh-router:7447"]')

session = zenoh.open(config)

# key_expr = "**"
key_expr = "mqtt/demo/**"

def listener(sample):
    payload = sample.payload.to_string()
    print(f"✓ [{sample.key_expr}]: {payload}")
    
subscriber = session.declare_subscriber(key_expr, listener)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass
finally:
    session.close()
    

