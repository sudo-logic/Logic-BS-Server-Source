# coding: utf-8
import bs
try:
    from flask import Flask, request, render_template
    _flask = True
except:
    _flask = False
import thread
import detect
import sys
import time
import os
import logging
import some
os.environ['FLASK_APP'] = 'LogicApp'
os.environ['FLASK_ENV'] = 'development'

log = logging.getLogger('werkzeug')
log.setLevel(logging.CRITICAL)

if _flask:
    app = Flask(__name__)

    @app.route('/enter', methods=['GET', 'POST'])
    def home():
        if request.method == 'GET':
            return render_template('LimitChange.html',
                                   online=detect.players_num)
        elif request.method == 'POST':
            if request.form['text'].isdigit():
                if request.form['pass'] == '69':
                    return change_size(request.form['text'])
                else:
                    return 'Wrong Password'
            else:
                return 'Input Must Be Integer'

    @app.route('/serverlist', methods=['GET'])
    def returnlist():
        return open(bs.getEnvironment()['userScriptsDirectory'] +
                    '/ServerList.json').read()

    @app.route('/roster', methods=['GET'])
    def roster():
        return detect.old

    @app.route('/len', methods=['GET'])
    def returnlen():
        return str(detect.players_num)

    @app.route('/')
    def change_size(size=None):
        if size is not None:
            size = int(size)
            print 'Limit Change To {} Requested'.format(size)
            detect.maxPlayers = size
            return (
                'Players Online: {}<br>Player Limit Changed To: {}<br>You Have 30 Seconds To Join The Party'
                .format(detect.players_num, detect.maxPlayers))
        elif detect.maxPlayers <= detect.players_num:
            size = detect.players_num + 2
            print 'Limit Change To {} Requested'.format(size)
            detect.maxPlayers = size
            thread.start_new_thread(timer, ())
            return (
                'Players Online: {}<br>Player Limit Changed To: {}<br>You Have 30 Seconds To Join The Party'
                .format(detect.players_num, detect.maxPlayers))
        else:
            return render_template('NotFull.html', online=detect.players_num)

    def timer():
        time.sleep(30)
        detect.reset()

    def flush():
        pass

    sys.stdout.flush = flush

    if some.is_logic: flask_run = thread.start_new_thread(
        app.run, ("0.0.0.0", bs.getConfig()['Port'], False))
