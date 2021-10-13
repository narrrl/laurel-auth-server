from flask import session
from sqlalchemy import Integer, Column, String

from server.env import Env
from server.database import database


class User(database.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(128), nullable=False)
    language = Column(String(4), nullable=False)
    title = Column(String(16), nullable=False)
    name = Column(String(128), nullable=False)
    # either employee, student or admin
    role = Column(String(32), nullable=False)
    # student related
    matrikelnummer = Column(Integer, nullable=True)
    semester = Column(String(32), nullable=True)
    studies = Column(String(32), nullable=True)

    def __str__(self):
        return self.username

    def __eq__(self, other):
        if not other:
            return False
        else:
            return self.email == other.email and \
                   self.language == other.language and \
                   self.title == other.title and \
                   self.name == other.name and \
                   self.matrikelnummer == other.matrikelnummer and \
                   self.semester == other.semester and \
                   self.studies == other.studies

    def get_user_id(self):
        return self.id

    def is_admin(self):
        return self.role == "admin"

    def update(self, ldap_user):
        with database:
            self.email = ldap_user.email
            self.language = ldap_user.language
            self.title = ldap_user.title
            self.name = ldap_user.name
            self.matrikelnummer = ldap_user.matrikelnummer
            self.semester = ldap_user.semester
            self.studies = ldap_user.studies

    @staticmethod
    def session_or_none():
        if 'id' in session:
            return User.query.get(session['id'])

    @staticmethod
    def session_or_unauthorized(admin=False):
        user = User.session_or_none()
        if not user:
            raise UnauthorizedError()

        if admin and not user.is_admin():
            raise UnauthorizedError()

        return user

    @staticmethod
    def from_ldap(ldap):
        return User(
            username=ldap["uid"],
            title=ldap.get("rufAnrede", ""),
            email=ldap.get("rufPreferredMail", f"{ldap['uid']}@uni-freiburg.de"),
            role=ldap.get("rufAccountType", "student") if ldap["uid"] not in Env.get_admins() else "admin",
            language=ldap.get("preferredLanguage", "de"),
            name=ldap.get("displayName", ldap["uid"]),
            matrikelnummer=ldap.get("rufMatNr", None),
            studies=ldap.get("rufStudienfach", None),
            semester=ldap.get("rufSemester", None)
        )

    @staticmethod
    def dummy(username):
        return User(
            username=username,
            title="",
            email=username + "@uni-freiburg.de",
            role="student" if username not in Env.get_admins() else "admin",
            language="de",
            name=username,
            matrikelnummer=1234567,
            studies="11-420",
            semester="19701-1:19702-0"
        )


class UnauthorizedError(Exception):
    pass
