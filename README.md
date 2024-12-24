# SaasCopilot

Create a local virtual environment, for example using the venv module. Then, activate it. 
python -m venv venv 
source venv/bin/activate
pytest -s
pytest -W ignore::DeprecationWarning -vv
isort *.py
black .

Install the dependencies. pip install -r requirements.txt

Launch the app python app.py

#####################################

TODO items:
- Logics update + Use rag output in generate_brd
- Self Consistancy
- Gradio

- FAST API
- Docker
- CICD
- EC2 deployment
- Prometheus Grafana

Review below:
- STATE to be managed centrally from workflow file. Not from other py classes/agents.
- 