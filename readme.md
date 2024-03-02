unilever_version_1_with_MTSOS
Github: https://github.com/RH-NAYM/Unilever_priority_1.git
HuggingFace: https://huggingface.co/rakib72642/UBL_Deploy_with_MTSOS_v1
sudo apt install iproute2 && sudo apt install wget && sudo apt install unzip && apt install nvtop && sudo apt-get install git-lfs && apt-get update && apt-get install libgl1

git clone https://huggingface.co/rakib72642/UBL_Deploy_with_MTSOS_v1 && cd UBL_Deploy_with_MTSOS_v1 && pip install -r requirements.txt

sudo apt update && sudo apt upgrade

python apiUBL.py

curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok

ngrok config add-authtoken 2Qm8hS1zPhVXiLjEdlI4738tLzF_2QJwGJMK5oTbQD33QSVXS && ngrok http --domain=batnlp.ngrok.app 5656

old:
run: ngrok http --domain=brief-crow-lovely.ngrok-free.app 5656 auth: ngrok config add-authtoken 2Q8xOjna6gvwQRiMTZayN1uEgWy_6uRD8M1b6rZtYMz4yLzAw

new:
ngrok config add-authtoken 2NiinQNrE1VtIkQIJZjOenVAXr6_5aCtpeiifRSmcijtuqYPC

ngrok http --domain=desired-vastly-cod.ngrok-free.app 5656