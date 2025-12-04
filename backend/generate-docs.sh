#!/bin/bash
# Generate API documentation using pdoc

echo "Generating API documentation..."
uv run pdoc src/backend -o docs

if [ $? -eq 0 ]; then
    echo "✓ Documentation generated successfully in docs/"
    echo "  Open docs/index.html in your browser to view"
else
    echo "✗ Failed to generate documentation"
    exit 1
fi
