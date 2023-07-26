from attrs import define


@define
class Flower:
    name: str
    count: int
    cost: int
    id: int = 0


class FlowersRepository:
    flowers: list[Flower]

    def __init__(self):
        self.flowers = []

    def get_all(self):
        return self.flowers

    def save_flower(self, flower: Flower):
        flower.id = len(self.flowers)+1
        self.flowers.append(flower)

    def get_flower_by_name(self, name: str) -> Flower:
        for flower in self.flowers:
            if flower.name == name:
                return flower
        
        return None

    def get_flower_by_id(self, id: int) -> Flower:
        for flower in self.flowers:
            if flower.id == id:
                return flower

        return None
