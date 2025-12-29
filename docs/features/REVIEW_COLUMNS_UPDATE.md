# Review Command Column Structure Update

## Overview

The `lcr review` command has been enhanced with separate columns for ID, Difficulty, and Title to enable better filtering and data analysis.

## New Column Structure

### Past Reviews Table
```
╭─────┬──────┬───────────────────┬────────────┬────────────┬────────────╮
│ ID  │ Diff │ Title             │ Scheduled  │ Completed  │ Status     │
├─────┼──────┼───────────────────┼────────────┼────────────┼────────────┤
│ 215 │ -    │ Kth Largest...    │ 2025-12-10 │ 2025-12-09 │ ✓ On Time  │
│ 700 │ E    │ Search in BST     │ 2025-12-10 │ 2025-12-09 │ ✓ On Time  │
│ 787 │ M    │ Cheapest Flights  │ 2025-12-10 │ 2025-12-09 │ ✓ On Time  │
╰─────┴──────┴───────────────────┴────────────┴────────────┴────────────╯
```

### Future Reviews Table
```
╭─────┬──────┬───────────────────┬────────────┬────────────┬───────────╮
│ ID  │ Diff │ Title             │ Scheduled  │ Days Until │ Iteration │
├─────┼──────┼───────────────────┼────────────┼────────────┼───────────┤
│ 42  │ -    │ Trapping Rain...  │ 2025-12-10 │ +0         │ #1        │
│ 700 │ E    │ Search in BST     │ 2025-12-10 │ +0         │ #1        │
│ 787 │ M    │ Cheapest Flights  │ 2025-12-10 │ +0         │ #1        │
╰─────┴──────┴───────────────────┴────────────┴────────────┴───────────╯
```

## Column Definitions

### 1. ID Column
- **Content**: Pure problem ID number
- **Example**: `215`, `700`, `787`
- **Style**: Cyan color, no-wrap
- **Purpose**: Unique identifier for filtering and sorting

### 2. Diff Column (Difficulty)
- **Content**: Single character difficulty indicator
- **Values**:
  - `E` (Easy) - Green color
  - `M` (Medium) - Yellow color
  - `H` (Hard) - Red color
  - `-` (Unknown) - Dimmed/gray
- **Style**: No-wrap, color-coded
- **Purpose**: Quick visual difficulty assessment

### 3. Title Column
- **Content**: Clean problem title only
- **Extracted From**: Original title with preprocessing
- **Removes**:
  - Difficulty tags: `(E)`, `(M)`, `(H)`
  - ID prefixes: `215.`, `700.`, etc.
- **Example Transformations**:
  - Input: `(E) 700. Search in a Binary Search Tree`
  - Output: `Search in a Binary Search Tree`
  
  - Input: `215. Kth Largest Element`
  - Output: `Kth Largest Element`
  
  - Input: `42`
  - Output: `42`
- **Style**: White color, wraps if needed
- **Purpose**: Human-readable problem description

## Implementation Details

### TitleParser Utility

New utility class: `src/lcr/utils/title_parser.py`

```python
class TitleParser:
    """Parser for extracting difficulty and clean title."""
    
    @classmethod
    def parse_title(cls, title: str) -> Tuple[Optional[str], str]:
        """Parse title to extract difficulty and clean title."""
        # Returns: (difficulty, clean_title)
        
    @classmethod
    def format_difficulty(cls, difficulty: Optional[str]) -> str:
        """Format difficulty with color coding."""
```

### Parsing Logic

1. **Difficulty Extraction**
   - Pattern: `^\(([EMH])\)\s*`
   - Matches: `(E) `, `(M) `, `(H) ` at start of string
   - Extracts: Single letter `E`, `M`, or `H`

2. **ID Removal**
   - Pattern: `^\d+\.\s*`
   - Matches: Any digits followed by dot and space
   - Removes: `215. `, `700. `, etc.

3. **Clean Title**
   - After removing difficulty tag and ID prefix
   - Trims whitespace
   - Fallback to original if empty

## Benefits

### 1. Better Data Organization
- Separate columns for independent data types
- Each column has single responsibility
- Clean separation of concerns

### 2. Easier Filtering
With separate columns, future filtering features can target specific fields:
```bash
# Future possibilities
lcr review --difficulty E      # Show only Easy problems
lcr review --id 215            # Show specific problem
lcr review --title "Search"    # Search in titles
```

### 3. Visual Clarity
- Color-coded difficulty at a glance
- Clean titles without clutter
- Easy to scan and identify problems

### 4. Export-Friendly
Structured data in separate columns makes it easier to:
- Export to CSV/JSON
- Process with scripts
- Generate reports
- Build analytics

## Color Coding

### Difficulty Colors
- **Easy (E)**: `[green]E[/green]` 🟢
- **Medium (M)**: `[yellow]M[/yellow]` 🟡
- **Hard (H)**: `[red]H[/red]` 🔴
- **Unknown (-)**: `[dim]-[/dim]` ⚪

### Other Colors
- **ID**: Cyan
- **Title**: White
- **Status**: Green (on time) / Red (delayed) / Magenta (status text)
- **Dates**: Yellow (scheduled) / Green (completed)

## Examples

### Example 1: Mixed Difficulties
```
Past Reviews:
│ 1   │ E    │ Two Sum              │ 2025-12-09 │ 2025-12-09 │ ✓ On Time │
│ 215 │ M    │ Kth Largest Element  │ 2025-12-10 │ 2025-12-09 │ ✓ On Time │
│ 42  │ H    │ Trapping Rain Water  │ 2025-12-10 │ 2025-12-11 │ ⚠ 1 day   │
```

### Example 2: No Difficulty Tags
```
Future Reviews:
│ 100 │ -    │ Year-End Review      │ 2025-12-31 │ +22        │ #1        │
│ 999 │ -    │ 999                  │ 2026-01-01 │ +23        │ #1        │
```

### Example 3: Long Titles (Wrapped)
```
│ 787 │ M    │ Cheapest Flights     │ 2025-12-10 │ +0         │ #1        │
│     │      │ Within K Stops       │            │            │           │
```

## Testing Results

✅ **Title Parsing**: Correctly extracts difficulty and cleans titles  
✅ **Color Coding**: E (green), M (yellow), H (red), - (dim)  
✅ **ID Separation**: Pure numbers in ID column  
✅ **Clean Titles**: No ID prefixes or difficulty tags  
✅ **Wrapping**: Long titles wrap properly  
✅ **Backward Compatibility**: Works with existing data  

## Future Enhancements

Potential improvements enabled by this structure:

1. **Filtering Options**
   ```bash
   lcr review --difficulty E,M    # Show Easy & Medium only
   lcr review --min-days 7        # Show reviews 7+ days away
   lcr review --status delayed    # Show only delayed reviews
   ```

2. **Sorting Options**
   ```bash
   lcr review --sort difficulty   # Group by difficulty
   lcr review --sort id           # Sort by problem ID
   lcr review --sort days         # Sort by days until/delay
   ```

3. **Export Features**
   ```bash
   lcr review --export csv        # Export to CSV
   lcr review --export json       # Export to JSON
   ```

4. **Statistics**
   ```bash
   lcr review --stats             # Show difficulty distribution
   ```

## Conclusion

The updated column structure provides:
- ✅ Clear data separation
- ✅ Color-coded difficulty
- ✅ Clean, readable titles
- ✅ Filter-ready structure
- ✅ Export-friendly format

**Status**: ✅ COMPLETE  
**Backward Compatible**: Yes  
**User Impact**: Positive - Better organization and clarity
