# Feedback & Sentiment Analysis Service

AI-enabled microservice for collecting customer feedback and generating sentiment insights.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Frontend  │────▶│   Feedback   │────▶│   Message       │
│   (Submit)  │     │   API        │     │   Queue         │
└─────────────┘     └──────────────┘     └────────┬────────┘
                           │                      │
                           ▼                      ▼
                    ┌──────────────┐     ┌─────────────────┐
                    │   Database   │◀────│   Background    │
                    │   (Store)    │     │   Worker (AI)   │
                    └──────────────┘     └─────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Insights   │────▶  Analytics/Marketing
                    │   API        │
                    └──────────────┘
```

## Processing Model

| Operation | Mode | Description |
|-----------|------|-------------|
| Feedback submission | **Real-time** | Immediate acknowledgment, non-blocking |
| Sentiment analysis | **Async/Batch** | Background processing via queue |
| Insights retrieval | **Batch** | Aggregated summaries for analytics |

## AI Failure Handling

1. **Retry with backoff**: Configurable retries before failing
2. **Fallback analyzer**: Rule-based fallback when AI unavailable
3. **Graceful degradation**: Feedback stored even if analysis fails
4. **Re-queue**: Failed items retried in next batch cycle

## API Endpoints

- `POST /api/v1/feedback` - Submit feedback (real-time)
- `GET /api/v1/feedback/{ref}` - Get feedback with sentiment
- `GET /api/v1/feedback/{ref}/status` - Check analysis status
- `GET /api/v1/insights/summary` - Aggregated insights
- `GET /api/v1/insights/venues/{id}` - Venue-specific insights

## Quick Start

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8007
```

## Configuration

Key environment variables:
- `AI_API_KEY` - OpenAI API key
- `DATABASE_URL` - PostgreSQL connection string
- `RABBITMQ_URL` - Message broker URL


