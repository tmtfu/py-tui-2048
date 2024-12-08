import curses

def addstr_robust(stdscr: curses.window,
                  y: int,
                  x: int,
                  string: str,
                  *args) -> None:
    """
    A better window.addstr()

    params:
        stdscr: the curses window
        y: the y to add the string at
        x: the x to add the string at
        string: the string to add
        *args: any other attributes
    """

    # *args are the string arguments
    try:
        stdscr.addstr(max(y, 0), max(x, 0), string, *args)

    except curses.error:
        pass

