import sys
import argparse
import requests


def get_response(url, par):
    try:
        response = requests.get(url, par).json()['response']
    except ConnectionError:
        print("error: vk connection problem")
        exit(1)
    except TimeoutError:
        print("error: vk connection timeout")
        exit(2)
    except KeyError:
        print("response error, check user id and token values")
        exit(3)
    else:
        return response


def get_friends_list(user_id, token):
    max_friends = 1000
    parameters = {'access_token': token, 'v': '5.65', 'user_id': user_id, 'count': max_friends}
    return get_response('https://api.vk.com/method/friends.get', parameters)['items']


def get_friends_statuses(token, users_ids):
    parameters = {'access_token': token, 'v': '5.65', 'user_ids': "[{}]".format(",".join(map(str, users_ids))),
                  'fields': ['online']}
    return get_response('https://api.vk.com/method/users.get', parameters)


def friend_is_online(friend_data):
    return friend_data['online']


def get_online_friends(user_id, api_token):
    friends = get_friends_list(user_id, api_token)
    return list(filter(friend_is_online, get_friends_statuses(api_token, friends)))


def main(user_id, api_token):
    friends_online = get_online_friends(user_id, api_token)
    names_of_online_friends = [friend['first_name'] + ' ' + friend['last_name'] for friend in friends_online]
    print("friends online: {}".format(', '.join(names_of_online_friends)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='This program shows friends online of the VK user')
    ap.add_argument("--user", dest="user", action="store", required=True, help="  user id or short 'screen name'")
    ap.add_argument("--token", dest="token", action="store", required=True, help="  vk api access token")
    args = ap.parse_args(sys.argv[1:])

    main(args.user, args.token)
