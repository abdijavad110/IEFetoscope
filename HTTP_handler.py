# Python 3 server example
import os
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer, SimpleHTTPRequestHandler
import time

hostName = "localhost"
serverPort = 8080

HR = None
BL = None
AC = None
VR = None
FIG = ""

LOGO = open("templates/img/pregnantLady.png", 'rb').read()
PROFILE = open("templates/img/user-female.png", 'rb').read()
HRRECORD_PAGE = open("templates/HRRecord.html", 'rb').read()
PATIENTSLIST_PAGE = open("templates/patientsList.html", 'rb').read()
PATIENTHISTORY_PAGE = open("templates/patientHistory.html", 'rb').read()


class MyServer(SimpleHTTPRequestHandler):
    def do_GET(self):
        lower_path = self.path.lower()

        self.send_response(200)
        if lower_path == '/info':
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("%s,%s,%s,%s" % (str(HR), str(BL), str(AC), str(VR)), "utf-8"))
            return
        elif lower_path in ['/hrrecord', '/patienthistory', '/patientslist', '/plot']:
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            if lower_path == '/hrrecord':
                self.wfile.write(HRRECORD_PAGE)
            elif lower_path == '/patienthistory':
                self.wfile.write(PATIENTHISTORY_PAGE)
            elif lower_path == '/patientslist':
                self.wfile.write(PATIENTSLIST_PAGE)
            elif lower_path == '/plot':
                self.wfile.write(bytes(FIG, 'utf-8'))
        elif lower_path in ['/logo', '/profile']:
            self.send_header("Content-Type", "")
            self.end_headers()
            if lower_path == '/logo':
                self.wfile.write(LOGO)
            elif lower_path == '/profile':
                self.wfile.write(PROFILE)
        else:
            SimpleHTTPRequestHandler.do_GET(self)


class Server:
    @staticmethod
    def initiate():
        os.chdir('templates/')
        webServer = ThreadingHTTPServer((hostName, serverPort), MyServer)
        print("Server started http://%s:%s" % (hostName, serverPort))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")

    @staticmethod
    def new_info(info, fig):
        global HR, BL, AC, VR, FIG
        HR, BL, AC, VR = info
        FIG = fig
