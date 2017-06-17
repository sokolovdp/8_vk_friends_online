import sys
import argparse
import requests


def make_response(data, error):
    return {'data': data, 'err': error, 'ok': error is None}


def get_response(url, par):
    try:
        data = requests.get(url, par).json()['response']
        return make_response(data, None)
    except ConnectionError:
        return make_response(None, "error: vk connection problem")
    except TimeoutError:
        return make_response(None, "error: vk connection timeout")
    except KeyError:
        return make_response(None, "key error, check user id and token ")
    except Exception:
        return make_response(None, "unknown error")


def get_friends_list(user_id, token):
    max_friends = 1000
    parameters = {'access_token': token, 'v': '5.65', 'user_id': user_id, 'count': max_friends}
    response = get_response('https://api.vk.com/method/friends.get', parameters)
    if response['ok']:
        return response['data']['items']
    else:
        print("can't load user {} friend list, error {}".format(user_id, response['err']))
        exit()


def get_friends_statuses(token, users_ids):
    parameters = {'access_token': token, 'v': '5.65', 'user_ids': "[{}]".format(",".join(map(str, users_ids))),
                  'fields': ['online']}
    response = get_response('https://api.vk.com/method/users.get', parameters)
    if response['ok']:
        return response['data']
    else:
        print("can't load user friend's statuses, error {}".format(response['err']))
        exit()


def friend_is_online(friend_data):
    return friend_data['online']


def get_online_friends(user_id, api_token):
    friends = get_friends_list(user_id, api_token)
    if friends:
        return list(filter(friend_is_online, get_friends_statuses(api_token, friends)))


def main(user_id, api_token):
    friends_online = get_online_friends(user_id, api_token)
    if friends_online:
        names_of_online_friends = [friend['first_name'] + ' ' + friend['last_name'] for friend in friends_online]
        print("friends online: {}".format(', '.join(names_of_online_friends)))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='shows friends online of the vk user')
    ap.add_argument("--user", dest="user", action="store", required=True, help="  user id or short 'screen name'")
    ap.add_argument("--token", dest="token", action="store", required=True, help="  vk api access token")
    args = ap.parse_args(sys.argv[1:])

    main(args.user, args.token)
