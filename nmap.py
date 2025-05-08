import nmap
import requests

def scan_subdomains(domain, subdomains):
    nm = nmap.PortScanner()
    live_hosts = []

    for subdomain in subdomains:
        full_domain = f"{subdomain}.{domain}"
        try:
            nm.scan(hosts=full_domain, arguments='-sn')  # Ping scan
            if nm.all_hosts():
                live_hosts.append(full_domain)
        except Exception as e:
            print(f"Error scanning {full_domain}: {e}")

    return live_hosts

def check_http_status(hosts):
    valid_hosts = []

    for host in hosts:
        try:
            response = requests.get(f"http://{host}", timeout=5)
            if response.status_code == 200:
                valid_hosts.append(host)
        except requests.RequestException:
            pass

    return valid_hosts

def save_to_file(filename, hosts):
    with open(filename, 'w') as file:
        for host in hosts:
            file.write(f"{host}\n")

if __name__ == "__main__":
    domain = input("Enter the domain to scan (e.g., example.com): ")
    subdomains = [
        "www", "mail", "ftp", "test", "dev", "api", "blog", "shop"
    ]  # Add more subdomains as needed

    print("Scanning for live subdomains...")
    live_hosts = scan_subdomains(domain, subdomains)

    print("Checking HTTP status of live hosts...")
    valid_hosts = check_http_status(live_hosts)

    output_file = "valid_hosts.txt"
    print(f"Saving valid hosts to {output_file}...")
    save_to_file(output_file, valid_hosts)

    print("Done!")