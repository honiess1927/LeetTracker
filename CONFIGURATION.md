# LCR Configuration Guide

## Overview

LCR supports configuration files to customize your learning experience. You can adjust review intervals, display preferences, and default settings without modifying code.

---

## Configuration File Locations

LCR searches for configuration files in the following order (first found is used):

1. `.lcrrc` - Current directory (project-specific config)
2. `~/.lcrrc` - Home directory (user-wide config)
3. `~/.config/lcr/config.yaml` - XDG config directory (standard location)

**Tip:** Use the example config as a starting point:
```bash
cp config.example.yaml ~/.lcrrc
```

---

## Configuration Format

Configuration files use YAML format. All settings are optional - missing values use sensible defaults.

### Complete Example

```yaml
# Spaced repetition intervals
intervals:
  default: [1, 7, 18, 35]
  randomization: 0.15

# Display preferences
display:
  timezone: "UTC"
  date_format: "%Y-%m-%d"
  use_colors: true
  use_emoji: true

# Database settings
database:
  path: "~/.lcr/lcr.db"
  backup_on_start: false

# Default command options
defaults:
  review_times: 4
```

---

## Configuration Options

### Intervals Section

Controls spaced repetition scheduling:

#### `intervals.default`
- **Type**: Array of integers
- **Default**: `[1, 7, 18, 35]`
- **Description**: Base intervals in days for review scheduling
- **Research-based**: Optimized for long-term retention of coding problems

**Examples:**
```yaml
# Faster learning curve
intervals:
  default: [1, 3, 7, 14, 30]

# More gradual spacing
intervals:
  default: [2, 10, 25, 50, 100]

# Intensive short-term
intervals:
  default: [1, 2, 4, 7]
```

#### `intervals.randomization`
- **Type**: Float (0.0 to 1.0)
- **Default**: `0.15` (±15%)
- **Description**: Randomization factor to prevent review clustering
- **How it works**: Intervals vary by ±(randomization × 100)%

**Examples:**
```yaml
# No randomization (consistent scheduling)
intervals:
  randomization: 0.0

# More variation (±25%)
intervals:
  randomization: 0.25

# Slight variation (±10%)
intervals:
  randomization: 0.10
```

**Effect on scheduling:**
- `randomization: 0.0` → Always exact intervals
- `randomization: 0.15` → 7-day interval becomes 6-8 days
- `randomization: 0.30` → 7-day interval becomes 5-9 days

---

### Display Section

Controls output appearance:

#### `display.timezone`
- **Type**: String (IANA timezone name)
- **Default**: `"UTC"`
- **Description**: Timezone for date/time display
- **Note**: Database always stores UTC internally

**Examples:**
```yaml
# Pacific Time
display:
  timezone: "America/Los_Angeles"

# Eastern Time
display:
  timezone: "America/New_York"

# London
display:
  timezone: "Europe/London"

# Tokyo
display:
  timezone: "Asia/Tokyo"
```

#### `display.date_format`
- **Type**: String (Python strftime format)
- **Default**: `"%Y-%m-%d"` (e.g., 2025-12-09)
- **Description**: Date format string for display

**Examples:**
```yaml
# US format: 12/09/2025
display:
  date_format: "%m/%d/%Y"

# European format: 09-12-2025
display:
  date_format: "%d-%m-%Y"

# Verbose: December 09, 2025
display:
  date_format: "%B %d, %Y"

# Short: 09-Dec-2025
display:
  date_format: "%d-%b-%Y"
```

#### `display.use_colors`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable/disable colored terminal output

```yaml
# Disable colors (useful for terminals without color support)
display:
  use_colors: false
```

#### `display.use_emoji`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Enable/disable emoji in output

```yaml
# Disable emoji (useful for environments with poor emoji support)
display:
  use_emoji: false
```

---

### Database Section

Controls database storage:

#### `database.path`
- **Type**: String
- **Default**: `"~/.lcr/lcr.db"`
- **Description**: Path to SQLite database file
- **Note**: Tilde (~) expands to home directory

**Examples:**
```yaml
# Custom location
database:
  path: "~/Documents/lcr_data.db"

# Dropbox sync
database:
  path: "~/Dropbox/LCR/lcr.db"

# Project-specific
database:
  path: "./local_lcr.db"
```

#### `database.backup_on_start`
- **Type**: Boolean
- **Default**: `false`
- **Description**: Automatically backup database on each CLI invocation
- **Note**: Currently not implemented (planned feature)

---

### Defaults Section

Controls default command options:

#### `defaults.review_times`
- **Type**: Integer (≥ 1)
- **Default**: `4`
- **Description**: Default number of review iterations for `lcr add` command

**Examples:**
```yaml
# More reviews for thorough learning
defaults:
  review_times: 6

# Fewer reviews for quick refresh
defaults:
  review_times: 3

# Extensive spaced repetition
defaults:
  review_times: 8
```

**Effect:**
```bash
# Without config (or review_times: 4)
lcr add 215  # Creates 4 reviews

# With review_times: 6
lcr add 215  # Creates 6 reviews

# Override config with --times flag
lcr add 215 --times 8  # Creates 8 reviews (ignores config)
```

---

## Usage Examples

### Example 1: Intensive Learning

For cramming before interviews:

