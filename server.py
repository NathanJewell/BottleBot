import SimpleHTTPServer
import SocketServer

PORT = 8000
handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(("", PORT), handler)

print("Servering on port {}".format(PORT))
httpd.serve_forever()