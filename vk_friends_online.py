import sys
import argparse
import requests

vk_api_friends = 'https://api.vk.com/method/friends.get'
vk_api_users = 'https://api.vk.com/method/users.get'
MAX_FRIENDS = 1000


def make_response(response_data=None, error=None):
    return {'data': response_data, 'err': error, 'ok': error is None}


def get_response(url, par):
    try:
        response = requests.get(url, par).json()['response']
        return make_response(response_data=response)
    except ConnectionError:
        return make_response(error="error: vk connection problem")
    except TimeoutError:
        return make_response(error="error: vk connection timeout")
    except KeyError:
        return make_response(error="key error, check user id and token ")


def get_friends_list(user_id, token):
    parameters = {'access_token': token, 'v': '5.65', 'user_id': user_id, 'count': MAX_FRIENDS}
    response = get_response(vk_api_friends, parameters)
    if response['ok']:
        return response['data']['items']
    else:
        print("can't load user {} friend list, error {}".format(user_id, response['err']))


def get_friends_statuses(token, users_ids):
    parameters = {'access_token': token, 'v': '5.65', 'user_ids': "[{}]".format(",".join(map(str, users_ids))),
                  'fields': ['online']}
    response = get_response(vk_api_users, parameters)
    if response['ok']:
        return response['data']
    else:
        print("can't load user friend's statuses, error {}".format(response['err']))


def get_online_friends(user_id, api_token):
    friends = get_friends_list(user_id, api_token)
    if friends:
        return [friend for friend in get_friends_statuses(api_token, friends) if friend['online']]


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
