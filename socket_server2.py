import socket

def Main():
   
    
    host = '192.168.100.187' #Server ip
    port = 4000

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    
    print("Server Started")
    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode('utf-8')
        print("Message from: " + str(addr))
        print("From connected user: " + data)
        data = data.upper()
        #print(type(data))
        print("Sending: " + data)
        s.sendto(data.encode('utf-8'), addr)
        a=[345.34, 56.43]
        #b=str(a[0])+','+str(a[1])
#         b=str(a).strip('[]')
        b=str(a)
        s.sendto(b.encode(),addr)
    c.close()

if __name__=='__main__':
    Main()
