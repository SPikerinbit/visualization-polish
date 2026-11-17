from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from sema_prototype.logical_operator.query_plan import NodeType, PlanNode

VALID_MERGE_ALGORITHMS = {"sliding_window", "loser_tree", "auto"}
VALID_ALGORITHMS = {"listwise"}
VALID_MODES = {"buffer", "full"}
VALID_SHUFFLE_MODES = {"balanced", "progressive", "none"}


def normalize_static_orderby_params(
    merge_algorithm, *, k=None, h=None, m=12, limit=None, parameter_policy=None
):
    from sema_prototype.physical_operator.orderby.merge._shared.plan import MergeRequest

    request = MergeRequest(
        algorithm=merge_algorithm,
        k=k,
        h=h,
        m=m,
        limit=limit,
        parameter_policy="token_best" if parameter_policy is None else parameter_policy,
    )
    return dict(
        merge_algorithm=request.algorithm,
        k=k,
        h=h,
        m=m,
        parameter_policy=request.parameter_policy,
    )


@dataclass(frozen=True)
class OrderbyConfig:
    limit: int | None = None
    K: int | None = None
    ascending: bool = False
    algorithm: str = "listwise"
    merge_algorithm: str = "sliding_window"
    k: int | None = None
    h: int | str | None = None
    m: int = 12
    mode: str | None = None
    parameter_policy: str | None = None
    input_token_counting: Any | None = None
    input_token_profile: Any | None = None
    use_evidence: bool = False
    shuffle_mode: str = "none"
    listwise_buffer_config: Any | None = None
    input_partition: str = "contiguous"
    input_partition_seed: int = 0
    full_tail_correction: bool = True
    tail_cache_dir: str | None = None
    mc_samples: int = 16384
    mc_seed: int = 2410000
    prefetch: bool = True

    def to_params(self):
        if type(self.prefetch) is not bool:
            raise ValueError("prefetch must be boolean")
        if self.input_partition not in {"contiguous", "random"}:
            raise ValueError("input_partition must be contiguous or random")
        if isinstance(self.input_partition_seed, bool) or not isinstance(self.input_partition_seed, int):
            raise ValueError("input_partition_seed must be an integer")
        from sema_prototype.physical_operator.orderby.merge._shared.finite import validate_sampling
        validate_sampling(self.mc_samples, self.mc_seed)
        if not isinstance(self.full_tail_correction, bool):
            raise ValueError("full_tail_correction must be boolean")
        from sema_prototype.physical_operator.orderby.merge._shared.evidence import (
            normalize_evidence_config,
        )

        evidence_config = normalize_evidence_config(
            self.listwise_buffer_config, use_evidence=self.use_evidence
        )
        if self.input_token_counting is not None:
            from sema_prototype.llm.input_tokens import TokenCountingConfig

            TokenCountingConfig(**self.input_token_counting)
        profile = self.input_token_profile
        if profile is not None:
            from sema_prototype.physical_operator.orderby.merge._shared.plan import (
                InputTokenProfile,
            )

            if not isinstance(profile, InputTokenProfile):
                profile = InputTokenProfile(
                    **{k: v for k, v in profile.items() if k != "rho"}
                )

        limit = self.limit if self.limit is not None else self.K
        if self.limit is not None and self.K is not None and self.limit != self.K:
            raise ValueError("limit and K must match when both are provided")
        if limit is not None and (
            isinstance(limit, bool) or not isinstance(limit, int) or limit < 0
        ):
            raise ValueError("limit must be a non-negative integer")
        if self.algorithm not in VALID_ALGORITHMS:
            raise ValueError(f"Unknown algorithm {self.algorithm!r}")
        if self.mode is not None and self.mode not in VALID_MODES:
            raise ValueError(f"Unknown mode {self.mode!r}")
        if self.shuffle_mode not in VALID_SHUFFLE_MODES:
            raise ValueError(f"Unknown shuffle_mode {self.shuffle_mode!r}")
        params = normalize_static_orderby_params(
            self.merge_algorithm,
            k=self.k,
            h=self.h,
            m=self.m,
            limit=limit,
            parameter_policy=self.parameter_policy,
        )
        return dict(
            params,
            limit=limit,
            K=limit,
            ascending=self.ascending,
            algorithm=self.algorithm,
            mode=self.mode,
            input_token_profile=profile,
            input_token_counting=self.input_token_counting,
            use_evidence=self.use_evidence,
            shuffle_mode=self.shuffle_mode,
            listwise_buffer_config=evidence_config,
            input_partition=self.input_partition,
            input_partition_seed=self.input_partition_seed,
            full_tail_correction=self.full_tail_correction,
            tail_cache_dir=self.tail_cache_dir,
            mc_samples=self.mc_samples,
            mc_seed=self.mc_seed,
            prefetch=self.prefetch,
        )


def build_orderby_node(user_instruction, **kwargs):
    return PlanNode(
        NodeType.ORDERBY, user_instruction, params=OrderbyConfig(**kwargs).to_params()
    )
