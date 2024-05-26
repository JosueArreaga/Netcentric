
import sys
import socket
import ssl

# Helper function to parse URLs
def parse_url(url):
    try:
        protocol, rest = url.split('://')
        host_path = rest.split('/', 1)
        host = host_path[0]
        path = '/' + host_path[1] if len(host_path) > 1 else '/'
        port = 443 if protocol == 'https' else 80
        return protocol, host, port, path
    except ValueError:
        print(f"Error parsing URL: {url}. Expected format 'protocol://host/path'.")
        return None, None, None, None


# Function to manually send HTTP requests and fetch the status
def fetch_url(url):
    protocol, host, port, path = parse_url(url)
    sock = None
    response = b''
    
    try:
        # Create a TCP socket
        if protocol == 'https':
            context = ssl.create_default_context()
            sock = context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=host)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sock.connect((host, port))
        # Manually construct and send HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.send(request.encode('utf-8'))

        # Receive HTTP response
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data
    except Exception as e:
        print(f'URL: {url}\nStatus: Network Error\n{str(e)}\n')
        return

    # Close the socket
    sock.close()
    # Decode and analyze the HTTP response
    response_decoded = response.decode('utf-8')
    status_line = response_decoded.split('\r\n')[0]
    status_code = status_line.split(' ')[1]
    print(f'URL: {url}\nStatus: {status_code} {status_line.split(" ", 2)[2]}\n')

# Main function to process URLs from file
def main(urls_file):
    try:
        with open(urls_file, 'r') as file:
            urls = file.readlines()
        for url in urls:
            fetch_url(url.strip())
    except Exception as e:
        print(f'Error reading URLs file: {str(e)}')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python monitor.py urls-file')
        sys.exit(1)

    urls_file = sys.argv[1]
    main(urls_file)
