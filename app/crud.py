from datetime import datetime, timezone
import logging
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app import auth, models, schemas

logger = logging.getLogger(__name__)

# ----- DEVELOPER -----

def get_developer(db: Session, field: str, value: str) -> Optional[models.UserDeveloper]:
    if field not in models.UserDeveloper.__table__.columns:
        logger.error(f"Invalid field: {field}")
        return None
    try:
        developer = db.query(models.UserDeveloper).filter(getattr(models.UserDeveloper, field) == value).first()
        if developer is None:
            logger.warning(f"Developer with {field} {value} not found")
        return developer
    except SQLAlchemyError as e:
        logger.error(f"Error fetching developer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the developer with {field} {value}")

def create_developer(db: Session, user: schemas.DeveloperCreate) -> bool:
    try:
        user_data = user.model_dump()
        user_data["hashed_password"] = auth.pwd_context.hash(user_data.pop("password"))
        db_user = models.UserDeveloper(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while creating user (developer): {e}")
        db.rollback()
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while creating user (developer): {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating user (developer): {e}")
        db.rollback()
        return False

def update_developer(db: Session, developer_id: int, user_update: schemas.DeveloperUpdate) -> Optional[models.UserDeveloper]:
    try:
        developer = db.query(models.UserDeveloper).filter(models.UserDeveloper.id == developer_id).first()
        if not developer:
            logger.warning(f"Developer with id {developer_id} not found")
            return None
        
        update_data = user_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(developer, key, value)
        
        db.commit()
        db.refresh(developer)
        return developer
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while updating developer with id {developer_id}: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred while updating developer with id {developer_id}: {e}")
        db.rollback()
        return None

# ----- EMPLOYER -----

def get_employer(db: Session, field: str, value: str) -> Optional[models.UserEmployer]:
    if field not in models.UserEmployer.__table__.columns:
        logger.error(f"Invalid field: {field}")
        return None
    try:
        employer = db.query(models.UserEmployer).filter(getattr(models.UserEmployer, field) == value).first()
        if employer is None:
            logger.warning(f"Employer with {field} {value} not found")
        return employer
    except SQLAlchemyError as e:
        logger.error(f"Error fetching employer with {field} {value}: {e}")
        raise Exception(f"An error occurred while retrieving the employer with {field} {value}")

def create_employer(db: Session, user: schemas.EmployerCreate) -> bool:
    try:
        user_data = user.model_dump()
        user_data["hashed_password"] = auth.pwd_context.hash(user_data.pop("password"))
        db_user = models.UserEmployer(**user_data)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return True
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while creating user (employer): {e}")
        db.rollback()
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while creating user (employer): {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while creating user (employer): {e}")
        db.rollback()
        return False

# ----- TASK -----

def get_task(db: Session, task_id: int) -> Optional[models.Task]:
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if task is None:
            logger.warning(f"Task with id {task_id} not found")
        return task
    except SQLAlchemyError as e:
        logger.error(f"Error fetching task with id {task_id}: {e}")
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

def get_tasks(db: Session, skip: int = 0, limit: int = 10, all: bool = False) -> List[models.Task]:
    try:
        if all:
            return db.query(models.Task).all()
        return db.query(models.Task).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching tasks: {e}")
        raise Exception(f"An error occurred while retrieving the tasks")

def get_tasks_by_employer(db: Session, employer_id: int, skip: int = 0, limit: int = 10, all: bool = False) -> List[models.Task]:
    try:
        if all:
            return db.query(models.Task).filter(models.Task.employer_id == employer_id).all()
        return db.query(models.Task).filter(models.Task.employer_id == employer_id).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        logger.error(f"Error fetching tasks from employer with id {employer_id}: {e}")
        raise Exception(f"An error occurred while retrieving the tasks from employer with id {employer_id}")

def is_developer_reacted(db: Session, task_id: int, developer_id: int) -> bool:
    try:
        return db.query(models.TaskReaction).filter_by(task_id=task_id, developer_id=developer_id).scalar() is not None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while checking reaction: {e}")
        raise Exception(f"An error occurred while retrieving the task with id {task_id}")

def add_task(db: Session, task: models.Task) -> Optional[models.Task]:
    try:
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while adding task: {e}")
        db.rollback()
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding task: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding task: {e}")
        db.rollback()
        return None

# def update_task(db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
#     try:
#         task = db.query(models.Task).filter(models.Task.id == task_id).first()
#         if not task:
#             logger.warning(f"Task with id {task_id} not found")
#             return None
        
#         update_data = task_update.model_dump(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(task, key, value)
        
#         db.commit()
#         db.refresh(task)
#         return task
#     except SQLAlchemyError as e:
#         logger.error(f"Database error occurred while updating task with id {task_id}: {e}")
#         db.rollback()
#         return None
#     except Exception as e:
#         logger.error(f"Unexpected error occurred while updating task with id {task_id}: {e}")
#         db.rollback()
#         return None

def delete_task(db: Session, task_id: int) -> bool:
    try:
        task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not task:
            logger.warning(f"Task with id {task_id} not found")
            return False
        
        db.delete(task)
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while deleting task with id {task_id}: {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while deleting task with id {task_id}: {e}")
        db.rollback()
        return False

def complete_task(db: Session, task_id: int) -> bool:
    try:
        task = get_task(db, task_id)
        if task is None:
            return False
        task.completed = True
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while completing task with id {task_id}: {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while completing task with id {task_id}: {e}")
        db.rollback()
        return False

# ----- TASK REACTION -----

def get_reaction(db: Session, task_id: int) -> Optional[models.TaskReaction]:
    try:
        reaction = db.query(models.TaskReaction).filter(models.TaskReaction.id == task_id).first()
        if reaction is None:
            logger.warning(f"Task reaction with id {task_id} not found")
        return reaction
    except SQLAlchemyError as e:
        logger.error(f"Error fetching task reaction with id {task_id}: {e}")
        raise Exception(f"An error occurred while retrieving the task reaction with id {task_id}")

def add_reaction(db: Session, reaction: models.TaskReaction) -> Optional[models.TaskReaction]:
    try:
        db.add(reaction)
        db.commit()
        db.refresh(reaction)
        return reaction
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while adding reaction: {e}")
        db.rollback()
        return None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding reaction: {e}")
        db.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding reaction: {e}")
        db.rollback()
        return None

# def update_reaction(db: Session, reaction_id: int, reaction_update: schemas.TaskReactionUpdate) -> Optional[models.TaskReaction]:
#     try:
#         reaction = db.query(models.TaskReaction).filter(models.TaskReaction.id == reaction_id).first()
#         if not reaction:
#             logger.warning(f"Task reaction with id {reaction_id} not found")
#             return None
        
#         update_data = reaction_update.model_dump(exclude_unset=True)
#         for key, value in update_data.items():
#             setattr(reaction, key, value)
        
#         db.commit()
#         db.refresh(reaction)
#         return reaction
#     except SQLAlchemyError as e:
#         logger.error(f"Database error occurred while updating reaction with id {reaction_id}: {e}")
#         db.rollback()
#         return None
#     except Exception as e:
#         logger.error(f"Unexpected error occurred while updating reaction with id {reaction_id}: {e}")
#         db.rollback()
#         return None

def delete_reaction(db: Session, reaction_id: int) -> bool:
    try:
        reaction = db.query(models.TaskReaction).filter(models.TaskReaction.id == reaction_id).first()
        if not reaction:
            logger.warning(f"Task reaction with id {reaction_id} not found")
            return False
        
        db.delete(reaction)
        db.commit()
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while deleting reaction with id {reaction_id}: {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while deleting reaction with id {reaction_id}: {e}")
        db.rollback()
        return False

# ----- ACHIEVEMENTS -----

def get_all_achievements_templates(db: Session) -> List[models.AchievementTemplate]:
    try:
        return db.query(models.AchievementTemplate).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while fetching all achievements: {e}")
        raise Exception("An error occurred while retrieving all achievements")
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching all achievements: {e}")
        raise Exception("An unexpected error occurred while retrieving all achievements")

def has_achievement(db: Session, developer_id: int, achievement_id: int) -> bool:
    try:
        return db.query(models.AchievementTemplate).filter(
            models.DeveloperAchievement.developer_id == developer_id,
            models.DeveloperAchievement.id == achievement_id
        ).first() is not None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while checking achievement with id {achievement_id} for developer {developer_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while checking achievement with id {achievement_id} for developer {developer_id}: {e}")
        return False

def award_achievement(db: Session, developer_id: int, achievement_id: int) -> bool:
    try:
        if not db.query(models.AchievementTemplate).filter(models.AchievementTemplate.id == achievement_id).first():
            logger.warning(f"Achievement with id {achievement_id} not found.")
            return False
        
        if db.query(models.DeveloperAchievement).filter_by(developer_id=developer_id, achievement_id=achievement_id).first():
            logger.info(f"Achievement with id {achievement_id} is already awarded to user (developer) {developer_id}.")
            return False

        user_achievement = models.DeveloperAchievement(developer_id=developer_id, achievement_id=achievement_id)
        db.add(user_achievement)
        db.commit()
        db.refresh(user_achievement)
        return True
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while awarding achievement with id {achievement_id} to developer {developer_id}: {e}")
        db.rollback()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while awarding achievement with id {achievement_id} to developer {developer_id}: {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while awarding achievement with id {achievement_id} to developer {developer_id}: {e}")
        db.rollback()
        return False

def get_achievements(db: Session, developer_id: int) -> List[models.DeveloperAchievement]:
    try:
        return db.query(models.DeveloperAchievement).options(
            joinedload(models.DeveloperAchievement.achievement)
        ).filter_by(developer_id=developer_id).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while fetching achievements for developer {developer_id}: {e}")
        raise Exception(f"An error occurred while retrieving achievements for developer {developer_id}")
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching achievements for developer {developer_id}: {e}")
        raise Exception(f"An unexpected error occurred while retrieving achievements for developer {developer_id}")

def get_all_skills_templates(db: Session) -> List[models.SkillTemplate]:
    try:
        return db.query(models.SkillTemplate).all()
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while fetching all skills: {e}")
        raise Exception("An error occurred while retrieving all skills")
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching all skills: {e}")
        raise Exception("An unexpected error occurred while retrieving all skills")

def has_skill(db: Session, developer_id: int, skill_id: int) -> bool:
    try:
        return db.query(models.SkillTemplate).filter(
            models.DeveloperSkill.developer_id == developer_id,
            models.DeveloperSkill.id == skill_id
        ).first() is not None
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while checking skill with id {skill_id} for developer {developer_id}: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while checking skill with id {skill_id} for developer {developer_id}: {e}")
        return False

def add_skill(db: Session, developer_id: int, skill_id: int) -> bool:
    try:
        if not has_skill(db, developer_id, skill_id):
            user_skill = models.DeveloperSkill(developer_id=developer_id, skill_id=skill_id)
            db.add(user_skill)
            db.commit()
            return True
        return False
    except IntegrityError as e:
        logger.error(f"Integrity error occurred while adding skill with id {skill_id} to developer {developer_id}: {e}")
        db.rollback()
        return False
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while adding skill with id {skill_id} to developer {developer_id}: {e}")
        db.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error occurred while adding skill with id {skill_id} to developer {developer_id}: {e}")
        db.rollback()
        return False

def get_skills(db: Session, developer_id: int) -> List[str]:
    try:
        return [
            user_skill.skill.name if user_skill.skill else "Unknown Skill"
            for user_skill in db.query(models.DeveloperSkill)
                .options(joinedload(models.DeveloperSkill.skill))
                .filter_by(developer_id=developer_id)
                .all()
        ]
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred while fetching all skills for developer {developer_id}: {e}")
        raise Exception("An error occurred while retrieving all skills")
    except Exception as e:
        logger.error(f"Unexpected error occurred while fetching all skills for developer {developer_id}: {e}")
        raise Exception("An unexpected error occurred while retrieving all skills")
