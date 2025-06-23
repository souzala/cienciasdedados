import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd

# -----------------------------
# 🌟 Configuração da página
# -----------------------------
st.set_page_config(page_title="📊 Censo Escolar 2022", layout="wide")
st.markdown("## 🎓 Dashboard - Censo Escolar 2022")
st.markdown("Visualize e explore as principais características das escolas brasileiras com base nos microdados do INEP.")

# -----------------------------
# 📁 Carregando os dados
# -----------------------------
url = "https://drive.google.com/file/d/18sfTL_N1xRqunmsO77aAt1wfI0qbz3I5/view?usp=sharing"
df = pd.read_csv(url, sep=';', encoding='latin1')

# Mapeando variáveis
df['Dependência'] = df['TP_DEPENDENCIA'].map({1: 'Federal', 2: 'Estadual', 3: 'Municipal', 4: 'Privada'})
df['Localização'] = df['TP_LOCALIZACAO'].map({1: 'Urbana', 2: 'Rural'})
df['Energia'] = df['IN_ENERGIA_RENOVAVEL'].map({1: 'Com Renovável', 0: 'Sem Renovável'})

# -----------------------------
# 🧱 Barra lateral de filtros
# -----------------------------
st.sidebar.header("🔍 Filtros")
tipo_dependencia = st.sidebar.multiselect(
    "Tipo de Escola",
    options=df['Dependência'].unique(),
    default=df['Dependência'].unique()
)

# Aplicando o filtro
df_filtro = df[df['Dependência'].isin(tipo_dependencia)]

# -----------------------------
# 📂 Abas de visualização
# -----------------------------
tabs = st.tabs([
    "📍 Dados gerais",
    "🗺️ Escolas por Região",
    "♻️ Sustentabilidade",
])

# -----------------------------
# 📍 Aba 1: Dados gerais
# -----------------------------
with tabs[0]:
    st.subheader("📍 Dados gerais")

    local = df_filtro['Localização'].value_counts().reset_index()
    local.columns = ['Localização', 'Quantidade']
    fig1 = px.pie(local, values='Quantidade', names='Localização', title='📍 Localização das Escolas')
    st.plotly_chart(fig1, use_container_width=True)

    dep = df_filtro['Dependência'].value_counts().reset_index()
    dep.columns = ['Dependência', 'Quantidade']
    fig3 = px.bar(dep, x='Dependência', y='Quantidade', color='Dependência',
                  title='🏩 Tipo de Dependência Administrativa')
    st.plotly_chart(fig3, use_container_width=True)

    raca_cols = [
        'QT_MAT_BAS_ND', 'QT_MAT_BAS_BRANCA', 'QT_MAT_BAS_PRETA',
        'QT_MAT_BAS_PARDA', 'QT_MAT_BAS_AMARELA', 'QT_MAT_BAS_INDIGENA'
    ]

    # Verifica se as colunas estão presentes
    colunas_existentes = [col for col in raca_cols if col in df.columns]
    if len(colunas_existentes) == len(raca_cols):
        # Soma total por grupo
        totais_raca = df[raca_cols].sum().sort_values(ascending=True)

        nomes_legiveis = {
            'QT_MAT_BAS_ND': 'Não declarado',
            'QT_MAT_BAS_BRANCA': 'Branca',
            'QT_MAT_BAS_PRETA': 'Preta',
            'QT_MAT_BAS_PARDA': 'Parda',
            'QT_MAT_BAS_AMARELA': 'Amarela',
            'QT_MAT_BAS_INDIGENA': 'Indígena'
        }

        df_raca = pd.DataFrame({
            'Cor/Raça': [nomes_legiveis[col] for col in totais_raca.index],
            'Quantidade': totais_raca.values
        })

        fig_raca = px.bar(
            df_raca,
            x='Quantidade',
            y='Cor/Raça',
            orientation='h',
            text='Quantidade',
            color='Cor/Raça',
            color_discrete_sequence=px.colors.sequential.Greens_r,
            title='🌈 Matrículas na Educação Básica por Cor/Raça'
        )

        fig_raca.update_layout(
            xaxis_title='Quantidade de Matrículas',
            yaxis_title='Cor/Raça',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(categoryorder='total ascending')
        )

        fig_raca.update_traces(textposition='outside')

        st.plotly_chart(fig_raca, use_container_width=True)
    else:
        st.warning("⚠️ Nem todas as colunas de cor/raça estão disponíveis no DataFrame.")


