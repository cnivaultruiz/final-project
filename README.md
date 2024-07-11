

Himalayan Expedition Success Prediction
This project aims to analyze the success and risk factors of Himalayan expeditions to improve the planning and safety of future expeditions. The project was commissioned by the Union of Himalayan Agencies (UHA) to provide crucial data for sustainable and secure expedition management.

Table of Contents
Context
Objective
Project Planning
Data Gathering
Data Cleaning
Exploratory Data Analysis (EDA)
Machine Learning
API Development
Streamlit Application
Challenges
Conclusion

Context
The Himalayan region has seen a constant increase in the number of climbers each year. This growth necessitates better data management and analysis to ensure the safety and success of expeditions. The UHA, which brings together the main trekking agencies, has taken the initiative to address this need.

Objective
The primary goal of this project is to analyze the success and risk factors of Himalayan expeditions. The insights derived from this analysis are intended to help the UHA improve the planning and safety of future expeditions, thus preserving the beauty and integrity of these mythical peaks for future generations.

Project Planning
The project was managed using the Kanban method with Trello, and included the following steps:

Topic Selection
Data Source Identification
Data Cleaning
Dataset Enrichment
SQL Implementation
Exploratory Data Analysis (EDA) using Python
Data Visualization with Tableau
API Development
Report Generation
Machine Learning Model Development
Streamlit Application Development
Final Presentation
Data Gathering
Data was collected from three main sources:

Kaggle: Expedition archives by Elizabeth Hawley.
Nominatim API: GPS coordinates of the peaks.
Web Scraping: Temperature and weather data by season for Mount Everest from the Topchinatravel website.
Data Cleaning
The data cleaning process involved managing missing values by:

Replacing NaNs with medians for numerical columns.
Replacing NaNs with "Unknown" for categorical columns.
Handling specific date-related columns.
Dropping remaining NaNs where necessary.
Exploratory Data Analysis (EDA)
EDA was conducted using Python and Tableau to uncover insights from the data. Visualizations such as heatmaps were used to show correlations and key trends.

Tableau public link :
https://public.tableau.com/views/Himalaya-expeditions-Story/Histoire1?:language=fr-FR&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link 

Machine Learning
Various machine learning models were tested, including Random Forest, AdaBoost, Gradient Boosting, and Bagging Classifier. The features and targets were defined, data was normalized, and necessary features were engineered. The models were evaluated based on performance scores such as accuracy, precision, recall, and F1-score.

API Development
A Flask API was developed to expose the data with endpoints for peaks, expeditions, and statistics. This API facilitates easy data access for further analysis.

Streamlit Application
A Streamlit application was developed to help the UHA anticipate risks. The app uses the machine learning model to predict the success or failure of expeditions based on specific parameters.

Challenges
The main challenges encountered during the project were:

Inability to retrieve historical weather data via an API.
Difficulty in creating a high-performing model in Streamlit.
Managing the time with the extensive amount of work.
Conclusion
Risk and Evolution: There has been a significant increase in climbers and oxygen usage, leading to higher risks.
Contribution of the Project: This project equips the UHA with advanced predictive tools for better expedition management.
Vision for the Future: The goal is to maintain responsible access to high peaks, ensure an exceptional experience for future generations, and reduce the ecological footprint while maximizing safety.
Usage
To use this project, clone the repository and follow the instructions in the Installation section.
