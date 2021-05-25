from fastapi import FastAPI, Depends, status, Response, HTTPException
from . import models, schemas
from .database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post('/blogs', status_code=status.HTTP_201_CREATED)
def create(body: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=body.title, body=body.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.put('/blogs/{blog_id}', status_code=status.HTTP_202_ACCEPTED)
def update(blog_id: int, body: schemas.Blog, db: Session = Depends(get_db)):
    update_data = body.dict(exclude_unset=True)

    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)

    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'details': f'Blog with id {blog_id} not found.'})

    blog.update(update_data)
    db.commit()

    return ''


@app.get('/blogs')
def index(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


@app.get('/blogs/{blog_id}', status_code=status.HTTP_201_CREATED)
def get(blog_id: int, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()

    if blog is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'details': f'Blog with id {blog_id} not found.'})
    return blog


@app.delete('/blogs/{blog_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(blog_id: int, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id)

    if blog.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail={'details': f'Blog with id {blog_id} not found.'})

    blog.delete(synchronize_session=False)
    db.commit()
    return ''
