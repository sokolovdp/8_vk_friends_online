# Watcher of Friends Online

vk_friends_online shows user friends who are online in vk

usage: 
------
```
python vk_friends_online.py [--help] --user USER --token TOKEN

Arguments:
  --help         show this help message and exit
  --user USER    user id or short 'screen name'
  --token TOKEN  VK API access token
```
sample output:
--------------
```
friends online: Иван Асютин, Ольга Теплова
```
how to get vk api token:
------------------------
Documentation: https://vk.com/dev/oauth_gettoken

API_ID you can get in your private cabinet, section - Managed Apps

Sample Python code to get API token:
```
AUTHORIZE_URL = 'https://oauth.vk.com/authorize'
APP_ID = 1234567  # Your application ID
auth_data = {
    'client_id': APP_ID,
    'display': 'mobile',
    'response_type': 'token',
    'scope': 'friends', 'status'
    'v': '5.65',
}
token_url = '?'.join((AUTHORIZE_URL, urlencode(auth_data)))
print(token_url)
```

# Project Goals

The code is written for educational purposes. Training course for web-developers - [DEVMAN.org](https://devman.org)
