# import socket
# import ssl
# import re

# def fetch_url(url, is_redirect=False):
#     try:
#         parsed_url = re.match(r'http(s)?://([^/]+)(.*)', url)
#         if not parsed_url:
#             return url, "Invalid URL"

#         protocol = parsed_url.group(1)
#         host = parsed_url.group(2)
#         path = parsed_url.group(3) if parsed_url.group(3) else '/'
        
#         port = 443 if protocol == 's' else 80
#         address = (host, port)
#         request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        
#         if protocol == 's':
#             context = ssl.create_default_context()
#             with socket.create_connection(address) as sock:
#                 with context.wrap_socket(sock, server_hostname=host) as ssock:
#                     ssock.sendall(request.encode())
#                     response = ssock.recv(4096).decode()
#         else:
#             with socket.create_connection(address) as sock:
#                 sock.sendall(request.encode())
#                 response = sock.recv(4096).decode()
        
#         headers, _, body = response.partition('\r\n\r\n')
#         status_line = headers.splitlines()[0]
#         status_code = int(status_line.split()[1])
        
#         # Formatting the status correctly
#         status_message = " ".join(status_line.split()[2:])
        
#         if status_code in (301, 302):
#             location_header = re.search(r'Location: (.*)', headers, re.IGNORECASE)
#             if location_header:
#                 new_url = location_header.group(1).strip()
#                 if not new_url.startswith('http'):
#                     new_url = f"http://{host}{new_url}"
#                 if not is_redirect:
#                     print(f"URL: {url}\nStatus: {status_code} {status_message}")
#                 print(f"Redirected URL: {new_url}")
#                 redirected_url, redirected_status = fetch_url(new_url, True)
#                 print(f"Status: {redirected_status}")
#                 return new_url, redirected_status
        
#         return url, f"{status_code} {status_message}"

#     except socket.gaierror:
#         return url, "Network Error"
#     except Exception as e:
#         return url, f"Error: {e}"

# def main(file_path):
#     with open(file_path) as f:
#         urls = f.readlines()

#     for url in urls:
#         url = url.strip()
#         fetched_url, status = fetch_url(url)
#         if fetched_url == url:
#             print(f"URL: {fetched_url}\nStatus: {status}\n")

# if __name__ == '__main__':
#     import sys
#     if len(sys.argv) != 2:
#         print("Usage: python monitor.py <urls-file>")
#         sys.exit(1)
#     main(sys.argv[1])

import socket
import ssl
import re

def fetch_url(url, is_redirect=False):
    try:
        parsed_url = re.match(r'http(s)?://([^/]+)(.*)', url)
        if not parsed_url:
            return url, "Invalid URL"

        protocol = parsed_url.group(1)
        host = parsed_url.group(2)
        path = parsed_url.group(3) if parsed_url.group(3) else '/'
        
        port = 443 if protocol == 's' else 80
        address = (host, port)
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        
        if protocol == 's':
            context = ssl.create_default_context()
            with socket.create_connection(address) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    ssock.sendall(request.encode())
                    response = ssock.recv(4096).decode()
        else:
            with socket.create_connection(address) as sock:
                sock.sendall(request.encode())
                response = sock.recv(4096).decode()
        
        headers, _, body = response.partition('\r\n\r\n')
        status_line = headers.splitlines()[0]
        status_code = int(status_line.split()[1])
        
        # Formatting the status correctly
        status_message = " ".join(status_line.split()[2:])
        
        if status_code in (301, 302):
            location_header = re.search(r'Location: (.*)', headers, re.IGNORECASE)
            if location_header:
                new_url = location_header.group(1).strip()
                if not new_url.startswith('http'):
                    new_url = f"http://{host}{new_url}"
                if not is_redirect:
                    print(f"URL: {url}\nStatus: {status_code} {status_message}")
                print(f"Redirected URL: {new_url}")
                redirected_url, redirected_status = fetch_url(new_url, True)
                print(f"Status: {redirected_status}\n")
                return new_url, redirected_status
        
        return url, f"{status_code} {status_message}"

    except socket.gaierror:
        return url, "Network Error"
    except Exception as e:
        return url, f"Error: {e}"

def main(file_path):
    with open(file_path) as f:
        urls = f.readlines()

    for url in urls:
        url = url.strip()
        fetched_url, status = fetch_url(url)
        if fetched_url == url:
            print(f"URL: {fetched_url}\nStatus: {status}\n")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python monitor.py <urls-file>")
        sys.exit(1)
    main(sys.argv[1])
