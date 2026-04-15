from mbdb.common import engine, Base, sessionmaker, scoped_session


Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
ScopedSession = scoped_session(Session)


def get_session():
    """Generator for a non-scoped SQLAlchemy session."""
    session = Session()
    try:
        yield session
    finally:
        session.close()


def get_scoped_session():
    """Generator for a thread-local SQLAlchemy session."""
    session = ScopedSession()
    try:
        yield session
    finally:
        ScopedSession.remove()
