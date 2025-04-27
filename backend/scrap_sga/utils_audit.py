from .models import AuditLog
from django.forms.models import model_to_dict
from django.utils import timezone
import json
import datetime
from decimal import Decimal

def log_audit(model_instance, action, changed_by=None, diff=None, source='sync_script'):
    """
    Enregistre une entrée dans l'audit log.
    - model_instance : instance du modèle concerné
    - action : 'created', 'updated', 'deleted'
    - changed_by : utilisateur ou 'script'
    - diff : dict {avant, apres} ou valeurs modifiées
    - source : origine de la modif (script, admin, ...)
    """
    AuditLog.objects.create(
        model_name=model_instance.__class__.__name__,
        object_id=str(getattr(model_instance, 'pk', None) or getattr(model_instance, 'id', None)),
        action=action,
        changed_by=changed_by,
        change_time=timezone.now(),
        diff=json_ready(diff) if diff else None,
        source=source
    )


def compute_diff(old_obj, new_obj):
    """
    Retourne un dict des différences entre deux objets Django (model_to_dict).
    """
    old = model_to_dict(old_obj) if old_obj else {}
    new = model_to_dict(new_obj) if new_obj else {}
    diff = {'before': {}, 'after': {}}
    for k in set(old.keys()).union(new.keys()):
        if old.get(k) != new.get(k):
            diff['before'][k] = old.get(k)
            diff['after'][k] = new.get(k)
    return diff if diff['before'] or diff['after'] else None


def json_ready(obj):
    """Rend un dict (ou tout objet) JSON serializable (datetime, Decimal, etc.)"""
    if isinstance(obj, dict):
        return {k: json_ready(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [json_ready(v) for v in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        try:
            # Cas où c'est un objet complexe (ex : queryset, model, etc.), on tente une conversion str
            return str(obj)
        except Exception:
            return None


def log_delete(model_instance, changed_by=None, source='sync_script'):
    AuditLog.objects.create(
        model_name=model_instance.__class__.__name__,
        object_id=str(getattr(model_instance, 'pk', None) or getattr(model_instance, 'id', None)),
        action='deleted',
        changed_by=changed_by,
        change_time=timezone.now(),
        diff={'before': json_ready(model_to_dict(model_instance)), 'after': None},
        source=source
    )
