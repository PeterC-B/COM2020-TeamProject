from flask import Blueprint, jsonify, request
from sqlalchemy import select
from dataclasses import dataclass

@dataclass(frozen=True)
class MissionsResult:
    names: list[str]
    question: list[str]
    all_answers: list[list[str]]
    correct_answer: list[str]


class Mission:
    def __init__(self, mission_repo):
        self.mission_repo = mission_repo

    def 