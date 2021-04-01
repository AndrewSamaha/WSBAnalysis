# WSBAnalysis
An analysis of posts on r/WallStreetBets

# Background
In the January 2021, a large group of individual investors held together by an online forums (r/WallStreetBets) pushed a stock (GME) from a modest $17/share to $347/share. This was considered noteworthy because a) institutional investors had signaled the company was overvalued and were shorting it and b) those institutional investors lost a significant amount of money, with one allegedly going bankrupt.

Hence, the structure of this online community is worthy of investigation because of its ability to steer the behavior of a large number of invidivual investors in a way that negates contrary messaging of top-down institutional decision makers and actors. With that in mind, the purpose of this investigation is to gain an understanding of the structure of the online community, how it communicates about stock, how messages about stocks disseminate and maintain in the discourse, and so on.



# The Data

As of 04/01/21, the dataset consisted of 1689 submissions to r/WallStreetBets from 03/18/21 to 03/31/21. These were scraped using the Reddit API using a tool I developed, [WSBScraper](https://github.com/AndrewSamaha/WSBScraper), which saves posts to a MongoDB.

A Sample:
```
{ "_id" : ObjectId("605bb15d5df7eedfb49c1b8d"), "id" : "mchdcf", "fullname" : "t3_mchdcf", "selftext" : "", "created_utc" : "2021-03-24 17:36:29", "num_comments" : 2, "score" : 7, "upvote_ratio" : 1, "is_original_content" : false, "permalink" : "/r/wallstreetbets/comments/mchdcf/im_an_abe_and_i_eat_crayons_keeping_those_gme/", "title" : "I’m an abe 🦍 and I eat crayons 🖍 Keeping those GME contracts because selling is a loss all in its own! 17K down and still holding strong!", "author" : "Powerful-Ad812", "firstseen" : "2021-03-24 21:38:37.008913" }
```

# The authors
A total of 1300 submission authors are represented in the data. The plot below shows a histogram of the authors ranked from most to lease posts. Note the vast majority of posters only posted once during the time period. Conversely, a minority of posters contributed 6 or more posts.
![Figure 1](figures/pda_numposts.png)
![Figure 1](figures/pda_numposts_hist.png)
![Figure 1](figures/pda_biggestposters.png)
<Figure size 432x432 with 1 Axes><Figure size 432x432 with 1 Axes><Figure size 432x432 with 1 Axes>

| Poster | Post Count |
|--------|------------|
| <a href=https://www.reddit.com/user/OPINION_IS_UNPOPULAR/>OPINION_IS_UNPOPULAR</a> | 44 |
| <a href=https://www.reddit.com/user/disgruntledbkbum/>disgruntledbkbum</a> | 18 |
| <a href=https://www.reddit.com/user/pdwp90/>pdwp90</a> | 10 |
| <a href=https://www.reddit.com/user/AutoModerator/>AutoModerator</a> | 9 |
| <a href=https://www.reddit.com/user/CMScientist/>CMScientist</a> | 9 |
| <a href=https://www.reddit.com/user/Jesus_Gains_Christ/>Jesus_Gains_Christ</a> | 9 |
| <a href=https://www.reddit.com/user/GrubbyWango/>GrubbyWango</a> | 8 |
| <a href=https://www.reddit.com/user/Citor3_scenes/>Citor3_scenes</a> | 8 |
| <a href=https://www.reddit.com/user/DanyeelsAnulmint/>DanyeelsAnulmint</a> | 7 |
| <a href=https://www.reddit.com/user/dvdgelman7/>dvdgelman7</a> | 7 |
| <a href=https://www.reddit.com/user/Anal_Chem/>Anal_Chem</a> | 7 |
| <a href=https://www.reddit.com/user/Professional_War1998/>Professional_War1998</a> | 6 |
| <a href=https://www.reddit.com/user/indonesian_activist/>indonesian_activist</a> | 6 |
| <a href=https://www.reddit.com/user/GmeCalls-UrWifesBf/>GmeCalls-UrWifesBf</a> | 6 |



# Technology Stack
1. Python
1. Jupyter Labs (pda/eda)
1. MongoDB (database)
1. Matplotlib (visualization)
1. PWeave (this readme)

_This file was compiled on 2021-04-01._
