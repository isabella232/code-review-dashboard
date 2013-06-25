from auth import requires_auth
from flask import Flask, render_template
from github import Github
import config
import timeit

app = Flask(__name__)


@app.route("/")
@requires_auth
def index(auth=None):
    github = Github(auth)
    summaries = {'hot': [], 'cold': [], 'burning': []}

    start = timeit.default_timer()
    author = github.user()
    result = github.search_pulls()
    end = timeit.default_timer()

    for pull in result['pulls']:
        summaries[categorize_pull(pull)].append(pull)

    return render_template('columns.html',
                           title=config.TITLE,
                           pulls=summaries,
                           total_threads=result['total-threads'],
                           total_requests=result['total-requests'],
                           rate_limit=result['rate-limit'],
                           process_time=(end - start),
                           old_days=config.OLD_DAYS,
                           login=author)


def categorize_pull(pull):
    likes = pull['likes']
    if likes >= 2:
        return 'burning'
    elif likes > 0:
        return 'hot'
    return 'cold'


if __name__ == "__main__":
    app.debug = True
    app.run(host=config.LISTEN_ADDRESS)
