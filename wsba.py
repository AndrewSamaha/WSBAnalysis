'''
Helper functions for use in README.pmd and
readme-testing.ipynb
'''
from pymongo import MongoClient
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import timedelta
import random
import numpy as np
#%matplotlib inline

# defining some gloabl variables
inited = False
db = None
wsbs = None

def setup_seaborn():
    # Pilfered from https://towardsdatascience.com/making-matplotlib-beautiful-by-default-d0d41e3534fd
    sns.set(
        #font='Franklin Gothic Book',
        rc={
             'axes.axisbelow': False,
             'axes.edgecolor': 'lightgrey',
             'axes.facecolor': 'None',
             'axes.grid': False,
             'axes.labelcolor': 'dimgrey',
             'axes.spines.right': False,
             'axes.spines.top': False,
             'figure.facecolor': 'white',
             'lines.solid_capstyle': 'round',
             'patch.edgecolor': 'w',
             'patch.force_edgecolor': True,
             'text.color': 'dimgrey',
             'xtick.bottom': True,
             'xtick.color': 'dimgrey',
             'xtick.direction': 'out',
             'xtick.top': False,
             'ytick.color': 'dimgrey',
             'ytick.direction': 'out',
             'ytick.left': True,
             'ytick.right': False})
    sns.set_context("notebook", rc={"font.size":16,
                                    "axes.titlesize":20,
                                    "axes.labelsize":18})

def setup_mongo():
    global db
    global wsbs
    #pymongo stuff
    client = MongoClient('localhost', 27017)
    # Access/Initiate Database
    db = client['samdatascidb']
    # Access/Initiate Collection
    wsbs = db['wsb_submissions']

def setup(force=False):
    global inited
    if not inited or force:
        setup_seaborn()
        setup_mongo()
        inited = True

    
def getnumsubmissions():
    '''
    returns the number of submissions
    '''
    num = wsbs.count_documents({})
    return num

def findone():
    '''
    returns one example submission
    '''
    return str(wsbs.find_one())

def getdaterange():
    '''
    returns the date range of the submissions in a tuple
    first, last
    '''
    first = None
    last = None
    dates_sorted = wsbs.aggregate( [ { '$project': { 'date': { '$dateFromString': 
        { 'dateString': '$created_utc' } } } }, { '$sort': { 'date' : 1} } ] )
    for val in dates_sorted:
        first = val
        break
    dates_sorted = wsbs.aggregate( [ { '$project': { 'date': { '$dateFromString': 
        { 'dateString': '$created_utc' } } } }, { '$sort': { 'date' : -1} } ] )
    for val in dates_sorted:
        last = val
        break
    
    #print(first,last)
    return first,last

def get_days():
    first,last = getdaterange()
    diff = last['date']-first['date']
    return diff.days+diff.seconds/60/60/24

def get_authors(show=False, min=0, max=999_999, sortby='rate', returnDictionary=False):
    authors = wsbs.aggregate([ 
        { 
            "$group": {
                "_id": "$author",
                "count": { "$sum": 1 },
                "totalscore": { "$sum": "$score"},
                "totalcomments": { "$sum": "$num_comments"}
            } 
        },
        { 
            "$project": {
                #"author": "$author",
                "count": 1,
                "totalscore": "$totalscore",
                "totalcomments": "$totalcomments",
                "rate": { "$divide": ["$count",get_days()] },
                "avgScorePerPost": { "$divide": ["$totalscore","$count"] },
                "avgScorePerDay": { "$divide": ["$totalscore", get_days()] },
                "avgCommentsPerPost": { "$divide": ["$totalcomments","$count"] },
                "avgCommentsPerDay": { "$divide": ["$totalscore", get_days()] }
            } 
        },
        {    
            "$sort": {
                'rate':-1  
            }
        }
    ])
    i = 0
    data = dict()
    data['posters'] = []
    data['postCount'] = []
    data['postRate'] = []
    data['totalScore'] = []
    data['totalComments'] = []
    data['avgScorePerDay'] = []
    data['avgScorePerPost'] = []
    data['avgCommentsPerDay'] = []
    data['avgCommentsPerPost'] = []
    
    posters = []
    post_counts = []
    post_rates = []
    for x in authors:
        #if i > 10:
        #    return
        
        if x['count'] > 1 and show:
            pass
    
        if x['count'] >= min and x['count'] <= max:
            if show:
                print(x)
                #print(x,round(x['count'],2),round(x['rate'],2),round(x['totalscore'],2),round(x['avgScorePerPost'],2),round(x['avgScorePerDay'],2))
            i += 1
            data['postCount'].append(x['count'])
            data['posters'].append(x['_id'])
            data['postRate'].append(x['rate'])
            data['totalScore'].append(x['totalscore'])
            data['totalComments'].append(x['totalcomments'])
            data['avgScorePerDay'].append(x['avgScorePerDay'])
            data['avgScorePerPost'].append(x['avgScorePerPost'])
            data['avgCommentsPerDay'].append(x['avgCommentsPerDay'])
            data['avgCommentsPerPost'].append(x['avgCommentsPerPost'])
            
    
    if returnDictionary:
        return data
    
    return (i, data['posters'], data['postCount'], data['postRate'])

