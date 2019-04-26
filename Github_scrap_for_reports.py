import requests
import json
# from datetime import date
import datetime
import argparse
import distutils.core
import os

token=os.getenv("TOKEN")

def list_repos(user):
    num_tries = 0
    repo_url=f'https://api.github.com/users/{user}/repos?token={token}'
    while num_tries<3:
        try:
            repos_full=requests.get(repo_url).json()
            repositories=[dict['name'] for dict in repos_full if dict['private']==False]
            return repositories
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Repos by user URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def weekly_stats(user,repo):
    num_tries = 0
    stats_url=f'https://api.github.com/repos/{user}/{repo}/stats/contributors?token={token}'
    while num_tries<3:
        try:
            stats=requests.get(stats_url).json()
            stats_user=[(dict['weeks'][0]['w'], dict['weeks'][0]['a'],dict['weeks'][0]['d']) for dict in stats if dict['author']['login']=='ansufei']
            if not stats_user==[]:
                return stats_user[0]
            else:
                return (0,0,0)
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Weekly statistics URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")


def daily_stats(user,repo):
    num_tries = 0
    stats_url= f'https://api.github.com/repos/{user}/{repo}/stats/punch_card?token={token}'
    while num_tries<3:
        try:
            stats=requests.get(stats_url).json()
            today=datetime.date.today().weekday()
            stats_user=[stats[i][2] for i in range(0,168) if stats[i][0]==today]
            return sum(stats_user)
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Daily statistics URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def daily_stats1(user,repo):
    num_tries = 0
    URL = "https://github-contributions-api.now.sh/v1/"
    stats_url = URL + user + f'?format=nested&token={token}'
    while num_tries<3:
        try:
            stats=requests.get(stats_url).json()
            today = datetime.date.today()
            contribution = stats['contributions']['contributions'][str(today.year)][str(today.month)][str(today.day-1)]['count']
            return contribution
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Daily statistics URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def main(participants,daily=False,weekly=False):
    print(participants,'daily: ',daily,'weekly: ',weekly)
    list_commits=[]
    list_additions=[]
    list_deletions=[]
    for owner in participants:
        print(owner)
        user_commits=0
        user_additions=0
        user_deletions=0
        for repo in list_repos(owner):
            print(repo)
            if weekly:
                week,additions,deletions=weekly_stats(owner,repo)
                print(additions,deletions)
                user_additions+=additions
                user_deletions+=deletions
            if daily:
                commits=daily_stats(owner,repo)
                user_commits+=commits
        list_additions.append(user_additions)
        list_deletions.append(user_deletions)
        list_commits.append(user_commits)
    return participants, list_commits, list_additions,list_deletions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--participants', help='List of brand names in order (space separated)', nargs='+', required=True)
    #parser.add_argument('--daily', help='Will generate statistics for the daily report', type=bool, required=False)
    #parser.add_argument('--weekly', help='Will generate statistics for the weekly report', type=bool, required=False)
    parser.add_argument('--daily', dest='daily', help='Will generate statistics for the daily report', type=lambda x:bool(distutils.util.strtobool(x)))
    parser.add_argument('--weekly', dest='weekly', help='Will generate statistics for the weekly report', type=lambda x:bool(distutils.util.strtobool(x)))

    args = parser.parse_args()
    main(args.participants, args.daily,args.weekly)

