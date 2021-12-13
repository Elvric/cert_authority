# Black Box Review
In this section we will describe our approach to breach the system in a black-box penetration testing. We used a machine connecting to the External Firewall from the Internet, simulating an external attacker trying to violate the system.

## Port Scanning

### Port status
`nmap -p 0-65535 www.imovies.com` shows port 22,80,443 as open. Ports 8008 and 8080 are closed. All the other ports are filtered.
This means that ports 8008 and 8080 are not filtered by any firewall rule, but no service on the host is listening on such ports.
### Reconnaissance
`nmap -O -sV -p 80,443,22,8008,8080 www.imovies.com` gives the version of the services running on the ports as well as information on the host Operating System. Note that we probe also closed ports, in order to have a complete fingerprint of the TCP/IP stack running on the host OS.
Results:
- ports 80 and 443 expose a nginx reverse proxy version 1.18.0. (Ubuntu)
- port 22 exposes OpenSSH version 8.2p1 Ubuntu 4ubuntu0.3 (Ubuntu Linux; protocol 2.0)
We do not have clear information regarding the kernel version of the host, since `nmap` confidence for guesses ranging from kernel version 2.6.32 to 4.11.
However, considering the versions of the installed service, we can infer with good probability that the host is running Ubuntu Focal 20.04 LTS.

#### Webserver (unrealistic, we can't really access webserver from outside no?)
`nmap webserver` reports the host as down. This is because nmap first pings the host machine (ICMP) and if up starts performing a port scan. The external firewall blocks ICMP to webserver.

## Enumeration
`ffuf -t 10  -mc all -u https://www.imovies.com/FUZZ -w contents.txt -fc 404` we are able to enumerate the following endpoints, thanks to the `contents.txt` file feeded to `ffuf`, a Go based fuzzer for penetration testing. With this setting we are filtering all requests which return a 404 Not Found status. This file contains common endpoint names used in real web application recovered from `https://gist.github.com/yassineaboukir/8e12adefbd505ef704674ad6ad48743d`, plus some endpoints we defined having in mind that the scope of the system is to serve as a Certificate Authority for the company (e.g we applied simple transformations, such as from "admin" to "admin_ca", "ca_admin", "admin-ca", "ca-admin").
The results are the following (the list is meant to be non-exhaustive):
- revoke-certificate      [Status: 302, Size: 272, Words: 21, Lines: 4]
- ca-admin                [Status: 302, Size: 252, Words: 21, Lines: 4]
- issue                   [Status: 302, Size: 246, Words: 21, Lines: 4]
- login                   [Status: 200, Size: 1016, Words: 130, Lines: 34] (the request has a query arg ?next=/ . It's useless, it's just used by Flask login thingy)
- logout                  [Status: 302, Size: 208, Words: 21, Lines: 4]
All endpoints but `login` return a 302 status since they are redirecting to `login` for user authentication.

## Vulnerabilities
Using `BurpSuite`, we conducted an active scan on the hosts and its endpoints. Furthermore, we have tried payloads for testing common web vulnerabilities, in particular XSS, SQLi, and SSTI. The application seems to be not vulnerable to these attacks.
The only vulnerability (of low severity) we managed to find in this step is related to the session cookie. It lacks the secure flag set. If an attacker were able to sniff requests to http://www.imovies.com, she would be able to steal the session cookie from the victim. Note that this applies even if the reviewed system redirects to `https`. An acceptable countermeasure is the use of `Strict-Transport-Security`, which is correctly applied by the system with a timeout of around 2 years.
There is also a minor issue in the TLS certificate provided by the webserver: the certificate is only valid for the domain `imovies.com`, not `www.imovies.com`. This might lead to MITM attacks if attacker were able to register the `www.imovies.com` domain and have a certificate issued for that.

# White Box reviewing

## External Firewall
The machine runs just a firewall service using `nftables`. No other services are hosted on the machine apart from `OpenSSH`. The firewall rules meet the security requirements of the system.
The firewall accepts only SSH traffic and HTTP/S traffic as input, while it forwards only HTTP/S traffic to the webserver. The forwarding is implemented via a `nat hook`: incoming traffic from internet is nat-ed such that the destination address is the one of the webserver. The source address of the traffic is then set to the one of the firewall interface facing the DMZ, i.e `192.168.5.3`.
The only critical point found in the configuration is that no filtering on the outbound traffic is done: this might lead to potential data exfiltration if one the webserver gets compromised.

## Webserver
The webserver hosts the main logic of the application. The stack of the application is the following:
- `nftables` rules to filter inbound traffic. Open ports are: 80,443, 8080,8008,22,631 (should we investigate 631?)
- `nginx` as reverse proxy. There are 2 `server` blocks defined: one listens for http traffic and redirects it to https (the only endpoint server on http is `/crl.pem` to retrieve the revocation list). The https server offers `STS` with 2 years timeout, and optional TLS client authentication.
- `gunicorn` serves as "Web Server Gateway Interface" (WSGI) HTTP server (version 20.1.0)
- `Flask` the main application is served through Flask (v 2.0.3). The Frontend is realized thanks to Flask `render_template` function, which exploits `Jinja2` rendering engine. The application connects to the database thanks to `mysqlclient` (v 2.0.3), and to the internal "ca-server" thanks to the `requests` library (v 2.26.0). The application follows all the security common practice regarding users' input sanitization. We tested the application using a Black Box approach, looking for common web vulnerabilities like SQLi, XSS, HTML attribute injection. In our White Box review, once acknowledged that the application runs `Flask`, we extensively tested for SSTI. By Black Box testing and White Box code inspection, we could assess the all users' inputs are correctly sanitized (e.g SQL queries use prepared statements, Flask correctly applies template rendering using curly braces and Jinja2 autoescape feature for preventing SSTI and XSS attacks).
User login and session management is implemented using `flask_login` library, which provides a session cookie (refer to the Black Box review for the Secure Flag vulnerability). The application deploy also CSRF protection using Flask `flask_wtf` library. Every POST request must include the CSRF token generated by the application in order to be valid.

#Back Doors

##1. Broken Access Control
It is possible to login as any user by intercepting the POST request to the /login endpoint and stripping away the password parameter. It is thus sufficient to know the userid of the user.