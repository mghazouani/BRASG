from celery import shared_task, chain
import subprocess

@shared_task
def sync_bc_linbc_task(*args, **kwargs):
    subprocess.call(['python', 'manage.py', 'sync_BcLinbc'])

@shared_task
def sync_alimentation_solde_task(*args, **kwargs):
    subprocess.call(['python', 'manage.py', 'sync_alimentation_solde'])

@shared_task
def sync_bc_and_alimentation_task(*args, **kwargs):
    return chain(sync_bc_linbc_task.s(), sync_alimentation_solde_task.s())()
