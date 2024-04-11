from dataclasses import dataclass
from typing import Any
from pants.core.goals.lint import LintResult, LintTargetsRequest
from pants.core.util_rules.partitions import PartitionerType
from pants.backend.javascript.subsystems import nodejs_tool
from pants.backend.javascript.subsystems.nodejs_tool import NodeJSToolRequest
from pants.core.util_rules.source_files import SourceFilesRequest, SourceFiles
from pants.engine.internals.selectors import Get
from pants.engine.process import FallibleProcessResult
from pants.option.option_types import SkipOption
from pants.engine.rules import collect_rules, rule
from pants.util.logging import LogLevel
from pants.util.strutil import pluralize
from pants.engine.target import (
    COMMON_TARGET_FIELDS,
    SingleSourceField,
    Target, FieldSet,
)


class CowsayField(SingleSourceField):
    pass


class CowsayTarget(Target):
    alias = "cowsay_source"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        CowsayField,
    )


class CowsayTool(nodejs_tool.NodeJSToolBase):
    options_scope = "cowsay"
    name = "Cowsay"
    default_version = "cowsay@1.4.0"
    help = "The Cowsay utility for printing cowsay messages"
    skip = SkipOption("lint")


@dataclass(frozen=True)
class SpectralFieldSet(FieldSet):
    required_fields = (CowsayField,)
    sources: CowsayField


class CowsayRequest(LintTargetsRequest):
    field_set_type = SpectralFieldSet
    tool_subsystem = CowsayTool
    partitioner_type = PartitionerType.DEFAULT_ONE_PARTITION_PER_INPUT


@rule(desc="Lint with Cowsay", level=LogLevel.DEBUG)
async def run_spectral(
    request: CowsayRequest.Batch[SpectralFieldSet, Any],
    cowsay: CowsayTool,
) -> LintResult:
    target_sources = await Get(
        SourceFiles,
        SourceFilesRequest(
            (field_set.sources for field_set in request.elements),
            for_sources_types=(CowsayField,),
            enable_codegen=True,
        ),
    )

    process_result = await Get(
        FallibleProcessResult,
        NodeJSToolRequest,
        cowsay.request(
            args=(target_sources.files[0],),
            input_digest=target_sources.snapshot.digest,
            description=f"Run Cowsay on {pluralize(len(request.elements), 'file')}.",
            level=LogLevel.DEBUG,
        ),
    )

    return LintResult.create(request, process_result)


def rules():
    return [
        *collect_rules(),
        *nodejs_tool.rules(),
        *CowsayTool.rules(),
        *CowsayRequest.rules(),
    ]


def target_types():
    return [
        CowsayTarget,
    ]
