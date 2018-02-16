import os
import pytz
import datetime

class Settings:
    BASEDIR = os.path.realpath(os.path.dirname(__file__))
    WEBSITE_NAME = 'Online Judge'
    # SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://username:mypassword@localhost/codepass'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/codepass.db'
    SECRET_KEY = 'you can copy from: python -c "print(repr(__import__(\"os\").urandom(30)))"'
    WEBROOT = ''
    TMP_UPLOAD_DIR = 'data/tmp_upload'
    TESTCASES_DIR = 'data/testcases'

    WEB = {
        'PROBLEM_FORMAT': [
            dict(key='title', type='string', title='Title'),
            dict(key='source', type='string', title='Source'),
            dict(key='author', type='string', title='Author'),
            dict(key='time_limit', type='int', title='Time Limit', hint='ms, per testcase'),
            dict(key='memory_limit', type='int', title='Memory Limit', hint='KB'),
            dict(key='description', type='markdown', title='Description'),
            dict(key='input_format', type='markdown', title='Input Format'),
            dict(key='output_format', type='markdown', title='Output Format'),
            dict(key='samples', type='combo', content=[
                dict(key='input', type='code', title='Sample Input'),
                dict(key='output', type='code', title='Sample Output'),
                dict(key='explanation', type='markdown', title='Sample Explanation')
            ]),
            dict(key='hints', type='markdown', title='Hints'),
        ],
    }
