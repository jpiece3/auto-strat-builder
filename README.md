# Brothers Automate Intelligence Agent

Autonomous brand and competitor intelligence platform using AI agents to crawl, research, and analyze brands and their competitive landscape.

## Overview

This application combines a FastAPI backend with a React frontend to deliver comprehensive brand intelligence reports. AI agents work autonomously to:

- **Brand Discovery** - Crawl and analyze brand identity, messaging, and positioning
- **Competitor Intelligence** - Identify and profile competitors with SEO metrics
- **SEO Analysis** - Analyze keywords, backlinks, rankings, and traffic
- **Web Presence** - Scan social profiles and online reputation
- **Report Compilation** - Generate professional HTML and Markdown reports

## Tech Stack

**Backend:**
- Python 3.11+
- FastAPI
- Pydantic
- Firecrawl (web scraping)
- Tavily (search & research)
- Playwright (automation)
- DataForSEO (SEO metrics)

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Router

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+
- API keys for: Firecrawl, Tavily, Playwright, DataForSEO

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/jpiece3/brand-intel.git
   cd brand-intel
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Add your API keys to .env
   ```

### Running Locally

1. **Start the backend server**
   ```bash
   cd agent
   uvicorn server:app --reload --port 8000
   ```

2. **Start the frontend dev server**
   ```bash
   npm run dev
   ```

3. **Open your browser**
   ```
   http://localhost:5173
   ```

## Building for Production

1. **Build the frontend**
   ```bash
   npm run build
   ```

2. **Run the combined server**
   The FastAPI server serves both the API and the built frontend:
   ```bash
   cd agent
   uvicorn server:app --host 0.0.0.0 --port 8000
   ```

## Deployment

### Railway

This app is configured for one-click Railway deployment:

```bash
railway up
```

The `Dockerfile` and `railway.toml` handle the build and deployment automatically.

### Environment Variables

Required environment variables:
- `FIRECRAWL_API_KEY` - Web scraping
- `TAVILY_API_KEY` - Search and research
- `PLAYWRIGHT_API_KEY` - Browser automation
- `DATAFORSEO_API_KEY` - SEO metrics

## Project Structure

```
.
├── agent/                    # Python backend
│   ├── agents/              # AI agent implementations
│   ├── workflows/           # Multi-agent workflows
│   ├── server.py            # FastAPI server
│   └── models.py            # Data models
├── src/                     # React frontend
│   ├── components/          # UI components
│   ├── pages/              # Page components
│   └── lib/                # Utilities
└── public/                 # Static assets
```

## API Endpoints

- `POST /api/analyze` - Start a new brand analysis
- `GET /api/status/{job_id}` - Check analysis status
- `GET /api/jobs` - List all analyses
- `GET /api/reports/{job_id}/html` - View HTML report
- `GET /api/reports/{job_id}/markdown` - View Markdown report
- `DELETE /api/jobs/{job_id}` - Delete an analysis

## Features

- **Real-time Progress** - Watch AI agents work through each stage
- **Professional Reports** - Brothers Automate branded HTML reports
- **Dashboard** - Manage and view past analyses
- **Export Options** - HTML, Markdown, and JSON formats

## License

Proprietary - Brothers Automate

## Support

For questions or support, contact: support@brothersautomate.com
