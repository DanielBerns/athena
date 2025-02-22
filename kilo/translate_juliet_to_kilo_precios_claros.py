from components.precios_claros import create_juliet_to_kilo_precios_claros

def main() -> None:
    actor = create_juliet_to_kilo_precios_claros("live")
    actor.update_storage()

if __name__ == "__main__":
    main()