# -----------------------------
# 🗺️ Aba 1: Escolas por Região (Mapa)
# -----------------------------
import folium
from streamlit_folium import folium_static

with tabs[1]:
    st.subheader("🗺️ Distribuição de Escolas por Região no Mapa (com fundo real)")

    coordenadas_regioes = {
        "NORTE": (-2.5, -60.0),
        "NORDESTE": (-8.5, -38.5),
        "CENTRO-OESTE": (-15.5, -56.1),
        "SUDESTE": (-20.5, -43.5),
        "SUL": (-27.5, -50.5)
    }

    # GeoJSON com as regiões e nomes adicionados no "properties"
    regioes_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "NORDESTE"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-40.67903904165121, -7.45422727545693],
                            [-36.2482829151121, -5.059977128629697],
                            [-46.08278962216633, -1.1681709934621267],
                            [-48.48087055394922, -5.356846540247204],
                            [-45.77920049877491, -10.234002439909986],
                            [-45.89924469017694, -15.07994933079884],
                            [-39.21321675849694, -16.328293321510742],
                            [-36.522815100240734, -10.403407729700646],
                            [-35.27641880295877, -9.298407351776618],
                            [-34.79177225438133, -7.741517186520468],
                            [-34.85057688217205, -6.95466776545193],
                            [-35.37953855620711, -5.284216318685651],
                            [-36.27472482919853, -5.086640614104013],
                            [-40.67903904165121, -7.45422727545693]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "NORTE"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-57.47240113250581, -4.953633058372716],
                            [-46.10428011709209, -1.0820241870264624],
                            [-49.1984364350603, -0.068605637657285],
                            [-50.50756531138589, -0.1902638347461192],
                            [-49.85515473114501, 1.5036431563006403],
                            [-51.00802963931278, 3.19287017881922],
                            [-51.62795502289225, 4.198230591559636],
                            [-52.93241238529558, 2.1234626448792397],
                            [-54.33872358907553, 2.29745105887946],
                            [-54.892379099875754, 2.3193151748452863],
                            [-56.13605971032315, 2.44240861970421],
                            [-57.24394327683311, 1.9171466343266133],
                            [-59.00079139243037, 1.3149689099185053],
                            [-59.901656934596545, 2.360813715446369],
                            [-59.74662661896875, 4.023944653890666],
                            [-60.161960200076834, 5.096262655419551],
                            [-61.19911050584933, 4.573463276331736],
                            [-62.810002399316915, 4.053615823982042],
                            [-63.706497127276435, 3.81021696444553],
                            [-64.69729370748203, 4.278213354265404],
                            [-63.794809134092645, 2.456368575031206],
                            [-64.41653389812777, 1.3181097603574585],
                            [-66.00323687139162, 1.0204984425151054],
                            [-67.04252335370794, 1.6102027460764958],
                            [-68.41288783950941, 1.918404750634025],
                            [-69.88587947203096, 1.8399980639244404],
                            [-69.09774404914425, 0.7084494418087246],
                            [-70.04742673515625, 0.21491353285425419],
                            [-69.88463420977709, -4.367706335093715],
                            [-72.22592043177715, -4.563950770883878],
                            [-73.05639708671072, -5.686490583946835],
                            [-73.8598731034134, -7.0877280035153944],
                            [-73.03247809423239, -8.985955775368879],
                            [-72.34082884108614, -9.541622345928772],
                            [-71.93951920392979, -10.080064296146702],
                            [-70.66730416876368, -9.672282506973104],
                            [-70.45947677683236, -11.034938973392599],
                            [-67.50379648419378, -10.853515117109694],
                            [-65.7579696189404, -9.835809854549893],
                            [-65.17064264421998, -11.777180051035572],
                            [-60.32396139917719, -13.79421335344118],
                            [-59.971289563185906, -12.511749319059305],
                            [-60.033513303885286, -11.299043758353292],
                            [-61.534486356717565, -10.852717544488527],
                            [-61.51845083897163, -9.095763297088126],
                            [-61.10282889058787, -8.623567515506423],
                            [-58.45674020124224, -8.74779602097567],
                            [-58.304147272088954, -7.4993962312749005],
                            [-57.45070890005604, -8.708377734048568],
                            [-56.41128733559711, -9.378042625948808],
                            [-50.26904222125236, -9.778763983236757],
                            [-50.45914443519098, -12.549860355626663],
                            [-48.95214804506858, -12.847316372467773],
                            [-47.2519610741725, -13.383283629200406],
                            [-46.04331850549934, -12.90354819585373],
                            [-45.84384126948092, -10.590379596762162],
                            [-46.461017195715925, -9.299946942725427],
                            [-48.43505280778791, -5.375558728402922],
                            [-46.10491879156265, -1.1434936988622013],
                            [-57.47240113250581, -4.953633058372716]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "SUL"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-51.732054539886576, -27.25298385888113],
                            [-48.084178171590736, -25.371785160105716],
                            [-48.86091244029578, -24.667157722138967],
                            [-49.24662687123171, -24.312086312297367],
                            [-49.585978639463036, -23.600224502927304],
                            [-49.92342528376906, -22.88325116624314],
                            [-51.20413440940612, -22.699417383521123],
                            [-52.92499461792676, -22.561192576050004],
                            [-53.808273513571805, -23.08135820092636],
                            [-54.27403578991772, -23.935889644360287],
                            [-54.65572548944121, -25.66177747584453],
                            [-53.937629884005105, -25.61416611275709],
                            [-53.5186471726505, -26.260497693235813],
                            [-53.68762342516055, -27.04141047863707],
                            [-54.8467424711838, -27.51043988812009],
                            [-55.57591077867356, -28.074232357007077],
                            [-56.93903857971763, -29.613275951407324],
                            [-57.68263610175133, -30.186598623999792],
                            [-57.196268797663535, -30.207680593971553],
                            [-56.66526842855541, -30.229380625339864],
                            [-53.02412870290283, -32.85509845407443],
                            [-53.407080224741236, -33.80653056071963],
                            [-50.233079397013455, -30.276989854265857],
                            [-48.75911574284595, -28.40290148011389],
                            [-48.11846540688896, -25.32605533559689],
                            [-51.732054539886576, -27.25298385888113]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "CENTRO-OESTE"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-52.946822393396644, -15.959627079117396],
                            [-60.30353944378476, -13.881180205468894],
                            [-60.54007948625804, -15.186319384504415],
                            [-60.1750452411232, -16.298624312883007],
                            [-58.229326111215926, -16.237427023943155],
                            [-58.45984514770612, -17.116471091815583],
                            [-57.52148914753491, -18.04834779789323],
                            [-58.01054790659083, -19.80280987647491],
                            [-57.92670871875836, -22.085106537222615],
                            [-56.89036800873954, -22.289099047242786],
                            [-55.75886923135961, -22.356257771670116],
                            [-55.38045417312239, -24.119838078459992],
                            [-54.283526576922924, -23.950015248833637],
                            [-50.83639773272537, -19.910187347091394],
                            [-50.83168627953353, -19.43124688424372],
                            [-50.274208805177096, -18.695105832801403],
                            [-49.40293220895032, -18.566491967113535],
                            [-48.2583094192826, -18.389137833886352],
                            [-47.20602568778659, -18.11889959420452],
                            [-47.262303096496055, -17.205835528128688],
                            [-47.26862218840415, -16.552153897062468],
                            [-47.545070855955174, -16.119126593264],
                            [-47.13696227040046, -15.982328557403676],
                            [-46.86621726087995, -15.71518940121507],
                            [-46.00945543456771, -14.684890045051702],
                            [-45.83700029196038, -12.762441018290644],
                            [-47.150931104671145, -13.422940681108003],
                            [-50.34794892418279, -12.680656026688169],
                            [-50.349857233667194, -9.931266367045865],
                            [-56.3661570129501, -9.488580924176048],
                            [-58.28867485908005, -7.604903663192715],
                            [-58.42008288951686, -8.867242873611389],
                            [-61.126237718731204, -8.608440000749553],
                            [-61.557364252092924, -9.062806488975568],
                            [-61.46795570849167, -10.887005151650087],
                            [-59.977135906947325, -11.303862821108098],
                            [-59.91974153117944, -12.748088604237424],
                            [-60.338701946548454, -13.877199153177614],
                            [-52.946822393396644, -15.959627079117396]
                        ]
                    ]
                }
            },
            {
                "type": "Feature",
                "properties": {"name": "SUDESTE"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-44.27763435898399, -19.70092578253609],
                            [-45.94595103094261, -14.894259925311005],
                            [-46.51275529597356, -15.214725638741058],
                            [-47.52699472418425, -16.13412942712469],
                            [-47.08883316450084, -18.168339743033826],
                            [-49.588748000471725, -18.750591321395277],
                            [-50.270556726216455, -18.644973153953913],
                            [-50.87776175090255, -19.436745991467916],
                            [-50.879082699141264, -20.011382389083053],
                            [-52.905056432171165, -22.57256251715897],
                            [-49.95550323291633, -22.803991635568707],
                            [-49.24092662478182, -24.34350764695553],
                            [-48.03402849071307, -25.415475359939734],
                            [-46.20480880805556, -24.08578787324697],
                            [-44.378957375263184, -23.025951678560034],
                            [-41.87554235496893, -22.96175743967295],
                            [-40.96292038760146, -21.895290357358604],
                            [-40.10510869176662, -19.8299862885401],
                            [-39.535250628675186, -18.08919440006801],
                            [-38.984664304477974, -16.28252508086905],
                            [-41.3882598963217, -16.0027536931656],
                            [-45.9062864215345, -15.116717845969603],
                            [-44.27763435898399, -19.70092578253609]
                        ]
                    ]
                }
            }
        ]
    }

    df_filtro['NO_REGIAO'] = df_filtro['NO_REGIAO'].astype(str).str.strip().str.upper()
    escolas_por_regiao = df_filtro['NO_REGIAO'].value_counts().reset_index()
    escolas_por_regiao.columns = ['Região', 'Quantidade']

    mapa = folium.Map(location=[-14.5, -52.5], zoom_start=4)

    # Adiciona polígonos para todas as regiões
    folium.GeoJson(
        regioes_geojson,
        name="Regiões do Brasil",
        style_function=lambda feature: {
            'fillColor': {
                "NORTE": "#fde091",
                "NORDESTE": "#9c4002",
                "SUL": "#e7b44c",
                "CENTRO-OESTE": "#fff7cd",
                "SUDESTE": "#b96f00"
            }[feature['properties']['name']],
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.3,
        },
        tooltip=folium.GeoJsonTooltip(fields=["name"], aliases=["Região:"])
    ).add_to(mapa)
    for i, row in escolas_por_regiao.iterrows():
            regiao = row['Região']
            qtd = row['Quantidade']
            lat, lon = coordenadas_regioes.get(regiao, (None, None))
            if lat and lon:
                folium.Marker(
                    location=[lat, lon],
                    popup=f"<b>{regiao}</b><br>Escolas: {qtd}",
                    icon=folium.Icon(color='darkblue', icon='school', prefix='fa')
                ).add_to(mapa)

    folium_static(mapa, width=700, height=500)



