# InvinciNote
### Bezpieczna aplikacja do przechowywania notatek

## Testowe uruchomienie

```bash
git clone <repo-url>
```

```bash
openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout localhost.key -out localhost.crt
```

common name: localhost

```bash
docker-compose build
```

```bash
docker-compose up
```

Otwarcie <https://127.0.0.1>

## Architektura
- aplikacja Flask
- baza danych SQLite 
- serwer uWSGI
- serwer proxy Nginx
  
## Zaimplementowane funkcje
- publiczne i prywatne notatki obsługujące markdown
- szyfrowanie notatki
- przechowywanie hashy haseł z solą i pieprzem
- weryfikacja siły hasła
- dwuetapowa weryfikacja totp
