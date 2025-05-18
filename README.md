````markdown
# 🌞 Solar Challenge Week 1 🚀

> **“Harnessing the power of the sun, one panel at a time!”**

## 👋 Welcome!

Welcome to **Solar Challenge Week 1**!  
In this module, you’ll configure your local environment, explore core solar-energy scripts, and get hands-on with your first simulations. Let’s light up those panels! 🔆

---

## ⚙️ Environment Setup

1. **Clone the repository**  
   ```bash
   git clone https://github.com/boaztulu/solar-challenge-week1.git
   cd solar-challenge-week1
````

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Run local scripts**

   ```bash
   python scripts/data_cleaning.py
   python scripts/eda.py
   ```

   *(Adjust script names or paths as needed.)*

---

## 🔎 EDA & Data Profiling

* **Data Exploration**: We generated summary statistics, visualizations, and distribution plots for key solar variables (GHI, DNI, DHI, etc.).
* **Data Profiling**: Using Pandas, Seaborn, and other libraries, we analyzed missing values, outliers, and correlations to gain insights into each country’s solar resource potential.
* **Data Cleaning**: Outliers were handled via IQR-based or Z-score methods, and missing values were imputed with medians where appropriate. This ensured higher data quality for subsequent analyses.

---

## 🌐 Streamlit App

We built an **interactive Streamlit dashboard** to visualize and compare the cleaned solar datasets.
**Access the live dashboard here**:
[https://solar-challenge-week1-bt.streamlit.app/](https://solar-challenge-week1-bt.streamlit.app/)

**Features**:

* **Country Comparisons**: Side-by-side boxplots of GHI, DNI, and DHI.
* **Statistical Tests**: ANOVA/Kruskal–Wallis test results for GHI across countries.
* **Dynamic Filtering**: Select which countries or metrics to display.
* **Summary Tables**: Mean, median, and standard deviation for quick reference.

> **Note**: You can also run `streamlit run app/main.py` locally if you prefer a local version.

---

## 🗂 Suggested Folder Structure

```
solar-challenge-week1/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── main.py      # Streamlit app entry point
│   └── ...
├── notebooks/
│   └── eda.ipynb    # Exploratory notebooks
├── scripts/
│   ├── data_cleaning.py
│   └── eda.py
├── data/
│   └── cleaned/     # Cleaned CSV files
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---

Thanks for checking out **Solar Challenge Week 1**! Feel free to open issues or PRs with feedback.

```
```
