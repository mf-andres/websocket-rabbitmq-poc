import asyncio
import threading
from typing import List

import pika
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()


def prepare_channel():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    # configure from wsmanager message pipe
    channel.exchange_declare(exchange='wsmanager', exchange_type='fanout')

    # configure to wsmanager message pipe
    channel.exchange_declare(exchange='towsmanager', exchange_type='fanout')
    queue_declaration_result = channel.queue_declare(queue='', exclusive=True)
    queue_name = queue_declaration_result.method.queue
    channel.queue_bind(exchange='towsmanager', queue=queue_name)
    channel.basic_consume(
        queue=queue_name, on_message_callback=towsmanager_callback, auto_ack=True
    )

    return channel


def towsmanager_callback(ch, method, properties, body):
    print("broadcasting")
    asyncio.run(manager.broadcast(body.decode("utf-8")))


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
            channel.basic_publish(exchange='wsmanager', routing_key='', body=data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} left the chat")


def listen_to_messages(channel):
    channel.start_consuming()


channel = prepare_channel()
manager = ConnectionManager()
x = threading.Thread(target=listen_to_messages, args=(channel,)).start()
