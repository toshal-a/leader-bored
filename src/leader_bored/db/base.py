# Import all the models, so that Base has them before being
# imported by Alembic
from leader_bored.db.base_class import Base #noqa
from leader_bored.models.user import User