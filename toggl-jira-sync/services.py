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

    _endpoint = "https://%s/rest/api/latest/issue/%s/worklog"
    _endpoint_t = "https://%s/rest/api/2/issue/%s/transitions"

    def __init__(self, user, password, host, toggl_entries):
        self.user = user
        self.password = password
        self.host = host

        for e in toggl_entries:
            i = e["start"].rindex(":")
            s = e["start"][:i] + e["start"][i + 1:]
            try:
                start = datetime.strptime(s, "%Y-%m-%dT%H:%M:%S%z")
            except:
                from dateutil.parser import parse
                start = parse(s)

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
                self._endpoint % (self.host, key), 
                auth = (self.user, self.password)
            )
        if r.status_code != requests.codes.ok:
            print("Error: %d" % r.status_code)
            return False
        return r.json()

    def add_worklog(self, key, start, seconds):
        if(seconds < 60):
            print(Lang.WARN_JIRA_MIN % key)
            return False

        h = {
            'Content-Type':'application/json',
            'Accept':'*/*'
        }
        p = {
            "comment": "",
            "started": start.__format__("%Y-%m-%dT%H:%M:%S.000%z"),
            "timeSpentSeconds": seconds
        }
        r = requests.post(
            self._endpoint % (self.host, key),
            auth = (self.user, self.password),
            data = json.dumps(p),
            headers = h
        )
        if r.status_code == 400:
            print(Lang.INFO_JIRA_CLOSED_ISSUE)
            r2 = requests.get(
                self._endpoint_t % (self.host, key),
                auth = (self.user, self.password),
                headers = h
            )
            transitions = r2.json()["transitions"]
            reopen_id = -1
            close_id = -1
            for t in transitions:
                name = t["name"].lower()
                if "reopen" in name:
                    reopen_id = int(t["id"])
                elif "close" in name:
                    close_id = int(t["id"])

            if reopen_id < 0:
                print(Lang.ERROR_JIRA_NO_TRANSITION % key)
                return False

            p2 = {
                "update": {
                    "comment": [{"add":{"body":"Reopen for log work."}}]
                },
                "transition": { "id": reopen_id }
            }
            r3 = requests.post(
                self._endpoint_t % (self.host, key),
                auth = (self.user, self.password),
                data = json.dumps(p2),
                headers = h
            )
            if r3.status_code != 204:
                print("Error: %d" % r.status_code)
                print(r.text)
                return False

            r = requests.post(
                self._endpoint % (self.host, key),
                auth = (self.user, self.password),
                data = json.dumps(p),
                headers = h
            )

            if close_id < 0:
                print(Lang.WARN_JIRA_CLOSE % key)
            else:
                p3 = {
                    "update": { 
                        "comment":[{"add":{"body":"Closing after log work."}}]
                    },
                    "transition": { "id": close_id }
                }
                r4 = requests.post(
                    self._endpoint_t % (self.host, key),
                    auth = (self.user, self.password),
                    data = json.dumps(p3),
                    headers = h
                )

        if r.status_code > 399:
            print("Error: %d" % r.status_code)
            print(r.text)
            return False
        
        print(Lang.INFO_UPDATED_LOG % key)
        return True