def makeauthorfigures():
    (num_unique_posters, posters, post_counts, post_rates) = get_authors(show=False)

    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.scatter(
        x=stats.norm.rvs(
            1,
            size=len(post_counts),
            scale=.2),
        y=post_counts,
        s=10,
        alpha=.4)
    ax.set_ylabel(f'Number of Posts (n={sum(post_counts)})')
    ax.set_ylim(ymin=0)
    ax.set_xlim(xmin=0,xmax=2)
    _ = plt.tight_layout()
    _ = plt.savefig('figures/pda_numposts.png')
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.hist(x=post_counts)
    ax.set_ylabel(f'Number of Posters (n={num_unique_posters})')
    ax.set_xlabel('Number of Posts')
    _ = plt.tight_layout()
    plt.yscale('log')
    _ = plt.savefig('figures/pda_numposts_hist.png')
    
    num, authors, counts, rates = get_authors(show=False, min=6)
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.barh(y=authors, width=counts)
    ax.set_ylabel('Most Productive Posters')
    ax.set_xlabel('Number of Posts')
    _ = plt.tight_layout()
    _ = plt.savefig('figures/pda_biggestposters.png')
    
def makebiggestauthortable():
    data = get_authors(show=False, min=6, returnDictionary=True)
    print('| Poster | Post Count | Posts/Day | Avg Score/Post | Avg Comments/Post |')
    print('|--------|------------|-----------|----------------|-------------------|')
    for author,count,rate,scores,comments in zip(data['posters'],data['postCount'],data['postRate'],data['avgScorePerPost'],data['avgCommentsPerPost']):
        print(f'| <a href=https://www.reddit.com/user/{author}/>{author}</a> | {count} | {round(rate,2)} | {scores} | {comments} ')

def getsubmissiondeltas(max=None,log=True,save=None):
    submission_dates = wsbs.aggregate( [ {
        '$project': {
            'date': {
                '$dateFromString': {
                    'dateString': '$created_utc'
                 }
             }
        }
    }, { '$sort': { 'date' : -1} } ] )
    
    i = 0
    lastTime = None
    deltas = []
    for x in submission_dates:
        i += 1
        if lastTime != None:
            delta = (lastTime - x['date']).seconds
            if max == None or delta <= max:
                deltas.append(delta)
        #print(i, x)
        lastTime = x['date']
        #if i >= 30:
        #    break
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.hist(x=deltas)
    ax.set_ylabel(f'Number of Deltas (n={len(deltas)})')
    ax.set_xlabel('Deltas (Seconds Between Submissions)')
    _ = plt.tight_layout()
    if log:
        _ = plt.yscale('log')
    if save:
        _ = plt.savefig(save)
    pass

def groupby_hour(save=None):
    '''
    deprecated, replaced by posts_per_hour
    '''
    
    dates_sorted = wsbs.aggregate( [ 
        {
            '$project': {
                'hour': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%H"
                    }
                }
            }
        },
        {
            "$group": { 
                '_id':"$hour" ,
                'numsubmissions': { '$sum':1 }
            }#z
            
        },
        {
            "$sort":  { '_id': 1 } # This worked when there was a groupby for only a single field
            #"$sort":  { '_id': {'day':1, 'hour':1} }
        }
    ] )
    i = 0
    hours = []
    submissions = []
    for val in dates_sorted:
        hours.append(int(val['_id']))
        submissions.append(int(val['numsubmissions']))
        i += 1
        if i >= 10:
            pass
        
    
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.plot(hours, submissions)
    ax.set_ylabel(f'Number of Submissions (n={sum(submissions)})')
    ax.set_xlabel('Hour (UTC)')
    _ = plt.gca().set_ylim(bottom=0)
    _ = plt.tight_layout()
    if save:
        _ = plt.savefig(save)

