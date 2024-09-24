import functools
import inspect
import types
import typing
from contextlib import AsyncExitStack

from fastapi.dependencies import utils as deputils
from fastapi.dependencies.models import Dependant
from fastapi.params import Depends as DependsClass
from strawberry.extensions import FieldExtension
from strawberry.types import Info
from strawberry.types.field import StrawberryField


def get_func_with_only_deps(func: typing.Callable[..., typing.Any]) -> typing.Callable[..., typing.Any]:
    """This function returns a copy of the function with all the arguments that are not DependsClass
    updated to have a type annotation of "str".  We do this because Pydantic explodes if it sees any
    parameter annotationss that rely on the strawberry.lazy() functionality that Strawberry requires t
    handle forward-refs properly. Basically Strawberry and pydantic use different and incompatible tricks
    for handling forward refs and we decided that it was better to workaround Pydantic than Strawberry."""
    tmp_func = types.FunctionType(
        func.__code__,
        func.__globals__,
        name=func.__name__,
        argdefs=func.__defaults__,
        closure=func.__closure__,
    )
    newfunc = functools.update_wrapper(tmp_func, func)
    signature = inspect.signature(func)
    for param in signature.parameters.values():
        if isinstance(param.default, DependsClass):
            continue
        newfunc.__annotations__[param.name] = str

    return newfunc


class DependencyExtension(FieldExtension):
    def __init__(self) -> None:
        self.dependency_args: list[typing.Any] = []
        self.strawberry_field_names = ["self"]

    def apply(self, field: StrawberryField) -> None:
        func = field.base_resolver.wrapped_func  # type: ignore
        func = get_func_with_only_deps(func)  # type: ignore
        self.dependant: Dependant = deputils.get_dependant(path="/", call=func)  # type: ignore
        # Remove fastapi Depends arguments from the list that strawberry tries to resolve
        field.arguments = [item for item in field.arguments if not isinstance(item.default, DependsClass)]

    async def resolve_async(
        self,
        next_: typing.Callable[..., typing.Any],
        source: typing.Any,
        info: Info,
        **kwargs: dict[str, typing.Any],
    ) -> typing.Any:
        request = info.context["request"]
        try:
            if "dependency_cache" not in request.context:
                request.context["dependency_cache"] = {}
        except AttributeError:
            request.context = {"dependency_cache": {}}

        async with AsyncExitStack() as async_exit_stack:
            request.scope["sberrystack"] = AsyncExitStack()

            solved_result = await deputils.solve_dependencies(
                request=request,
                dependant=self.dependant,
                body={},
                dependency_overrides_provider=request.app,
                dependency_cache=request.context["dependency_cache"],
                async_exit_stack=async_exit_stack,
                embed_body_fields=False,
            )
            solved_values = solved_result.values
            new_cache = solved_result.dependency_cache
            request.context["dependency_cache"].update(new_cache)

            kwargs = solved_values | kwargs  # solved_values has None values that need to be overridden by kwargs
            res = await next_(source, info, **kwargs)
        return res
