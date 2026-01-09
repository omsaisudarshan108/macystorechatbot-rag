# Question History Feature Documentation

## Overview

The RAG platform now includes a question history feature that allows store associates to view their recently asked questions and quickly reuse them. This feature improves user experience by providing easy access to previous queries.

## Features

### For Store Associates

1. **Recent Questions List**
   - View the last 10 questions asked
   - Questions displayed in reverse chronological order (newest first)
   - Each question shows timestamp in tooltip

2. **Click-to-Reuse**
   - Click any question to populate it in the question input field
   - Automatically pre-fills the question text
   - Ready to submit immediately or modify first

3. **Smart Truncation**
   - Long questions (>60 characters) are truncated for display
   - Full question visible in tooltip on hover
   - Maintains readability in the sidebar

4. **Clear History**
   - One-click button to clear all history
   - Useful for privacy or starting fresh
   - Cannot be undone

5. **Duplicate Prevention**
   - Consecutive identical questions are not saved twice
   - Keeps history clean and relevant

## UI Components

### Question History Panel (Sidebar)

Located in the sidebar under "📜 Recent Questions":

```
┌─────────────────────────────────┐
│ 📜 Recent Questions             │
├─────────────────────────────────┤
│ Click a question to ask again   │
│                                 │
│ 🔄 What are the return...      │ ← Most recent
│ 🔄 How do I process a...       │
│ 🔄 What are the store h...     │
│ 🔄 Can I accept returns...     │
│                                 │
│ [🗑️ Clear History]             │
└─────────────────────────────────┘
```

### Features

- **Expandable Panel**: Collapsed by default to save space
- **Recent First**: Most recent question at the top
- **Truncation**: Questions longer than 60 chars are shortened
- **Tooltips**: Hover to see full question and timestamp
- **Full Width Buttons**: Easy to click on mobile

## How It Works

### Data Structure

Each question entry contains:
```python
{
    'question': "What are the store hours?",
    'timestamp': "2026-01-09 12:15:30",
    'store_id': "NY_001"
}
```

### Storage

- **Location**: Streamlit session state (`st.session_state.question_history`)
- **Persistence**: Lasts for the browser session
- **Capacity**: Last 10 questions displayed (unlimited stored)
- **Format**: List of dictionaries

### Workflow

1. **User asks question** → Question submitted via "Ask" button
2. **Check for duplicates** → Skip if same as last question
3. **Add to history** → Append with timestamp and store_id
4. **Display in sidebar** → Show in Recent Questions panel
5. **Click to reuse** → Populate question input field
6. **Submit or modify** → User can edit before asking

## Implementation Details

### Session State Variables

**`question_history`**: List of question dictionaries
```python
st.session_state.question_history = [
    {
        'question': "What are the store hours?",
        'timestamp': "2026-01-09 12:15:30",
        'store_id': "NY_001"
    },
    ...
]
```

**`reuse_question`**: Temporary storage for clicked question
```python
st.session_state.reuse_question = "What are the store hours?"
```

### Key Code Sections

**Initialize History** (lines 20-22):
```python
if 'question_history' not in st.session_state:
    st.session_state.question_history = []
```

**Add Question** (lines 157-168):
```python
# Add question to history (with timestamp)
from datetime import datetime
question_entry = {
    'question': question,
    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    'store_id': store_id
}

# Avoid duplicate consecutive questions
if not st.session_state.question_history or \
   st.session_state.question_history[-1]['question'] != question:
    st.session_state.question_history.append(question_entry)
```

**Display History** (lines 91-125):
```python
with st.sidebar.expander("📜 Recent Questions", expanded=False):
    if st.session_state.question_history:
        # Display most recent questions first (last 10)
        recent_questions = st.session_state.question_history[-10:][::-1]

        for idx, q_data in enumerate(recent_questions):
            question_text = q_data['question']
            timestamp = q_data['timestamp']

            # Truncate long questions
            display_text = question_text if len(question_text) <= 60 else question_text[:57] + "..."

            # Create a button for each question
            if st.button(
                f"🔄 {display_text}",
                key=f"history_{idx}",
                help=f"Asked at {timestamp}\n\n{question_text}",
                use_container_width=True
            ):
                # Set the question in session state to reuse
                st.session_state.reuse_question = question_text
                st.rerun()
```

**Reuse Question** (lines 131-137):
```python
# Check if we need to reuse a question from history
default_question = ""
if 'reuse_question' in st.session_state and st.session_state.reuse_question:
    default_question = st.session_state.reuse_question
    st.session_state.reuse_question = None  # Clear after using

question = st.text_input("Enter your question", value=default_question)
```

## User Experience

### Typical Usage Flow

1. **Store associate asks question**: "What is the return policy?"
2. **Gets answer** and provides feedback
3. **Asks another question**: "How do I process a return?"
4. **Later wants to check return policy again**
5. **Opens Recent Questions panel** in sidebar
6. **Clicks on** "What is the return policy?"
7. **Question pre-filled** in input field
8. **Clicks Ask** or modifies question first

