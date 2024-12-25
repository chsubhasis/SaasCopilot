# SaasCopilot

Create a local virtual environment, for example using the venv module. Then, activate it. 
python -m venv venv 
source venv/bin/activate
pytest -s
pytest -W ignore::DeprecationWarning -vv
black .

Install the dependencies. pip install -r requirements.txt

Launch the app python app.py

#####################################

TODO items:
- PyTest updates. Bring outside. - 12/27
- FAST API - 12/27
- Docker - 12/28
- CICD - 12/29
- EC2 deployment - 12/30
- Prometheus Grafana - 12/30