"""Convenient server starter script."""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("  Student CRUD API Server Starting")
    print("  Web Dashboard:       http://127.0.0.1:8000")
    print("  Interactive Docs:    http://127.0.0.1:8000/docs")
    print("  ReDoc Alternative:   http://127.0.0.1:8000/redoc")
    print("=" * 60)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
