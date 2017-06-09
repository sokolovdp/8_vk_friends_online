import requests
import time
import sys
import argparse

VERSION = '5.65'  # VK API Version
MAX_FRIENDS = 1000  # Max number of friends to analyse
VK_TIMEOUT = 1.01  # Time in secs to pause when limit of requests is reached
VK_REQ_LIMIT = 3  # Max number of requests to VK API per second


class VkUser:
    def __init__(self, user_id=0, token=0):
        self.counter = 0
        pars = {'access_token': token, 'v': VERSION, 'user_ids': [], 'fields': ['counters']}
        response = self._get_response('https://api.vk.com/method/users.get', pars)
        if not response:
            print("invalid token: {}".format(token))
            exit(1)
        self.token = token
        pars = {'access_token': token, 'v': VERSION, 'user_ids': [user_id], 'fields': ['counters']}
        response = self._get_response('https://api.vk.com/method/users.get', pars)
        if not response:
            print("invalid user id: {}".format(user_id))
            exit(2)
        self.uid = response[0]['id']
        self.name = response[0]['first_name'] + ' ' + response[0]['last_name']

    def _get_response(self, url, par):
        try:
            response = requests.get(url, par).json()['response']
        except ConnectionError:
            print("error: vk connection problem")
            return {}
        except TimeoutError:
            print("error: vk connection timeout")
            return {}
        except KeyError:
            return {}
        else:
            if self.counter >= VK_REQ_LIMIT:  # check that there is not more than 3 operations per 1 sec
                time.sleep(VK_TIMEOUT)
                self.counter = 0
            else:
                self.counter += 1
            return response

    def get_friends_list(self):
        pars = {'access_token': self.token, 'v': VERSION, 'user_id': self.uid, 'count': MAX_FRIENDS}
        try:
            return self._get_response('https://api.vk.com/method/friends.get', pars)['items']
        except ValueError:
            print("can't load friends list")

    def get_main_user_name(self):
        return self.name

    def get_friends_statuses(self, users_ids):
        pars = {'access_token': self.token, 'v': VERSION, 'user_ids': "[{}]".format(",".join(map(str, users_ids))),
                'fields': ['online']}
        friends_statuses = self._get_response('https://api.vk.com/method/users.get', pars)
        return friends_statuses


def status_online(data):
    return data['online']


def get_online_friends(api):
    friends = api.get_friends_list()
    online_friends_data = list(filter(status_online, api.get_friends_statuses(friends)))
    return [friend['first_name'] + " " + friend['last_name'] for friend in online_friends_data]


def main(api):
    friends_online = get_online_friends(api)
    print("\n{} has the following friends online: {}".format(api.get_main_user_name(), ", ".join(friends_online)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='This program shows friends online of the given VK user')
    ap.add_argument("--user", dest="user", action="store", required=True, help="  user id or short 'screen name'")
    ap.add_argument("--token", dest="token", action="store", required=True, help="  vk api access token")

    args = ap.parse_args(sys.argv[1:])

    main(VkUser(user_id=args.user, token=args.token))
