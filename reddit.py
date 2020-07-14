def post_to_reddit():
    reddit = praw.Reddit(client_id='',
                         client_secret='',
                         user_agent='devlogr:v0.0.1 (by /u/samsfacee)',
                         username='',
                         password=getpass.getpass('reddit password: '))
 
    subreddit = 'samsfacee_praw_test'

    print('creating submission to r/{}'.format(subreddit))
    title = "PRAW documentation"
    url = 'https://praw.readthedocs.io'
    submission = reddit.subreddit(subreddit).submit(title, url=url)
    print('submission is up: https://reddit.com{}'.format(submission.permalink))

    print('replying to submission with CTA...')
    submission.reply("reply")