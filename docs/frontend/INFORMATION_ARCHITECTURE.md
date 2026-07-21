# SpeakLift: Information Architecture

The information architecture of SpeakLift is strictly organized around user goals (Action, Insight, Configuration) rather than backend modules (Models, Repositories).

## Goal-Oriented Hierarchy

### Primary Navigation (The Sidebar)
The sidebar is minimal, focusing on the core loops of the product.
1. **Dashboard (Home)**: The command center. Goal: Determine what to do right now.
2. **Interviews (Action)**: The practice arena. Goal: Conduct mock sessions and view past performance.
3. **Roadmap (Growth)**: The learning hub. Goal: Review AI-generated study paths and achievements.
4. **Profile (Context)**: The identity layer. Goal: Update resumes, job targets, and experience.

### Secondary Navigation (In-Page Tabs)
Used to subdivide complex primary views without burying information.
- **Interviews Page**: `Recent Reports` | `Saved JDs`
- **Profile Page**: `Resume Details` | `Target Jobs` | `Skill Matrix`

### Contextual Navigation
When inside an active task, global navigation disappears.
- **During an Interview**: Sidebar is hidden. Only "End Session" or "Pause" is available. Focus is 100%.
- **Inside a Report**: Breadcrumb navigation (`Interviews > Report #124`) allows quick escape, but the focus remains on the data.

## Command Palette (`Cmd+K`)
The command palette transcends traditional navigation. It acts as an omnipresent search and action bar.
- **Navigation**: "Go to Dashboard", "Go to Settings".
- **Action**: "Start new interview", "Upload resume".
- **Discovery**: Searches past reports ("Find feedback on React").

## Search Behavior
- Standard search bars are minimized. The Command Palette handles global search.
- Contextual search (e.g., filtering a table of past interviews) is localized to that specific page header.

## Breadcrumb Philosophy
- Use breadcrumbs for hierarchical drill-downs (e.g., `Dashboard > Interviews > Full Stack Eng at Stripe`).
- Do not use breadcrumbs for top-level pages (e.g., `Dashboard`).
