from fastapi import Response, status, HTTPException, Depends, APIRouter
from app.database import get_db
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, models, oauth2
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["Post"])


@router.get("/", response_model=List[schemas.PostOut])
# @router.get("/")
def get_post(
    db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""
):
    # posts = (
    #     db.query(models.Post)
    #     .filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )

    posts_query = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    # posts = []

    # for post_obj, count in posts_query:
    #     post = post_obj.returnPost()
    #     post["vote"] = count
    #     posts.append(post)

    return posts_query


@router.get("/lastest")
def get_lastest_post():
    return "lastest post"


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db)):
    post = (
        db.query(models.Post, func.count(models.Vote.post_id).label("votes"))
        .join(models.Vote, models.Vote.post_id == models.Post.id, isouter=True)
        .group_by(models.Post.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found")

    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post = post.dict()
    new_post = models.Post(owner_id=current_user.id, **post)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.patch("/{id}")
def update_post(
    id: int,
    updated_post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id={id} not found"
        )

    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return {"code": 200, "message": "success"}


@router.delete("/{id}")
def delete_post(
    id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == id)
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"NOT FOUND")

    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")

    db.query(models.Post).filter(models.Post.id == id).delete()
    db.commit()

    return "deleted post"
