import logging
from sqlalchemy.orm import Session

from app import crud

logger = logging.getLogger(__name__)

# Checks user for met achievements conditions and automatically awards them.
def check_and_award(db: Session, user_id: int):
    pass
    # ex: Achievement "Hackathon Winner" - if at least one task is completed
    # TODO: check here is user already completed this achievement to not filter in db (save resource)
    # TODO: just use crud.has_achievement(db, developer_id, achievement_id) for that
    # completed_tasks_count = db.query(models.Task).filter(models.Task.employer_id == user_id, models.Task.completed == True).count()
    # if completed_tasks_count > 0:
    #     _award(db, user_id, "Hackathon Winner")

def _award(db: Session, user_id: int, achievement_id: int):
    crud.award_achievement(db, user_id, achievement_id)
