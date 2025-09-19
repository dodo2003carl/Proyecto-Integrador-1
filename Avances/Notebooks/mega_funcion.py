import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def recomendar_rest(id_usuario, rest, users, top_n=5):
    """
    Recomienda restaurantes para un usuario dado según sus preferencias alimenticias y estrato socioeconómico.

    Args:
        id_usuario (int or str): ID del usuario para el cual se realizarán las recomendaciones.
        rest (pd.DataFrame): DataFrame con la información de los restaurantes.
        users (pd.DataFrame): DataFrame con la información de los usuarios.
        top_n (int, optional): Número de restaurantes a recomendar. Por defecto es 5.

    Returns:
        None. Imprime los datos del usuario y muestra una tabla con los restaurantes recomendados.
    """
    mapeo = {
        'Carnes': ['chicken_wings', 'cajun', 'steak', 'bbq', 'burgers', 'chickenshop', 'argentine', 'southern', 'newamerican', 'spanish', 'kebab', 'latin', 'delis', 'comfortfood', 'caribbean', 'polish', 'venezuelan', 'sandwiches', 'tapas', 'tradamerican', 'australian', 'halal', 'mexican', 'korean', 'chinese', 'filipino', 'tacos', 'sardinian', 'modern_european', 'french', 'italian', 'pizza', 'hotpot', 'turkish', 'german', 'british', 'gastropubs', 'pastashops', 'tapasmallplates', 'diners'],
        'Mariscos': ['seafood', 'fishnchips'],
        'Vegetariano': ['vietnamese', 'noodles', 'mideastern', 'cambodian', 'asianfusion', 'thai', 'lebanese', 'indpak', 'soup', 'salad', 'himalayan', 'mediterranean', 'vegetarian', 'falafel', 'malaysian', 'singaporean', 'african'],
        'Otro': ['speakeasies', 'gourmet', 'restaurants', 'whiskeybars', 'desserts', 'icecream', 'bakeries', 'beerbar', 'cafes', 'intlgrocery', 'cocktailbars', 'coffee', 'wine_bars', 'lounges', 'beer_and_wine', 'pubs', 'venues', 'tikibars', 'breweries', 'brewpubs', 'supperclubs', 'karaoke', 'bars', 'food_court', 'brasseries'],
        'Pescado': ['sushi', 'peruvian', 'dimsum', 'japanese', 'izakaya', 'ramen', 'poke', 'hainan', 'japacurry'],
        'Vegano': ['taiwanese', 'somali', 'piadina']
    }
    import unicodedata
    usuario = users[users['id_persona'] == id_usuario].iloc[0]
    pref = usuario['preferencias_alimenticias']
    estrato = usuario['estrato_socioeconomico']
    def normalizar(texto):
        if pd.isnull(texto):
            return ""
        texto = str(texto).strip().lower()
        texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
        texto = texto.replace(" ", "")
        return texto
    pref_norm = normalizar(pref)
    categorias = []
    for key in mapeo:
        if normalizar(key) in pref_norm or pref_norm in normalizar(key):
            categorias = mapeo[key]
            break
    alias_cols = [col for col in rest.columns if col.startswith('alias_')]
    cols_filtrar = []
    for cat in categorias:
        cat_norm = normalizar(cat)
        for col in alias_cols:
            if cat_norm == normalizar(col.replace('alias_', '')):
                cols_filtrar.append(col)
    if cols_filtrar:
        mask = rest[cols_filtrar].sum(axis=1) > 0
        rest_filtrado = rest[mask].copy()
    else:
        rest_filtrado = rest.copy()
    scores = []
    for _, restaurante in rest_filtrado.iterrows():
        compatibilidad = {
            'Bajo': {'1': 0.9, '2': 0.3, '3': 0.1, '4': 0.0},
            'Medio': {'1': 0.7, '2': 0.9, '3': 0.4, '4': 0.1},
            'Alto': {'1': 0.5, '2': 0.8, '3': 0.9, '4': 0.7},
            'Muy Alto': {'1': 0.3, '2': 0.6, '3': 0.8, '4': 0.9}
        }
        price_str = str(restaurante['price_num'])
        score_precio = compatibilidad.get(estrato, {}).get(price_str, 0.0)
        score_comida = 0.9 if cols_filtrar else 0.1
        rating_norm = restaurante['rating'] / 5.0
        popularidad_norm = min(restaurante['review_count'] / 1000, 1.0)
        score_calidad = (rating_norm * 0.7) + (popularidad_norm * 0.3)
        score_total = (score_precio * 0.5) + (score_comida * 0.3) + (score_calidad * 0.2)
        scores.append({
            'restaurante_id': restaurante['id'],
            'nombre': restaurante.get('alias', 'Sin nombre'),
            'direccion': restaurante.get('address', '')
        })
    scores_df = pd.DataFrame(scores)
    top_recommendations = scores_df.head(top_n)
    print("--- Datos del usuario ---")
    print(f"Nombre: {usuario.get('nombre_completo', 'N/A')}")
    print(f"Preferencia alimenticia: {usuario.get('preferencias_alimenticias', 'N/A')}")
    print(f"Estrato socioeconómico: {usuario.get('estrato_socioeconomico', 'N/A')}")
    print(f"Gasto promedio comida: {usuario.get('promedio_gasto_comida', 'N/A')}")
    print("\nRestaurantes recomendados:")
    try:
        from IPython.display import display
        display(top_recommendations[['nombre', 'direccion']].rename(columns={'nombre': 'Nombre Restaurante', 'direccion': 'Dirección'}))
    except ImportError:
        print(top_recommendations[['nombre', 'direccion']].rename(columns={'nombre': 'Nombre Restaurante', 'Dirección': 'Dirección'}))
    # No retornamos nada para evitar doble impresión

