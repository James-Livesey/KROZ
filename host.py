import http.server
import socketserver
import urllib
import sys

targetPlayer = -1
inputBuffer = []
outputBuffer = []
pollerConnection = None

def handleInput(message = "", flush = True):
    global inputBuffer, outputBuffer

    if len(inputBuffer) > 0:
        bufferResult = inputBuffer[0]

        if flush:
            inputBuffer.pop(0)

        return bufferResult
    else:
        return ""

def handleOutput(line = ""):
    global outputBuffer

    outputBuffer.append(line)

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        global targetPlayer, inputBuffer, outputBuffer

        path = urllib.parse.unquote(self.path)
        returnMessage = "KROZ V0.1.0"

        if path == "/":
            pass
        elif len(path.split("/")) == 2:
            inputBuffer.append(path.split("/")[1])

            pollerConnection()

            returnMessage = "\n".join(outputBuffer)
            outputBuffer = []
        elif len(path.split("/")) == 3:
            targetPlayer = int(path.split("/")[1])
            inputBuffer.append(path.split("/")[2])

            pollerConnection()

            returnMessage = "\n".join(outputBuffer)
            outputBuffer = []
        
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        self.wfile.write(returnMessage.encode("utf-8"))
    
    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        http.server.BaseHTTPRequestHandler.end_headers(self)

def serve(ipAddress, port):
    socketserver.TCPServer.allow_reuse_address = True

    try:
        httpSocket = socketserver.TCPServer((ipAddress, int(port)), Handler)
    except Exception as e:
        print(e)
        return "Couldn't start server. Check that the IP address and port is not in use."
    
    try:
        httpSocket.serve_forever()
    except Exception as e:
        print(e)
        httpSocket.shutdown()
    
    return ""
