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
        """
        Sends an HTTP GET request.
        Returns a yielded iteration. 
        example: next(request('users', sort='fullName', query='role:admin AND locale:en_US'))
        """
        url = self.url % path + ('?' + urlencode(kwargs) if len(kwargs) else '')
        last = False
        while not last:
            r = requests.get(url, headers=self.headers).json()
            yield r
            if 'paging' in r and 'next' in r['paging']:
                url = r['paging']['next']
            else:
                last = True

    def delete(self, path, **kwargs):
        """
        Sends an HTTP DELETE request.
        example: delete('users/' + username)
        """
        url = self.url % path + ('?' + urlencode(kwargs) if len(kwargs) else '')
        return requests.delete(url, headers=self.headers).json()

    def patch(self, path, payload, **kwargs):
        """
        Sends an HTTP PATCH request.
        example: patch('escalations/' + username, {'rules': rules})
        """
        url = self.url % path + ('?' + urlencode(kwargs) if len(kwargs) else '')
        return requests.patch(url, json=payload, headers=self.headers).json()

    def dump_users(self, filename, query=''):
        """
        Dumps user list to csv file
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
        """
        Decorator method for exiting user
        """
        def inner(self, username):
            r = requests.get(self.url % 'users/' + username, headers=self.headers)
            if r.status_code == requests.codes.ok and 'data' in r.json():
                return func(self, username)
            else:
                print('[Error] User account {} not found'.format(username))
        return inner

    def remove_user_from_escalations(self, username):
        """
        Removes given user from its escalations. 
        Newly vacant escalations and routing-rules will be deleted
        """
        for user_esc in next(self.request(f'users/{username}/escalations'))['data']:
            escalation = next(self.request('escalations/' + user_esc['id']))['data']
            esc_rules = list(filter(lambda r: not(r['recipient']['type'] == 'user' and username == r['recipient']['username']), escalation['rules']))
            if len(esc_rules) == 0:
                if 'ownerTeam' in escalation:
                    for rule in next(self.request('/teams/' + escalation['ownerTeam']['id'] + '/routing-rules'))['data']:
                        if ('notify' in rule and rule['notify']['type'] == 'escalation' and rule['notify']['id'] == user_esc['id']):
                            try:
                                r = self.delete(
                                    'teams/' + escalation['ownerTeam']['id'] + '/routing-rules/' + rule['id'])
                                if 'result' not in r or r['result'] != 'Deleted':
                                    raise Exception(r['message'])
                                print('[ OK  ] Remove vacant routing-rules {} for {}'.format(rule['notify']['name'], username))
                            except Exception as e:
                                print('[Error] Remove vacant routing-rules {} for {}'.format(rule['notify']['name'], username))
                                print("\tException " + str(e))
                try:
                    r = self.delete('escalations/' + user_esc['id'])
                    if 'result' not in r or r['result'] != 'Deleted':
                        raise Exception(r['message'])
                    print('[ OK  ] Remove vacant escalation {} for {}'.format(user_esc['name'], username))
                except Exception as e:
                    print('[Error] Remove vacant escalation {} for {}'.format(user_esc['name'], username))
                    print("\tException " + str(e))
            else:
                try:
                    r = self.patch('escalations/' + user_esc['id'], {'rules': esc_rules})
                    if 'result' not in r or r['result'] != 'Updated':
                        raise Exception(r['message'])
                    print('[ OK  ] Remove {} from escalation {}'.format(username, user_esc['name']))
                except Exception as e:
                    print('[Error] Remove {} from escalation {}'.format(username, user_esc['name']))
                    print("\tException " + str(e))

    def remove_user_from_schedules(self, username):
        """
        Removes given user from its schedules. 
        Newly vacant rotations will be deleted.
        Vacant schedules can be removed by delete_empty_teams() method.
        """
        for schedule in next(self.request(f'users/{username}/schedules'))['data']:
            rotations = next(self.request('schedules/' + schedule['id'] + '/rotations'))['data']
            for kr, rotation in enumerate(rotations):
                participants = list(filter(lambda p: not('username' in p and p['username'] == username), rotation['participants']))
                if len(participants) == 0:
                    try:
                        r = self.delete('schedules/{}/rotations/{}'.format(schedule['id'], rotations[kr]['id']))
                        if 'result' not in r or r['result'] != 'Deleted':
                            raise Exception(r['message'])
                        print('[ OK  ] Remove {} and the vacant rotation {}/{}'.format(username, schedule['name'], rotation['name']))
                    except Exception as e:
                        print('[Error] Remove {} and the vacant rotation {}/{}'.format(username, schedule['name'], rotation['name']))
                        print("\tException " + str(e))
                else:
                    try:
                        r = self.patch('schedules/{}/rotations/{}'.format(schedule['id'], rotations[kr]['id']),
                                       {'participants': participants})
                        if 'result' not in r or r['result'] != 'Updated':
                            raise Exception(r['message'])
                        print('[ OK  ] Remove {} from rotation {}/{}'.format(username, schedule['name'], rotation['name']))
                    except Exception as e:
                        print('[Error] Remove {} from rotation {}/{}'.format(username, schedule['name'], rotation['name']))
                        print("\tException " + str(e))

    def remove_user_from_teams(self, username):
        """
        Removes given user from its schedules. 
        Newly vacant rotations will be deleted.
        Vacant schedules can be removed by delete_empty_teams() method.
        """
        for team in next(self.request(f'users/{username}/teams'))['data']:
            try:
                r = self.delete('teams/{}/members/{}'.format(team['id'], username))
                if 'result' not in r or r['result'] != 'Removed':
                    raise Exception(r['message'])
                print('[ OK  ] Remove {} from team {}'.format(username, team['name']))
            except Exception as e:
                print('[Error] Remove {} from team {}'.format(username, team['name']))
                print("\tException " + str(e))

    def delete_user(self, username):
        """
        Deletes user from the app. 
        """
        try:
            r = self.delete('users/' + username)
            if 'result' not in r or r['result'] != 'Deleted':
                raise Exception(r['message'])
            print('[ OK  ] Remove user account {}'.format(username))
        except Exception as e:
            print('[Error] Remove user account {}'.format(username))
            print("\tException " + str(e))

    @for_existing_user
    def deep_user_remove(self, username):
        """
        All in one user clean up. Removes given user from escalations, schedules, teams and from the application. 
        """        
        self.remove_user_from_escalations(username)
        self.remove_user_from_schedules(username)
        self.remove_user_from_teams(username)
        self.delete_user(username)
        
    def delete_empty_teams(self):
        """
        Deletes all vacant teams (teams without members).
        """        
        for teams in g.request('teams'):
            for team in teams['data']:
                info = next(g.request('teams/{}'.format(team['id'])))['data']
                if not 'members' in info:
                    try:
                        r = self.delete('teams/{}'.format(team['id']))
                        if 'result' not in r or r['result'] != 'Deleted':
                            raise Exception(r['message'])
                        print('[ OK  ] Deleted empty team {}'.format(team['name']))
                    except Exception as e:
                        print('[Error] Deleted empty team {}'.format(team['name']))
                        print("\tException " + str(e))
                else:
                    print('[Skipp] Team {} with {} member(s)'.format(team['name'], len(info['members'])))
        
    def delete_disabled_integrations(self):
        """
        Removes all disabled integrations. 
        """        
        for integrations in g.request('integrations'):
            for integration in integrations['data']:
                if not integration['enabled']:
                    try:
                        r = self.delete('integrations/{}'.format(integration['id']))
                        if 'result' not in r or r['result'] != 'Deleted':
                            raise Exception(r['message'])
                        print('[ OK  ] Deleted disabled integration {}'.format(integration['name']))
                    except Exception as e:
                        print('[Error] Deleted disabled integration {}'.format(integration['name']))
                        print("\tException " + str(e))
                else:
                    print('[Skipp] Enabled integration {}'.format(integration['name']))

