import dataclasses


@dataclasses.dataclass
class Repo:
    base: str

    def __post_init__(self) -> None:
        if self.base.endswith('/'):
            raise ValueError(f'{self.base} cannot end with /')

    def tags(self, local_tags: list[str]) -> list[str]:
        return [f'{self.base}/{tag}' for tag in local_tags]
