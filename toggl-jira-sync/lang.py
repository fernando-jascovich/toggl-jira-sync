#!/usr/bin/python

class Lang:
    ERROR_USAGE_TMPL = ("\nUsage: %s [options]\n"
    + "-s, --start\t Start date MM/DD/YYYY\n"
    + "-e, --end\t End date MM/DD/YYYY\n"
    + "\n")
    
    ERROR_DATE_INPUT = "Wrong date format, try again please!"
    ERROR_DATE_END_GT = "End date should be greater or equal to start date."
    ERROR_DATE_ST_FUTURE = "Planning to read the future?"

    PROMPT_TOGGL_API_KEY = "Toggl api key: "
    PROMPT_TOGGL_WORKSPACE = "Toggl workspace id: "
    PROMPT_JIRA_USER = "Jira username: "
    PROMPT_JIRA_PASS = "Jira password: "
    PROMPT_ST_DATE = "Start date (MM/DD/YYYY): "
    PROMPT_END_DATE = "End date (MM/DD/YYYY): "

    INFO_REQUESTING_TOGGL = "Toggl: requesting data..."
    INFO_CHECK_EXISTING_LOGS = "Jira: checking existing worklogs for %s..."
    INFO_UPDATING_LOG = "Jira: updating %s..."
    INFO_UPDATED_LOG = "Jira: %s updated successfully"
