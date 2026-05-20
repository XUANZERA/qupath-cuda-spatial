from registry import REGISTRY

class Engine:

    def run(
        self,
        primitive: str,
        backend: str,
        data,
    ):
        
        if primitive not in REGISTRY:
            raise ValueError(f"Unknown Primitive: {primitive}")
        if backend not in REGISTRY:
            raise ValueError(f"Unknown Backend: {backend}")
        
        func = REGISTRY[primitive][backend]
        result = func(data)

        return result