def groupby_month_day_hour(save=None):
    '''
    deprecated, replaced by posts_per_hour
    '''
    def hour_of_year(month,day,hour):
        '''given an hour, day, and month, return the number of hours since the beginning of the year'''
        dayspermonth =[0,31,28,31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return hour + day*24 + sum(dayspermonth[:month]) * 24
    
    first = None
    last = None
    
    dates_sorted = wsbs.aggregate( [ 
        {
            '$project': {
                'month': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%m"
                    }
                },
                'day': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%d"
                    }
                },
                'hour': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%H"
                    }
                }
            }
        },
        {
            "$group": { 
                '_id':{'month':'$month','day':'$day','hour':"$hour"} ,
                'numsubmissions': { '$sum':1 }
            }#z
            
        },
        {
            "$sort":  { '_id': 1 } # This worked when there was a groupby for only a single field
            #"$sort":  { '_id': {'day':1, 'hour':1} }
        }
    ] )
    i = 0
    hours = []
    submissions = []
    
    #build a list of lists
    # submissions_each_hour[0] returns a list of submissions during midnight across all days
    # submissions_each_hour[1] returns a list of submissions during 1am across all days
    # and so on
    submissions_each_hour = []
    for hour in range(0,23):
        submissions_each_hour.append([])
        
    for val in dates_sorted:
        submissions_each_hour[ int(val['_id']['hour']) ].append( int(val['numsubmissions']) )
        hours.append(hour_of_year(int(val['_id']['month']),int(val['_id']['day']),int(val['_id']['hour'])))
        submissions.append(int(val['numsubmissions']))
        #print(val)
        i += 1
        if i >= 10:
            pass
        #break
    
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.plot(hours, submissions)
    ax.set_ylabel(f'Number of Submissions (n={sum(submissions)})')
    ax.set_xlabel('Hour Since the Beginning of the Year')
    _ = plt.gca().set_ylim(bottom=0)
    _ = plt.tight_layout()
    if save:
        _ = plt.savefig(save)