def plot_custom(df, tipo, x=None, y=None, hue=None, order=None, palette='magma', title='', xlabel='', ylabel='', horizontal=False, bins=None, figsize=(10,6)):
    """
    Genera gráficos exploratorios personalizados utilizando seaborn/matplotlib.

    Args:
        df (pd.DataFrame): DataFrame con los datos a graficar.
        tipo (str): Tipo de gráfico ('bar', 'count', 'hist', 'box', 'scatter', 'heatmap', 'pairplot').
        x (str, optional): Nombre de la columna para el eje X.
        y (str, optional): Nombre de la columna para el eje Y.
        hue (str, optional): Variable categórica para colorear.
        order (list, optional): Orden personalizado para las categorías.
        palette (str, optional): Paleta de colores.
        title (str, optional): Título del gráfico.
        xlabel (str, optional): Etiqueta del eje X.
        ylabel (str, optional): Etiqueta del eje Y.
        horizontal (bool, optional): Si True, invierte los ejes en gráficos de barras.
        bins (int, optional): Número de bins para histogramas.
        figsize (tuple, optional): Tamaño de la figura.

    Returns:
        None. Muestra el gráfico generado.
    """

    if tipo == 'pairplot':
        pairplot_kwargs = {'data': df, 'corner': True}
        if isinstance(hue, str) and hue not in [None, '', 'None']:
            pairplot_kwargs['hue'] = hue
            if palette is not None and palette != '':
                pairplot_kwargs['palette'] = palette
        sns.pairplot(**pairplot_kwargs)
        plt.suptitle(title, y=1.02)
        plt.show()
        return
    elif tipo == 'heatmap':
        plt.figure(figsize=figsize)
        sns.heatmap(df, annot=True, cmap=palette if palette else 'coolwarm')
        plt.title(title)
        plt.tight_layout()
        plt.show()
        return
    elif tipo == 'bar':
        plt.figure(figsize=figsize)
        if horizontal:
            sns.barplot(x=x, y=y, data=df, order=order, palette=palette)
        else:
            sns.barplot(x=x, y=y, data=df, order=order, palette=palette)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()
        return
    elif tipo == 'count':
        plt.figure(figsize=figsize)
        if horizontal:
            sns.countplot(y=y, data=df, order=order, palette=palette, hue=hue)
        else:
            sns.countplot(x=x, data=df, order=order, palette=palette, hue=hue)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()
        return
    elif tipo == 'hist':
        plt.figure(figsize=figsize)
        sns.histplot(data=df, x=x, bins=bins, hue=hue, palette=palette)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()
        return
    elif tipo == 'box':
        plt.figure(figsize=figsize)
        sns.boxplot(data=df, x=x, y=y, palette=palette, hue=hue)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()
        return
    elif tipo == 'scatter':
        plt.figure(figsize=figsize)
        sns.scatterplot(data=df, x=x, y=y, hue=hue, palette=palette)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()
        return
    elif tipo == 'violin':
        plt.figure(figsize=figsize)
        sns.violinplot(data=df, x=x, y=y, palette=palette, hue=hue)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.tight_layout()
        plt.show()
        return
    else:
        raise ValueError("Tipo de gráfico no soportado")

