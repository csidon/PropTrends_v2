# def drop_everything():
#     """(On a live db) drops all foreign key constraints before dropping all tables.
#     Workaround for SQLAlchemy not doing DROP ## CASCADE for drop_all()
#     (https://github.com/pallets/flask-sqlalchemy/issues/722)
#     """
#     from sqlalchemy.engine.reflection import Inspector
#     from sqlalchemy.schema import DropConstraint, DropTable, MetaData, Table

#     con = db.engine.connect()
#     trans = con.begin()
#     inspector = Inspector.from_engine(db.engine)

#     # We need to re-create a minimal metadata with only the required things to
#     # successfully emit drop constraints and tables commands for postgres (based
#     # on the actual schema of the running instance)
#     meta = MetaData()
#     tables = []
#     all_fkeys = []

#     for table_name in inspector.get_table_names():
#         fkeys = []

#         for fkey in inspector.get_foreign_keys(table_name):
#             if not fkey["name"]:
#                 continue

#             fkeys.append(db.ForeignKeyConstraint((), (), name=fkey["name"]))

#         tables.append(Table(table_name, meta, *fkeys))
#         all_fkeys.extend(fkeys)

#     for fkey in all_fkeys:
#         con.execute(DropConstraint(fkey))

#     for table in tables:
#         con.execute(DropTable(table))

#     trans.commit()




# from proptrends import db
# drop_everything()
# print("All tables dropped")
# db.create_all()
# print("New tables added")
# from proptrends.models import Listing
# l1=Listing(prop_url="lalala")
# db.session.add(l1)
# db.session.commit()
# db.session.refresh(l1)
# print(l1.id)

from proptrends import db
db.create_all()
print("New tables added")
