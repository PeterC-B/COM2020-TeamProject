import enum
import uuid
from datetime import date, datetime

from flask import has_request_context
from flask_jwt_extended import get_jwt_identity
from sqlalchemy import event, insert, inspect

from app.extensions import db
from app.models.database_change_log_model import DatabaseChangeLogModel

INSERT_OP = "INSERT"
UPDATE_OP = "UPDATE"
DELETE_OP = "DELETE"

_hooks_registered = False


def _make_json_safe(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_make_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _make_json_safe(item) for key, item in value.items()}
    return str(value)


def _get_record_id(instance):
    mapper = inspect(instance).mapper
    primary_key_parts = [str(getattr(instance, column.key, "")) for column in mapper.primary_key]
    return "|".join(primary_key_parts)


def _get_current_user_id():
    if not has_request_context():
        return None

    try:
        identity = get_jwt_identity()
    except (RuntimeError, TypeError, ValueError):
        return None

    if identity is None:
        return None
    if isinstance(identity, uuid.UUID):
        return identity

    try:
        return uuid.UUID(str(identity))
    except (TypeError, ValueError):
        return None


def _read_column_values(instance):
    mapper = inspect(instance).mapper
    return {column.key: _make_json_safe(getattr(instance, column.key)) for column in mapper.columns}


def _read_changed_column_values(instance):
    state = inspect(instance)
    old_values = {}
    new_values = {}

    for column_attr in state.mapper.column_attrs:
        history = state.attrs[column_attr.key].history
        if not history.has_changes():
            continue

        old_source = history.deleted[0] if history.deleted else getattr(instance, column_attr.key)
        new_source = history.added[0] if history.added else getattr(instance, column_attr.key)

        old_values[column_attr.key] = _make_json_safe(old_source)
        new_values[column_attr.key] = _make_json_safe(new_source)

    return old_values, new_values


def _log_change(connection, instance, operation):
    table_name = getattr(instance, "__tablename__", "")
    if table_name == DatabaseChangeLogModel.__tablename__:
        return

    old_values = None
    new_values = None

    if operation == INSERT_OP:
        new_values = _read_column_values(instance)
    elif operation == UPDATE_OP:
        old_values, new_values = _read_changed_column_values(instance)
        if not old_values and not new_values:
            return
    elif operation == DELETE_OP:
        old_values = _read_column_values(instance)

    connection.execute(
        insert(DatabaseChangeLogModel).values(
            table_name=table_name,
            record_id=_get_record_id(instance),
            operation=operation,
            changed_by_user_id=_get_current_user_id(),
            old_values=old_values,
            new_values=new_values,
        )
    )


def _after_insert(_mapper, connection, target):
    _log_change(connection, target, INSERT_OP)


def _after_update(_mapper, connection, target):
    _log_change(connection, target, UPDATE_OP)


def _after_delete(_mapper, connection, target):
    _log_change(connection, target, DELETE_OP)


def init_change_logging():
    global _hooks_registered
    if _hooks_registered:
        return

    event.listen(db.Model, "after_insert", _after_insert, propagate=True)
    event.listen(db.Model, "after_update", _after_update, propagate=True)
    event.listen(db.Model, "after_delete", _after_delete, propagate=True)
    _hooks_registered = True
