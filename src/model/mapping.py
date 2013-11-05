# -*- coding: utf-8 -*-

from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import String, Enum, Integer

from src.model.constants import TYPE_LIST, PRIORITY_LIST
from src.model.database import MappedBase


# map the many-to-many relationship between use cases and requirements
_uc_req = Table('UseCasesRequirements', MappedBase.metadata,
        Column('req_id', String, ForeignKey('Requirements.req_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
        Column('uc_id', String, ForeignKey('UseCases.uc_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True))

# map the many-to-many relationship between tests and requirements
_req_test = Table('RequirementsTests', MappedBase.metadata,
        Column('req_id', String, ForeignKey('Requirements.req_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True),
        Column('test_id', String, ForeignKey('SystemTests.test_id',
        ondelete='CASCADE', onupdate='CASCADE'), primary_key=True))


class Source(MappedBase):
    """Representation of the source of a requirement.
    """
    # mapped table
    __tablename__ = 'Sources'
    # field mapping
    source_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    def __init__(self, name):
        super(Source, self).__init__()
        self.name = name


class UseCase(MappedBase):
    """Representation of a system use case.
    """
    # mapped table
    __tablename__ = 'UseCases'
    # field mapping
    uc_id = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    parent_id = Column(String, ForeignKey('UseCases.uc_id',
            ondelete='CASCADE', onupdate='CASCADE'))
    image = Column(String)
    # relationships
    children = relationship('UseCase', cascade='all', lazy='joined',
            join_depth=3, backref=backref('parent',
            remote_side='UseCase.uc_id', lazy='joined', join_depth=3))
    requirements = relationship('Requirement', secondary=_uc_req,
            cascade='all', lazy='joined', join_depth=1)

    def __init__(self, uc_id, description, image, parent_id):
        super(UseCase, self).__init__()
        self.uc_id = uc_id
        self.description = description
        self.image = image
        self.parent_id = parent_id


class Requirement(MappedBase):
    """Representation of a system requirement.
    """
    # mapped table
    __tablename__ = 'Requirements'
    # field mapping
    req_id = Column(String, primary_key=True)
    description = Column(String)
    parent_id = Column(String, ForeignKey('Requirements.req_id',
            ondelete='CASCADE', onupdate='CASCADE'))
    req_type = Column(Enum(*TYPE_LIST))
    priority = Column(Enum(*PRIORITY_LIST))
    source_id = Column(Integer, ForeignKey('Sources.source_id',
            onupdate='CASCADE', ondelete='SET NULL'))
    # relationships
    children = relationship('Requirement', lazy='joined', join_depth=3,
            backref=backref('parent', remote_side='Requirement.req_id',
            lazy='joined', join_depth=3))
    use_cases = relationship('UseCase', secondary=_uc_req, cascade='all',
            lazy='joined', join_depth=1)
    tests = relationship('SystemTest', secondary=_req_test, cascade='all',
            lazy='joined', join_depth=1)
    source = relationship('Source', lazy='joined', join_depth=3, uselist=False)

    def __init__(self, req_id, description, req_type, priority, source_id,
            parent_id):
        super(Requirement, self).__init__()
        self.req_id = req_id
        self.description = description
        self.req_type = req_type
        self.priority = priority
        self.source_id = source_id
        self.type = type
        self.parent_id = parent_id


class SystemTest(MappedBase):
    """Representation of a system test.
    """
    # mapped table
    __tablename__ = 'SystemTests'
    # field mapping
    test_id = Column(String, primary_key=True)
    description = Column(String)
    # relationships
    requirements = relationship('Requirement', secondary=_req_test,
            cascade='all', lazy='joined', join_depth=1)

    def __init__(self, test_id, description):
        super(SystemTest, self).__init__()
        self.test_id = test_id
        self.description = description
