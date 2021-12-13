# Black Box Review

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
`ffuf -t 10  -mc all -u https://www.imovies.com/FUZZ -w contents.txt -fc 404` we are able to enumerate the following endpoints, thanks to the `contents.txt` file feeded to `ffuf`, a Go based fuzzer for penetration testing. With this setting we are filtering all requests which return a 404 Not Found status. This file contains common endpoint names used in real web application recovered from `https://gist.github.com/yassineaboukir/8e12adefbd505ef704674ad6ad48743d`, plus some endpoints we defined having in mind that the scope of the system is to serve as a Certificate Authority for the company.
The results are the following (the list is meant to be non-exhaustive):
- revoke-certificate      [Status: 302, Size: 272, Words: 21, Lines: 4]
- ca-admin                [Status: 302, Size: 252, Words: 21, Lines: 4]
- issue                   [Status: 302, Size: 246, Words: 21, Lines: 4]
- login                   [Status: 200, Size: 1016, Words: 130, Lines: 34]
- logout                  [Status: 302, Size: 208, Words: 21, Lines: 4]
All endpoints but `login` return a 302 status since they are redirecting to `login` for user authentication.

## Vulnerabilities
Using `BurpSuite`, we conducted an active scan on the hosts and its endpoints. Furthermore, we have tried payloads for testing common web vulnerabilities, in particular XSS, SQLi, and SSTI. The application seems to be not vulnerable to these attacks.
The only vulnerability (of low severity) we managed to find in this step is related to the session cookie. It lacks the secure flag set. If an attacker were able to sniff requests to http://www.imovies.com, she would be able to hijack the session cookie for the victim. Note that this applies even if the reviewed system redirects to `https`. An acceptable countermeasure is the use of `Strict-Transport-Security`, which is correctly applied by the system with a timeout of around 2 years.
There is also a minor issue in the TLS certificate provided by the webserver: the certificate is only valid for the domain `imovies.com`, not `www.imovies.com`. This might lead to MITM attacks if attacker were able to register the `www.imovies.com` domain and have a certificate issued for that.