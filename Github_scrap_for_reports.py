import os
import requests
import json
import datetime
import argparse
import distutils.core
from dotenv import load_dotenv

load_dotenv()
token=os.getenv("TOKEN")
github_account=os.getenv("USER")


def list_repos(user):
    num_tries = 0
    repo_url=f'https://api.github.com/users/{user}/repos'
    while num_tries<3:
        try:
            repos_full=requests.get(repo_url, auth=(github_account,token)).json()
            # repositories=[dict['name'] for dict in repos_full if dict['private']==False and dict['fork']==False]
            languages={dict['name']:dict['language'] for dict in repos_full if dict['private']==False and dict['fork']==False} 
            repositories=languages.keys()
            return repositories,languages
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Repos by user URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def weekly_stats(user,repo):
    num_tries = 0
    stats_url=f'https://api.github.com/repos/{user}/{repo}/stats/contributors'
    while num_tries<3:
        try:
            stats=requests.get(stats_url, auth=(github_account,token)).json()
            if not stats==[]:
                stats_user=[(dict['weeks'][-1]['w'], dict['weeks'][-1]['a'],dict['weeks'][-1]['d']) for dict in stats if dict['author']['login']==user]
                if not stats_user==[]:
                    return stats_user[0]
            else:
                return (0,0,0)
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Weekly statistics URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def daily_stats(user):
    num_tries = 0
    stats_url = f'https://github-contributions-api.now.sh/v1/{user}'
    while num_tries<3:
        try:
            stats=requests.get(stats_url, auth=(github_account,token)).json()
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
    leaderboard={}
    for owner in participants:
        user_commits=0
        user_additions=0
        user_deletions=0
        if daily:
            print(f'Daily commits for {owner}:')
            list_commits.append(daily_stats(owner))
        repos,languages=list_repos(owner)
        if weekly:
            print(f'Weekly additions and deletions by repository for {owner}:')
            for repo in repos:
                week,additions,deletions=weekly_stats(owner,repo)
                print(repo, languages[repo],'additions:',additions,'deletions:',deletions)
                user_additions+=additions
                user_deletions+=deletions
        list_additions.append(user_additions)
        list_deletions.append(user_deletions)
    return participants, list_commits, list_additions,list_deletions

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--participants', help='List of brand names in order (space separated)', nargs='+', required=True)
    parser.add_argument('--daily', dest='daily', help='Will generate statistics for the daily report', type=lambda x:bool(distutils.util.strtobool(x)))
    parser.add_argument('--weekly', dest='weekly', help='Will generate statistics for the weekly report', type=lambda x:bool(distutils.util.strtobool(x)))

    args = parser.parse_args()
    main(args.participants, args.daily,args.weekly)

