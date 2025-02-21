from components.juliet.juliet_paths import JulietPaths
from components.juliet.juliet_io import juliet_precios_claros_update
from components.juliet.juliet_precios_claros_target import JulietPreciosClarosTarget
from components.kilo.kilo_paths import KiloPaths
from components.precios_claros.juliet_to_kilo_precios_claros_target import JulietToKiloPreciosClarosTarget

class JulietToKiloPreciosClaros:

    def __init__(self, juliet_paths: JulietPaths, kilo_paths: KiloPaths) -> None:
        self._juliet_paths = juliet_paths
        self._kilo_paths = kilo_paths

    @property
    def juliet_paths(self) -> JulietPaths:
        return self._juliet_paths

    @property
    def kilo_paths(self) -> KiloPaths:
        return self._kilo_paths

    def update_storage(self) -> None:
        target = JulietToKiloPreciosClarosTarget(self.kilo_paths)
        juliet_precios_claros_update(self.juliet_paths, target)


def create_juliet_to_kilo_precios_claros(mode: str) -> JulietToKiloPreciosClaros:
    juliet_paths = JulietPaths(mode)
    kilo_paths = KiloPaths(mode)
    return JulietToKiloPreciosClaros(juliet_paths, kilo_paths)
