from typing import Annotated

from fastapi import APIRouter, Form, UploadFile, Depends, HTTPException
from fastapi.responses import FileResponse

from src.schemas.article import DeleteArticle
from src.handlers.article import ArticleHandler
from src.utils.security_utils.decorators import CookieAuthentication

auth = CookieAuthentication()

app = APIRouter(tags=["Articles"], prefix="/api")
handler = ArticleHandler()

@app.post("/articles/create")
def add_article(
    article_header: Annotated[str, Form()],
    article_body: Annotated[str, Form()],
    thumbnailImage: UploadFile,
    email=Depends(auth),
    ):
    if isinstance(email, HTTPException):
        return email
    
    handler.add_one_article(
        email=email,
        article_header=article_header,
        article_body=article_body,
        thumbnailImage=thumbnailImage,
    )
    return {"status": True, "data": "OK"}


@app.post("/articles/delete")
def delete_article(
    article: DeleteArticle,
    email=Depends(auth),
    ):
    return handler.delete_one_article(
        email=email,
        article=article,
    )


@app.get("/articles")
def get_all_articles(
):  
    response = handler.get_all_articles()
    return {"status": True, "data": response}

@app.get("/articles/my")
def get_my_articles(
    email=Depends(auth),
):  
    response = handler.get_my_articles(email)
    return {"status": True, "data": response}

@app.get("/articles/{article_id}")
def get_one_article(
    article_id: str
):
    article_data = handler.get_one_article(article_id=article_id)
    return {"status": True, "data": article_data}


@app.get(
    "/articles/{article_id}/image",
    responses = {200: {"content": {"image/png": {}}}},
    response_class=FileResponse,
)
def get_image(
    article_id: str,
):
    img_path = handler.get_one_article_image(article_id=article_id)
    return FileResponse(
        path=img_path,
        media_type="image/png",
    )