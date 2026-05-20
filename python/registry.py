from collections.abc import Callable


REGISTRY: dict[str, Callable] = dict()


def register_primitive(
    primitive_name: str,
    backend_name: str
) -> Callable:
    
    def decorator(func):

        if primitive_name not in REGISTRY:
            REGISTRY[primitive_name] = {}
        
        REGISTRY[primitive_name][backend_name]=func
    
    return decorator