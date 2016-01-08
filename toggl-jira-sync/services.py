#!/usr/bin/python

import requests
import sys
from lang import Lang
import json
from datetime import datetime

class Toggl:

    _endpoint = "https://toggl.com/reports/api/v2/details"
    entries = []
    
    def __init__(self, api_token, workspace, st, end):
        self.api_token = api_token
        self.params = {
            'user_agent': 'fernando.ej@gmail.com',
            'workspace_id': workspace,
            'since': st,
            'until': end,
            'page': 1
        }
        print(Lang.INFO_REQUESTING_TOGGL)
        
        q1 = self.query()
        self.entries.extend(q1['data'])
        while len(self.entries) < q1['total_count']:
            self.params["page"] += 1
            q2 = self.query()
            self.entries.extend(q2['data'])

    def query(self):
        r = requests.get(
                self._endpoint, 
                params = self.params,
                auth = (self.api_token, 'api_token'))
        j = r.json()
        if r.status_code != requests.codes.ok:
            print("Code %d" % j['error']['code'])
            print(j['error']['message'])
            print(j['error']['tip'])
            sys.exit(2)
        return j


class Jira:

    _endpoint = "https://jira.gfrmedia.com/rest/api/latest/issue/%s/worklog"

    def __init__(self, user, password, toggl_entries):
        self.user = user
        self.password = password

        for e in toggl_entries:
            i = e["start"].rindex(":")
            s = e["start"][:i] + e["start"][i + 1:]
            start = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")

            spent = int(e["dur"] / 1000)
            key = e["description"]

            print(Lang.INFO_CHECK_EXISTING_LOGS % key)
            w = self.get_worklog(key)
            if not w: continue

            exists = False
            for log in w["worklogs"]:
                d = datetime.strptime(log["started"], "%Y-%m-%dT%H:%M:%S.%f%z")
                if d == start:
                    exists = True
                    break

            if not exists:
                print(Lang.INFO_UPDATING_LOG % key)
                self.add_worklog(key, start, spent)

    def get_worklog(self, key):
        r = requests.get(
                self._endpoint % key, 
                auth = (self.user, self.password)
            )
        if r.status_code != requests.codes.ok:
            print("Error: %d" % r.status_code)
            return False
        return r.json()

    def add_worklog(self, key, start, seconds):
        p = {
            "comment": "",
            "started": start.__format__("%Y-%m-%dT%H:%M:%S.000%z"),
            "timeSpentSeconds": seconds
        }
        r = requests.post(
                self._endpoint % key,
                auth = (self.user, self.password),
                data = json.dumps(p),
                headers = {
                    'Content-Type':'application/json',
                    'Accept':'*/*'
                    }
                )
        if r.status_code > 399:
            print("Error: %d" % r.status_code)
            print(r.text)
            return False
        
        print(Lang.INFO_UPDATED_LOG % key)
        return True

