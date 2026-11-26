# MobilePhone_Price_Prediction
# 📱 Mobile Phone Price Range Classification Using Machine Learning

## 📌 Project Overview

This project uses Machine Learning to predict the price range of a mobile phone based on its hardware specifications.

The user enters mobile phone details such as RAM, battery power, internal memory, camera, screen dimensions and other specifications. The trained Machine Learning model analyzes these inputs and predicts the mobile phone's price category.

The project also includes an interactive web application developed using **Streamlit**, where users can enter mobile specifications and receive predictions.

## 🎯 Project Objectives

- Predict mobile phone price ranges using Machine Learning.
- Perform data preprocessing and exploratory data analysis (EDA).
- Select the most relevant features for model training.
- Train and compare multiple classification algorithms.
- Evaluate model performance using different metrics.
- Deploy the trained model through a Streamlit web application.

## 📊 Dataset Information

The project uses a mobile phone dataset containing:

- Total records: 2,000
- Total columns: 21
- Input features: 20
- Target variable: `price_range`
- Price categories: 4

### Price Categories

| Class | Price Category |
|---|---|
| 0 | Low Cost |
| 1 | Medium Cost |
| 2 | High Cost |
| 3 | Very High Cost |

The dataset contains 500 records in each price category.

### Important Features

The project selects the following 10 features based on their absolute correlation with the target variable:

1. RAM
2. Battery Power
3. Pixel Width
4. Pixel Height
5. Internal Memory
6. Screen Width
7. Primary Camera
8. Mobile Weight
9. Touch Screen
10. Screen Height

## ⚙️ Technologies Used

- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn
- Scikit-learn
- Streamlit
- Joblib
- Jupyter Notebook

## 🧠 Machine Learning Algorithms

Four classification algorithms were implemented and compared:

### 1. Logistic Regression
A classification algorithm that predicts the probability of a data point belonging to different classes.

### 2. K-Nearest Neighbors (KNN)
Predicts the class of a new data point based on the classes of its nearest neighbors.

### 3. Decision Tree
Uses a tree-like structure of conditions to make predictions.

### 4. Random Forest
Combines multiple decision trees and uses majority voting to produce the final prediction.

## 🔄 Project Workflow

1. Load the mobile phone dataset.
2. Perform exploratory data analysis (EDA).
3. Check missing values and duplicate records.
4. Analyze feature correlations.
5. Separate features and target variable.
6. Split the dataset into 80% training data and 20% testing data.
7. Apply stratified sampling.
8. Select the top 10 features using absolute correlation.
9. Apply StandardScaler to Logistic Regression and KNN inputs.
10. Train four Machine Learning algorithms.
11. Evaluate and compare model performance.
12. Select the best-performing model using weighted F1 score.
13. Save the trained model using Joblib.
14. Deploy the model using Streamlit.

## 📈 Model Performance

The models were evaluated using Accuracy, Precision, Recall and F1 Score.

| Algorithm | Accuracy |
|---|---:|
| Logistic Regression | 98.00% |
| KNN | 68.75% |
| Decision Tree | 86.25% |
| Random Forest | 91.25% |

**Best Performing Model: Logistic Regression**

Logistic Regression achieved the highest accuracy of 98% on the test dataset and was selected as the best model based on weighted F1 score.

## 🌐 Web Application

The project includes an interactive Streamlit web application.

### Main Features

- Enter mobile phone specifications.
- Predict one of four mobile price categories.
- View prediction confidence.
- Explore hardware specifications.
- Compare the entered specifications with dataset benchmarks.
- View visual insights about the predicted price category.

## 🚀 How to Run the Project

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

### Step 2: Open the Project Folder

```bash
cd MobilePhone_Price_Prediction-main
```

### Step 3: Create a Virtual Environment (Optional)

```bash
python -m venv .venv
```

Activate it:

**Mac/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Run the Streamlit Application

```bash
streamlit run app.py
```

The application will open in your browser.

## 📁 Project Structure

```text
MobilePhone_Price_Prediction/
│
├── app.py
│
├── mobile_price_prediction.ipynb
│
├── train.csv
│
├── mobile_price_model.pkl
│
├── requirements.txt
│
├── requirement.txt
│
├── README.md
│
└── static/
    └── pcb_bg.mp4
```

## 💾 Model Saving

The trained model is saved using Joblib in:

```text
mobile_price_model.pkl
```

The saved model bundle contains:

- Best trained model
- Model name
- Selected features
- Scaler (when required)

This allows the Streamlit application to load and reuse the trained model without retraining it every time.

## 🔮 Future Improvements

- Add more mobile phone specifications.
- Experiment with additional Machine Learning algorithms.
- Improve prediction performance.
- Use larger and more diverse datasets.
- Deploy the application online.

## 👩‍💻 Project Information

**Project Title:** Mobile Phone Price Range Classification Using Machine Learning

**Domain:** Machine Learning – Supervised Learning

**Problem Type:** Multi-Class Classification

**Framework:** Streamlit

**Language:** Python

---

⭐ If you find this project useful, consider giving the repository a star!


