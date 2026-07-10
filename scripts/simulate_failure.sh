#!/bin/bash
echo "Injecting CPU infinite loop into backend container..."
docker exec -d backend python -c "while True: pass"
echo "Failure simulation active! Watch the CPU spike using 'docker stats backend'."
