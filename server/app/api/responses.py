from typing import Any, Dict, Optional

from flask import jsonify


def ok(data: Any = None, *, meta: Optional[Dict[str, Any]] = None, status: int = 200):
    """
    Standard success response:
      { "data": ..., "meta": ... }
    """
    payload: Dict[str, Any] = {"data": data}
    if meta is not None:
        payload["meta"] = meta
    return jsonify(payload), status


def created(data: Any = None, *, meta: Optional[Dict[str, Any]] = None):
    """201 Created success. """
    return ok(data, meta=meta, status=201)


def no_content():
    """204 No Content."""
    return "", 204


def error(
    *,
    code: str,
    message: str,
    status: int,
    details: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
):
    """
    Following the standard error format:
      { "error": { "code": "...", "message": "...", "details": {...} } }
    """
    err_obj: Dict[str, Any] = {"code": code, "message": message}
    if details is not None:
        err_obj["details"] = details

    resp = jsonify({"error": err_obj})
    resp.status_code = status

    if headers:
        for k, v in headers.items():
            resp.headers[k] = v

    return resp
