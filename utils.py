import string
import random


def generate_random_string(length, include_specials, include_digits):
    chars = string.ascii_letters
    if include_digits:
        chars += string.digits
    if include_specials:
        chars += '!"№;%:?*()_+'

    return ''.join(random.choice(chars) for _ in range(length))
