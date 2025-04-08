# Authorization Service

Authentication and authorization service built with Litestar, AsyncPG, and advanced security practices.

## Features

- User authentication (login/logout)
- Session management
- JWT token handling
- Role-based access control
- Scheduled session cleanup
- Comprehensive logging

## Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Poetry 1.8

## Quick Start

1. Clone the repository:
   ```bash
   git clone https://github.com/NeZlox/authorization-service.git
   ```

2. Navigate to the project directory:
   ```bash
   cd authorization-service
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   (Edit the `.env` file with your configuration)

4. Start the services:
   ```bash
   docker-compose up -d
   ```

5. To stop the services:
   ```bash
   docker-compose down
   ```

## Project Structure

```
authorization-service/
├── app/                          # Main application code
│   ├── adapters/                 # Interface adapters
│   │   ├── inbound/              # Input adapters (HTTP controllers)
│   │   └── outbound/             # Output adapters (repositories)
│   ├── application/              # Business logic layer
│   ├── config/                   # Configuration settings
│   ├── infrastructure/           # Technical infrastructure
│   │   ├── db/                   # Database setup and migrations
│   │   └── di/                   # Dependency injection
│   ├── lib/                      # Shared libraries
│   │   ├── errors/               # Exception handling
│   │   ├── security/             # Auth utilities
│   │   └── utils/                # Helper functions
│   └── server/                   # Server configuration
│       ├── cron/                 # Scheduled jobs
│       └── life_cycle/           # Application lifecycle hooks
└── scripts/                      # Utility scripts
```

## Configuration

Edit these files for your environment:

- `.env` - Environment variables
- `app/config/*` - Another settings

## Development Setup (Manual)

For local development without Docker:

1. Prepare environment:
   ```bash
   cp .env.example .env
   # Edit .env to use your local Postgres credentials
   ```

2. Install dependencies:
   ```bash
   poetry update
   poetry install
   ```

3. Setup database:
   ```bash
   litestar database upgrade
   ```

4. Run development server:
   ```bash
   uvicorn app.asgi:app --host 127.0.0.1 --port 8000 --reload
   ```
   
## Development Commands

| Command                               | Description               |
|---------------------------------------|---------------------------|
| `poetry install`                      | Install all dependencies  |
| `poetry update`                       | Update all dependencies   |
| `poetry run ruff check .\app --fix  ` | Run code linting          |
| `poetry run test`                     | Run tests                 |
| `litestar database upgrade`           | Apply database migrations |
| `litestar database downgrade`         | Revert last migration     |
| `uvicorn app.asgi:app`                | Run application           |

##  ――✧✦⋆ 𝓐𝓾𝓽𝓱𝓸𝓻: [**NeZlox**](https://github.com/NeZlox) ⋆✦✧――
