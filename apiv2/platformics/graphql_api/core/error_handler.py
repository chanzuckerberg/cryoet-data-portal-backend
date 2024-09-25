from abc import ABC, abstractmethod
from typing import Any, Iterator, List

from graphql.error import GraphQLError
from pydantic import ValidationError
from strawberry.extensions.base_extension import SchemaExtension

from platformics.graphql_api.core.errors import PlatformicsError


class ExceptionHandler(ABC):
    @abstractmethod
    def convert_exception(self, err: Any) -> list[Any]:
        raise NotImplementedError


class NoOpHandler(ExceptionHandler):
    def convert_exception(self, err: PlatformicsError) -> list[PlatformicsError]:
        return [err]


class ValidationExceptionHandler(ExceptionHandler):
    def convert_exception(self, err: GraphQLError) -> list[GraphQLError]:
        validation_error: ValidationError | None = err.original_error  # type: ignore
        errors: list[GraphQLError] = []
        if not validation_error:
            return []
        if not validation_error.errors():
            return errors
        for field_err in validation_error.errors():
            errors.append(
                GraphQLError(
                    message=f"Validation Error: {'.'.join(field_err['loc'])} - {field_err['msg']}",  # type: ignore
                    nodes=err.nodes,
                    source=err.source,
                    positions=err.positions,
                    path=err.path,
                    original_error=None,
                ),
            )
        return errors


class DefaultExceptionHandler(ExceptionHandler):
    error_message: str = "Unexpected error."

    def convert_exception(self, err: Any) -> list[GraphQLError]:
        return [
            GraphQLError(
                message=self.error_message,
                nodes=err.nodes,
                source=err.source,
                positions=err.positions,
                path=err.path,
                original_error=None,
            ),
        ]


class HandleErrors(SchemaExtension):
    def __init__(self) -> None:
        self.handlers: dict[type, ExceptionHandler] = {
            ValidationError: ValidationExceptionHandler(),
            PlatformicsError: NoOpHandler(),
        }
        self.default_handler = DefaultExceptionHandler()

    def process_error(self, error: GraphQLError) -> list[GraphQLError]:
        handler = self.handlers.get(type(error.original_error), self.default_handler)
        return handler.convert_exception(error)

    def on_operation(self) -> Iterator[None]:
        yield
        result = self.execution_context.result
        if result and result.errors:
            processed_errors: List[GraphQLError] = []
            for error in result.errors:
                processed_errors.extend(self.process_error(error))

            result.errors = processed_errors
