def read_frame(name: str):
    with open(f'frames/{name}', 'r') as file:
        frame = file.read()

    return frame


def get_frame_size(text):
    lines = text.splitlines()
    rows = len(lines)
    columns = max([len(line) for line in lines])

    return rows, columns


class Frame:
    def __init__(self, file: str):
        self.uid = file.removesuffix(".txt")
        self.frame = read_frame(file)
        self.rows, self.columns = self.sizes = get_frame_size(self.frame)
        self.center = self.columns // 2


SHIP_FRAMES = tuple(
    [Frame(item) for item in ('rocket_frame_1.txt', 'rocket_frame_2.txt')]
)

GARBAGE_FRAMES = tuple(
    [
        Frame(item) for item in (
            'duck.txt',
            'hubble.txt',
            'lamp.txt',
            'trash_large.txt',
            'trash_small.txt',
            'trash_x1.txt'
        )
    ]
)
