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
