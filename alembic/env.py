# Import necessary modules and functions
from logging.config import fileConfig
import os
from alembic import context
from sqlalchemy import pool, engine_from_config
from sqlalchemy.orm import declarative_base


# Import your Base and models
from app.api.models import *  # This imports all your models

# Import your database session configuration
from app.api.dependencies.database import async_database_session, DATABASE_URL, ssl_context  # adjust to your actual import

config = context.config
fileConfig(config.config_file_name)
Base = declarative_base()

target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Define the configuration for the Alembic runtime environment
    configuration = config.get_section(config.config_ini_section)
    
    # Use the DATABASE_URL from your custom configuration
    configuration['sqlalchemy.url'] = DATABASE_URL

    # Create an engine with your custom SSL context and other settings
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={"ssl": ssl_context}  # Use your custom SSL context
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Include additional options here as needed
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()  # This function remains the same as in your original env.py
else:
    run_migrations_online()
