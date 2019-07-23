import requests
import ssl

#Post Access Token Request
headers = { 'Content-Type': 'application/x-www-form-urlencoded' }
data = { 'grant_type': 'refresh_token', 'access_type': 'offline',
    'refresh_token': 'jPkgKy8CQ+v4BhxuwPUtkngDA1K40hjTOzysMSyoNjS0pqdxrzdpj5Xcnf2Iqb48fFzU9u2MFngSYSyhjcMYv4IJlPnnMQJ5rrUgtE9EvfsRS3Oz6J6z6cEeJd7x0diHUmS9bsh5XCVT42Gg8olDhGW0yw4w2rrE1z5N0nRjo7QM7ihSuHGarSoa9f/RjagbjLDRqnOSxK9TE3Q8VSKS4aWqZjt9FoBg0MT3BxDyQcpXJa+11mUGg9MEMUqMTKsy1kzuWmokXhvp4FYm0KwXViEOWo6gBYc+McAOctHhkxZOTRs/GWlyweevki7pfBkE85vhJG3Cy2E43vGh+LRoCJ/hEoKtbaEAYCVvvZ1OiHYKVXRVWMbemQj268HVuvjjRpmytzbqi9xwEwFeZfzVKbaTiR7TMQYrzq08kR9QQW/aq0qlByujqDXwP4R100MQuG4LYrgoVi/JHHvlc9Bo9D7bFHC2h/fgMbPXe36jaOQojdPAKaLUvsC30sGUkVu8GtyiD+HfVu5DpW7wyk8CESK2E28nLZ7gDzC+gjqFveFonxzhmWa5wHlvgyZG4n5TatB5J2ZguTcisS0/kgVoUHNim6CG+wTubQPp4CqXj5aDYg86T8xxz5GYuvUzdHKhycKwUBbJZYIDW/g63ptMMT2Buk57WTMFwUxkXX8OE+wbebQc5tjfYdr8UmmvOTzubSeRGkYpC2RLApKIjVUv7RUpCxBK6Qt/t+VUrEl5R3hTKtTEIp+5xZ1c7g/sTToo29E3GPMBwSGmvN1sA2zslV0AE4BaqV6Lbq9ipjLs5PCe4u946loMqVFTc2tof6+aTfLoGlMNNDPpiewNmzHl70tUzuEwWz2UXgZT/ZgWZxhyzEuMVjNGb+L6j1A2cTkvg+XUcKcvhvY=212FD3x19z9sWBHDJACbC00B75E',
    'client_id': 'MTD405', 'redirect_uri': 'http://localhost:8080'}
authReply = requests.post('https://api.tdameritrade.com/v1/oauth2/token', headers=headers, data=data)
        
print(authReply.text)
