import enum, random, bitstruct

class DNSRequestType(enum.Enum):
    QUERY = 0
    RESPONSE = 1

class DNSMessage:
    HDR_LEN = 12
    def __init__(self, type, url="", from_bytes=None ):
        self.FMT = ["u16", "u1u4u1u1u1u1u3u4",
              "u16", "u16", "u16", "u16"]
        self.DNS_HDR = {
          "id": 0, "qr": 0, "opcode": 0,
          "aa": 1, "tc": 0, "rd": 0, "ra": 0,
          "z": 0, "rcode": 0, "qdcount": 1, 
          "ancount": 0, "nscount": 0, 
          "arcount": 0
        }
        self.QUERY = {
            "qname": [], # list of octets
            "qtype": int("0001", 16),
            "qclass": int("0001", 16),
        }
        self.ANSWER = {
            "name": int("C00C", 16),
            "type": int("0001", 16),
            "class": int("0001", 16),
            "ttl": 0,
            "rdlen": 0,
            "rddata": []
        }
        self.ANSWERS = []
        self.DNS_HDR['id'] = random.randint(0, 65535)
        self.DNS_HDR['qr'] = type.value
        self.type = type
        if type == DNSRequestType.QUERY and url:
            self.QUERY['qname'] = self.generate_qname(url)
        
        if from_bytes:
            self.from_bytes(from_bytes)
    
    def change_type(self, type):
        self.DNS_HDR['qr'] = type.value
        self.type = type
    
    def url_from_qname(self):
        substrings = []
        i = 0
        while i < len(self.QUERY["qname"]):
            length = self.QUERY["qname"][i]
            if length == 0:
                break
            substring = self.QUERY["qname"][i+1:i+1+length]
            substrings.append("".join(chr(byte) for byte in substring))
            i += length + 1
        return '.'.join(substrings)
        

    def generate_reply(self):
        # start with query message
        ans = DNSMessage(DNSRequestType.QUERY, from_bytes=self.to_bytes())
        ans.change_type(DNSRequestType.RESPONSE)
        return ans

    def add_answer(self, ttl, rd_len, rd_data):
        assert(rd_len == len(rd_data))
        ans = dict(self.ANSWER)
        ans["ttl"] = ttl
        ans["rdlen"] = rd_len
        ans["rddata"] = rd_data
        self.ANSWERS.append(ans)
        self.DNS_HDR["ancount"] += 1
        assert(self.DNS_HDR["ancount"] == len(self.ANSWERS))

    def generate_qname(self, url):
        labels = url.split('.')
        octets = bytearray()
        for l in labels:
            b = l.encode()
            octets.append(len(b))
            octets.extend(b)
        octets.append(0)
        return octets

    def to_bytes(self):
        # Create format string for hdr + question
        q_fmt = "u8"*len(self.QUERY["qname"]) + "u16u16"
        hdr_fmt = "".join(self.FMT)
        fmt = hdr_fmt + q_fmt

        q_tuple = tuple(self.QUERY["qname"]) + \
          (self.QUERY["qtype"], self.QUERY["qclass"])
        values = tuple(self.DNS_HDR.values()) + q_tuple
        if self.type == DNSRequestType.RESPONSE:
            # Answer section
            for i in range(self.DNS_HDR["ancount"]):
                a_fmt = "u16"*3 + "u32u16" + "u8"*self.ANSWERS[i]["rdlen"]
                a_tuple = (self.ANSWERS[i]["name"],
                           self.ANSWERS[i]["type"],
                           self.ANSWERS[i]["class"],
                           self.ANSWERS[i]["ttl"],
                           self.ANSWERS[i]["rdlen"]) + tuple(self.ANSWERS[i]["rddata"])
                fmt += a_fmt
                values += a_tuple

        return bitstruct.pack(fmt, *values)
    
    def from_bytes(self, bytes):
        # Parse header into dictionary
        hdr_len = self.HDR_LEN
        hdr_bytes = bytes[:hdr_len]
        hdr_fmt = "".join(self.FMT)
        hdr_values = bitstruct.unpack(hdr_fmt, hdr_bytes)
        for key, value in zip(self.DNS_HDR.keys(), hdr_values):
            self.DNS_HDR[key] = value
        
        # Parse query section
        msg_bytes = bytes[hdr_len:]
        i = 0
        while i < len(msg_bytes):
            if msg_bytes[i] == 0:
                i+= 1
                break
            i += msg_bytes[i] + 1
        q_len = i + 4
        q_bytes = msg_bytes[:q_len]
        q_fmt = "u8"*len(q_bytes[:-4]) + "u16u16"
        q_values = bitstruct.unpack(q_fmt, q_bytes)
        self.QUERY["qname"] = list(q_values[:-2])
        self.QUERY["qtype"] = q_values[-2]
        self.QUERY["qclass"] = q_values[-1]

        if self.type == DNSRequestType.RESPONSE:
          a_bytes = msg_bytes[q_len:]
          for i in range(self.DNS_HDR["ancount"]):
              # Read answer values
              a_fmt = "u16"*3 + "u32u16" 
              a_values = bitstruct.unpack(a_fmt, a_bytes)
              self.ANSWERS.append(dict(self.ANSWER))
              self.ANSWERS[i]["name"] = a_values[0]
              self.ANSWERS[i]["type"] = a_values[1]
              self.ANSWERS[i]["class"] = a_values[2]
              self.ANSWERS[i]["ttl"] = a_values[3]
              self.ANSWERS[i]["rdlen"] = a_values[4]
              rd_len = self.ANSWERS[i]["rdlen"]
              a_fmt = "u8"*self.ANSWERS[i]["rdlen"]
              a_hdr_len = 12
              a_bytes = a_bytes[a_hdr_len:]
              self.ANSWERS[i]["rddata"] = list(bitstruct.unpack(a_fmt, a_bytes))
              d_len = self.ANSWERS[i]["rdlen"]
              a_bytes = a_bytes[d_len:]

    def print_responses(self):
        assert self.type == DNSRequestType.RESPONSE
        print("Response: ")
        for ans in self.ANSWERS:
            print("{}: type A, class IN, TTL {}, addr ({}) {}".format(
                self.url_from_qname(), ans["ttl"], ans["rdlen"], '.'.join([str(d) for d in ans["rddata"]])
            ))