# Websockets-python-async-server
Server on websockets for **Python3**. It's collecting all connections into set with several custom attributes: uuid, name, status, etc.

# Features
- Track connections. Register/Unregister
- Default port 1300. Add attribute `port=<port_number>` to override.


# How to run?
1. Get server.py
2. Execute script: "python server.py"
3. To run it from pm2: "pm2 start server.py --interpreter=python3"

## Requirements
- `pip install websockets`
- `pip install uuid`
- `pip install asyncio`