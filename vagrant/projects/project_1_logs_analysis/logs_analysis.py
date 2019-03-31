#!/usr/bin/env python

import psycopg2 as psql

DASHES = '\n----------------------------------------------------------------'


def question_1():
    print("Question 1:\tWhat are the most popular three articles of all time?")
    query = """
    SELECT total, title
    FROM successful_reads
    GROUP BY title,total
    ORDER BY total DESC
    LIMIT 3
    """
    answer = "Answer 1:\tThe three most popular articles are:"
    run_query(query, answer)


def question_2():
    print("Question 2:\tWho are the most popular article authors of all time?")
    query = """
    SELECT sum(total) AS author_total, name
    from successful_reads
    GROUP BY name
    ORDER BY author_total DESC
    """
    answer = "Answer 2:\tThe most popular authors are:"
    run_query(query, answer)


def question_3():
    print("Question 3:\t\
On which days did more than 1% of requests lead to errors?")
    # this looks dumb because I had to remove all tabs in order to preserve
    # the prior formatting while avoiding any pycodestyle errors.
    query = """
    SELECT day, pct_404
    FROM daily_percent_http_status
    WHERE pct_404 > 1;
    """
    answer = "Answer 3:\tOn the following days >1% of requests had errors:"
    run_query(query, answer)


def select_query(query):
    db = psql.connect(dbname='news')
    cursor = db.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    db.close()
    return results


def output_results(answer, results):
    print(answer+DASHES)
    for result in results:
        line = ''
        # Not quite exactly the same ;P       ....All quibbling aside....
        # I appreciate the formatting feedback, but opted to leave this
        # the way I had it. For this project, I was trying to generalize
        # the output to be topic/row width agnostic. If I were trying to
        # build out a more detailed output interface I would likely use
        # your method.
        for item in result:
            line += '\t' + str(item)
        print(line)
    print('\n')


def run_query(query, answer):
    results = select_query(query)
    output_results(answer, results)


if __name__ == '__main__':
    print(DASHES)
    print("\tLOGS ANALYSIS" + DASHES + '\n')
    try:
        question_1()
        question_2()
        question_3()
    except Exception as e:
        print('EXCEPTION: {}'.format(str(e)))
