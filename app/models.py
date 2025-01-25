from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Date, Table, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

developer_task_association = Table(
    'developer_task_association', Base.metadata,
    Column('developer_id', Integer, ForeignKey('users_dev.id'), primary_key=True),
    Column('task_id', Integer, ForeignKey('tasks.id'), primary_key=True)
)

class UserDeveloper(Base):
    __tablename__ = "users_dev"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    first_name = Column(String)
    second_name = Column(String)
    middle_name = Column(String)
    birth_date = Column(Date)
    city = Column(String)
    phone_number = Column(String)

    assigned_tasks = relationship(
        'Task',
        secondary=developer_task_association,
        back_populates='assigned_developers'
    )
    tasks_reactions = relationship(
        "TaskReaction",
        back_populates="developer",
        cascade="all, delete-orphan"
    )
    achievements = relationship(
        "DeveloperAchievement",
        back_populates="developer",
        cascade="all, delete-orphan"
    )
    skills = relationship(
        "DeveloperSkill",
        back_populates="developer",
        cascade="all, delete-orphan"
    )

class UserEmployer(Base):
    __tablename__ = "users_emp"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    company_name = Column(String)

    created_tasks = relationship(
        "Task",
        back_populates="employer", 
        cascade="all, delete-orphan"
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    employer_id = Column(Integer, ForeignKey("users_emp.id"), nullable=False)
    employer = relationship(
        "UserEmployer",
        back_populates="created_tasks",
    )

    reactions = relationship(
        'TaskReaction',
        back_populates='task', 
        cascade="all, delete-orphan"
    )
    assigned_developers = relationship(
        'UserDeveloper',
        secondary=developer_task_association,
        back_populates='assigned_tasks',
    )
    
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class TaskReaction(Base):
    __tablename__ = "tasks_reactions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(Text)

    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship(
        "Task",
        back_populates="reactions",
    )

    developer_id = Column(Integer, ForeignKey("users_dev.id"))
    developer = relationship(
        "UserDeveloper",
        back_populates="tasks_reactions",
    )

class AchievementTemplate(Base):
    __tablename__ = "achievements_templates"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)

class DeveloperAchievement(Base):
    __tablename__ = "developer_achievements"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("users_dev.id"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements_templates.id"), nullable=False)
    date_awarded = Column(DateTime, default=datetime.now(timezone.utc))

    developer = relationship(
        "UserDeveloper",
        back_populates="achievements"
    )
    achievement = relationship("AchievementTemplate")

class SkillTemplate(Base):
    __tablename__ = "skills_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    developers = relationship(
        "DeveloperSkill",
        back_populates="skill", 
        cascade="all, delete-orphan"
    )

class DeveloperSkill(Base):
    __tablename__ = "developer_skills"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("users_dev.id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills_templates.id"), nullable=False)

    developer = relationship(
        "UserDeveloper",
        back_populates="skills", 
        cascade="all, delete-orphan",
        single_parent=True
    )
    skill = relationship(
        "SkillTemplate",
        back_populates="developers",
    )

