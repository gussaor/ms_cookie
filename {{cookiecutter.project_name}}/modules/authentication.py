import asyncio
import functools
import inspect
import re
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union
from urllib.parse import urlencode

from starlette.authentication import AuthenticationError, BaseUser
from starlette.exceptions import HTTPException
from starlette.requests import HTTPConnection, Request
from starlette.responses import JSONResponse, RedirectResponse, Response

from core.config import settings
from modules.token_jwt import TokenJWT

HEADER_KEY = "Authorization"


class AuthenticationBackend:
    async def authenticate(
        self, conn: HTTPConnection
    ) -> Optional[Tuple["AuthCredentials", "BaseUser"]]:
        raise NotImplementedError()  # pragma: no cover


class AuthCredentials:
    def __init__(
        self,
        user_id: str = "",
        groups_scopes: Optional[Sequence[str]] = None,
        roles_scopes: Optional[Sequence[str]] = None,
        permissions_scopes: Optional[Sequence[str]] = None,
    ):
        self.user_id = user_id
        self.groups_scopes = [] if groups_scopes is None else list(groups_scopes)
        self.roles_scopes = [] if roles_scopes is None else list(roles_scopes)
        self.permissions_scopes = (
            [] if permissions_scopes is None else list(permissions_scopes)
        )


def has_required_scope(
    conn: HTTPConnection,
    groups_scopes: Sequence[str],
    roles_scopes: Sequence[str],
    permissions_scopes: Sequence[str],
    validate_owner: bool = False,
) -> bool:
    has_access = False

    for group in groups_scopes:
        print(group)
        print(conn.auth.groups_scopes)
        if group in conn.auth.groups_scopes:
            has_access = True

    if not has_access:
        for role in roles_scopes:
            if role in conn.auth.roles_scopes:
                has_access = True

    if not has_access:
        for permission in permissions_scopes:
            if permission in conn.auth.permissions_scopes:
                has_access = True

    is_owner = False

    if validate_owner:
        if "user_id" in conn.query_params:
            if conn.auth.user_id == conn.query_params["user_id"]:
                is_owner = True

    return is_owner or has_access


def requires(
    groups_scopes: Union[str, Sequence[str]] = "",
    roles_scopes: Union[str, Sequence[str]] = "",
    permissions_scopes: Union[str, Sequence[str]] = "",
    validate_owner: bool = False,
    status_code: int = 403,
    redirect: Optional[str] = None,
) -> Callable:
    scopes_groups_list = (
        [groups_scopes] if isinstance(groups_scopes, str) else list(groups_scopes)
    )

    scopes_roles_list = (
        [roles_scopes] if isinstance(roles_scopes, str) else list(roles_scopes)
    )

    scopes_permissions_list = (
        [permissions_scopes]
        if isinstance(permissions_scopes, str)
        else list(permissions_scopes)
    )

    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        for idx, parameter in enumerate(sig.parameters.values()):
            if parameter.name == "request" or parameter.name == "websocket":
                type_ = parameter.name
                break
        else:
            raise Exception(
                f'No "request" or "websocket" argument on function "{func}"'
            )

        if asyncio.iscoroutinefunction(func):
            # Handle async request/response functions.
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Response:
                request = kwargs.get("request", args[idx] if idx < len(args) else None)
                assert isinstance(request, Request)

                if not has_required_scope(
                    request,
                    scopes_groups_list,
                    scopes_roles_list,
                    scopes_permissions_list,
                    validate_owner,
                ):
                    if redirect is not None:
                        orig_request_qparam = urlencode({"next": str(request.url)})
                        next_url = "{redirect_path}?{orig_request}".format(
                            redirect_path=request.url_for(redirect),
                            orig_request=orig_request_qparam,
                        )
                        return RedirectResponse(url=next_url, status_code=303)
                    raise HTTPException(status_code=status_code)
                return await func(*args, **kwargs)

            return async_wrapper

    return decorator


class AuthUser(BaseUser):
    def __init__(self, id: str, username: str) -> None:
        self.id = id
        self.username = username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def identity(self) -> str:
        raise NotImplementedError()


def on_auth_error(exc: Exception):
    return JSONResponse({"error": str(exc)}, status_code=401)


class AuthBackend(AuthenticationBackend):
    def __init__(self, excluded_urls: List[str] = None):
        self.excluded_urls = [] if excluded_urls is None else excluded_urls

    async def authenticate(self, conn):
        reg_ex = (
            "[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}"
        )
        url_to_access = re.sub(reg_ex, "", conn.url.path)
        last_char = len(url_to_access) - 1
        if url_to_access[last_char] == "/":
            url_to_access = url_to_access[:last_char]

        if conn.url.path in self.excluded_urls:
            return (
                AuthCredentials(
                    groups_scopes=["authenticated"],
                    roles_scopes=[],
                    permissions_scopes=[],
                ),
                "Unauthenticated User",
            )

        if HEADER_KEY not in conn.headers:
            raise AuthenticationError("UNAUTHORIZED")

        try:
            api_key = conn.headers[HEADER_KEY]
            token_prefix, token = api_key.split(" ")

        except Exception as err:
            print(err)
            raise AuthenticationError("Malformed payload in token")

        if token_prefix != settings.jwt_token_prefix:
            raise AuthenticationError("UNAUTHORIZED")

        # token_jwt = TokenJWT()
        user_access = TokenJWT().get(token)

        groups_scopes = ["authenticated"]
        groups_scopes.extend(user_access["groups"])
        groups_roles = []
        groups_permissions = []

        return AuthCredentials(
            user_access["id"], groups_scopes, groups_roles, groups_permissions
        ), AuthUser(id=user_access["id"], username=user_access["username"])