# -----------------------------
# ⚡ Aba 2: Sustentabilidade
# -----------------------------
with tabs[2]:
    st.subheader("♻️ Sustentabilidade")

    energia = df_filtro['Energia'].value_counts().reset_index()
    energia.columns = ['Energia', 'Quantidade']
    fig2 = px.pie(energia, values='Quantidade', names='Energia', title='⚡ Uso de Energia Renovável')
    st.plotly_chart(fig2, use_container_width=True)

    renovavel_por_tipo = df[df['Energia'] == 'Com Renovável']['Dependência'].value_counts().sort_values(ascending=True)

    df_energia_tipo = renovavel_por_tipo.reset_index()
    df_energia_tipo.columns = ['Tipo de Escola', 'Quantidade']

    fig5 = px.bar(
        df_energia_tipo,
        x='Quantidade',
        y='Tipo de Escola',
        orientation='h',
        text='Quantidade',
        color='Tipo de Escola',
        color_discrete_sequence=px.colors.sequential.Greens_r,
        title='✨ Escolas com Energia Renovável por Tipo de Dependência'
    )

    fig5.update_layout(
        yaxis=dict(categoryorder='total ascending'),
        xaxis_title='Quantidade de Escolas',
        yaxis_title='Tipo de Escola',
        plot_bgcolor='rgba(0,0,0,0)',
        title_x=0.3
    )

    fig5.update_traces(textposition='outside')

    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("🚰 Abastecimento de Água nas Escolas")
    agua_cols = [
        'IN_AGUA_POTAVEL', 'IN_AGUA_REDE_PUBLICA', 'IN_AGUA_POCO_ARTESIANO',
        'IN_AGUA_CACIMBA', 'IN_AGUA_FONTE_RIO', 'IN_AGUA_INEXISTENTE'
    ]
    agua_legenda = [
        'Água Potável', 'Rede Pública', 'Poço Artesiano',
        'Cacimba', 'Fonte/Rio', 'Sem Abastecimento'
    ]

    agua_data = df_filtro[agua_cols].sum()
    fig4 = px.bar(
        x=agua_legenda,
        y=agua_data,
        title="🚰 Distribuição por Tipo de Abastecimento de Água",
        labels={'x': 'Tipo de Abastecimento', 'y': 'Quantidade de Escolas'},
        color=agua_legenda,
        color_discrete_sequence=px.colors.sequential.Greens_r
    )
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("♻️ Tratamento de Resíduos nas Escolas")

    # Selecionar colunas relevantes
    lixo_cols = [
        'IN_TRATAMENTO_LIXO_SEPARACAO',
        'IN_TRATAMENTO_LIXO_REUTILIZA',
        'IN_TRATAMENTO_LIXO_RECICLAGEM',
        'IN_TRATAMENTO_LIXO_INEXISTENTE'
    ]

    # Verificar se as colunas existem
    if all(col in df_filtro.columns for col in lixo_cols):
        # Soma total por tipo
        totais_lixo = df_filtro[lixo_cols].sum().sort_values()

        # Nome legível para o eixo
        nomes_lixo = {
            'IN_TRATAMENTO_LIXO_SEPARACAO': 'Separação',
            'IN_TRATAMENTO_LIXO_REUTILIZA': 'Reutilização',
            'IN_TRATAMENTO_LIXO_RECICLAGEM': 'Reciclagem',
            'IN_TRATAMENTO_LIXO_INEXISTENTE': 'Sem Tratamento'
        }

        df_lixo = pd.DataFrame({
            'Tipo': [nomes_lixo[c] for c in totais_lixo.index],
            'Quantidade': totais_lixo.values
        })

        fig_lixo = px.bar(
            df_lixo,
            x='Quantidade',
            y='Tipo',
            orientation='h',
            color='Tipo',
            text='Quantidade',
            title='♻️ Tipos de Tratamento de Lixo nas Escolas',
            color_discrete_sequence=px.colors.sequential.Greens_r
        )

        fig_lixo.update_layout(
            yaxis_title='Tipo de Tratamento',
            xaxis_title='Quantidade de Escolas',
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(categoryorder='total ascending')
        )

        fig_lixo.update_traces(textposition='outside')

        st.plotly_chart(fig_lixo, use_container_width=True)
    else:
        st.warning("Colunas de tratamento de lixo não encontradas no DataFrame.")


    st.subheader("🔄 Correlação entre Abastecimento de Água, Lixo, Energia Renovável e Tipo de Escola")

    # Definir colunas de interesse
    colunas_corr = [
        'IN_ENERGIA_RENOVAVEL',
        'TP_DEPENDENCIA',
        'IN_AGUA_POTAVEL', 'IN_AGUA_REDE_PUBLICA', 'IN_AGUA_POCO_ARTESIANO',
        'IN_AGUA_CACIMBA', 'IN_AGUA_FONTE_RIO', 'IN_AGUA_INEXISTENTE',
        'IN_TRATAMENTO_LIXO_SEPARACAO', 'IN_TRATAMENTO_LIXO_REUTILIZA',
        'IN_TRATAMENTO_LIXO_RECICLAGEM', 'IN_TRATAMENTO_LIXO_INEXISTENTE'
    ]

    # Verifica se todas as colunas estão presentes
    colunas_existentes = [col for col in colunas_corr if col in df.columns]

    if len(colunas_existentes) >= 2:
        # Calcular matriz de correlação
        matriz_corr = df[colunas_existentes].corr(numeric_only=True).round(2)

        # Criar heatmap com Plotly
        fig_corr = px.imshow(
            matriz_corr,
            text_auto=True,
            color_continuous_scale='YlGnBu',
            title='🔄 Correlação: Água, Lixo, Energia Renovável e Tipo de Escola',
            aspect='auto'
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("⚠️ Algumas colunas esperadas não foram encontradas no DataFrame.")


    

agua_data = df_filtro[agua_cols].sum()
fig4 = px.bar(x=agua_legenda, y=agua_data, title="Abastecimento de Água nas Escolas")
st.plotly_chart(fig4, use_container_width=True)
