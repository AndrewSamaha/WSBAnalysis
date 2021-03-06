# WSBAnalysis
I'm interested in understanding posting and post-popularity in WallStreetBets. WallStreetBets is online community of individual and often unruly investors. Their communication style is meme-driven and often provocative. Their elevate underdogs and denegrate the financial establishment. When they act as a group, they can have surprising effects on the market, e.g., Game Stop. 



# The Dataset

As of 05/19/21, the dataset consisted of 5203 submissions to r/WallStreetBets from a period of 62.2 days beginning 03/18/21 and ending 05/19/21. These were scraped using the Reddit API and a tool I developed, [WSBScraper](https://github.com/AndrewSamaha/WSBScraper), which saves posts to a MongoDB.

A Sample:
```
{ 
    "_id" : ObjectId("605bb15d5df7eedfb49c1b8d"), 
    "id" : "mchdcf", 
    "fullname" : "t3_mchdcf", 
    "selftext" : "", 
    "created_utc" : "2021-03-24 17:36:29", 
    "num_comments" : 2, 
    "score" : 7, 
    "upvote_ratio" : 1, 
    "is_original_content" : false, 
    "permalink" : "/r/wallstreetbets/comments/mchdcf/im_an_abe_and_i_eat_crayons_keeping_those_gme/", 
    "title" : "Iām an abe š¦ and I eat crayons š Keeping those GME contracts because selling is a loss all in its own! 17K down and still holding strong!", 
    "author" : "Powerful-Ad812", 
    "firstseen" : "2021-03-24 21:38:37.008913" 
}
```

# Questions
For this analysis, I focused on four questions:
1. When do people post?
1. Who posts?
1. What relationships exist between Reddit's various post-popularity metrics?
1. What makes for a popular post?

# When do people post?
Figure 1, below, shows the total number of posts for each hour. The x-axis is hours in January 1st, 2021 and the y-axis shows the count in each of the plotted hours. Note the extreme outlier -- those took place during a four-hour period on March 24th, 2021 (shortly after 2000 hours on the graph below).<br>
![Figure 1](figures/posts_per_hour.png "Figure 1")
<Figure size 432x432 with 1 Axes><Figure size 432x432 with 1 Axes>

Figure 2, below, shows the same data aggregated across hours plotted with 95% bootstrapped confidence bands (60k resamples each hour). Note the intra-day pattern, with the lowest frequency of posts occurring between midnight and 9AM UTC. Also note the peak, which appears at 16 UTC or between 4-5pm EST, one hour before market close.<br>
![Figure 2](figures/avg_posts_per_hour.png "Figure 2")

<Figure size 432x432 with 1 Axes>
Below is a histogram of submission deltas (seconds between posts) plotted with a log y-axis. As can be seen in the figure, the majority of the posts occur less than 5,000 seconds apart, or ~83 minutes. 

![Figure 3](figures/submissiondeltas.png "Figure 3")


Removing deltas above 5000 gives us a smooth distribution that we can plot in arithmatic space:<br>
![Figure 4](figures/submissiondeltas_clean.png "Figure 4")
<Figure size 432x432 with 1 Axes>

Also, it's worth examining the left-side of the distribution more closely to make sure the geometric shape still holds true at shorter deltas.<br>
![Figure 5](figures/submissiondeltas_left.png "Figure 5")
<Figure size 432x432 with 1 Axes>

These data show that the most frequently-occurring interval between submissions is 20 s or less. And it roughly follows an exponential decline, suggesting that post occurrences could be modeled as independent and randomly occurring events.

# Who posts?

A total of 3438 submission authors are represented in the data. The plot below shows a histogram of the authors ranked from most to lease posts. Note the vast majority of posters only posted once during the time period. Conversely, a minority of posters contributed 6 or more posts.

![Figure 6](figures/pda_numposts_hist.png "Figure 6")
![Figure 7](figures/pda_biggestposters.png "Figure 7")
<Figure size 432x432 with 1 Axes><Figure size 432x432 with 1 Axes><Figure size 432x432 with 1 Axes>



(Note: Redditor names have been anonymized/sanitized.)

# What relationships exist between Reddit's various post-popularity metrics?

![Figure](figures/num_comments_by_scoreNone.png)
<Figure size 432x432 with 1 Axes>

These figures show the relationship between a submission's score and the number of comments it's received. The figure seems to show three clusters of data points:
1. A set there the number of comments remains relatively low but there can be very high scores.
2. A set there the score is around 20-25k through a big range of comments.
3. A set where the scores are relatively low but there is a big range of number of comments.

The first set looks like the biggest (n = 87%), so let's focus on those for now by truncating the set to those with fewer than 2000 comments:

![Figure](figures/num_comments_by_score_logx_logyNone.png)
<Figure size 432x432 with 1 Axes>
This figure shows a clear correlation between the logs of the score and number of comments.

Now, let's turn our attention back toward the remaining comparisons:

![Figure](figures/num_comments_by_upvote_ratio_logxNone.png)
<Figure size 432x432 with 1 Axes>
The relationship between score and upvote ratio is a monotonicly incresing, negatively accelerated function.

![Figure](figures/score_by_upvote_ratio_logxNone.png)
<Figure size 432x432 with 1 Axes>
Interestingly, the relationship between upvote ratio and score is bitonic, which is to say that score and upvote ratio increase together and then at some point, that relationship reverses: For example, posts with the most up votes are likely to have a higher proportion of down votes than posts with only somewhat fewer upvotes. Perhaps posts that attract the most upvotes are exceptionally controversial, and therefore likely to obtain proportionally fewer votes than slightly less popular posts. Or maybe, as posts become more popular, they attract more dissenters and contrarians.


# What makes for a popular post?
Here, I was interesting in two questions that felt intuitively likely:
1. Are older posts more popular?

![Figure](figures/score_by_age_logy.png)
<Figure size 432x432 with 1 Axes>


![Figure](figures/upvote_ratio_by_age.png)
<Figure size 432x432 with 1 Axes>


![Figure](figures/num_comments_by_age_logy.png)
<Figure size 432x432 with 1 Axes>

Each point in the above figure represents a submission, it's age, and a popularity metric. If a post's popularity increased with age, then then we'd expect to see data point arranged in a increasing pattern. No such pattern is apparent in the data for any of the metrics.


2. Are posts by more frequently posters more popular?
In the figure below, each data point represents a different poster. The data are segregated into two groups: those posting only once during the observation window (represented by the pink data point) and those with 4 or more posts (represented by the blue data point). If frequent posters were associated with more popularity, then we'd expect to see the data points either above the pink or arranged at a steeper incline. However, that is not the case. In fact, frequent posters appear exactly in the middle of the one-time poster distribution. Perhaps the variability in frequent posters is smaller, however that's difficult to see visually given the relatively smaller sample size of the group.

![Figure](figures/postcount_by_avgscoreperpost.png)
<Figure size 432x432 with 1 Axes>


No.


# Results Summary
For this analysis, I focused on four questions:
#### 1. When do people post?
On most days, there are between 0 and 14 posts per hour, with most posts happening in the hour before the close of trading in US markets (4-5pm EST).
#### 2. Who posts?
Most posters created only one post during the obversaion window, with only a minority of posters creating more than 6 posts.
#### 3. What relationships exist between Reddit's various post-popularity metrics?
Most of Reddit's post-popularity metrics are positively correlated and monotonic, with an exception being the relaltionship between upvote ratio and score, which appears to be bi-tonic: increasing to a point and then decreasing.
#### 4. What makes for a popular post?
Two of the most intuitively likely candidates (post age and the productivity of the poster) had no clear reltaionship with post productivity.

# Future Directions
In the future, I'm interested in:
1. Content Analyses -- The current analysis was contain naive, future analyses could examine content (images/text) to see if can be used to predict popularity, to examine meme references, and stock ticker mentions.
2. Relationships to other datasets, e.g., do stock price swings predict discussions on Reddit, or vice-versa?
3. Post life cycle -- It might be interesting to examine post popularity over time to identify if post-popularity metrics within the first few hours or minutes of a post predict asympototic popularity.
4. Investigating whether frequent posters have less variability as a group in post popularity as compared to one-time posters.
5. Examine those three clusters of points in the post-popularity comparison between score and number of comments.

# About Me
I'm a software developer, a former academic, and a yoga instructor. My passion is communicating stories with data. I leverage my creativity, deep curiosity of problems, and skills to create compelling and meaningful narratives. My strengths are software development, quantitative analysis/visualization, and communicating with non-technical audiences.

# Technology Stack
1. Python
1. Jupyter Labs (pda/eda)
1. WSBScraper, MongoDB, Docker (backend)
1. Matplotlib, Seaborn (visualization)
1. PWeave, Bash (CI/CD: this readme)

_This file was compiled on 2021-05-19._
