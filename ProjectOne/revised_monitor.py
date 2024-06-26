
import socket
import ssl
import re

def fetch_url(url, is_redirect=False, is_referenced=False):
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
                    response = b""
                    while True:
                        data = ssock.recv(4096)
                        if not data:
                            break
                        response += data
        else:
            with socket.create_connection(address) as sock:
                sock.sendall(request.encode())
                response = b""
                while True:
                    data = sock.recv(4096)
                    if not data:
                        break
                    response += data
        
        headers, _, body = response.partition(b'\r\n\r\n')
        headers = headers.decode()
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
        
        if not is_redirect and not is_referenced:
            print(f"URL: {url}\nStatus: {status_code} {status_message}")
        
        if status_code == 200 and not is_redirect and not is_referenced:
            # Find all referenced images in the body
            try:
                body_text = body.decode()
                image_urls = re.findall(r'<img\s+src=["\'](.*?)["\']', body_text, re.IGNORECASE)
                for img_url in image_urls:
                    if not img_url.startswith('http'):
                        if img_url.startswith('/'):
                            img_url = f"http://{host}{img_url}"
                        else:
                            img_url = f"http://{host}/{img_url}"
                    referenced_url, referenced_status = fetch_url(img_url, False, True)
                    print(f"Referenced URL: {referenced_url}\nStatus: {referenced_status}")
            except UnicodeDecodeError as e:
                print(f"\nReferenced URL: {url}\nStatus: Error: {e}")
        
        return url, f"{status_code} {status_message}"

    except socket.gaierror:
        print(f'\nURL: {url}\nStatus: Network Error')
        return url, "Network Error"
    except Exception as e:
        return url, f"Error: {e}"

def main(file_path):
    with open(file_path) as f:
        urls = f.readlines()

    processed_urls = set()
    for url in urls:
        url = url.strip()
        if url not in processed_urls:
            fetched_url, status = fetch_url(url)
            processed_urls.add(fetched_url)
            if fetched_url == url:
                print("\n")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: python monitor.py <urls-file>")
        sys.exit(1)
    main(sys.argv[1])


