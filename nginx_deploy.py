#!/usr/bin/env python3

import os
import subprocess
import argparse
from pathlib import Path

NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"
WEB_ROOT_TEMPLATE = "/var/www/{domain}/html"

def run(cmd, check=True):
    print(f"→ {cmd}")
    subprocess.run(cmd, shell=True, check=check)

def ensure_packages():
    run("apt update")
    run("apt install nginx certbot python3-certbot-nginx -y")

def create_web_root(domain):
    web_root = WEB_ROOT_TEMPLATE.format(domain=domain)
    os.makedirs(web_root, exist_ok=True)
    index_path = os.path.join(web_root, "index.html")
    if not os.path.exists(index_path):
        with open(index_path, "w") as f:
            f.write(f"<h1>Welcome to {domain} - Secured by Let's Encrypt</h1>")

def create_nginx_config(domain):
    config = f"""
server {{
    listen 80;
    server_name {domain} www.{domain};

    root {WEB_ROOT_TEMPLATE.format(domain=domain)};
    index index.html;

    location / {{
        try_files $uri $uri/ =404;
    }}
}}
"""
    config_path = os.path.join(NGINX_SITES_AVAILABLE, domain)
    with open(config_path, "w") as f:
        f.write(config)

    symlink_path = os.path.join(NGINX_SITES_ENABLED, domain)
    if not os.path.exists(symlink_path):
        os.symlink(config_path, symlink_path)

    run("nginx -t")
    run("systemctl reload nginx")

def obtain_certificate(domain):
    run(f"certbot --nginx -n --agree-tos --redirect -m admin@{domain} -d {domain} -d www.{domain}")

def check_dns(domain):
    print(f"🔍 Checking DNS for {domain}...")
    import socket
    try:
        ip = socket.gethostbyname(domain)
        print(f"✅ {domain} resolves to {ip}")
    except socket.gaierror:
        print(f"⚠️ Domain {domain} does not resolve. Set up DNS first.")
        exit(1)

def main():
    if os.geteuid() != 0:
        print("❌ This script must be run as root (use sudo)")
        exit(1)

    parser = argparse.ArgumentParser(description="Secure a domain with Nginx + Let's Encrypt")
    parser.add_argument("-d", "--domain", required=True, help="Domain name to secure")
    args = parser.parse_args()
    domain = args.domain

    check_dns(domain)
    ensure_packages()
    create_web_root(domain)
    create_nginx_config(domain)
    obtain_certificate(domain)

    print(f"\n✅ {domain} is now secured and accessible at https://{domain}/")

if __name__ == "__main__":
    main()
