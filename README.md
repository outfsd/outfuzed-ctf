# Outfuzed – CTF Writeup


# How I built it
Outfuzed is a small self-hosted Flask CTF: a fake fruit-store website hiding a login flow, a forgeable session cookie and a knowledge check. It consists of three levels, which are explained below. I built it with Python and Flask and hosted it on my VM. Each Level is a a seperate route with its own flag, and the session cookie is intentionally signed with a weak secret so it can be forged.

# Play it
The CTF is also available as Tryhackme room: https://tryhackme.com/jr/outfuzedctf

## Hosting

```bash
cd cybersec-project
source venv/bin/activate
python3 app.py
```
---

## Level 1 — Bruteforce

### The two logins

The nav **Login** button leads to a form posting to `/fake-login`  the honeypot. Any input logs you in and redirects to `/wrongdashboard`, which tells you you're in the wrong place.

The real login is at `/login`, not linked anywhere on the site. Correct creds redirect to `/dashboard`, where the flag is.

### Finding the real login

Not linked in the UI  found via recon: viewing page source shows the honeypot form is a dead end, and directory brute-forcing (`gobuster`, `ffuf`, etc. against common paths) quickly reveals `/login`.


gobuster dir -u http://127.0.0.1:5000 -w ~/common.txt


### Cracking it

Standard credential bruteforce with Hydra against a common wordlist (e.g. `rockyou.txt`) hits fast, since `admin`/`password123` are both very common values.

- Set Burp as your browser's proxy, turn on intercept.
- Submit the login form with any test input.
- Burp catches the POST request — check the path (`/login`) and the body param names (`uname`, `psw`).
- Submit wrong creds, look at the response — grab the failure string (`Invalid credentials`).
- Plug those three into Hydra's `http-post-form` syntax.


hydra -l admin -P ~/rockyou.txt 127.0.0.1 -s 5000 http-post-form "/login:uname=^USER^&psw=^PASS^:Invalid credentials"


### Results

- Credentials: `admin` / `password123`
- Flask `secret_key`: `supersecretkey123`
- Flag: `FLAG{you_bruteforced_your_way_in_123}`

---

## Level 2 — Cookie Forging

### Finding the lead

Viewing the page source of `/dashboard` (after solving Level 1) reveals a comment hinting at `/admin-panel` and a `superadmin` cookie field.

### The vulnerability

The Flask session cookie is signed with a weak `secret_key`. If you can crack the key, you can forge your own valid cookie — no login required.

### Steps

1. **Get a signed cookie** — log in normally, then grab the `session` cookie value from DevTools (Application → Cookies).
2. **Crack the secret key:**
```bash
   flask-unsign --unsign --cookie 'YOUR_COOKIE' --wordlist /usr/share/wordlists/rockyou.txt --no-literal-eval
```
   (`--no-literal-eval` avoids a crash on numeric-looking wordlist entries.)
3. **Forge a new cookie** with the cracked secret:
```bash
   flask-unsign --sign --cookie "{'superadmin': True}" --secret 'CRACKED_SECRET'
```
4. **Swap the cookie** — paste the forged value over your `session` cookie in DevTools, reload.
5. **Visit the protected route:**

http://127.0.0.1:5000/admin-panel


### Results

- Secret key: `letmein`
- Flag: `FLAG{cooked_the_cookie_myself_456}`

---

## Level 3 — Knowledge Check

### Finding it

`/admin-panel` (from Level 2) has a "Take the Knowledge Check →" button, plus a hint that this isn't the final flag yet. The route itself is gated behind the same `superadmin` session as `/admin-panel`, so it can't be reached out of order.

### The gate

`/quiz` asks four questions about the tools used in Levels 1 and 2. Answering all four correctly sets a session flag that unlocks `/vault` — visiting `/vault` directly without passing the quiz redirects you back.

### Answers

1. Bruteforce tool used on the login → `hydra`
2. Tool used to intercept HTTP requests → `burp`
3. What you forged to bypass authentication → `cookie`
4. Tool used to crack the Flask secret key → `flask-unsign`

### Results

- Flag: `FLAG{knowledge_is_the_real_exploit_789}`

---

**Note:** press F12 to open DevTools.
**Note:**
I used AI (Claude) as a support tool for planning and troubleshooting while building this project.
