# ============================================================
# registry.py
# ============================================================

from dataclasses import dataclass, field
from collections.abc import Callable


# ============================================================
# PRIMITIVE SPEC
# ============================================================

@dataclass
class PrimitiveSpec:

    name: str

    input_builder: Callable | None = None

    implementations: dict[str, Callable] = field(
        default_factory=dict
    )


# ============================================================
# GLOBAL REGISTRY
# ============================================================

REGISTRY: dict[str, PrimitiveSpec] = {}


# ============================================================
# INTERNAL
# ============================================================

def _get_or_create_spec(
    primitive_name: str,
) -> PrimitiveSpec:

    if primitive_name not in REGISTRY:

        REGISTRY[primitive_name] = PrimitiveSpec(
            name=primitive_name
        )

    return REGISTRY[primitive_name]


# ============================================================
# REGISTER IMPLEMENTATION
# ============================================================

def register_implementation(
    primitive_name: str,
    backend_name: str,
):

    def decorator(func):

        spec = _get_or_create_spec(
            primitive_name
        )

        spec.implementations[
            backend_name
        ] = func

        print(
            f"[REGISTRY] "
            f"implementation registered: "
            f"{primitive_name}:{backend_name}"
        )

        return func

    return decorator


# ============================================================
# REGISTER INPUT BUILDER
# ============================================================

def register_input_builder(
    primitive_name: str,
):

    def decorator(func):

        spec = _get_or_create_spec(
            primitive_name
        )

        spec.input_builder = func

        print(
            f"[REGISTRY] "
            f"input builder registered: "
            f"{primitive_name}"
        )

        return func

    return decorator


# ============================================================
# GET IMPLEMENTATION
# ============================================================

def get_implementation(
    primitive_name: str,
    backend_name: str,
):

    if primitive_name not in REGISTRY:

        raise ValueError(
            f"Unknown primitive: "
            f"{primitive_name}"
        )

    spec = REGISTRY[primitive_name]

    if backend_name not in spec.implementations:

        raise ValueError(
            f"Unknown backend: "
            f"{backend_name}"
        )

    return spec.implementations[
        backend_name
    ]


# ============================================================
# GET INPUT BUILDER
# ============================================================

def get_input_builder(
    primitive_name: str,
):

    if primitive_name not in REGISTRY:

        raise ValueError(
            f"Unknown primitive: "
            f"{primitive_name}"
        )

    spec = REGISTRY[primitive_name]

    if spec.input_builder is None:

        raise ValueError(
            f"No input builder for "
            f"{primitive_name}"
        )

    return spec.input_builder