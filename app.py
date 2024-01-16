import folium
import geopandas
import pandas as pd
import streamlit as st
from shapely.geometry import Point
from streamlit_folium import st_folium
from streamlit_star_rating import st_star_rating
from folium.plugins import Draw
from streamlit_carousel import carousel
from streamlit_tags import st_tags, st_tags_sidebar
import requests
from bs4 import BeautifulSoup
import aspose.words as aw

def image_scraper(place_id):
    print('image=', place_id)
    if place_id == None:
        return [dict(
        title="Slide 1",
        text="A tree in the savannah",
        interval=None,
        img="https://img.freepik.com/free-photo/wide-angle-shot-single-tree-growing-clouded-sky-during-sunset-surrounded-by-grass_181624-22807.jpg?w=1380&t=st=1688825493~exp=1688826093~hmac=cb486d2646b48acbd5a49a32b02bda8330ad7f8a0d53880ce2da471a45ad08a4",)]
        
    else:
        url = f'https://park4night.com/de/place/{place_id}'
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"}
        page = requests.get(url, headers=headers)
        soup1 = BeautifulSoup(page.text, features='lxml')
        result = soup1.find(class_="place-header")
        images = result.find_all('img')
        img_list = []
        for link in images:
            if link['alt'] == 'Description':
                img_list.append(dict(
                    title=" ",
                    text="",
                    interval=None,
                    img=f"{link['src']}",
                ))
        return img_list


def init_map(center=(50.8715, 9.7116), zoom_start=6, map_type="OpenStreetMap"):
    return folium.Map(location=center, zoom_start=zoom_start, tiles=map_type)

