# ============================================================
# engine.py
# ============================================================

from qupath_cuda_spatial.core.registry import (
    get_implementation
)


class Engine:

    def run(
        self,
        primitive: str,
        backend: str,
        data,
    ):

        implementation = get_implementation(
            primitive_name=primitive,
            backend_name=backend,
        )

        result = implementation(data)

        return result   