def  imputar(df, objetivo, operacion, filtro1, filtro2, tc):
    
    print('Antes')
    
    frecuencia_tabla = df[objetivo].value_counts().sort_index()
    print(f"Tabla de frecuencia de {objetivo}:")
    print(frecuencia_tabla)
    
    if tc == 'media': 
    
        if operacion == 'nulo':
            df["media_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[~x.isnull()].mean())
            )
            df.loc[df[objetivo].isnull(), objetivo] = df.loc[df[objetivo].isnull(), "media_segmentada"]
            df.drop(columns="media_segmentada", inplace=True)
            
        elif operacion == 'negativo':
            df["media_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[x >= 0].mean())
            )
            df.loc[df[objetivo] < 0, objetivo] = df.loc[df[objetivo] < 0, "media_segmentada"]
            df.drop(columns="media_segmentada", inplace=True)
            
        elif operacion == 'cero':
            df["media_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[x != 0].mean())
            )
            df.loc[df[objetivo] == 0, objetivo] = df.loc[df[objetivo] == 0, "media_segmentada"]
            df.drop(columns="media_segmentada", inplace=True)
            df[objetivo] = df[objetivo].astype(int)
            
    elif tc == 'mediana':
    
        if operacion == 'nulo':
            df["mediana_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[~x.isnull()].median())
            )
            df.loc[df[objetivo].isnull(), objetivo] = df.loc[df[objetivo].isnull(), "mediana_segmentada"]
            df.drop(columns="mediana_segmentada", inplace=True)
            
        elif operacion == 'negativo':
            df["mediana_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[x >= 0].median())
            )
            df.loc[df[objetivo] < 0, objetivo] = df.loc[df[objetivo] < 0, "mediana_segmentada"]
            df.drop(columns="mediana_segmentada", inplace=True)
            
        elif operacion == 'cero':
            df["mediana_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[x != 0].median())
            )
            df.loc[df[objetivo] == 0, objetivo] = df.loc[df[objetivo] == 0, "mediana_segmentada"]
            df.drop(columns="mediana_segmentada", inplace=True)
            df[objetivo] = df[objetivo].astype(int)
            
    elif tc == 'moda':
    
        if operacion == 'nulo':
            df["moda_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[~x.isnull()].mode()[0] if not x[~x.isnull()].mode().empty else np.nan)
            )
            df.loc[df[objetivo].isnull(), objetivo] = df.loc[df[objetivo].isnull(), "moda_segmentada"]
            df.drop(columns="moda_segmentada", inplace=True)
            
        elif operacion == 'negativo':
            df["moda_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[x >= 0].mode()[0] if not x[x >= 0].mode().empty else np.nan)
            )
            df.loc[df[objetivo] < 0, objetivo] = df.loc[df[objetivo] < 0, "moda_segmentada"]
            df.drop(columns="moda_segmentada", inplace=True)
            
            
        elif operacion == 'cero':
            df["moda_segmentada"] = (
                df.groupby([filtro1, filtro2])[objetivo]
                .transform(lambda x: x[x != 0].mode()[0] if not x[x != 0].mode().empty else np.nan)
            )
            df.loc[df[objetivo] == 0, objetivo] = df.loc[df[objetivo] == 0, "moda_segmentada"]
            df.drop(columns="moda_segmentada", inplace=True)
              
            
            
    print(f"Imputación de {objetivo} con {operacion} por {filtro1} y {filtro2} usando {tc} completada.")
    
    print('----'*5)
    print('Después')
    frecuencia_tabla = df[objetivo].value_counts().sort_index()
    
    print(f"Tabla de frecuencia de {objetivo}:")
    
    print(frecuencia_tabla)
    return df