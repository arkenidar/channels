from bottle import template, static_file, Bottle, abort, request
import os.path
from gevent.pywsgi import WSGIServer
from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

app = Bottle()


# Dynamic content via old HTTP Request+Response model
@app.route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)


# Static Files
@app.route('/<filename>')
def serve_static_files(filename):
    ext = os.path.splitext(filename)[1][1:]
    ext_map = {'image': ['png', 'gif', 'jpg', 'ico'], 'js': ['js']}
    sub_folder = next((k for k, v in ext_map.items() if ext in v),'')
    return static_file(filename, root='static/'+sub_folder)


# Dynamic content via HTTP Websockets bi-directional channel new model
@app.route('/channel1')
def handle_channel():
    channel = request.environ.get('wsgi.websocket')
    if not channel:
        abort(400, 'Expected WebSocket request.')

    while True:
        try:
            message = channel.receive()
            channel.send("Your message was: %r" % message)
        except WebSocketError:
            break


@app.route('/channel2')
def handle_channel2():
    channel = request.environ.get('wsgi.websocket')
    if not channel:
        abort(400, 'Expected WebSocket request.')

    i = 0
    while True:
        i += 1
        try:
            # try uncommenting the following line: it stops on receive
            #message = channel.receive()
            channel.send("%d" % i)
        except WebSocketError:
            break

server_address = ('localhost', 8080)
server = WSGIServer(server_address, app,
                    handler_class = WebSocketHandler)
print('running on %r' % (server_address,))
server.serve_forever()