def layer(m):
    folium.TileLayer('CartoDB Positron', attr='CartoDB Positron').add_to(m)
    folium.TileLayer(tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',name='Earth', attr='My Data Attribution').add_to(m)
    Draw(export=True).add_to(m)
    folium.LayerControl().add_to(m)
    return m

def create_point_map(df):
    # Cleaning
    df[['latitude', 'longitude']] = df[['latitude', 'longitude']].apply(pd.to_numeric, errors='coerce')
    # Convert PandasDataFrame to GeoDataFrame
    df['coordinates'] = df[['latitude', 'longitude']].values.tolist()
    df['coordinates'] = df['coordinates'].apply(Point)
    df = geopandas.GeoDataFrame(df, geometry='coordinates')
    df = df.dropna(subset=['latitude', 'longitude', 'coordinates'])
    return df


def plot_from_df(df):
    fg = folium.FeatureGroup(name="places")
    df = create_point_map(df)
    for i, row in df.iterrows():
        icon = folium.features.CustomIcon(IM_CONSTANTS[row.place_type_id])
        fg.add_child(folium.Marker([row.latitude, row.longitude],
                      tooltip=f'''ID: {row.place_id}<br>
                      Rating: {row.rating}''',
                      popup= f"""<a href=https://park4night.com/de/place/{row.place_id} target=_blank rel=noopener noreferrer>Park4Night</a>
                      <a href=https://www.google.com/maps/dir/?api=1&destination={row.latitude},{row.longitude} target=_blank rel=noopener noreferrer>Reiseroute</a>
                      """,
                      icon=icon))
     
    return fg

@st.cache_data(ttl=3600)
def load_description(place_id):
    conn = st.connection('mysql', type='sql')
    query = f"""SELECT 
                place_title,
                place_description
                FROM place_description
                where place_id = '{place_id}'"""
    df_description = conn.query(query, ttl=600)
    return df_description


@st.cache_data(ttl=3600)
def load_comments(place_id):
    conn = st.connection('mysql', type='sql')
    query = f"""SELECT 
                comments,
                comment_date,
                compound
                FROM comments c
                inner join sentiment_analysis sa on c.comment_id = sa.comment_id
                where c.place_id = '{place_id}'"""
    df_comments = conn.query(query, ttl=600)
    return df_comments

@st.cache_data(ttl=3600)
def load_place_services(place_id):
    conn = st.connection('mysql', type='sql')
    query = f"""SELECT service_id 
                FROM  place_services
                where place_id = '{place_id}'"""
    df_place_services = conn.query(query, ttl=600)
    doc = aw.Document()
    builder = aw.DocumentBuilder(doc)
    df_place_services = [IM_CONSTANTS[svg] for svg in df_place_services['service_id'].values.tolist()]
    df_place_services = [builder.insert_image(svg).image_data.save("Output.png") for svg in df_place_services]
    return df_place_services

@st.cache_data(ttl=3600)
def query_services(service_id):
    if len(service_id) == 0:
        query = '#'
        return query
    else:
        query = ''
        for index in range(0,len(service_id)):
            if index == 0:
                query = (f"and (p.place_id in (select {service_id[0]}.place_id from (select * from place_services where service_id = '{service_id[0]}') {service_id[0]}\n")
            else:
                query = query + (f"inner join (select * from place_services where service_id = '{service_id[index]}') {service_id[index]} on {service_id[0]}.place_id = {service_id[index]}.place_id\n")
        query = query + "))"
        return query 
    
@st.cache_data(ttl=3600)
def query_comment_tag(tag_comment):
    if len(tag_comment) == 0:
        query = '#'
        return query
    else:
        query = ''
        for index in range(0,len(tag_comment)):
            if index == 0:
                query = (f"and (p.place_id not in (select c1.place_id from (select * from comments where (comments like '%{tag_comment[index]}%'")
            else:
                query = query + (f" or comments like '%{tag_comment[index]}%'")
        query = query +"))c1))"
        return query 
    
@st.cache_data(ttl=3600)
def query_comment_tag_in(tag_comment_in):
    if len(tag_comment_in) == 0:
        query = '#'
        return query
    else:
        query = ''
        for index in range(0,len(tag_comment_in)):
            if index == 0:
                query = (f"and (p.place_id in (select c2.place_id from (select * from comments where (comments like '%{tag_comment_in[index]}%'")
            else:
                query = query + (f" and comments like '%{tag_comment_in[index]}%'")
        query = query +"))c2))"
        return query 
    
@st.cache_data(ttl=3600)
def load_country():
    conn = st.connection('mysql', type='sql')
    query = """SELECT distinct
                country
                FROM place_location"""
    df_countries = conn.query(query, ttl=600)
    return df_countries

@st.cache_data(ttl=3600)
def load_place_type():
    conn = st.connection('mysql', type='sql')
    query = """SELECT *
                FROM place_type"""
    df_place_type = conn.query(query, ttl=600)
    return df_place_type

@st.cache_data(ttl=3600)
def load_services():
    conn = st.connection('mysql', type='sql')
    query = """SELECT * FROM services
                        where service_id not in ('s10', 's11', 's12', 's18', 's2', 's20', 's21', 's23', 's26','s27','s28','s29','s9')"""
    df_services = conn.query(query, ttl=600)
    return df_services



@st.cache_data(ttl=3600)
def load_df(country=['Germany'], place_type_id=['pt0'],limit=100,rating=5,service_id='#', count_rating=0, tag_comment='#',tag_comment_in='#'):
    conn = st.connection('mysql', type='sql')
    if limit == 10000:
        limit = '#'
    else:
        limit = f"limit {limit}"
    query = f"""SELECT 
                p.place_id,
                rating,
                place_type_id,
                longitude,
                latitude,
                country
                FROM place p 
                inner join place_location pl on p.place_id = pl.place_id
                where ({len(country)}=0 or country in ({', '.join(["'"+i+"'" for i in country+['']])}))
                and ({len(place_type_id)}=0 or place_type_id in ({', '.join(["'"+i+"'" for i in place_type_id+['']])}))
                and (rating >= {rating})
                and (count_ratings >= {count_rating})
                {service_id}
                {tag_comment}
                {tag_comment_in}
                order by p.rating desc
                {limit}
                """

    df = conn.query(query, ttl=600)
    return df


FACT_BACKGROUND = """
                    <div style="width: 100%;">
                        <div style="
                                    background-color: #ECECEC;
                                    border: 1px solid #ECECEC;
                                    padding: 1.5% 1% 1.5% 3.5%;
                                    border-radius: 10px;
                                    width: 100%;
                                    color: white;
                                    white-space: nowrap;
                                    ">
                          <p style="font-size:20px; color: black;">{}</p>
                          <p style="font-size:33px; line-height: 0.5; text-indent: 10px;""><img src="{}" alt="Example Image" style="vertical-align: middle;  width:{}px;">  {} &emsp; &emsp; </p>
                        </div>
                    </div>
                    """

TITLE = 'Park4Night'

IM_CONSTANTS = {'LOGO': 'https://leisuregraphics.co.uk/cdn/shop/products/MountainsTwo-layup-cut_1024x1024@2x.jpg',
                'pt0': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_p@4x.png',
                'pt1': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_pj@4x.png',
                'pt2': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_acc_g@4x.png',
                'pt3': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_apn@4x.png',
                'pt4': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_pn@4x.png',
                'pt5': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_c@4x.png',
                'pt6': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_ass@4x.png',
                'pt7': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_pss@4x.png',
                'pt8': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_acc_p@4x.png',
                'pt9': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_acc_pr@4x.png',
                'pt10': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_ar@4x.png',
                'pt11': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_f@4x.png',
                'pt12': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_or@4x.png',
                'pt13': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_ds@4x.png',
                'pt14': 'https://cdn6.park4night.com/images/bitmap/icons/pins/pins_ep@4x.png',
                's0': 'https://cdn6.park4night.com/images/svg/icons/services/service_poubelle.svg',
                's1': 'https://cdn6.park4night.com/images/svg/icons/services/service_animaux.svg',
                's3': 'https://cdn6.park4night.com/images/svg/icons/services/service_point_eau.svg',
                's4': 'https://cdn6.park4night.com/images/svg/icons/services/service_eau_noire.svg',
                's5': 'https://cdn6.park4night.com/images/svg/icons/services/service_eau_usee.svg',
                's6': 'https://cdn6.park4night.com/images/svg/icons/services/service_wc_public.svg',
                's7': 'https://cdn6.park4night.com/images/svg/icons/services/service_boulangerie.svg',
                's8': 'https://cdn6.park4night.com/images/svg/icons/services/service_piscine.svg',
                's13': 'https://cdn6.park4night.com/images/svg/icons/services/service_douche.svg',
                's14': 'https://cdn6.park4night.com/images/svg/icons/services/service_electricite.svg',
                's15': 'https://cdn6.park4night.com/images/svg/icons/services/service_wifi.svg',
                's16': 'https://cdn6.park4night.com/images/svg/icons/services/service_laverie.svg',
                's17': 'https://cdn6.park4night.com/images/svg/icons/services/service_donnees_mobile.svg',
                's19': 'https://cdn6.park4night.com/images/svg/icons/services/service_caravaneige.svg',
                's22': 'https://cdn6.park4night.com/images/svg/icons/services/service_lavage.svg',
                's24': 'https://cdn6.park4night.com/images/svg/icons/services/service_gaz.svg',
                's25': 'https://cdn6.park4night.com/images/svg/icons/services/service_gpl.svg',
                's10': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_eaux_vives.svg',
                's11': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_baignade.svg',
                's12': 'https://www.svgrepo.com/show/440750/fellow-question-none.svg',
                's18': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_vtt.svg',
                's2': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_visites.svg',
                's20': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_peche.svg',
                's21': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_jeux_enfants.svg',
                's23': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_windsurf.svg',
                's26': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_escalade.svg',
                's27': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_point_de_vue.svg',
                's28': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_peche_pied.svg',
                's29': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_moto.svg',
                's9': 'https://cdn6.park4night.com/images/svg/icons/activities/activity_rando.svg'
                }


SELECTED_MAP = {'Monkey': 'pt0', 'Banana': 'pt1'}



 
#@st.cache_data
#@st.cache_resource
@st.cache_data
def load_map(country,place_type_id, limit,rating,service_id, count_rating, tag_comment,tag_comment_in):
    # Load the map
    m = init_map()  # init
    m = layer(m)

    df = load_df(country,place_type_id, limit,rating,service_id, count_rating, tag_comment,tag_comment_in)  # load data
    fg = plot_from_df(df)  # plot points

    return m, fg


def main():
    # format page
    st.set_page_config(TITLE, page_icon=IM_CONSTANTS['LOGO'], layout='wide')


    st.title('Park4Night')
    col1, col2 = st.columns([0.7, 0.3] )  

    df_countries = load_country()
    df_place_type = load_place_type()
    df_services = load_services()
    with col2:
        rating = st_star_rating("Minimum Rating", maxValue=5, defaultValue=3, key="rating")
        count_rating = st.slider("Minimum Anzahl Bewertungen", 0, 10, value=1)
        
        limit = st.slider("Limit Suchergebnisse - sortiert nach rating:", 1, 10000, value=100)
        country = st.multiselect("Welche Länder interessieren dich?",df_countries, 'Germany')
        place_type_id = st.multiselect("Ort/Platzarten filtern",df_place_type['place_type_name'], 'Parkplatz Tag und Nacht')
        place_type_id = df_place_type[df_place_type['place_type_name'].isin(place_type_id)]['place_type_id'].values.tolist()

        service_id = st.multiselect("Services filtern",df_services['service_name'], 'Abfalleimer')
        service_id = df_services[df_services['service_name'].isin(service_id)]['service_id'].values.tolist()
        service_id = query_services(service_id)
        tag_comment = st_tags(
        label='Enter Keywords nicht in Kommentaren:',
        text='Press enter to add more', value=['einbruch', 'mücken'],
        suggestions=['polizei', 'diebstahl'],
        maxtags = 10,
        key='tag_out')   
        tag_comment = query_comment_tag(tag_comment)
        
        tag_comment_in = st_tags(
        label='Enter Keywords in Kommentaren:',
        text='Press enter to add more', value=['klettersteig'],
        suggestions=['aussicht', 'freundlich'],
        maxtags = 10,
        key='tag_in')  
        tag_comment_in = query_comment_tag_in(tag_comment_in)
        
        

    if "output" not in st.session_state:       
        st.session_state.output = None

    m, fg = load_map(country,place_type_id, limit,rating, service_id, count_rating, tag_comment,tag_comment_in)
            # init stored values
    with col1:
        level1_map_data = st_folium(m, feature_group_to_add=fg, returned_objects=["last_object_clicked_tooltip"], height=700, width=1000) 
        st.session_state.output = level1_map_data
        
        if "output" in st.session_state:       
            #st.write(st.session_state.output)
            place_id = st.session_state.output["last_object_clicked_tooltip"].split()[1]
            place_rating = st.session_state.output["last_object_clicked_tooltip"].split()[-1]
            
            test_items = image_scraper(place_id)
            place_title = load_description(place_id)
            st.title(place_title['place_title'][0])
            st.write(place_title['place_description'][0])
            df_place_services = load_place_services(place_id)
            df_comments = load_comments(place_id)
            st.image(df_place_services)
            stars = st_star_rating('', 5, place_rating,read_only=True)
            st.write(f"Rating: {stars}")
            st.write(f"Sentiment Score: {str(round(df_comments['compound'].mean(), 2))}")
            carousel(items=test_items, height=500, width=0.9)
            
            df_comments = load_comments(place_id)
            st.dataframe(df_comments)
            
    


if __name__ == "__main__":
    main()
