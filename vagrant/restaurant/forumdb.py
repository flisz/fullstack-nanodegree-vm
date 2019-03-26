# "Database code" for the DB Forum.

import datetime
import psycopg2
import bleach

POSTS = [("This is the first post.", datetime.datetime.now())]

def get_posts():
  """Return all posts from the 'database', most recent first."""
  db = psycopg2.connect(dbname='forum')
  cursor = db.cursor()
  query = 'SELECT content, time FROM posts ORDER BY time DESC'
  cursor.execute(query)
  results = cursor.fetchall()
  db.close()
  output = []
  for result in results:
    items = ()
    for item in result:
      if isinstance(item,str):
        item = bleach.clean(item)
      items += (item,)
    output.append(items)
  return output

def add_post(content):
  """Add a post to the 'database' with the current timestamp."""
  #POSTS.append((content, datetime.datetime.now()))
  data = (content,datetime.datetime.now())
  db = psycopg2.connect(dbname='forum')
  cursor = db.cursor()
  query = 'INSERT INTO posts (content, time) VALUES (%s,%s)'
  cursor.execute(query,data)
  db.commit()
  db.close()





