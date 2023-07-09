import datetime
import os
import re

from typing import Annotated, List
from uuid import uuid4

from fastapi import Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from src.common.settings import config
from src.schemas.article import DeleteArticle
from src.utils import redis_util


class ArticleHandler:

    def get_article_id(
            self,
            article_header: str,
    ) -> str:
        _id = re.sub(' +', ' ', article_header)
        _id = re.sub('[^A-Za-z0-9 -]+', '', _id)

        _id = _id.lower().replace(' ', '-')
        
        if redis_util.retrive_articles(article_id=_id):
            print("Adding UID to id as it already exists!")
            _postfix = str(uuid4()).split('-')[0]
            _id += "-"+_postfix
            return self.get_article_id(_id)
        return _id
    
    
    @staticmethod
    def get_all_articles() -> List[dict]:
        response = []
        article_data = redis_util.retrive_articles()
        for key, value in article_data.items():
            value.update({"article_id": key})
            response.append(value)
        return sorted(response, key=lambda d: datetime.datetime.strptime(d['article_date'], "%d %B, %Y")) 
        
    @staticmethod
    def get_my_articles(email: str) -> List[dict]:
        response = []
        article_data = redis_util.retrive_articles()
        for key, value in article_data.items():
            if value.get("email") == email:
                value.update({"article_id": key})
                response.append(value)
        return sorted(response, key=lambda d: datetime.datetime.strptime(d['article_date'], "%d %B, %Y")) 
        

    @staticmethod
    def get_one_article(
        article_id: str,
    ) -> dict:
        article_data = redis_util.retrive_articles(article_id=article_id)
        article_owner = redis_util.get_user(email=article_data.get('email', '')).get('name', '')
        del article_data['email']
        article_data['name'] = article_owner
        return article_data

    
    @staticmethod
    def get_one_article_image(
        article_id: str,
    ):
        article_data = redis_util.retrive_articles(article_id=article_id)
        return os.path.join(config.thumbnail_directory, article_data["thumbnailImage"])
    
        
    def add_one_article(
            self,
            email: str,
            article_header: Annotated[str, Form()],
            article_body: Annotated[str, Form()],
            thumbnailImage: UploadFile,
    ):
        _article_id = self.get_article_id(article_header)
        _article_data = {
            "email": email,
            "article_body": article_body,
            "article_header": article_header,
            "thumbnailImage": f"{_article_id}-{thumbnailImage.filename}",
            "article_date": datetime.datetime.now().strftime("%d %B, %Y")
        }
        redis_util.insert_one_article(
            article_id=_article_id,
            article_data=_article_data,
        )
        if not os.path.exists(config.thumbnail_directory):
            os.makedirs(config.thumbnail_directory)
            
        _thumbnail_path = os.path.join(config.thumbnail_directory, f"{_article_id}-{thumbnailImage.filename}")
        with open(_thumbnail_path, 'wb+') as f:
            f.write(thumbnailImage.file.read())
        return


    @staticmethod
    def delete_one_article(
            email: str,
            article: DeleteArticle,
    ):
        article_data = redis_util.retrive_articles(article_id=article.article_id)
        if article_data.get('email', '') != email:
            raise HTTPException(status_code=401, detail="User unauthorised!")
        
        redis_util.delete_one_article(
            article_id=article.article_id,
        )
        return JSONResponse(content={"status": True, "data": "OK"})