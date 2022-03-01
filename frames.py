ship_frames = (
    'rocket_frame_1.txt',
    'rocket_frame_2.txt',
)

garbage_frames = (
    'duck.txt',
    'hubble.txt',
    'lamp.txt',
    'trash_large.txt',
    'trash_small.txt',
    'trash_x1.txt',
)


def read_frame(*names):
    """Read oneline animation from project folder."""
    frames = []
    for name in names:
        with open(f'frames/{name}', 'r') as file:
            text = file.read()
            frames.append(text)
    return tuple(frames)