```yaml
intervals:
  default: [1, 2, 4, 7, 14]
  randomization: 0.0  # Consistent schedule

defaults:
  review_times: 5
```

**Result**: 5 reviews over 2 weeks with exact intervals

---

### Example 2: Long-term Retention

For spaced learning over months:

```yaml
intervals:
  default: [1, 7, 21, 45, 90]
  randomization: 0.20  # More variation

defaults:
  review_times: 5
```

**Result**: 5 reviews over 3+ months with variation

---

### Example 3: Minimal Configuration

Just change review count:

```yaml
defaults:
  review_times: 6
```

**Result**: Everything else uses defaults, creates 6 reviews

---

### Example 4: Custom Timezone

Display times in your local timezone:

```yaml
display:
  timezone: "America/Los_Angeles"
  date_format: "%m/%d/%Y %I:%M %p"
```

**Result**: Dates show as "12/09/2025 02:30 PM"

---

## Validation Rules

Configuration is validated on load. Invalid values cause clear error messages:

### Intervals Validation
- `default` must be non-empty array of positive integers
- `randomization` must be between 0.0 and 1.0

### Defaults Validation
- `review_times` must be positive integer (≥ 1)

### Display Validation
- `use_colors` and `use_emoji` must be boolean
- `timezone` must be valid IANA timezone name
- `date_format` must be valid strftime format

**Example Error:**
```
ConfigurationError: intervals.default must contain positive integers
```

---

## Checking Current Configuration

To see which config file is loaded:

```python
from lcr.config import get_settings
settings = get_settings()
print(f"Config file: {settings.config_file}")
print(f"Intervals: {settings.intervals}")
print(f"Default times: {settings.default_review_times}")
```

---

## Configuration Priority

1. **Command-line flags** (highest priority)
   - Example: `lcr add 1 --times 8` overrides config

2. **Configuration file**
   - First found in search paths

3. **Built-in defaults** (lowest priority)
   - Used when no config file exists

---

## Tips & Best Practices

### 1. Start with Defaults
Don't create a config file until you need customization. Defaults work well for most users.

### 2. Experiment with Intervals
Try different intervals to find what works for your learning style:
- Visual learners: Shorter intervals (more reviews)
- Analytical learners: Longer intervals (deeper retention)

### 3. Disable Randomization for Consistency
Set `randomization: 0.0` if you prefer predictable schedules.

### 4. Use Project-Specific Configs
Place `.lcrrc` in interview prep directories for custom settings per project.

### 5. Version Control Your Config
Add config to dotfiles repository for consistent settings across machines.

---

## Troubleshooting

### Config File Not Found
- Check file location: `ls -la ~/.lcrrc ~/.config/lcr/config.yaml`
- Check permissions: `chmod 644 ~/.lcrrc`
- Check syntax: Validate YAML at https://www.yamllint.com/

### Invalid Config Error
- Read error message carefully - it shows which value is invalid
- Check data types (string vs number vs boolean)
- Check array syntax: `[1, 2, 3]` not `1, 2, 3`

### Config Not Taking Effect
- Verify you're editing the correct file (check search order)
- Restart CLI application
- Check for syntax errors in YAML

---

## Migration from Defaults

If you want to customize from current defaults:

1. **Copy example config:**
   ```bash
   cp config.example.yaml ~/.lcrrc
   ```

2. **Edit settings:**
   ```bash
   nano ~/.lcrrc
   # or
   code ~/.lcrrc
   ```

3. **Test with one problem:**
   ```bash
   lcr add 999 --title "Test"
   ```

4. **Verify schedule:**
   Check that intervals match your config

---

## Advanced Configuration

### Environment-Specific Configs

Use different configs for different purposes:

```bash
# Interview prep (intensive)
cp config.intensive.yaml .lcrrc

# Long-term learning (spaced)
cp config.longterm.yaml ~/.lcrrc
```

### Programmatic Config Changes

Not recommended, but possible via `reload_settings()`:

```python
from lcr.config import reload_settings

# After modifying config file
settings = reload_settings()
```

---

## Reference: strftime Format Codes

Common date format codes for `display.date_format`:

| Code | Meaning | Example |
|------|---------|---------|
| %Y | 4-digit year | 2025 |
| %y | 2-digit year | 25 |
| %m | Month (01-12) | 12 |
| %B | Full month name | December |
| %b | Short month name | Dec |
| %d | Day of month (01-31) | 09 |
| %A | Full day name | Monday |
| %a | Short day name | Mon |
| %H | Hour 24h (00-23) | 14 |
| %I | Hour 12h (01-12) | 02 |
| %M | Minute (00-59) | 30 |
| %p | AM/PM | PM |

**Example combinations:**
- `%Y-%m-%d` → 2025-12-09
- `%m/%d/%Y` → 12/09/2025
- `%B %d, %Y` → December 09, 2025
- `%d-%b-%Y %H:%M` → 09-Dec-2025 14:30

---

## Support

For configuration issues:
1. Check this documentation
2. Validate your YAML syntax
3. Check file permissions
4. Verify timezone names at: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
5. Test with minimal config first

---

## Related Documentation

- `DATABASE_MANAGEMENT.md` - Database operations
- `config.example.yaml` - Example configuration file
- `PHASE5_PLAN.md` - Technical implementation details
