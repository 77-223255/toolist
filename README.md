# toolist

A Python-based abstract avatar generator using recursive rectangle partitioning and matplotlib colormaps.

## Features

- **6 splitting algorithms**: random, average, complete_down, complete_line, mondrian, vertical_horizontal
- **100+ colormaps** from matplotlib for region coloring
- **Real-time preview** via Tkinter GUI
- **Export** to common image formats

## Usage

```bash
python avatar_generator.py
```

Configure algorithm, split count, colormap, and canvas size through the GUI, then export.

## References

- [matplotlib colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html)
- [Pillow (PIL)](https://python-pillow.org/)
- [Mondrian-style generative art](https://en.wikipedia.org/wiki/Piet_Mondrian)
- [Tkinter GUI framework](https://docs.python.org/3/library/tkinter.html)
