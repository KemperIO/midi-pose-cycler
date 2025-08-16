# Blender CLI Reference

For testing MIDI Pose Cycler addon via command line.

## Basic Command Structure

```bash
blender [options] [file] [--python script]
```

## Common Options for Testing

| Option                  | Description                                   |
|-------------------------|-----------------------------------------------|
| `--background`          | Run without UI (headless)                    |
| `--factory-startup`     | Skip user preferences and scripts            |
| `--python <script>`     | Run Python script                            |
| `--python-console`      | Run interactive Python console                |
| `--log-level <level>`   | Set logging level (0-5)                      |
| `--debug`               | Enable debug messages                        |
| `--debug-python`        | Enable Python debug messages                 |

## Testing Examples

### Run addon tests
```bash
"/mnt/c/Program Files/Blender Foundation/Blender 4.5/blender.exe" \
    --background \
    --factory-startup \
    --python test/test_workspace.py
```

### Test with specific blend file
```bash
blender test.blend --background --python test/run_tests.py
```

### Debug addon loading
```bash
blender --background --factory-startup --debug-python --python test/test_addon_load.py
```

## Output Control

| Option                | Description                      |
|-----------------------|----------------------------------|
| `--log-file <file>`   | Redirect output to file          |
| `--verbose <level>`   | Set verbosity (0-2)              |
| `-noaudio`            | Disable audio                    |
| `-nojoystick`         | Disable joystick                 |

## Python Script Arguments

Pass arguments after `--`:
```bash
blender --background --python script.py -- arg1 arg2
```

Access in Python:
```python
import sys
args = sys.argv[sys.argv.index("--") + 1:]
```

## Reference
- Official docs: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html