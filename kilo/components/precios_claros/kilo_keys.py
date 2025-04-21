class KiloKeys:
    @staticmethod
    def city_key(state_code: str, city: str) -> str:
        return f"({state_code})[{city}]"

    @staticmethod
    def place_key(state_code: str, city: str, address: str) -> str:
        return f"({state_code})[({city})({address})]"

    @staticmethod
    def point_of_sale_key(point_of_sale_code: str, flag: str) -> str:
        return f"({point_of_sale_code})({flag})"

    @staticmethod
    def article_card_key(article_code: str, brand: str, description: str, package: str) -> str:
        return f"[{article_code}]({brand})({description})({package})"

