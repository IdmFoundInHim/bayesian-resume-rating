def int_input(prompt: str, default: int) -> int:
    i = input(prompt)
    return int(i) if i.isdigit() else default
