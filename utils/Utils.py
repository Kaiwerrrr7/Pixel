from datetime import datetime
import requests

def get_formatted_datetime():
    return datetime.now().strftime("[%Y/%m/%d %H:%M:%S]")

def get_task_by_name(tasks, name):
    for task in tasks:
        if task["name"] == name:
            return task
    return None
    
def format_proxy(proxy_string):
    proxy_string = proxy_string.replace("\n", "")
    parts = proxy_string.split(':')
    
    if len(parts) == 4:
        ip, port, user, password = parts
        return f"{user}:{password}@{ip}:{port}"
    elif len(parts) == 2:
        ip, port = parts
        return f"{ip}:{port}"
    else:
        raise ValueError("Invalid proxy format. Must be 'user:pass:ip:port' or 'ip:port'.")