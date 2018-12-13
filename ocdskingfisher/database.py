import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
import datetime
import hashlib
import json
import os
import ocdskingfisher.maindatabase.config
from ocdskingfisher.models import Collection
import alembic.config


class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)


class DataBase:

    def __init__(self, config):
        self.config = config
        self._engine = None

        self.metadata = sa.MetaData()

        self.collection_table = sa.Table('collection', self.metadata,
                                    sa.Column('id', sa.Integer, primary_key=True),
                                    sa.Column('source_id', sa.Text, nullable=False),
                                    sa.Column('data_version', sa.Text, nullable=False),
                                    sa.Column('gather_start_at', sa.DateTime(timezone=False), nullable=True),
                                    sa.Column('gather_end_at', sa.DateTime(timezone=False), nullable=True),
                                    sa.Column('fetch_start_at', sa.DateTime(timezone=False), nullable=True),
                                    sa.Column('fetch_end_at', sa.DateTime(timezone=False), nullable=True),
                                    sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=False),
                                    sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                                    sa.Column('sample', sa.Boolean, nullable=False, default=False),
                                    sa.UniqueConstraint('source_id', 'data_version', 'sample'),
                                    )

        self.collection_file_status_table = sa.Table('collection_file_status', self.metadata,
                                                sa.Column('id', sa.Integer, primary_key=True),
                                                sa.Column('collection_id', sa.Integer,
                                                          sa.ForeignKey("collection.id"), nullable=False),
                                                sa.Column('filename', sa.Text, nullable=True),
                                                sa.Column('store_start_at', sa.DateTime(timezone=False), nullable=True),
                                                sa.Column('store_end_at', sa.DateTime(timezone=False), nullable=True),
                                                sa.Column('warnings', JSONB, nullable=True),
                                                sa.UniqueConstraint('collection_id', 'filename'),
                                                )

        self.data_table = sa.Table('data', self.metadata,
                              sa.Column('id', sa.Integer, primary_key=True),
                              sa.Column('hash_md5', sa.Text, nullable=False, unique=True),
                              sa.Column('data', JSONB, nullable=False),
                              )

        self.package_data_table = sa.Table('package_data', self.metadata,
                                      sa.Column('id', sa.Integer, primary_key=True),
                                      sa.Column('hash_md5', sa.Text, nullable=False, unique=True),
                                      sa.Column('data', JSONB, nullable=False),
                                      )

        self.release_table = sa.Table('release', self.metadata,
                                 sa.Column('id', sa.Integer, primary_key=True),
                                 sa.Column('collection_file_status_id', sa.Integer,
                                           sa.ForeignKey("collection_file_status.id"), nullable=False),
                                 sa.Column('release_id', sa.Text, nullable=True),
                                 sa.Column('ocid', sa.Text, nullable=True),
                                 sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                                 sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"),
                                           nullable=False),
                                 )

        self.record_table = sa.Table('record', self.metadata,
                                sa.Column('id', sa.Integer, primary_key=True),
                                sa.Column('collection_file_status_id', sa.Integer,
                                          sa.ForeignKey("collection_file_status.id"), nullable=False),
                                sa.Column('ocid', sa.Text, nullable=True),
                                sa.Column('data_id', sa.Integer, sa.ForeignKey("data.id"), nullable=False),
                                sa.Column('package_data_id', sa.Integer, sa.ForeignKey("package_data.id"),
                                          nullable=False),
                                )

        self.release_check_table = sa.Table('release_check', self.metadata,
                                       sa.Column('id', sa.Integer, primary_key=True),
                                       sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"), index=True,
                                                 unique=False, nullable=False),
                                       sa.Column('override_schema_version', sa.Text, nullable=True),
                                       sa.Column('cove_output', JSONB, nullable=False),
                                       sa.UniqueConstraint('release_id', 'override_schema_version',
                                                           name='ix_release_check_release_id_and_more')
                                       )

        self.record_check_table = sa.Table('record_check', self.metadata,
                                      sa.Column('id', sa.Integer, primary_key=True),
                                      sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True,
                                                unique=False,
                                                nullable=False),
                                      sa.Column('override_schema_version', sa.Text, nullable=True),
                                      sa.Column('cove_output', JSONB, nullable=False),
                                      sa.UniqueConstraint('record_id', 'override_schema_version',
                                                          name='ix_record_check_record_id_and_more')
                                      )

        self.release_check_error_table = sa.Table('release_check_error', self.metadata,
                                             sa.Column('id', sa.Integer, primary_key=True),
                                             sa.Column('release_id', sa.Integer, sa.ForeignKey("release.id"),
                                                       index=True,
                                                       unique=False, nullable=False),
                                             sa.Column('override_schema_version', sa.Text, nullable=True),
                                             sa.Column('error', sa.Text, nullable=False),
                                             sa.UniqueConstraint('release_id', 'override_schema_version',
                                                                 name='ix_release_check_error_release_id_and_more')
                                             )

        self.record_check_error_table = sa.Table('record_check_error', self.metadata,
                                            sa.Column('id', sa.Integer, primary_key=True),
                                            sa.Column('record_id', sa.Integer, sa.ForeignKey("record.id"), index=True,
                                                      unique=False, nullable=False),
                                            sa.Column('override_schema_version', sa.Text, nullable=True),
                                            sa.Column('error', sa.Text, nullable=False),
                                            sa.UniqueConstraint('record_id', 'override_schema_version',
                                                                name='ix_record_check_error_record_id_and_more')
                                            )

    def _get_engine(self):
        # We only create a connection if actually needed; sometimes people do operations that don't need a database
        # and in that case no need to connect.
        # But this side of kingfisher now always requires a DB, so there should not be a problem opening a connection!
        if not self._engine:
            self._engine = sa.create_engine(ocdskingfisher.maindatabase.config.get_database_uri(), json_serializer=SetEncoder().encode)
        return self._engine

    def delete_tables(self):
        engine = self._get_engine()
        engine.execute("drop table if exists record_check cascade")
        engine.execute("drop table if exists record_check_error cascade")
        engine.execute("drop table if exists release_check cascade")
        engine.execute("drop table if exists release_check_error cascade")
        engine.execute("drop table if exists record cascade")
        engine.execute("drop table if exists release cascade")
        engine.execute("drop table if exists package_data cascade")
        engine.execute("drop table if exists data cascade")
        engine.execute("drop table if exists collection_file_status cascade")
        engine.execute("drop table if exists source_session_file_status cascade")  # This is the old table name
        engine.execute("drop table if exists collection cascade")
        engine.execute("drop table if exists source_session cascade")  # This is the old table name
        engine.execute("drop table if exists alembic_version cascade")

    def create_tables(self):
        alembicargs = [
            '--config', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'mainalembic.ini')),
            '--raiseerr',
            'upgrade', 'head',
        ]
        alembic.config.main(argv=alembicargs)

    def get_or_create_collection_id(self, source_id, data_version, sample):

        with self._get_engine().begin() as connection:
            s = sa.sql.select([self.collection_table]) \
                .where((self.collection_table.c.source_id == source_id) &
                       (self.collection_table.c.data_version == data_version) &
                       (self.collection_table.c.sample == sample))
            result = connection.execute(s)
            collection = result.fetchone()
            if collection:
                return collection['id']

            value = connection.execute(self.collection_table.insert(), {
                'source_id': source_id,
                'data_version': data_version,
                'sample': sample,
                'store_start_at': datetime.datetime.utcnow(),
            })
            return value.inserted_primary_key[0]

    def get_all_collections(self):
        out = []
        with self._get_engine().begin() as connection:
            s = ocdskingfisher.database.sa.sql.select([self.collection_table])
            for result in connection.execute(s):
                out.append(Collection(
                    database_id=result['id'],
                    source_id=result['source_id'],
                    data_version=result['data_version'],
                    sample=result['sample'],
                ))
        return out