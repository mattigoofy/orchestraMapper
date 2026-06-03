# Orchestra Mapper

A Python script to generate orchestra seating layout visualizations. Takes a list of musicians and their sections, then arranges them in concentric half-circles representing the stage layout.

## Features

- Arrange musicians in rows of half-circles
- Multiple sections per row support
- Customizable colors per section
- Use instrument images instead of dots
- Configurable font and icon sizes
- Placeholder positions for easy arrangement

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

### Options

- `-i, --input` - Input JSON file (default: `orchestra.json`)
- `-o, --output` - Output image file (default: `orchestra_layout.png`)
- `--no-labels` - Hide section labels
- `--use-images` - Use instrument images instead of dots

## Configuration

Edit `orchestra.json` to customize your layout:

```json
{
  "font_size": 9,
  "icon_size": 400,
  "use_images": false,
  "image_dir": "figs",
  "conductor": {
    "name": "John",
    "color": "#8b4513"
  },
  "sections": [
    {
      "name": "trumpet",
      "color": "#e74c3c",
      "image": "violin.png",
      "row": 1,
      "start_index": 0,
      "names": ["Alice", "Bob", ""]
    }
  ]
}
```

### Config Options

- `font_size` - Size of musician names
- `icon_size` - Size of dots/images
- `use_images` - Enable instrument images
- `image_dir` - Directory containing images

### Section Options

- `name` - Section name (displayed as label)
- `color` - Hex color for dots/labels
- `image` - Image filename (optional, defaults to section name)
- `row` - Row number (1 = front)
- `start_index` - Position within row (for label grouping)
- `names` - Array of musician names (use `""` for invisible placeholder)

## Image Support

Place PNG images in the `figs` directory. Images are automatically scaled based on `icon_size`. Transparent PNGs work best.

## Example Output

![Orchestra Layout](orchestra_layout.png)
