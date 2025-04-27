from celery import shared_task
import subprocess

@shared_task
def sync_bc_linbc_task():
    subprocess.call(['python', 'manage.py', 'sync_BcLinbc', '--date', '1'])
