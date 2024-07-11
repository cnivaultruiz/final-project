import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# Afficher le logo
st.sidebar.image("streamlit/logo.png", use_column_width=True)

# Titre de l'application
st.title('Himalayan Expedition Success Prediction')

# Texte de bienvenue
st.markdown("""
Welcome to the Himalayan Expedition Success Prediction Application.
This application developed by the **Union of Himalayan Agencies** uses a machine learning model to predict the chances of success of your expedition based on various factors.
""")

# Image d'arrière-plan
st.image("streamlit/Himalaya.jpg", use_column_width=True)
st.markdown('Please enter the details of your expedition below.')

# Chargement des données combinées et du modèle
combined_df = pd.read_csv('csv/combined_df.csv')
model = joblib.load('streamlit/best_random_forest_model.pkl')
scaler = joblib.load('streamlit/scaler.pkl')

# Saisie des données utilisateur
peak_name = st.selectbox('Peak name', combined_df['peak_name_x'].unique())
season = st.selectbox('Season', ['Spring', 'Summer', 'Winter', 'Autumn'])
age = st.number_input('Age', min_value=18, max_value=100)
sex = st.selectbox('Sex', ['F', 'M'])
oxygen_used = st.selectbox('Do you plan to use oxygen', [0, 1], index=0)
hired = st.selectbox('Are you part of the staff?', [0, 1], index=0)
solo = st.selectbox('Do you plan to do this expedition alone?', [0, 1], index=0)
members = st.number_input('How many climbers will be part of the expedition?', min_value=0, max_value=100)
staff = st.number_input('How many staff will be part of the expedition?', min_value=0, max_value=100)
expedition_duration = st.number_input('Duration of the expedition (days)', min_value=1, max_value=365)

# Récupérer la hauteur pour le pic sélectionné
height_metres = combined_df.loc[combined_df['peak_name_x'] == peak_name, 'height_metres'].values[0]

# Convertir les données saisies en DataFrame
input_data = pd.DataFrame({
    'peak_name': [peak_name],
    'season': [season],
    'age': [age],
    'sex': [sex],
    'oxygen_used': [oxygen_used],
    'hired': [hired],
    'solo': [solo],
    'height_metres': [height_metres],
    'members': [members],
    'hired_staff': [staff],
    'expedition_duration': [expedition_duration]
})

# Appliquer les transformations prétraitées
input_data['F'] = (input_data['sex'] == 'F').astype(int)
input_data['M'] = (input_data['sex'] == 'M').astype(int)
input_data['Spring'] = (input_data['season'] == 'Spring').astype(int)
input_data['Summer'] = (input_data['season'] == 'Summer').astype(int)
input_data['Winter'] = (input_data['season'] == 'Winter').astype(int)
input_data['Autumn'] = (input_data['season'] == 'Autumn').astype(int)

# Sélection des colonnes d'entrée utilisées par le modèle
input_features = input_data[['hired', 'oxygen_used', 'Spring', 'Summer', 'Winter', 'Autumn', 'age', 'F', 'M', 'height_metres', 'solo', 'members', 'hired_staff', 'expedition_duration']]

# Normaliser les données d'entrée avec le même scaler utilisé lors de l'entraînement
input_features_norm = scaler.transform(input_features)

# Prédiction
if st.button('Predict'):
    #st.write(input_data)  # Vérifier les données saisies
    prediction = model.predict(input_features_norm)[0]
    if prediction == 1:
        st.success("The expedition has a chance of succeeding.")
    else:
        st.error("The expedition has a chance of failing.")

# Filtrer les données pour le pic sélectionné
filtered_df = combined_df.loc[combined_df['peak_name_x'] == peak_name]

# Compter le nombre d'expéditions par saison et succès
season_counts = filtered_df.groupby(['season', 'success']).size().unstack(fill_value=0)

# Plot avec couleurs pour succès (bleu) et échec (gris)
plt.figure(figsize=(10, 6))
season_counts.plot(kind='bar', stacked=True, color=['blue', 'grey'], rot=0)
plt.xlabel('Season')
plt.ylabel('Number of Expeditions')
plt.title('Number of Expeditions by Season and Success')
plt.legend(['Success', 'Failure'], loc='upper right')
st.pyplot(plt)
