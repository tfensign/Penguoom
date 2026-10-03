# Leaderboard UI Implementation

## What Was Added

A sleek, non-obtrusive leaderboard display on the home screen that shows the top 5 high scores for the currently selected difficulty.

### Visual Design

The leaderboard appears directly on the home screen, positioned between "Best Stats" and the difficulty selector:

```
┌─────────────────────────────────────┐
│  PENGUOOM                           │
│  [Game description...]              │
│  Best: Sector 8 / 10                │
│  ─────────────────────────────────  │
│  High Scores                        │
│  ╭─────────────────────────────────╮│
│  │ #1  Sector 8/10 · 87%    12,540 ││
│  │ #2  Sector 7/10 · 82%    11,200 ││
│  │ #3  Sector 6/10 · 76%     9,850 ││
│  │ #4  Sector 5/10 · 68%     8,100 ││
│  │ #5  Sector 4/10 · 62%     6,450 ││
│  ╰─────────────────────────────────╯│
│  ─────────────────────────────────  │
│  Difficulty:  [Beginner] Advanced   │
│  [ENTER THE ICE] [Settings] [Help]  │
└─────────────────────────────────────┘
```

### Design Principles

- **Compact**: Fits naturally in the vertical flow without dominating
- **Readable**: Clear hierarchy with rank, stats, and score
- **Consistent**: Uses game's cyan/green accent colors
- **Responsive**: Max-height with scrolling if needed (future-proofing for many entries)
- **Contextual**: Updates immediately when difficulty is switched
- **Graceful Degradation**: Empty state message for new players

### Color Scheme

- **Rank**: Cyan (#7fe8ff) - prominent identifier
- **Stats**: Muted cyan (#9fd8e6) - secondary information
- **Score**: Mint green (#7fffb0) - primary value (matches game's achievement color)
- **Background**: Subtle translucent navy (rgba(24,58,80,0.3)) - reads as part of UI
- **Border**: Faint cyan (rgba(150,225,255,0.25)) - defines container without prominence

### Information Displayed

Each leaderboard entry shows:

| Element | Purpose | Example |
|---------|---------|---------|
| **Rank** | Position in top 5 | #1, #2, ... #5 |
| **Sector** | Furthest level reached | Sector 8/10 |
| **Accuracy** | Shot accuracy % | 87% |
| **Score** | Final run score | 12,540 |

## Technical Implementation

### New Files/Edits

- **CSS** (22 lines): Leaderboard container, list, entries, and empty state styling
- **HTML** (3 lines): Leaderboard container in #overlay
- **JavaScript** (~50 lines):
  - `updateLeaderboardDisplay()`: Renders top 5 scores for current difficulty
  - Integration with `updateDifficultyUI()` for dynamic updates

### Data Flow

```
User selects difficulty
         ↓
setDifficulty() called
         ↓
updateDifficultyUI() called
         ↓
updateLeaderboardDisplay() called
         ↓
getHighScoresForDifficulty(difficultyKey)
         ↓
Render HTML for top 5 scores
         ↓
Display on home screen
```

### CSS Classes

```css
#leaderboardContainer          /* Main container, positioned between best stats and difficulty */
#leaderboardTitle             /* "High Scores" label */
#leaderboardList              /* Scrollable list of entries */
.leaderboardEntry             /* Individual score row */
.leaderboardRank              /* Rank number (#1, #2, etc) */
.leaderboardStats             /* Sector/accuracy info */
.leaderboardScore             /* Final score value */
#emptyLeaderboard             /* Message when no scores exist */
```

## Behavior

### On Home Screen
- Leaderboard displays automatically when home screen appears
- Shows scores for currently selected difficulty
- Difficulty buttons have implied affordance (player can click to switch)

### On Difficulty Change
- User clicks a difficulty button (Beginner/Advanced/Expert)
- Leaderboard re-renders with top 5 scores for that difficulty
- Smooth update, no page reload needed

### After First Run
- When a run completes, `recordRunStats()` saves the entry
- On returning to home screen, leaderboard includes the new run
- Player immediately sees their position (hopefully #1!)

### Empty State
- **New players**: "No runs yet on beginner · Start playing to appear here!"
- **Switch to untouched difficulty**: Shows message for that difficulty
- **Encourages engagement**: Implies "your run will appear here"

## Color Scheme Justification

The color choices align with the game's visual language:

- **Cyan** (accent-cyan): Used throughout HUD for primary information and achievements
- **Mint Green** (accent-mint): Used for achievement badges and important stats
- **Muted Cyan** (secondary): Information hierarchy - less important details

This creates a cohesive visual system where the leaderboard "feels" like part of the game UI, not an afterthought.

## Future Enhancements (Not Implemented)

These could be added without redesign:

1. **Time-based stats**: Show date/time of each run (using entry.date)
2. **Weapon info**: Display which weapon was used (already tracked)
3. **Category tabs**: Switch between "All Time", "This Week", "This Month"
4. **Personal bests**: Highlight user's own runs (requires tracking current player)
5. **Difficulty comparison**: Side-by-side leaderboards for all difficulties
6. **Streak counting**: "X runs in a row on Expert"

## Mobile Responsiveness

The leaderboard is built to scale:

- **Desktop**: Full display, readable at 560px max-width
- **Tablet**: Fits naturally in portrait/landscape
- **Mobile**: Compact font (0.75rem per entry), scrollable if needed

The 150px max-height means 5 entries fit without scrolling on most devices. The container is set to 560px max-width (matching other home screen elements) so it aligns visually.

## Testing Checklist

- [x] Displays top 5 scores on home screen
- [x] Updates when difficulty is switched
- [x] Shows empty state for new players
- [x] Shows empty state for untouched difficulties
- [x] Accuracy displays correctly (0-100%)
- [x] Sector display is correct (1-10)
- [x] Scrolling works if more than 5 entries (future-proofing)
- [x] Colors match game aesthetic
- [x] Responsive on mobile/tablet
- [x] Integrated with minified code
- [x] No performance impact

## Attribution

Implemented as part of the leaderboard/stats system rollout.
All backend tracking was already in place; this UI brings data to the player.
