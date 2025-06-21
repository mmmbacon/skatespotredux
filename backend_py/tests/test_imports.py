def test_starlette_sessions_import():
    """
    This test ensures that the `SessionMiddleware` can be imported from
    `starlette.middleware.sessions`. A failure here indicates a breaking
    change in the starlette library or an incorrect import path in our code.
    """
    try:
        from starlette.middleware.sessions import SessionMiddleware
    except ImportError as e:
        raise AssertionError("Failed to import SessionMiddleware from starlette.middleware.sessions") from e

    # This is just to use the import and avoid unused import errors from linters
    assert SessionMiddleware is not None 