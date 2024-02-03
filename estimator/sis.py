# -*- coding: utf-8 -*-
"""
High-level NTRU interface
"""

from functools import partial
from sage.all import oo

from .sis_lattice import lattice
from .sis_parameters import SISParameters as Parameters  # noqa
from .conf import (red_cost_model as red_cost_model_default,
                   red_shape_model as red_shape_model_default)
from .util import batch_estimate, f_name
from .reduction import RC


class Estimate:

    def rough(self, params, jobs=1, catch_exceptions=True):
        """
        This function makes the following somewhat routine assumptions:

        - The LGSA holds.
        - The Core-SVP model holds.

        This function furthermore assumes the following heuristics:
        - None at the moment. May change as more algorithms are added.

        :param params: SIS parameters.
        :param jobs: Use multiple threads in parallel.
        :param catch_exceptions: When an estimate fails, just print a warning.

        EXAMPLE ::

            >>> from estimator import *
            >>> _ = SIS.estimate.rough(schemes.Dilithium2_MSIS_WkUnf)
            lattice              :: rop: ≈2^123.5, red: ≈2^123.5, sieve: ≈2^-332.2, β: 423, η: 423, ζ: 1, d: 2303, ...

        """
        algorithms = {}

        # Only lattice attacks are supported on SIS for now
        algorithms["lattice"] = partial(lattice, red_cost_model=RC.ADPS16, red_shape_model="lgsa")

        res_raw = batch_estimate(
            params, algorithms.values(), log_level=1, jobs=jobs, catch_exceptions=catch_exceptions
        )
        res_raw = res_raw[params]
        res = {
            algorithm: v for algorithm, attack in algorithms.items()
            for k, v in res_raw.items()
            if f_name(attack) == k
        }

        for algorithm in algorithms:
            if algorithm not in res:
                continue
            result = res[algorithm]
            if result["rop"] != oo:
                print(f"{algorithm:20s} :: {result!r}")

        return res

    def __call__(
        self,
        params,
        red_cost_model=red_cost_model_default,
        red_shape_model=red_shape_model_default,
        deny_list=tuple(),
        add_list=tuple(),
        jobs=1,
        catch_exceptions=True,
    ):
        """
        Run all estimates.

        :param params: SIS parameters.
        :param red_cost_model: How to cost lattice reduction.
        :param red_shape_model: How to model the shape of a reduced basis (applies to primal attacks)
        :param deny_list: skip these algorithms
        :param add_list: add these ``(name, function)`` pairs to the list of algorithms to estimate.a
        :param jobs: Use multiple threads in parallel.
        :param catch_exceptions: When an estimate fails, just print a warning.

        EXAMPLE ::
            >>> from estimator import *
            >>> _ = SIS.estimate(schemes.Dilithium2_MSIS_StrUnf)
            lattice              :: rop: ≈2^150.8, red: ≈2^149.6, sieve: ≈2^149.9, β: 421, η: 429, ζ: 0, d: 2304, ...

            >>> params = SIS.Parameters(n=113, q=2048, length_bound=512, norm=2)
            >>> _ = SIS.estimate(params)
            lattice              :: rop: ≈2^89.7, red: ≈2^89.7, δ: 1.006095, β: 210, d: 862, tag: euclidian

            >>> _ = SIS.estimate(params.updated(norm=oo))
            lattice              :: rop: ≈2^55.7, red: ≈2^54.8, sieve: ≈2^54.5, β: 83, η: 107, ζ: 112, d: 750, ...

        """

        algorithms = {}

        algorithms["lattice"] = partial(
            lattice, red_cost_model=red_cost_model, red_shape_model=red_shape_model
        )

        algorithms = {k: v for k, v in algorithms.items() if k not in deny_list}
        algorithms.update(add_list)

        res_raw = batch_estimate(
            params, algorithms.values(), log_level=1, jobs=jobs, catch_exceptions=catch_exceptions
        )
        res_raw = res_raw[params]
        res = {
            algorithm: v
            for algorithm, attack in algorithms.items()
            for k, v in res_raw.items()
            if f_name(attack) == k
        }
        for algorithm in algorithms:
            if algorithm not in res:
                continue
            result = res[algorithm]
            if result["rop"] == oo:
                continue
            print(f"{algorithm:20s} :: {result!r}")

        return res


estimate = Estimate()
