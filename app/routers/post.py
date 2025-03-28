from fastapi import Response, status, HTTPException, APIRouter, Depends
from .. import models, schemas, oauth2
from ..schemas import PostResponse, PostOut
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from sqlalchemy import func

router = APIRouter(prefix="/posts", tags=["Posts"])


# @router.get(
#     "/",
#     response_model=List[PostResponse],
# )


@router.get("/", response_model=List[PostOut])
def get_posts(
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 15,
    skip: int = 0,
    search: Optional[str] = "",
):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()

    # print(search)

    # posts_query = db.query(models.Post).filter(models.Post.owner_id == current_user.id)

    # posts = (
    #     posts_query.filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )

    # if not posts:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND, detail="Posts not found"
    #     )

    # default join is left inner join
    # Query posts with search functionality

    post_query = (
        db.query(
            models.Post,
            func.count(models.Vote.posts_id).label("votes"),
            models.User,  # Include owner details inside the post
        )
        .join(models.Vote, models.Vote.posts_id == models.Post.id, isouter=True)
        .join(
            models.User, models.User.id == models.Post.owner_id
        )  # Join with User table
        .group_by(models.Post.id, models.User.id)
        .filter(models.Post.title.contains(search))  # Apply search filter
        .filter(models.Post.owner_id == current_user.id)  # Show only current user posts
        .offset(skip)  # Pagination: Skip results
        .limit(limit)  # Pagination: Limit results
        .all()
    )

    # Convert SQLAlchemy models to dictionaries
    formatted_results = [
        {
            "post": {
                **post.__dict__,
                "owner": {
                    "id": owner.id,
                    "email": owner.email,
                    "created_at": owner.created_at,
                },
            },
            "votes": votes,
        }
        for post, votes, owner in post_query  # Unpack correctly
    ]

    return formatted_results


# get single post
@router.get("/{id}", response_model=PostOut)
def get_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(""" SELECT * FROM posts WHERE id = %s """, (str(id)))
    # post = cursor.fetchone()

    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = (
        db.query(
            models.Post,
            func.count(models.Vote.posts_id).label("votes"),
            models.User,  # Include owner details inside the post
        )
        .join(models.Vote, models.Vote.posts_id == models.Post.id, isouter=True)
        .join(models.User, models.User.id == models.Post.owner_id)
        .group_by(models.Post.id, models.User.id)
        .filter(models.Post.id == id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found."
        )

    post_obj, votes, owner = post

    # if post.owner_id != current_user.id:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Not authorized to access this post.",
    #     )

    # Convert SQLAlchemy models to dictionaries
    return {
        "post": {  
            **post_obj.__dict__,
            "owner": {
                "id": owner.id,
                "email": owner.email,
                "created_at": owner.created_at,
            },
        },
        "votes": votes,
    }


# create post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostResponse)
def create_posts(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    # cursor.execute(
    #     """ INSERT INTO posts (title, content) VALUES (%s, %s) RETURNING * """,
    #     (post.title, post.content),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()
    new_post = models.Post(**post.dict(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# update post
@router.put("/{id}", response_model=PostResponse)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str((id))))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()

    if existing_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post doesn't exist.",
        )

    if existing_post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()


# delete post
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    # cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id)))
    # deleted_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} doesn't exist.",
        )

    if post.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
