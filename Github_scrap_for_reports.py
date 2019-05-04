import os
import requests
import json
import datetime
import argparse
import distutils.core
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt
# import seaborn
import pickle

load_dotenv()
token=os.getenv("TOKEN")
github_account=os.getenv("USER")
today = datetime.date.today()

def list_repos(user,languages):
    num_tries = 0
    repo_url=f'https://api.github.com/users/{user}/repos?type=all'
    while num_tries<3:
        try:
            repos_full=requests.get(repo_url, auth=(github_account,token)).json()
            lang={dict['name']:dict['language'] for dict in repos_full if dict['private']==False and dict['fork']==False}
            languages.update(lang)
            repositories=lang.keys()
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
            try:
                stats_user=[(dict['weeks'][-1]['w'], dict['weeks'][-1]['a'],dict['weeks'][-1]['d']) for dict in stats if dict['author']['login']==user]
                if not stats_user==[]:
                    return stats_user[0]
                else:
                    return (0,0,0)
            except:
                return (0,0,0)                
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Weekly statistics URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def daily_stats(user):
    num_tries = 0
    stats_url = f'https://github-contributions-api.now.sh/v1/{user}?format=nested'
    while num_tries<3:
        try:
            stats=requests.get(stats_url, auth=(github_account,token)).json()
            contribution = stats['contributions']['contributions'][str(today.year)][str(today.month)][str(today.day-1)]['count']
            return contribution
        except ValueError:
            num_tries += 1
            if num_tries<3:
                print("Daily statistics URL failed. Will retry...")
    raise RuntimeError("Error: Daily statistics URL failed.")

def main(participants,daily=False,weekly=False):
    if participants:
        dict_participants={x:x for x in participants}
    else:
        participants = open('github_accounts.txt').read().splitlines()
        dict_participants={x.split(',')[0]:x.split(',')[1] for x in participants}
        participants=dict_participants.keys()
    print(participants,'daily: ',daily,'weekly: ',weekly)
    list_commits={}
    languages={}
    leaderboard=pd.DataFrame(columns=['language','user','repository','total additions'])
    
    for owner in participants:
        user_commits=0
        user_additions=0
        user_deletions=0
        if daily:
            commit=daily_stats(owner)
            print(f'Daily commit(s) for {owner}:',commit)
            list_commits[owner]=commit
        repos,languages=list_repos(owner,languages)
        if weekly:
            print(f'Weekly additions by repository for {owner}:')
            for repo in repos:
                week,additions,deletions=weekly_stats(owner,repo)
                print(repo, languages[repo],additions-deletions)
                if additions-deletions!=0:
                    leaderboard=leaderboard.append({
                        "language": languages[repo],
                        "user":  owner,
                        "repository": repo,
                        "total additions": additions-deletions
                        }, ignore_index=True)
    if daily:
        print('daily commits by participant: ',list_commits)        

    if weekly:
        print(leaderboard)
        if not leaderboard.empty:
            leaderboard.to_csv(f'leaderboard_{today}.csv')
            sorted_leaderboard=leaderboard.groupby(['language','user']).sum().sort_values('total additions',ascending=False)
            list_colors=['blue','orange','green','red','purple','brown','pink','gray','olive','cyan','black','yellow']
            
            output = open('languages.pkl', 'wb')
            pickle.dump(languages, output)
            output.close()
            
            i=0
            for item in tuple(languages.dict_items()):
                colors[item]=list_colors[i]
                i+=1
            print(colors)
            fig, ax = plt.subplots()
            ax.barh(sorted_leaderboard['user'], sorted_leaderboard['total additions'], c=sorted_leaderboard['language'].apply(lambda x: colors[x]))
            plt.show(block=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--participants', help='List of brand names in order (space separated)', nargs='+', required=False)
    parser.add_argument('--daily', dest='daily', help='Will generate statistics for the daily report', type=lambda x:bool(distutils.util.strtobool(x)))
    parser.add_argument('--weekly', dest='weekly', help='Will generate statistics for the weekly report', type=lambda x:bool(distutils.util.strtobool(x)))

    args = parser.parse_args()
    main(args.participants, args.daily,args.weekly)

