# SaasCopilot

Create a local virtual environment, for example using the venv module. Then, activate it. 
python -m venv venv 
source venv/bin/activate
pytest -s
pytest -W ignore::DeprecationWarning -vv
black .
sudo docker build . -t saascopilot
docker images

Install the dependencies. pip install -r requirements.txt

Launch the app python app.py

#####################################

TODO items:
- Docker - 12/27
- CICD - 12/28
- EC2 deployment - 12/29
- Prometheus Grafana - 12/30

#####################################

- Self consistancies - can run in parallel
- BRD generation process will take time. API may face timeout. Easy way is to handle through 
BackgroundTasks
- 