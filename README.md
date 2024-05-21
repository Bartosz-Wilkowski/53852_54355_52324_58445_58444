# sign-language-interpreter

# to use the module run 'app.py' in cmd
# to check results open 'http://127.0.0.1:5000' in your browser 
# (change port number if youre using different port than 5000)



# dataset 'ASL Alphabet' from Kaggle
# https://www.kaggle.com/datasets/grassknoted/asl-alphabet
# https://datasets.cms.waikato.ac.nz/ufdl/american-sign-language-letters/
# https://public.roboflow.com/object-detection/american-sign-language-letters/1/download




structure

sign-language-interpreter/
│
├── templates/               # HTML
│   └── index.html           # HTML file
│
├── static/                  # static
│   ├── css/                 # CSS
│   │   └── style.css        # CSS file
│   └── js/                  # JavaScript
│       └── script.js        # JavaScript file
│
├── dataset/                 # dataset
│   ├── train/               # training data
│   └── test/                # test data
│
├── models/                  # saved models
│   ├── model/               # model.h5 file
│   └── final_model/         # final_model.h5 file
│   └── checkpoint_model/    # checkpoint_model.h5 file
│
├── results/                 # results
│   └── confusion_matrix.png # confusion matrix image
│
├── app.py                   # main
├── train_model.py              # model training
├── evaluation.py         # evaluation
├── compile_model.py           # compile model
├── README.md                # project description


