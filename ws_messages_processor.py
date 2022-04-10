#!/usr/bin/env python
import pika


def prepare_channel():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()

    channel.exchange_declare(exchange='wsmanager', exchange_type='fanout')
    queue_declaration_result = channel.queue_declare(queue='', exclusive=True)
    queue_name = queue_declaration_result.method.queue
    channel.queue_bind(exchange='wsmanager', queue=queue_name)
    channel.basic_consume(
        queue=queue_name, on_message_callback=callback, auto_ack=True
    )

    channel.exchange_declare(exchange='towsmanager', exchange_type='fanout')

    return channel


def callback(ch, method, properties, body):
    print(" [x] %r" % body)
    message = f"processed message: {body.decode('utf-8')}"
    channel_.basic_publish(exchange='towsmanager', routing_key='', body=message)
    print(f" sent {message}")


channel_ = prepare_channel()
print(' [*] Waiting for messages. To exit press CTRL+C')
channel_.start_consuming()
