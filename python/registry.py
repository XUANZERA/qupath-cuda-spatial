from collections.abc import Callable


REGISTRY: dict[str, dict[str, Callable]] = dict()


def register_primitive(
    primitive_name: str,
    backend_name: str
) -> Callable:
    
    def decorator(func):

        if primitive_name not in REGISTRY:
            REGISTRY[primitive_name] = {}
        
        REGISTRY[primitive_name][backend_name]=func
        print(f"[REGISTRY] Registered {primitive_name}:{backend_name}")  # 调试输出
        return func
    
    return decorator