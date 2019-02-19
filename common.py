

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def is_next(current, last):
    int_current = int(current)
    int_last = int(last)
    if int_current + 1 <= int_last:
        return str(int_current + 1)
    else:
        return str(int_last)


def is_previous(current, first):
    int_current = int(current)
    int_first = int(first)
    if int_current - 1 >= int_first:
        return str(int_current - 1)
    else:
        return str(int_first)
