import pydeck as pdk
#import plost
import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
# Titre de l'application
st.title("Le Dataset du FOOTIX")

top = pd.read_csv("SHN_2015.csv")

top['DepLib'] = top['DepLib'].str.replace('-', ' ')

# Créez une liste des valeurs à supprimer
valeurs_a_supprimer = ['NOUVELLE CALEDONIE', 'ETRANGER', 'MONACO','MAYOTTE','NOUMEA','HAUTE CORSE', 'ST PIERRE ET MIQUELON','CORSE', 'REUNION','LA REUNION' 'CORSE DU SUD']

# Supprimez les lignes correspondantes dans le DataFrame top
top = top[~top['DepLib'].isin(valeurs_a_supprimer)]

# Réindexez le DataFrame après la suppression
top = top.reset_index(drop=True)

dataframe = pd.read_csv("cities.csv")

df = dataframe[["latitude","longitude","department_name"]]

df['department_name'] = df['department_name'].str.upper()

df['department_name'] = df['department_name'].str.replace('-', ' ')

# Grouper par le département et calculer la moyenne de latitude et longitude
resultat = df.groupby('department_name')[['latitude', 'longitude']].mean().reset_index()


resultat = resultat.rename(columns={'department_name': 'DepLib'})


Footix = top.merge(resultat, on='DepLib', how='inner')

#st.write(Footix)

st.markdown('### Les classiques')

# Sélectionnez une variable pour l'axe x
x_variable = st.selectbox("Axe x:",
                     ['Sexe', 'FedNom'])

occurrences = Footix[x_variable].value_counts()

occurrences = occurrences.sort_values(ascending=False).head(15)


st.bar_chart(occurrences, color='#7f00ff')

# Créer un nouveau dataset groupé par la colonne "CatLib"
df = Footix.groupby('Catlib').size().reset_index(name='Occurrence')

st.markdown('### Donut chart')
###plost.donut_chart(
#        data=df,
#        theta='Occurrence',
#        color='Catlib',
#        legend='Catlib',
#        use_container_width=True)

# Créer un graphique en forme de donut
fig, ax = plt.subplots()
ax.pie(df['Occurrence'], labels=df['Catlib'], autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.4))

# Dessiner un cercle au milieu pour le transformer en donut
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig.gca().add_artist(centre_circle)

# Afficher le graphique
st.pyplot(fig)


st.title("Les Clubs de Sport les Plus Populaires")


s1 = st.selectbox("Sélectionnez une catégorie :", Footix['Catlib'].unique())
s2 = st.selectbox("Sélectionnez une discipline :", Footix['FedNom'].unique())

# Filtrage du DataFrame en fonction des sélections
filtered_data = Footix[(Footix['Catlib'] == s1) & (Footix['FedNom'] == s2)]

# Compter le nombre d'occurrences de chaque club par sexe
club_occurrences = filtered_data.groupby(['Club', 'Sexe']).size().reset_index(name='Occurrences')

#st.write(club_occurrences)


top_15_clubs = club_occurrences.groupby('Club')['Occurrences'].sum().nlargest(15).index
filtered_clubs = club_occurrences[club_occurrences['Club'].isin(top_15_clubs)]


color_discrete_map = {'F': 'red', 'M': 'blue'}

fig = px.bar(
    filtered_clubs,
    x='Club',
    y='Occurrences',
    color='Sexe',
    color_discrete_map=color_discrete_map,
    title=f'Clubs les plus populaires pour : {s1} et {s2}',
)


st.plotly_chart(fig)

# Grouper par "Fédération" et "Département" pour compter le nombre de joueurs
result = Footix.groupby(['Catlib', 'DepLib'])['DepLib'].count().reset_index(name='Nombre de Joueurs')
result = result.merge(resultat, on='DepLib', how='inner')
result['Coord'] = list(zip(result['longitude'], result['latitude']))


#st.write(result)


st.title('Informations sur les Départements')


s5 = st.selectbox("Sélectionnez une catégorie", result['Catlib'].unique())

# Filtrer les données en fonction de la catégorie sélectionnée
filter_data = result[result['Catlib'] == s5]


st.pydeck_chart(pdk.Deck(

    initial_view_state=pdk.ViewState(
        latitude=filter_data['latitude'].mean(),
        longitude=filter_data['longitude'].mean(),
        zoom=5,
        pitch=50,

    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=filter_data,
            opacity=0.8,
            get_position='Coord',
            get_radius=20000,
            get_color='[200, 45, 0, 190]',
            pickable=True,
            auto_highlight=True,
            elevation_scale='Nombre de Joueurs * 300',
            elevation_range=[0, 1000],
            toolip=True,
        ),
    ],

))

#st.write(filter_data)


filter_data2 = result[result['Catlib'] == s5]

# Tri des données par nombre de joueurs en ordre décroissant
filter_data2 = filter_data2.sort_values(by='Nombre de Joueurs', ascending=False)


filter_data2 = filter_data2.head(15)

# Créer le Fuel Chart
fig = px.funnel(filter_data2, x='Nombre de Joueurs', y='DepLib')

st.plotly_chart(fig)

