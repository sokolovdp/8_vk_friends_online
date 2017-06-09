import requests
import time
import sys
import argparse

# from pprint import pprint

VERSION = '5.65'  # VK API Version
MAX_FRIENDS = 1000  # Max number of friends to analyse
VK_TIMEOUT = 1.01  # Time in secs to pause when limit of requests is reached
VK_REQ_LIMIT = 3  # Max number of requests to VK API per second


class VkUser:
    def __init__(self, userid=0, token=0):
        self.counter = 0
        pars = {'access_token': token, 'v': VERSION, 'user_ids': [], 'fields': ['counters']}
        data = self._get_response('https://api.vk.com/method/users.get', pars)
        if not data:
            print("invalid token: {}".format(token))
            exit(4)
        self.token = token
        pars = {'access_token': token, 'v': VERSION, 'user_ids': [userid], 'fields': ['counters']}
        data = self._get_response('https://api.vk.com/method/users.get', pars)
        if not data:
            print("invalid user id: {}".format(userid))
            exit(5)
        self.uid = data[0]['id']
        self.name = data[0]['first_name'] + ' ' + data[0]['last_name']

    def _get_response(self, url, par):
        try:
            data = requests.get(url, par).json()['response']
        except ConnectionError:
            print("error: VK connection problem")
            exit(1)
        except TimeoutError:
            print("error: VK connection timeout")
            exit(2)
        except KeyError:
            return {}
        else:
            if self.counter >= VK_REQ_LIMIT:  # check that there is not more than 3 operations per 1 sec
                time.sleep(VK_TIMEOUT)
                self.counter = 0
            else:
                self.counter += 1
            return data

    def get_friends_list(self):
        pars = {'access_token': self.token, 'v': VERSION, 'user_id': self.uid, 'count': MAX_FRIENDS}
        try:
            return self._get_response('https://api.vk.com/method/friends.get', pars)['items']
        except ValueError:
            print("can't load friends list")

    def get_main_user_name(self):
        return self.name

    def get_users_status(self, users_ids):
        pars = {'access_token': self.token, 'v': VERSION, 'user_ids': "[{}]".format(",".join(map(str, users_ids))),
                'fields': ['online']}
        users_statuses = self._get_response('https://api.vk.com/method/users.get', pars)
        return users_statuses


def online_user(user_data):
    return user_data['online']


def get_online_friends(vkapi):
    friends = vkapi.get_friends_list()
    online_users_data = list(filter(online_user, vkapi.get_users_status(friends)))
    return [user['first_name'] + " " + user['last_name'] for user in online_users_data]


def output_friends_to_console(username, friends_online):
    print("\n{} has the following friends online: {}".format(username, ", ".join(friends_online)))


def main(vkapi):
    friends_online = get_online_friends(vkapi)
    output_friends_to_console(vkapi.get_main_user_name(), friends_online)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='This program shows friends online of the given VK user')
    ap.add_argument("--user", dest="user", action="store", required=True, help="  user id or short 'screen name'")
    ap.add_argument("--token", dest="token", action="store", required=True, help="  VK API access token")

    args = ap.parse_args(sys.argv[1:])

    main(VkUser(userid=args.user, token=args.token))
