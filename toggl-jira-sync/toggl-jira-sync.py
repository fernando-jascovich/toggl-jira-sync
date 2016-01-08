#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import getopt
import os.path
from lang import Lang
from settings import Settings
from datetime import date
from services import Toggl, Jira


def main(argv):
    st_date = ""
    end_date = ""
    try:
        opts, args = getopt.getopt(argv, "h:s:e:",["start=", "end="])
    except getopt.GetoptError:
        print(Lang.ERROR_USAGE_TMPL % os.path.basename(__file__))
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(Lang.ERROR_USAGE_TMPL % os.path.basename(__file__))
            sys.exit()
        elif opt in("-s", "--start"):
            st_date = parse_date(arg)
        elif opt in("-e", "--end"):
            end_date = parse_date(arg)

    settings = handle_settings()

    while not st_date:
        st_date = parse_date(prompt_user(Lang.PROMPT_ST_DATE))
        if not st_date: print(Lang.ERROR_DATE_INPUT)
        if st_date > date.today():
            st_date = False
            print(Lang.ERROR_DATE_ST_FUTURE)

    while not end_date:
        end_date = parse_date(prompt_user(Lang.PROMPT_END_DATE))
        if not end_date: print(Lang.ERROR_DATE_INPUT)
        if end_date < st_date:
            end_date = False
            print(Lang.ERROR_DATE_END_GT)

    t = Toggl(
        settings.toggl_api_token, 
        settings.toggl_workspace, 
        st_date, 
        end_date
        )
    Jira(
        settings.jira_user, 
        settings.jira_pass, 
        settings.jira_endpoint,
        t.entries
        )

def parse_date(input):
    try:
        arr = [int(x) for x in input.split("/")]
        return date(arr[2], arr[0], arr[1])
    except:
        return False

def handle_settings():
    s = Settings()
    while not s.toggl_api_token:
        s.set_toggl_api_token(prompt_user(Lang.PROMPT_TOGGL_API_KEY))

    while not s.toggl_workspace:
        s.set_toggl_workspace(prompt_user(Lang.PROMPT_TOGGL_WORKSPACE))

    while not s.jira_endpoint:
        s.set_jira_endpoint(prompt_user(Lang.PROMPT_JIRA_HOST))

    while not s.jira_user:
        s.set_jira_user(prompt_user(Lang.PROMPT_JIRA_USER))

    while not s.jira_pass:
        s.set_jira_pass(prompt_user(Lang.PROMPT_JIRA_PASS))

    return s

def prompt_user(label):
    try:
        s = raw_input(label)
    except NameError:
        s = input(label)
    return s


if __name__ == "__main__":
    main(sys.argv[1:]) 
