import requests
import re

AUTH_EMAIL = "" # Email address associated with Cloudflare account
AUTH_KEY = "" # Global API Key found in Cloudflare account settings
ZONE_ID = "" # e.g. 1234567890abcdef1234567890abcdef
RECORD_NAMES = [
    # e.g. subdomain.example.com
]

traceUrl = "https://ifconfig.me/ip"
baseUrl = f"https://api.cloudflare.com/client/v4/zones/{ZONE_ID}"

ipRegex = r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
headers = {
    "Content-Type": "application/json",
    "X-Auth-Email": AUTH_EMAIL,
    "X-Auth-Key": AUTH_KEY,
}

try:
    publicIp = requests.get(traceUrl).text
    
except requests.exceptions.RequestException:
    print("[-] Connection Problem. Unable to obtain your public IP address")
    exit(1)

if not (re.match(ipRegex, publicIp)):
    print("[-] Incorrect Format. Unable to update your DDNS record")
    exit(1)

try:
    for name in RECORD_NAMES:
        record = requests.get(f"{baseUrl}/dns_records?type=A&name={name}", headers=headers).json()
        domainIp = record["result"][0]["content"]
        recordId = record["result"][0]["id"]
        
        if (domainIp == publicIp):
            print(f"[+] No Change. Your cloudflare's DDNS record is up to date for {name}")
            break

        updateRecord = requests.put(f"{baseUrl}/dns_records/{recordId}", headers=headers, json={
            "type": "A",
            "name": name,
            "content": publicIp,
            "ttl": 1,
            "proxied": True
        }).json()

        print(f"[+] Success. Your cloudflare's DDNS record has been updated for {name}")

except (TypeError, requests.exceptions.RequestException):
    print("[-] Connection Problem. Unable to obtain your cloudflare's DDNS record")
    exit(1)