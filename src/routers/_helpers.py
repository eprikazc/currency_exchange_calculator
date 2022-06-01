from fastapi import HTTPException


def get_object_or_404(db_session, model_class, id):
    obj = db_session.query(model_class).get(id)
    if obj is None:
        raise HTTPException(
            status_code=400,
            detail=f"{model_class} with id {id} does not exist",
        )
    else:
        return obj
