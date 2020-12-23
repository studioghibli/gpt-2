# Fake News Generator

For this project, we wanted to see how easy it would be to generate convincing fake news by training GPT-2 models. We trained these models using articles from The New York Times on the topics of Black Lives Matter, COVID-19, and the 2020 U.S. election. You can find our trained models [here](https://drive.google.com/drive/folders/13xBv1TngYsshuoaZ2vwv1VmCwclc46zx?usp=sharing). This repository also provides a user interface for generating more articles.

## Download Pre-Requisites

In the root folder, run:
```
pip install -r requirements.txt
pip install flask
```
We use Python version 3.7.x to run this project.

## Run User Interface for Pre-Generated Samples

To generate random samples that we already created, go into fast-ui and run:
```
python -m http.server
```

## Run User Interface for Generating New Samples

Download models.zip, decompress it, and place the decompressed folder under src. In src, run:
```
export FLASK_APP=generate_sample.py
export FLASK_ENV=development
flask run
```

# Reference

Reference:  ["Beginner’s Guide to Retrain GPT-2 (117M) to Generate Custom Text Content"](https://medium.com/@ngwaifoong92/beginners-guide-to-retrain-gpt-2-117m-to-generate-custom-text-content-8bb5363d8b7f)