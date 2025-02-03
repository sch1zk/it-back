from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table, Text
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
    assigned_tasks = relationship('Task', secondary=developer_task_association, back_populates='assigned_developers')
    tasks_reactions = relationship("TaskReaction", back_populates="developer")

class UserEmployer(Base):
    __tablename__ = "users_emp"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    company_name = Column(String)
    created_tasks = relationship("Task", back_populates="employer")

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    employer_id = Column(Integer, ForeignKey("users_emp.id"), nullable=False)
    employer = relationship("UserEmployer", back_populates="created_tasks")
    reactions = relationship('TaskReaction', back_populates='task')
    assigned_developers = relationship('UserDeveloper', secondary=developer_task_association, back_populates='assigned_tasks')

class TaskReaction(Base):
    __tablename__ = "tasks_reactions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    message = Column(Text)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    task = relationship("Task", back_populates="reactions")
    developer_id = Column(Integer, ForeignKey("users_dev.id"))
    developer = relationship("UserDeveloper", back_populates="tasks_reactions")