def posts_per_hour(save=[None,None]):
    def hour_of_year(month,day,hour):
        '''given an hour, day, and month, return the number of hours since the beginning of the year'''
        dayspermonth =[0,31,28,31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        return hour + day*24 + sum(dayspermonth[:month]) * 24
    
    def add_zeros(num_hourly_submissions, num):
        '''
        adds zeros to each hourly submission until the total number of data points equals num
        '''
        for i, hour in enumerate(num_hourly_submissions):
            while len(num_hourly_submissions[i]) < num:
                num_hourly_submissions[i].append(0)
        return num_hourly_submissions
    
    def calc_avg_submissions_each_hour(num_hourly_submissions, num_days):
        '''
        given a list of submissions each hour, calculate the average number
        of submissions for each hour and return that in a list.
        
        num_days - used as the denominator in the calculation of the average
        '''
        submissions_each_hour = []
        for i, hour in enumerate(num_hourly_submissions):
            submissions_each_hour.append( sum(hour) / num_days)
        return submissions_each_hour
    
    def calc_bootstrap(num_hourly_submissions, num_samples=60_000):
        strap_space = np.zeros((24,num_samples))
        
        for hour, hour_sample_space in enumerate(num_hourly_submissions):
            for s in range(0,num_samples):
                strap_space[hour,s] = sum(random.choices(hour_sample_space,k=len(hour_sample_space))) / len(hour_sample_space)
        
        #print(strap_space)
        return strap_space
    
    dates_sorted = wsbs.aggregate( [ 
        {
            '$project': {
                'month': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%m"
                    }
                },
                'day': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%d"
                    }
                },
                'hour': {
                    '$dateToString': {
                        'date': { '$dateFromString': {'dateString': '$created_utc' } }
                        ,"format": "%H"
                    }
                }
            }
        },
        {
            "$group": { 
                '_id':{'month':'$month','day':'$day','hour':"$hour"} ,
                'numsubmissions': { '$sum':1 }
            }#z
            
        },
        {
            "$sort":  { '_id': 1 } # This worked when there was a groupby for only a single field
            #"$sort":  { '_id': {'day':1, 'hour':1} }
        }
    ] )
    i = 0
    hours = []
    submissions = []
    unique_days = []
    
    
    
    #submissions_each_hour is a list of lists
    # submissions_each_hour[0] returns a list of submissions during midnight across all days
    # submissions_each_hour[1] returns a list of submissions during 1am across all days
    # and so on
    submissions_each_hour = []
    for hour in range(0,24):
        submissions_each_hour.append([])
        
    for val in dates_sorted:
        submissions_each_hour[ int(val['_id']['hour']) ].append( int(val['numsubmissions']) )
        hours.append(hour_of_year(int(val['_id']['month']),int(val['_id']['day']),int(val['_id']['hour'])))
        submissions.append(int(val['numsubmissions']))
        unique_day = val['_id']['month'] + val['_id']['day']
        if not unique_day in unique_days:
            unique_days.append(unique_day)
        #print(val)
        i += 1
        if i >= 10:
            pass
        #break
    
    # used to choose a denominator when calculating average submissions per hour
    most_hourly_observations = 0 
    
    for i,hour in enumerate(submissions_each_hour):
        #print(f'{i}:{len(hour)} {hour}')
        if len(hour) > most_hourly_observations:
            most_hourly_observations = len(hour)
    
    submissions_each_hour = add_zeros(submissions_each_hour, most_hourly_observations)
    
    #for i,hour in enumerate(submissions_each_hour):
    #    print(f'{i}:{len(hour)} {hour}')
    
    
    
    
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.plot(hours, submissions)
    ax.set_ylabel(f'Number of Submissions (n={sum(submissions)})')
    ax.set_xlabel('Hour (UTC)')
    _ = plt.gca().set_ylim(bottom=0)
    _ = plt.tight_layout()
    if save[0]:
        _ = plt.savefig(save[0])
    
    bootstrap = calc_bootstrap(submissions_each_hour)
    avg_submissions_each_hour = calc_avg_submissions_each_hour(submissions_each_hour, len(unique_days))
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.plot(range(0,24), avg_submissions_each_hour)
    ax.plot(range(0,24), np.percentile(bootstrap, 2.5, axis=1), c='red')
    ax.plot(range(0,24), np.percentile(bootstrap, 97.5, axis=1), c='red')
    ax.set_ylabel(f'Avg Number of Submissions (n={sum(submissions)})')
    ax.set_xlabel('Hour (UTC)')
    _ = plt.gca().set_ylim(bottom=0)
    _ = plt.tight_layout()
    if save[1]:
        _ = plt.savefig(save[1])   
        

def fig_field_by_age(field='score',logx=False,logy=False,save=False,ymax=None,ymin=None,ymedian=False,ymean=False):
    '''
    returns the filename of a figure where some field is plotted 
    as a function of the age of the post in minutes
    '''
    age = wsbs.aggregate( [ 
        {
            '$project': {
                'minutes_old': {
                    '$divide': [
                        {
                            '$subtract': [
                                { '$dateFromString': {'dateString': '$lastseen' } },
                                { '$dateFromString': {'dateString': '$created_utc' } }
                            ]
                        }, 60_000 # per hour: 3_600_000
                        
                    ]
                },
                f'{field}': 1
            }
        }
    ] )
    
    i = 0
    data = []
    ages = []
    for item in age:
        i += 1
        data.append(item[field])
        ages.append(item['minutes_old'])

    
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.scatter(ages, data, alpha=.5)
    ax.set_ylabel(field.capitalize())
    ax.set_xlabel('Submission Age (min)')
    
    if ymedian:
        from statistics import median
        ymedian = median(data)
        ax.axhline(ymedian,c='red',linestyle='-.',label=f'median={round(ymedian,2)}')
    
    if ymean:
        from statistics import mean
        ymean = mean(data)
        ax.axhline(ymean,c='red',linestyle='--',label=f'mean={round(ymean,2)}')
        
    if ymin:
        plt.gca().set_ylim(bottom=ymin)
    if ymax:
        plt.gca().set_ylim(top=ymax)
    
    if logx:
        plt.xscale('log')
        logx = '_logx'
    else:
        logx = ''

    if logy:
        plt.yscale('log')
        logy = '_logy'
    else:
        logy = ''
    if ymedian or ymean:
        ax.legend()
        
    _=plt.tight_layout()
    if save:
        filename = f'figures/{field}_by_age{logx}{logy}.png'
        _=plt.savefig(filename)
        print(f'![Figure]({filename})')
        return

