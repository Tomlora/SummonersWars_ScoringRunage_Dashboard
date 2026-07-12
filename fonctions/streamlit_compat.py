from __future__ import annotations

from typing import Literal


def ensure_pygwalker_streamlit_compatibility() -> None:
    """Restore the Streamlit URL helper still imported by PyGWalker.

    Streamlit 1.59 removed ``make_url_path_regex`` while current PyGWalker
    releases still import it during module initialization. Re-introducing the
    small helper keeps PyGWalker optional and prevents unrelated pages from
    crashing as soon as ``fonctions.visualisation`` is imported.
    """
    import streamlit.web.server.server_util as server_util

    if hasattr(server_util, "make_url_path_regex"):
        return

    def make_url_path_regex(
        *path: str,
        trailing_slash: Literal["optional", "required", "prohibited"] = "optional",
    ) -> str:
        path_parts = [part.strip("/") for part in path if part]
        path_format = r"^/%s$"
        if trailing_slash == "optional":
            path_format = r"^/%s/?$"
        elif trailing_slash == "required":
            path_format = r"^/%s/$"
        return path_format % "/".join(path_parts)

    server_util.make_url_path_regex = make_url_path_regex
