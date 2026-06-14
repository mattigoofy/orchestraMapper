# Orchestra Mapper

A Python script to generate orchestra seating layout visualizations. Takes a list of musicians and their sections, then arranges them in concentric half-circles representing the stage layout. 
It is also available as a static website with a visual editor on GitHub Pages, check it out [here](https://mattigoofy.github.io/orchestraMapper/).

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
  "font_size": 15,
  "icon_size": 400,
  "title": "My overview",
  "use_images": true,
  "image_url": "https://raw.githubusercontent.com/mattigoofy/orchestraMapper/main/figs/",
  "show_labels": false,
  "show_row_count": false,
  "invert": false,
  "date": "10 jan 2025",
  "conductor": {
    "name": "John",
    "color": "#8b4513",
    "image": "conductor.png"

  },
  "sections": [
    {
      "name": "Flute",
      "color": "#e74c3c",
      "row": 1,
      "start_index": 0,
      "names": ["Alice", "Bob", ""]
    },
    {
      "name": "Oboe",
      "color": "#e67e22",
      "row": 1,
      "start_index": 1,
      "names": ["Carol", "Diana", "Eve"]
    },
    {
      "name": "Saxophone",
      "color": "#3498db",
      "row": 2,
      "start_index": 0,
      "names": ["Frank", "Grace", "Hank", "Ivy", ""]
    },
    {
      "name": "clarinet",
      "color": "#2ecc71",
      "row": 2,
      "start_index": 1,
      "names": ["Jack", "Kate"]
    },
    {
      "name": "bassoon",
      "color": "#9b59b6",
      "row": 3,
      "start_index": 0,
      "names": ["Leo", "Mia", "Noah", "Olivia", "Peter", "Quinn"]
    },
    {
      "name": "trumpet",
      "color": "#f39c12",
      "row": 3,
      "start_index": 1,
      "names": ["", "", "Rachel", "Sam", "Tina", "Uma", "Victor"]
    },
    {
      "name": "Trombone",
      "color": "#34495e",
      "row": 4,
      "start_index": 0,
      "names": ["Wendy", "Xander"]
    },
    {
      "name": "snare",
      "color": "#34495e",
      "row": 4,
      "start_index": 1,
      "names": ["Wendy", "Xander"]
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
