'''
Helper functions for use in README.pmd and
readme-testing.ipynb
'''
from pymongo import MongoClient
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns

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

def groupbyauthor(show=False, min=0):
    '''
    returns num_unique_posters, poster_names, poster_counts
    '''
    global wsbs
    authors = wsbs.aggregate([{"$group":{"_id":"$author","count": { "$sum":1 }}},{"$sort":{'count':-1}}])
    most = 10
    i = 0
    post_counts = []
    posters = []
    for x in authors:
        if x['count'] > 1 and show:
            print(x)
    
        if x['count'] >= min:
            i += 1
            post_counts.append(x['count'])
            posters.append(x['_id'])
            
    return (i, posters, post_counts)

def makeauthorfigures():
    (num_unique_posters, posters, post_counts) = groupbyauthor()

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
    plt.tight_layout()
    plt.savefig('figures/pda_numposts.png')
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.hist(x=post_counts)
    ax.set_ylabel(f'Number of Posters (n={num_unique_posters})')
    ax.set_xlabel('Number of Posts')
    plt.tight_layout()
    plt.yscale('log')
    plt.savefig('figures/pda_numposts_hist.png')
    
    num, authors, counts = groupbyauthor(show=False, min=6)
    fig, ax = plt.subplots(1,1, figsize=(6,6))
    ax.barh(y=authors, width=counts)
    ax.set_ylabel('Most Productive Posters')
    ax.set_xlabel('Number of Posts')
    plt.tight_layout()
    plt.savefig('figures/pda_biggestposters.png')
    
def makebiggestauthortable():
    num, authors, counts = groupbyauthor(show=False, min=6)
    print('| Poster | Post Count |')
    print('|--------|------------|')
    for author,count in zip(authors,counts):
        print(f'| <a href=https://www.reddit.com/user/{author}/>{author}</a> | {count} |')

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
    plt.tight_layout()
    if log:
        plt.yscale('log')
    if save:
        plt.savefig(save)
    pass

def groupby_hour(save=None):
    first = None
    last = None
    
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
    plt.gca().set_ylim(bottom=0)
    plt.tight_layout()
    if save:
        plt.savefig(save)

def groupby_month_day_hour(save=None):
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
    for val in dates_sorted:
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
    plt.gca().set_ylim(bottom=0)
    plt.tight_layout()
    if save:
        plt.savefig(save)

if __name__ != '__main__':
    setup()