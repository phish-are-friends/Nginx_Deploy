# Nginx_Deploy
Quick Python script for deploying a secure domain with Nginx and Cert Bot

For the script to work, you need to ensure that you have within your DNS records an A record for @ and www that point to your server IP address.

Once you DNS record is configured, simply run the script like so: python3 nginx_deploy.py -d yourdomainname.com
