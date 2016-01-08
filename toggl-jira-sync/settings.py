#!/usr/bin/python

import sys
import os.path
try:
    import ConfigParser as ConfigParser
except ImportError:
    import configparser as ConfigParser

class Settings:

    FILE_NAME = ".toggl-jira-sync-settings"
    TOGGL_SECTION = "Toggl"
    JIRA_SECTION = "Jira"

    _config = ConfigParser.RawConfigParser()
    _config_file_name = os.path.join(
        os.path.expanduser("~"), 
        ".toggl-jira-sync-settings"
    )

    toggl_api_token = False
    toggl_workspace = False
    jira_endpoint = False
    jira_user = False
    jira_pass = False

    def __init__(self):
        self._config.read(self._config_file_name)
        try:
            self.toggl_api_token = self._config.get(
                    Settings.TOGGL_SECTION, "toggl_api_token")
        except: pass
        try:
            self.toggl_workspace = self._config.get(
                    Settings.TOGGL_SECTION, "toggl_workspace")
        except: pass
        try:
            self.jira_endpoint = self._config.get(
                    Settings.JIRA_SECTION, "jira_endpoint")
        except: pass
        try:
            self.jira_user = self._config.get(
                    Settings.JIRA_SECTION, "jira_user")
        except: pass 
        try:
            self.jira_pass = self._config.get(
                    Settings.JIRA_SECTION, "jira_pass")
        except: pass

    def set_toggl_api_token(self, token):
        self.toggl_api_token = token
        self.update_config("toggl_api_token", token)

    def set_toggl_workspace(self, workspace):
        self.toggl_workspace = workspace
        self.update_config("toggl_workspace", workspace)

    def set_jira_endpoint(self, endpoint):
        self.jira_endpoint = endpoint
        self.update_config("jira_endpoint", endpoint)

    def set_jira_user(self, user):
        self.jira_user = user
        self.update_config("jira_user", user)

    def set_jira_pass(self, password):
        self.jira_pass = password
        self.update_config("jira_pass", password)

    def update_config(self, name, value):
        allowed = [
            "toggl_api_token", 
            "toggl_workspace", 
            "jira_endpoint",
            "jira_user", 
            "jira_pass"
        ]
        if name not in allowed: return

        if "toggl" in name:
            try:
                self._config.set(Settings.TOGGL_SECTION, name, value)
            except:
                self._config.add_section(Settings.TOGGL_SECTION)
                self._config.set(Settings.TOGGL_SECTION, name, value)
        else:
            try:
                self._config.set(Settings.JIRA_SECTION, name, value)
            except:
                self._config.add_section(Settings.JIRA_SECTION)
                self._config.set(Settings.JIRA_SECTION, name, value)

        with open(self._config_file_name, "w+") as f:
            self._config.write(f)
            
    
