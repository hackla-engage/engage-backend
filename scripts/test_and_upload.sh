#!/bin/bash
docker-compose -f docker-compose-test.yml up --abort-on-container-exit --exit-code-from backend
if [ $? -eq 0 ]; then
    echo Succeeded building and testing
    docker push hack4laengage/engage_backend_service
    exit 0;
else
    echo Failed building and testing
    exit 1;
fi
