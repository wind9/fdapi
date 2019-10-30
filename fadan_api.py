import requests
import logging
from yaml import safe_load
from queue import Queue
import os
import threading
import random
import time
import hashlib


volume_dir = os.path.join(os.path.dirname(__file__), 'volume')
print(volume_dir)
if not os.path.exists(volume_dir):
    os.mkdir(volume_dir)
log_file = os.path.join(volume_dir, 'fadan.log')
phone_file = os.path.join(volume_dir, 'phone.txt')
config_file = os.path.join(volume_dir, 'config.yaml')


def get_args():
    with open(config_file, 'r') as f:
        content = f.read()
    cf = safe_load(content)
    return cf


def get_log():
    log = logging.getLogger("发单api")
    log.setLevel(logging.DEBUG)
    handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


def init_queue():
    with open(phone_file, 'r') as f:
        for line in f.readlines():
            charge_info = {}
            charge_info['phone'] = line.strip().split()[0]
            charge_info['face'] = line.strip().split()[1]
            q.put(charge_info)


def md5(text):
    m = hashlib.md5()
    m.update(text)
    return m.hexdigest()


def charge(charge_info):
    phone = charge_info['phone']
    face = charge_info['face']
    param = {
        "agentId": str(charge_args.get('agentId')),
        "businessId": str(charge_args.get('businessId')),
        "reqStreamId": "fd{}{}".format(str(round(time.time()*1000)), random.randint(100, 1000)),
        "phone": str(phone),
        "face": str(face),
        "tradePwd": md5(str(charge_args.get('tradePwd')).encode()),
        "timeStamp": time.strftime('%Y%m%d%H%M%S'),
    }
    param2 = sorted(param)
    param['notify'] = ""
    source_str = "".join([param[k] for k in param2]) + charge_args.get('appKey')
    param['sign'] = md5(source_str.encode('utf-8'))
    r = requests.get(charge_args.get('charge_url'), params=param)
    resp = r.content.decode('utf-8')
    return resp


def run():
    while True:
        charge_info = q.get()
        resp = charge(charge_info)
        log.info("{}充值结果{}".format(charge_info, resp))
        q.task_done()


if __name__ == '__main__':
    global q, log, charge_args
    q = Queue()
    log = get_log()
    charge_args = get_args()
    init_queue()
    log.info("初始化充值队列完成")
    thread_num = charge_args.get('thread_num')
    thread_list = []
    for thread_id in range(thread_num):
        t = threading.Thread(target=run)
        thread_list.append(t)
    for t in thread_list:
        t.setDaemon(True)
        t.start()
    q.join()


