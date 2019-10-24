
# Engage Backend

- Live Website: https://sm.engage.town
- Live API Endpoint: http://backend.engage.town/api/
- Live API Documentation: https://backend.engage.town/swagger/
- Local API Endpoint http://localhost:8000/api
- Local API Documentation http://localhost:8000/swagger/

## Dev Setup

To setup the development environment:

Please use [engage-docker](https://github.com/hackla-engage/engage-docker)
You will find directions for setting up your environment there. Changes to this repo should be made using that repo as a starting place, this repo is included as a submodule (you can add a remote to your fork of this repository in that submodule).

## Continous Delivery

We have setup continous integration and deployment on CircleCI.

When you push to the `master` branch on this repo, this will trigger a build on the server and also run the Django test suite. If the tests fail, the build will not go through.
