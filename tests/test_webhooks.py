import subprocess
import time
from multiprocessing import Process
from threading import Thread

import dotenv

from webhook_server import app_init


def fire_webhook():
    app = app_init("test")
    app.testing = True
    env_vars = dotenv.dotenv_values()
    pr = app.extensions['plaid_ext']
    res = pr.sandbox_fire_webhook(
        access_token=env_vars.get('ACCESS_TOKEN'),
        webhook_type="TRANSACTIONS",
        webhook_code="SYNC_UPDATES_AVAILABLE",
        )
    assert res['request_id'] and res['webhook_fired']

def run_server():
    app = app_init("test")
    app.testing=True
    app.run(host="127.0.0.1", port=5000)

def start_server():
    server_run = Process(target=run_server, name="server_run")
    server_run.start()
    time.sleep(60)
    server_run.terminate()

def tunnel_sub():
    subproc = subprocess.Popen(args="cloudflared tunnel run --token $(cloudflared tunnel token myownbytes)", shell=True)
    time.sleep(60)
    subproc.terminate()

def start_tunnel():
    server_run = Process(target=tunnel_sub, name="server_run")
    server_run.start()
    time.sleep(65)
    server_run.terminate()

def test_webhooks():
    serve = Thread(target=start_server)
    tunnel = Thread(target=start_tunnel)
    serve.start()
    tunnel.start()

    if serve.is_alive() and tunnel.is_alive():
        time.sleep(20)
        fire_webhook()