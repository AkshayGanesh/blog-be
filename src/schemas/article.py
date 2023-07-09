from pydantic import BaseModel


class CreateArticle(BaseModel):
    article_header: str
    article_body: str


class DeleteArticle(BaseModel):
    article_id: str