def fig_field_by_field(fielda='score',fieldb='score',fielda_max=None,logx=False,logy=False,save=False,ymax=None,ymin=None,median=False,mean=False,xmax=None,xmin=None,spearman=None,pearson=None,regression=None):
    '''
    returns the filename of a figure where some field is plotted 
    as a function of the age of the post in minutes
    '''
    age = wsbs.aggregate( [ 
        {
            '$project': {
                f'{fielda}': 1,
                f'{fieldb}': 1
            }
        }
    ] )
    
    i = 0
    fielda_data = []
    fieldb_data = []
    for item in age:
        if fielda_max and item[fielda] > fielda_max:
            continue
        i += 1
        fielda_data.append(item[fielda])
        fieldb_data.append(item[fieldb])

    if spearman:
        spearman_rho, spearman_p = stats.spearmanr(a=fielda_data, b=fieldb_data)
        #print(f'spearman_rho={spearman_rho}   spearman_p={spearman_p}')
    
    if pearson:
        pearson_r, pearson_p = stats.pearsonr(x=fielda_data, y=fieldb_data)
        #print(f'pearson_r={pearson_r}   pearson_p={pearson_p}')
    
    lr_m=0
    lr_b=0
    lr_r=0
    lr_p=0
    lr_stredd = 0
    if regression:
        lr_m, lr_b, lr_r, lr_p, lr_stredd = stats.linregress(fielda_data, fieldb_data)
        def lr(x):
            return lr_m * x + lr_b
        #print("regression; pearson r: ", lr_r, lr_p, lr_stredd)
    
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.scatter(fielda_data, fieldb_data, alpha=.5)
    if regression:
        ax.plot([min(fielda_data),max(fielda_data)], [lr_m * min(fielda_data) + lr_b,lr_m * max(fielda_data) + lr_b],label=f'y={round(lr_m,2)}x+{round(lr_b)}, r={round(lr_r,2)} p={round(lr_p,4)}',c='red',linestyle='--')
        #print([min(fielda_data),max(fielda_data)])
        #print([lr_m * min(fielda_data) + lr_b,lr_m * max(fielda_data) + lr_b])
    ax.set_xlabel(fielda.capitalize())
    ax.set_ylabel(fieldb.capitalize())
    
    if median:
        median='median'
        from statistics import median
        xmedian = median(fielda_data)
        ymedian = median(fieldb_data)
        ax.scatter([xmedian],[ymedian],c='red',marker='o',s=100,label=f'median={round(xmedian,2)}, {round(ymedian,2)}',alpha=.5)
    
    if mean:
        mean='mean'
        from statistics import mean
        xmean = mean(fielda_data)
        ymean = mean(fieldb_data)
        ax.scatter([xmean],[ymean],c='red',marker='x',s=100,label=f'mean={round(xmean,2)}, {round(ymean,2)}',alpha=.5)
        
    if ymin!=None:
        plt.gca().set_ylim(bottom=ymin)
    if ymax:
        plt.gca().set_ylim(top=ymax)
    if xmax:
        plt.gca().set_xlim(right=xmax)
    if xmin!=None:
        plt.gca().set_xlim(left=xmin)
        
    if logx:
        plt.xscale('log')
        logx = '_logx'
    else:
        logx = ''

    if logy:
        plt.yscale('log')
        logy = '_logy'
    else:
        logy = ''
    if median or mean:
        ax.legend()
        
    _=plt.tight_layout()
    if save:
        filename = f'figures/{fielda}_by_{fieldb}{logx}{logy}{xmax}.png'
        _=plt.savefig(filename)
        print(f'![Figure]({filename})')
        return

def count(query):
    return wsbs.count_documents(query)
    
if __name__ != '__main__':
    setup()