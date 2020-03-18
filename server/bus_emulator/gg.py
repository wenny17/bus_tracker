import dataclasses


@dataclasses.dataclass()
class Bus:
    name: str
    unit_price: float

    def total_cost(self):
        return self.name

a = Bus("hh", 100)


print(a.gg)
