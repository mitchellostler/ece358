import socket
from DNSMessage import DNSMessage, DNSRequestType

DNS_TABLE = {
    "google.com" : [
        { "ttl": 260, "rd_len": 4, "rd_data": [192, 165, 1, 1] },
        { "ttl": 260, "rd_len": 4, "rd_data": [192, 165, 1, 10] }, 
    ], 
    "youtube.com": [{ "ttl": 160, "rd_len": 4, "rd_data": [192, 165, 1, 2] }],
    "uwaterloo.com": [{ "ttl": 160, "rd_len": 4, "rd_data": [192, 165, 1, 3] }],
    "wikipedia.org": [{ "ttl": 160, "rd_len": 4, "rd_data": [192, 165, 1, 4] }],
    "amazon.ca": [{ "ttl": 160, "rd_len": 4, "rd_data": [192, 165, 1, 5] }],
}

class Server:
    def __init__(self, host='localhost', port=12345):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(1)
        print("Server started, waiting for client to connect...")
        self.conn, self.addr = self.server_socket.accept()
        print(f"Client connected: {self.addr}")

    def send(self, data):
        self.conn.send(data)

    def recv(self):
        return self.conn.recv(1024)

    def cleanup(self):
        self.conn.close()

def out_data(label, data):
    print(label)
    packed_hex = ' '.join(f"{byte:02x}" for byte in data)
    packed_hex_lines = [packed_hex[i:i+48] for i in range(0, len(packed_hex), 48)]
    print("\n".join(packed_hex_lines))

if __name__ == "__main__":
    server = Server('localhost', 12345)
    while True:
        data = server.recv()
        out_data("Request: ", data)

        rx_query = DNSMessage(DNSRequestType.QUERY, from_bytes=data)
        ans = rx_query.generate_reply()
        url = rx_query.url_from_qname()
        try:
          for entry in DNS_TABLE[url]:
            ans.add_answer(**entry)
        except:
            print("Invalid Entry")
            break
        
        packed_ans = ans.to_bytes()
        out_data("Response: ", packed_ans)
        server.send(packed_ans)
    server.cleanup()
