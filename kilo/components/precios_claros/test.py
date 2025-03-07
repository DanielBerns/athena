from typing import Tuple

def get_tuple_of_strings(first: int, second: int, third: int) -> Tuple[str, str, str]:
    return (f"{first:03d}", f"{second:03d}", f"{third:03d}")

def main():
    alpha, bravo, charlie = get_tuple_of_strings(15, 17, 18)
    print(f"{alpha}/{bravo}/{charlie}")

if __name__ == "__main__":
    main()
