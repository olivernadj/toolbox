import json
import requests
from urllib.parse import urlencode
import csv


class GenieClient():
    def __init__(self, key):
        self.url = 'https://api.opsgenie.com/v2/%s'
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': 'GenieKey ' + key,
            'Cache-control': 'no-cache'
        }

    def request(self, path, **kwargs):
        url = self.url % path + ('?' + urlencode(kwargs) if len(kwargs) else '')
        last = False
        while not (last):
            r = requests.get(url, headers=self.headers).json()
            yield r
            if 'paging' in r and 'next' in r['paging']:
                url = r['paging']['next']
            else:
                last = True

    def delete(self, path, **kwargs):
        url = self.url % path + ('?' + urlencode(kwargs) if len(kwargs) else '')
        return requests.delete(url, headers=self.headers).json()

    def patch(self, path, payload, **kwargs):
        url = self.url % path + ('?' + urlencode(kwargs) if len(kwargs) else '')
        return requests.patch(url, json=payload, headers=self.headers).json()

    def dump_users(self, filename, query=''):
        """
        Dump user list to csv file
        example:
          filename='users.csv'
          query='role:user AND verified:1'
        """
        with open(filename, 'w', newline='') as csvfile:
            csvw = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvw.writerow(('name', 'email', 'role', 'verified'))
            for r in self.request('users', query=query):
                print('.')
                if 'data' in r:
                    for u in r['data']:
                        csvw.writerow((u['fullName'], u['username'], u['role']['name'], u['verified']))

    def for_existing_user(func):
        def inner(self, *args, **kwargs):
            r = requests.get(self.url % 'users/' + username, headers=self.headers)
            if ((r.status_code == requests.codes.ok) and ('data' in r.json())):
                return func(self, *args, **kwargs)
            else:
                print('[Error] User account {} not found'.format(username))

        return inner

    def remove_user_from_escalations(self, username):
        for user_esc in next(self.request(f'users/{username}/escalations'))['data']:
            escalation = next(self.request('escalations/' + user_esc['id']))['data']
            for kr, rule in enumerate(escalation['rules']):
                if rule['recipient']['type'] == 'user' and username == rule['recipient']['username']:
                    del escalation['rules'][kr]
            if len(escalation['rules']) == 0:
                if 'ownerTeam' in escalation:
                    for rule in next(g.request('/teams/' + escalation['ownerTeam']['id'] + '/routing-rules'))['data']:
                        if ('notify' in rule and rule['notify']['type'] == 'escalation' and rule['notify']['id'] ==
                                user_esc['id']):
                            try:
                                r = self.delete(
                                    'teams/' + escalation['ownerTeam']['id'] + '/routing-rules/' + rule['id'])
                                if (not ('result' in r) or r['result'] != 'Deleted'):
                                    raise Exception(r['message'])
                                print('[ OK  ] Remove vacant routing-rules {} for {}'.format(rule['notify']['name'],
                                                                                             username))
                            except Exception as e:
                                print('[Error] Remove vacant routing-rules {} for {}'.format(rule['notify']['name'],
                                                                                             username))
                                print("\tException " + str(e))
                try:
                    r = self.delete('escalations/' + user_esc['id'])
                    if (not ('result' in r) or r['result'] != 'Deleted'):
                        raise Exception(r['message'])
                    print('[ OK  ] Remove vacant escalation {} for {}'.format(user_esc['name'], username))
                except Exception as e:
                    print('[Error] Remove vacant escalation {} for {}'.format(user_esc['name'], username))
                    print("\tException " + str(e))
            else:
                try:
                    r = self.patch('escalations/' + user_esc['id'], {'rules': escalation['rules']})
                    if (not ('result' in r) or r['result'] != 'Updated'):
                        raise Exception(r['message'])
                    print('[ OK  ] Remove {} from escalation {}'.format(username, user_esc['name']))
                except Exception as e:
                    print('[Error] Remove {} from escalation {}'.format(username, user_esc['name']))
                    print("\tException " + str(e))

    def remove_user_from_schedules(self, username):
        for schedule in next(self.request(f'users/{username}/schedules'))['data']:
            rotations = next(self.request('schedules/' + schedule['id'] + '/rotations'))['data']
            for kr, rotation in enumerate(rotations):
                for kp, participant in enumerate(rotation['participants']):
                    if 'username' in participant and username == participant['username']:
                        del rotations[kr]['participants'][kp]
                if len(rotation['participants']) == 0:
                    print(
                        'remove {} and the vacant rotation {}/{}'.format(username, schedule['name'], rotation['name']))
                    print(self.delete('schedules/{}/rotations/{}'.format(schedule['id'], rotations[kr]['id'])))
                else:
                    try:
                        r = self.patch('schedules/{}/rotations/{}'.format(schedule['id'], rotations[kr]['id']),
                                       {'participants': rotation['participants']})
                        if (not ('result' in r) or r['result'] != 'Updated'):
                            raise Exception(r['message'])
                        print('[ OK  ] Remove {} from rotation {}/{}'.format(username, schedule['name'],
                                                                             rotation['name']))
                    except Exception as e:
                        print('[Error] Remove {} from rotation {}/{}'.format(username, schedule['name'],
                                                                             rotation['name']))
                        print("\tException " + str(e))

    def remove_user_from_teams(self, username):
        for team in next(self.request(f'users/{username}/teams'))['data']:
            try:
                r = self.delete('teams/{}/members/{}'.format(team['id'], username))
                if (not ('result' in r) or r['result'] != 'Removed'):
                    raise Exception(r['message'])
                print('[ OK  ] Remove {} from team {}'.format(username, team['name']))
            except Exception as e:
                print('[Error] Remove {} from team {}'.format(username, team['name']))
                print("\tException " + str(e))

    def delete_user(self, username):
        try:
            r = self.delete('users/' + username)
            if (not ('result' in r) or r['result'] != 'Deleted'):
                raise Exception(r['message'])
            print('[ OK  ] Remove user account {}'.format(username))
        except Exception as e:
            print('[Error] Remove user account {}'.format(username))
            print("\tException " + str(e))

    @for_existing_user
    def deep_user_remove(self, username):
        self.remove_user_from_escalations(username)
        self.remove_user_from_schedules(username)
        self.remove_user_from_teams(username)
        self.delete_user(username)
