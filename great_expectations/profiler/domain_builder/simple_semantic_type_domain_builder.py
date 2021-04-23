from enum import Enum
from typing import Any, Dict, Iterable, List, Optional, Union

from great_expectations.execution_engine.execution_engine import MetricDomainTypes
from great_expectations.profiler.domain_builder.column_domain_builder import (
    ColumnDomainBuilder,
)
from great_expectations.validator.validator import MetricConfiguration, Validator


class SimpleSemanticTypeColumnDomainBuilder(ColumnDomainBuilder):
    def __init__(self, semantic_types: Optional[List[str]] = None):
        if semantic_types is None:
            semantic_types = []
        self._semantic_types = semantic_types

    class SemanticDomainTypes(Enum):
        INTEGER = "integer"
        DATETIME = "datetime"

    def _get_domains(
        self,
        *,
        validator: Optional[Validator] = None,
        batch_ids: Optional[List[str]] = None,
        include_batch_id: Optional[bool] = False,
        # TODO: <Alex>ALEX -- The signature of this method is inconsistent with that in the base class.</Alex>
        # domain_type: Optional[MetricDomainTypes] = None,
        semantic_types: Optional[List[str]] = None,
        **kwargs
    ) -> List[Dict[str, Union[str, MetricDomainTypes, Dict[str, Any]]]]:
        """Find the semantic column type for each column and return all domains matching the specified type or types.

        Returns a list:
        [
            {
                domain,
                domain_type
            },
            ...
        ]
        """
        # TODO: <Alex>ALEX -- How does this work?  What information is provided in **kwargs?  Can this be made explicit?  Where is "_semantic_types" defined?</Alex>
        config: dict = kwargs
        # TODO: AJB 20210416 If the type keyword for the DomainBuilder can contain multiple semantic types, should it be renamed types and take a list instead? Not that we can’t guess from what a user adds but something to make it clear that multiple semantic types can be used to construct a domain?
        # TODO: <Alex>ALEX -- In general, to avoid confusion, we should avoid the use of "type" because it is a function in Python.</Alex>
        semantic_types: Union[str, Iterable, List[str]] = config.get("semantic_types")
        if semantic_types is None:
            # TODO: AJB 20210416 Add a test for the below comment - None = return all types
            # None indicates no selection; all types should be returned
            semantic_types = self._semantic_types
        elif isinstance(semantic_types, str):
            semantic_types = [self.SemanticDomainTypes[semantic_types]]
        elif isinstance(semantic_types, Iterable):
            semantic_types = [self.SemanticDomainTypes[x] for x in semantic_types]
        else:
            # TODO: <Alex>ALEX -- We should make this error message more informative.</Alex>
            raise ValueError("unrecognized")
        domains: List[Dict[str, Union[str, MetricDomainTypes, Dict[str, Any]]]] = []
        columns: List[str] = validator.get_metric(
            metric=MetricConfiguration(
                metric_name="table.columns",
                metric_domain_kwargs={},
                metric_value_kwargs=None,
                metric_dependencies=None,
            )
        )
        # TODO: <Alex>ALEX -- How can/should we use "batch_id" and "include_batch_id"?</Alex>
        column: str
        # A semantic type is distinguished from the column storage type;
        # An example of storage type would be "integer".  The semantic type would be "id".
        semantic_column_type: str
        for column in columns:
            semantic_column_type: str = self._get_column_semantic_type_name(
                validator=validator, column=column
            )
            if semantic_column_type in semantic_types:
                domains.append(
                    {
                        # TODO: AJB 20210419 why is column just the column name string - will this be different based on execution engine versions?
                        # "domain_kwargs": {"column": column.name},
                        "domain_kwargs": {"column": column},
                        "domain_type": semantic_column_type,
                    }
                )
        return domains

    # TODO: <Alex>ALEX -- This method seems to always return the same value ("integer")...</Alex>
    def _get_column_semantic_type_name(self, validator, column) -> str:
        # FIXME: DO CHECKS
        return self.SemanticDomainTypes["INTEGER"].value
