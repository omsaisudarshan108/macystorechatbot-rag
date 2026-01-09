# Feedback Feature Documentation

## Overview

The RAG platform now includes a comprehensive feedback system that allows store associates to rate answers and provide feedback on helpfulness. This feature helps improve the system over time by collecting user satisfaction data.

## Features

### For Store Associates

1. **Star Rating System** (1-5 stars)
   - Rate the quality of each answer
   - Visual star display for easy selection

2. **Helpfulness Indicator**
   - Simple Yes/No toggle
   - "Was this helpful in answering your query?"

3. **Optional Comments**
   - Free-text feedback field
   - Share specific concerns or suggestions

4. **Session Tracking**
   - Each session gets a unique ID
   - Track feedback across multiple queries

### For Administrators

1. **Feedback Statistics Dashboard**
   - Total feedback responses
   - Average rating (out of 5 stars)
   - Helpfulness percentage
   - Total comments received
   - Rating distribution histogram

2. **Data Export**
   - Feedback stored in JSONL format
   - Easy to analyze or export

## API Endpoints

### Submit Feedback

**POST** `/feedback`

Submit feedback for an answer.

**Request Body:**
```json
{
  "question": "What are the store hours?",
  "answer": "Store hours are 9 AM to 9 PM daily.",
  "rating": 5,
  "was_helpful": true,
  "comment": "Very clear and helpful!",
  "store_id": "NY_001",
  "session_id": "uuid-session-id"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Thank you for your feedback!",
  "feedback_id": "fb_c8ff5407592c"
}
```

### Get Feedback Statistics

**GET** `/feedback/stats`

Retrieve aggregate feedback statistics.

**Response:**
```json
{
  "status": "success",
  "stats": {
    "total_responses": 3,
    "average_rating": 4.0,
    "helpful_percentage": 66.7,
    "total_comments": 2,
    "rating_distribution": {
      "1": 0,
      "2": 0,
      "3": 1,
      "4": 1,
      "5": 1
    }
  }
}
```

## UI Components

### Feedback Widget (Main Interface)

After receiving an answer, users see:

1. **Rating Section**
   - Star rating (5 to 1 stars)
   - Displayed horizontally with visual stars

2. **Helpfulness Section**
   - 👍 Yes / 👎 No toggle
   - Clear question: "Was this helpful in answering your query?"

3. **Comment Section**
   - Optional text area
   - Placeholder: "Tell us how we can improve this answer..."

4. **Submit Button**
   - Primary styled button
   - Confirmation message on success

### Statistics Viewer (Sidebar - Admin)

Located in sidebar under "📊 Feedback Statistics":

- **Refresh Stats** button to load latest data
- Metrics display:
  - Total Responses
  - Average Rating (X/5.0)
  - Helpful %
  - Comments count
- Rating distribution chart

## Data Storage

### Development/Local

**Location:** `data/feedback/feedback.jsonl`

**Format:** JSON Lines (one JSON object per line)

**Example Record:**
```json
{
  "id": "fb_c8ff5407592c",
  "timestamp": "2026-01-09T16:55:12.938219",
  "question": "What are the store hours?",
  "answer": "Store hours are 9 AM to 9 PM daily.",
  "rating": 5,
  "was_helpful": true,
  "comment": "Very clear and helpful!",
  "store_id": "NY_001",
  "session_id": "uuid-session-id"
}
```

### Production Recommendations

For production deployment, consider:

1. **Cloud Storage**
   - Store feedback in Cloud Storage buckets
   - Partitioned by date for easier analysis

2. **Database Storage**
   - Use Cloud SQL or Firestore
   - Enable complex queries and analytics

3. **BigQuery Integration**
   - Stream feedback to BigQuery
   - Advanced analytics and reporting

## Implementation Details

### Backend

**Module:** `backend/feedback/feedback_store.py`

**Class:** `FeedbackStore`

**Methods:**
- `save_feedback()` - Save new feedback
- `get_all_feedback()` - Retrieve all feedback
- `get_feedback_stats()` - Calculate statistics

### Frontend

**File:** `ui/app.py`

**Components:**
- Session state management
- Feedback form with validation
- Stats viewer with refresh

**State Variables:**
- `session_id` - Unique session identifier
- `last_question` - Most recent question
- `last_answer` - Most recent answer

