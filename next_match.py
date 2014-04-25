#!/usr/bin/env python

from collections import defaultdict
from datetime import datetime, timedelta
import dateutil.parser
from dateutil.tz import tzlocal
import requests
import sys

SRWEB_ROOT = 'https://www.studentrobotics.org/'

COMP_API_ROOT = SRWEB_ROOT + 'comp-api/'

def get_comp(endpoint):
    return get(COMP_API_ROOT + endpoint)

def get(url):
    got = requests.get(url)
    try:
        return got.json()
    except:
        print >>sys.stderr, got.text

def describe_delta(delta):
    pieces = None
    if delta > timedelta(days = 1):
        pieces = ("day", delta.days)

    elif delta > timedelta(hours = 1):
        hours = divmod(delta.seconds, (60 * 60))[0]
        pieces = ("hour", hours)

    elif delta > timedelta(minutes = 2) and delta < timedelta(hours = 1):
        minutes = delta.seconds / 60
        pieces = ("minute", minutes)

    elif delta > timedelta(seconds = 1):
        pieces = ("second", delta.seconds)
    else:
        return "now"

    unit, value = pieces
    if value != 1:
        unit += 's'
    until = "in {0} {1}".format(value, unit)

    return until

def test_dd(*args, **kwargs):
    delta = timedelta(*args, **kwargs)
    print delta, "|", describe_delta(delta)

def time_until(when):
    dt = dateutil.parser.parse(when)
    #print dt
    now = datetime.now(tzlocal())
    assert dt > now
    delta = dt - now

    until = describe_delta(delta)
    return until

def describe_team(tla, teams_data):
    team_data = teams_data.get(tla, None)
    if team_data is not None:
        team_name = team_data.get('team_name', None)
        if team_name:
            return "{0} ({1})".format(team_name, tla)

    return tla

arenas = get_comp('arenas')
teams_data = get(SRWEB_ROOT + 'teams-data.php')

def get_match_data():
    data = defaultdict(dict)
    for arena in arenas['arenas']:
        matches = get_comp('matches/{0}?numbers=next'.format(arena))
        matches = matches['matches']
        assert len(matches) == 1
        match = matches[0]
        #print match #['number']
        #print match['teams']
        data['id'] = match['number']
        data['time'] = time_until(match['start_time'])
        data['arenas'][arena] = match

    return data

def describe_match(match_data):
    out = "Match {id} begins {time}.".format(**match_data)
    for arena, info in match_data['arenas'].items():
        teams = []
        for tla in info['teams']:
            description = describe_team(tla, teams_data)
            teams.append(description)

        assert len(teams) > 1
        teams_str = ", ".join(teams[:-1])
        teams_str += " and " + teams[-1]
        out += " Arena {0}: {1}.".format(arena, teams_str)

    return out

if __name__ == '__main__':
    match_data = get_match_data()
    print describe_match(match_data)

    if '--debug' in sys.argv:
        print
        print 'debug info:'
        test_dd(seconds = 1.5)
        test_dd(seconds = 15)
        test_dd(minutes = 1.5)
        test_dd(minutes = 5)
        test_dd(hours = 5)
        test_dd(days = 5)
        test_dd(days = 5, hours = 2, minutes = 5)
        test_dd(days = 5, hours = 2, seconds = 5)
        test_dd(minutes = 2, seconds = 5)