### Benefits

- **Saves typing**: Reuse common questions instantly
- **Quick reference**: See what was asked recently
- **Pattern recognition**: Notice frequently asked questions
- **Efficiency**: Less time typing, more time working
- **Learning**: Review past queries for context

## Privacy & Data

### Session-Based Storage

- History stored only in browser session
- No persistence across sessions
- Cleared when browser tab closed
- Not stored in backend database

### Clear History

Users can clear their history anytime:
1. Open "📜 Recent Questions" panel
2. Scroll to bottom
3. Click "🗑️ Clear History"
4. All history removed immediately

### Data Not Stored

- Question history is NOT sent to backend
- NOT stored in files or database
- NOT shared across users
- NOT persisted after session ends

## Customization Options

### Change Display Limit

To show more/fewer questions (default: 10):

```python
# Change from [-10:] to desired number
recent_questions = st.session_state.question_history[-20:][::-1]  # Show 20
```

### Change Truncation Length

To adjust when questions are truncated (default: 60 chars):

```python
# Change from 60 to desired length
display_text = question_text if len(question_text) <= 80 else question_text[:77] + "..."
```

### Default Expanded State

To show history panel expanded by default:

```python
# Change expanded=False to expanded=True
with st.sidebar.expander("📜 Recent Questions", expanded=True):
```

### Add Store Filter

To filter questions by store:

```python
# Filter by current store
store_questions = [q for q in st.session_state.question_history
                   if q['store_id'] == store_id]
```

## Future Enhancements

### Planned Features

1. **Persistent History**
   - Store history in backend database
   - Associate with user account
   - Access history across sessions

2. **Search History**
   - Search box to filter questions
   - Full-text search capability
   - Highlight matching terms

3. **Export History**
   - Download as CSV or JSON
   - Email history to self
   - Share with team

4. **Popular Questions**
   - Show most frequently asked questions
   - Aggregate across all users
   - Quick access to common queries

5. **Question Categories**
   - Auto-categorize questions
   - Filter by category
   - Tag questions manually

6. **Favorites/Bookmarks**
   - Mark important questions
   - Star frequently used queries
   - Quick access to favorites

## Troubleshooting

### History Not Showing

**Issue**: Recent Questions panel is empty

**Solutions**:
1. Ask at least one question first
2. Check if panel is collapsed - click to expand
3. Clear browser cache and refresh
4. Check console for JavaScript errors

### Questions Not Saving

**Issue**: Questions disappear after asking

**Solutions**:
1. Check browser console for errors
2. Verify session state is working
3. Try refreshing the page
4. Check if "Clear History" was clicked accidentally

### Duplicate Questions

**Issue**: Same question appears multiple times

**Solutions**:
1. This is expected if question is asked again later
2. Duplicate prevention only works for consecutive questions
3. Use "Clear History" to remove duplicates

### History Lost

**Issue**: History disappeared

**Reasons**:
1. Browser tab/session closed (expected behavior)
2. "Clear History" button clicked
3. Page refreshed with state loss
4. Browser cache cleared

## Best Practices

### For Users

1. **Review history regularly** - Keep track of what you've asked
2. **Clear old history** - Remove outdated questions periodically
3. **Use full question text** - Check tooltip for complete question
4. **Modify before resubmitting** - Update questions if needed

### For Administrators

1. **Monitor common patterns** - Notice frequently reused questions
2. **Create templates** - Document common questions for training
3. **Improve knowledge base** - Add docs for popular questions
4. **Track usage** - See which questions are asked repeatedly

## Integration with Other Features

### Works With Feedback Feature

- Question history preserved after feedback submission
- Can reuse questions that received good feedback
- Track which questions needed clarification

### Works With Store Selection

- Questions tagged with store_id
- Can filter history by store (future enhancement)
- Maintains context across store switches

### Works With Document Ingestion

- Questions remain after uploading documents
- Useful to retest after adding new knowledge
- Compare answers before/after document updates

## Performance Considerations

### Memory Usage

- Each question entry: ~200 bytes
- 10 questions: ~2 KB
- 100 questions: ~20 KB
- Negligible impact on performance

### Rendering Speed

- History panel loads instantly
- No network requests required
- Cached in session state
- Buttons render client-side

## Accessibility

- **Keyboard Navigation**: All buttons accessible via Tab
- **Screen Readers**: Proper ARIA labels on buttons
- **Tooltips**: Full question text available on hover
- **High Contrast**: Clear visual separation of items

## Support

For questions or issues with the question history feature:
1. Check this documentation
2. Review browser console for errors
3. Try clearing and rebuilding history
4. Contact support with session details

---

**Version:** 1.0.0
**Last Updated:** 2026-01-09
**Feature Type:** UI Enhancement
