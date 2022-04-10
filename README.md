# Websocket and Rabbitmq POC

## Introduction

In this POC I try to propagate the messages from a pool of websocket connections to a message broker an d vice versa.

This technique opens the way to implement event oriented architectures.

## Process description

We have three components: a client a web socket manager and a processor.

The client connects to the web socket manager through a websocket. It sends text messages and receives messages sent 
from other clients and processed messages sent by the processor.

The web socket manager deals with the pool of client connections. It takes care of sending the client messages to the 
rest of clients. It also connects to the message broker to propagate messages from the websocket pool to the broker and 
vice versa.

The processor receives messages from the broker and resends this message after some basic processing.

To listen to both websockets messages and broker messages the client uses two concurrent processes.

The message flow from the websockets to the processor is made possible by a fanout exchange in the broker name "wsmanager".

The reverse message flow from the processor to the websockets is made possible by another fanout exchange named "towsmanager".

Both the manager and the processor create and link a queue to receive messages from each exchange.

Here we use only a processor to listen to websockets sent message but we could add more processors or actors to 
react to theese messages.


## Requirements

- python
- pip
- docker

## Installation

Create and activate a virtual environment.

Install dependencies.

~~~
pip install -r requirements.txt
~~~

## Getting started

* Run RabbitMQ

~~~
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management
~~~

* Run the web_socket_manager

~~~
uvicorn web_socket_manager:app --reload
~~~

* Run the ws_messages_processor

~~~
python ws_messages_processor.py
~~~

* Open the client with a browser and send a message

The client page should show the sent message, and the processed message.

The web_socket_manager terminal should print the message sent by the client and the message received from the web socket 
messages processor.

The ws_messages_processor should print the message received from the web_socket_manager and the processed message that 
is going to send.
