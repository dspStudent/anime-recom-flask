# capstone/vector_service.py
from . import qdrant_client, vector_store, mongo_client
from qdrant_client.http import models
import pandas as pd

path=r"data\anime-dataset-2023.csv"
df=pd.read_csv(path)

def similarity_search(query: str, k: int = 5, anime_type: str = None):
    flt = None
    if anime_type:
        flt = models.Filter(
            should=[ models.FieldCondition(
                key="metadata.anime_type",
                match=models.MatchValue(value=anime_type),
            )]
        )
    results = vector_store.similarity_search(query=query, k=k, filter=flt)
    return [(doc.page_content, doc.metadata) for doc in results]


def record_user_click(db, user_id, anime_id):
    click = db.clicks.find_one({"userId": user_id, "animeId": anime_id})
    if click:
        db.clicks.update_one(
            {"userId": user_id, "animeId": anime_id},
            {"$inc": {"clickCount": 1}}
        )
    else:
        db.clicks.insert_one({"userId": user_id, "animeId": anime_id, "clickCount": 1})
    return {"success": True}, 200

def get_animes_by_clicks(db, search: str = None, token: str = None, k: int = 50):
    if search:
    
        hits1 = similarity_search(query=search, k=k, anime_type="Movie")
        hits2= similarity_search(query=search, k=k, anime_type="TV")
        tv_anime_ids = [hit[1]['anime_id'] for hit in hits1]
        movie_anime_ids = [hit[1]['anime_id'] for hit in hits2]
        record_user_click(db, token, tv_anime_ids[0])
        record_user_click(db, token, movie_anime_ids[0])
        tv_animes = df[df['anime_id'].isin(tv_anime_ids)].sort_values(by='Favorites', ascending=False).to_dict(orient='records')
        movie_animes = df[df['anime_id'].isin(movie_anime_ids)].sort_values(by='Favorites', ascending=False).to_dict(orient='records')


        return {"TV": tv_animes, "Movies": movie_animes}
    else:
        clicks = db.clicks.find({"userId": token}).sort("clickCount", -1).limit(30)
        anime_id_clicks = [click["animeId"] for click in clicks]

        likes = db.likes.find({"userId": token}).limit(30)
        anime_id_likes = [like["animeId"] for like in likes]
        
        anime_names=""
        if clicks or likes:
            anime_ids= list(set(anime_id_clicks + anime_id_likes))
            anime_names = df[df['anime_id'].isin(anime_ids)]['Name'].tolist()
        
        if anime_names:
            hits1 = similarity_search(query=" ".join(anime_names), k=k, anime_type="Movie")
            hits2 = similarity_search(query=" ".join(anime_names), k=k, anime_type="TV")
            tv_anime_ids = [hit[1]['anime_id'] for hit in hits1]
            movie_anime_ids = [hit[1]['anime_id'] for hit in hits2]

            tv_animes = df[df['anime_id'].isin(tv_anime_ids)].sort_values(by='Favorites', ascending=False).to_dict(orient='records')
            movie_animes = df[df['anime_id'].isin(movie_anime_ids)].sort_values(by='Favorites', ascending=False).to_dict(orient='records')

            return {"TV": tv_animes, "Movies": movie_animes}
        

    return {
        "TV": df[df['Type'] == 'TV'].sort_values(by='Favorites', ascending=False).head(k).to_dict(orient='records'),
        "Movies": df[df['Type'] == 'Movie'].sort_values(by='Favorites', ascending=False).head(k).to_dict(orient='records')
    }
