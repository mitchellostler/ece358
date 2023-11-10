import socket
from DNSMessage import DNSMessage, DNSRequestType
class Client:
    def __init__(self, host, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))

    def send(self, data):
        self.client_socket.send(data)

    def recv(self):
        return self.client_socket.recv(1024)
    
    def cleanup(self):
        self.client_socket.close()

if __name__ == "__main__":
    client = Client('localhost', 12345)
    while True:
        domain_name = input("Enter domain name: ")
        if domain_name.lower() == "end":
            print("Session Ended")
            client.cleanup()
            break
        query = DNSMessage(DNSRequestType.QUERY, domain_name)
        packed = query.to_bytes()
        client.send(packed)
        packed_ans = client.recv()
        rx_ans = DNSMessage(DNSRequestType.RESPONSE, from_bytes=packed_ans)
        rx_ans.print_responses()