## Usage Examples

### Testing with curl

```bash
# Submit feedback
curl -X POST http://localhost:8000/feedback \
  -H "Content-Type: application/json" \
  -d @feedback.json

# Get statistics
curl http://localhost:8000/feedback/stats
```

### Python Example

```python
import requests

# Submit feedback
feedback = {
    "question": "What are the store hours?",
    "answer": "Store hours are 9 AM to 9 PM daily.",
    "rating": 5,
    "was_helpful": True,
    "comment": "Very helpful!",
    "store_id": "NY_001"
}

response = requests.post(
    "http://localhost:8000/feedback",
    json=feedback
)
print(response.json())

# Get stats
stats = requests.get("http://localhost:8000/feedback/stats")
print(stats.json())
```

## Analytics & Insights

### Key Metrics to Track

1. **Answer Quality**
   - Average rating over time
   - Rating distribution
   - Low-rated answers for improvement

2. **Helpfulness**
   - Percentage of helpful answers
   - Correlation with ratings

3. **User Engagement**
   - Feedback submission rate
   - Comment frequency
   - Store-specific patterns

4. **Trends**
   - Rating trends over time
   - Most commented topics
   - Store performance comparison

### Sample Analysis Queries

```python
# Load feedback data
import json

feedback_data = []
with open('data/feedback/feedback.jsonl', 'r') as f:
    for line in f:
        feedback_data.append(json.loads(line))

# Find low-rated answers
low_rated = [f for f in feedback_data if f['rating'] <= 2]

# Unhelpful answers
unhelpful = [f for f in feedback_data if not f['was_helpful']]

# Store-specific stats
from collections import defaultdict
store_ratings = defaultdict(list)
for f in feedback_data:
    store_ratings[f['store_id']].append(f['rating'])

# Average by store
for store, ratings in store_ratings.items():
    avg = sum(ratings) / len(ratings)
    print(f"{store}: {avg:.2f}")
```

## Future Enhancements

### Planned Features

1. **Feedback Analysis**
   - Sentiment analysis of comments
   - Topic clustering
   - Automatic issue detection

2. **Alert System**
   - Notify when ratings drop
   - Flag consistently unhelpful answers

3. **Answer Improvement**
   - Use feedback to retrain models
   - Prioritize knowledge base updates

4. **User Segmentation**
   - Track by store
   - Track by user role
   - Track by time of day

5. **Export & Reporting**
   - CSV/Excel export
   - Automated weekly reports
   - Dashboard visualizations

## Best Practices

### For Development

1. **Regular Review**
   - Check feedback daily
   - Address low ratings promptly

2. **Data Backup**
   - Backup feedback regularly
   - Store in multiple locations

3. **Privacy**
   - Don't store personal information
   - Anonymize data for analysis

### For Production

1. **Scalability**
   - Use database for large volumes
   - Implement pagination for stats

2. **Performance**
   - Cache statistics
   - Async feedback submission

3. **Monitoring**
   - Track submission rate
   - Monitor storage usage
   - Alert on system errors

## Troubleshooting

### Feedback Not Saving

**Issue:** Feedback submission returns error

**Solutions:**
1. Check `data/feedback/` directory exists
2. Verify write permissions
3. Check backend logs for errors

### Stats Not Loading

**Issue:** Stats endpoint returns empty or error

**Solutions:**
1. Ensure feedback.jsonl file exists
2. Check file is valid JSON Lines format
3. Verify backend has read permissions

### UI Not Showing Feedback Form

**Issue:** Feedback widget not appearing

**Solutions:**
1. Ensure answer was received successfully
2. Check session state is initialized
3. Verify frontend can reach backend

## Security Considerations

1. **Input Validation**
   - Rating must be 1-5
   - Limit comment length
   - Sanitize user input

2. **Rate Limiting**
   - Prevent spam submissions
   - One feedback per answer

3. **Data Privacy**
   - No personal information stored
   - Session IDs are anonymous
   - Comply with data retention policies

## Support

For questions or issues with the feedback feature:
1. Check backend logs: `tail -f backend.log`
2. Review frontend console for errors
3. Check feedback storage: `ls -la data/feedback/`
4. Test API directly with curl/Postman

---

**Version:** 1.0.0
**Last Updated:** 2026-01-09
**Maintainer:** RAG Platform Team
