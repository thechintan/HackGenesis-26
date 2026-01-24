from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Post, AidRequest
from ..ai_logic import generate_heatmap_data, calculate_aid_priority
from pydantic import BaseModel

router = APIRouter(tags=["Authority"])

class AidRequestCreate(BaseModel):
    user_id: int
    description: str
    needs: str
    urgency: str
    contact: str
    location: str

@router.get("/authority/dashboard-data")
def get_authority_data(db: Session = Depends(get_db)):
    # 1. Prioritized Posts (Risk High to Low)
    prioritized_posts = db.query(Post).order_by(Post.risk_score.desc()).all()
    
    posts_data = []
    for p in prioritized_posts:
        posts_data.append({
            "id": p.id,
            "risk_score": p.risk_score,
            "location": p.location,
            "caption": p.caption,
            "description": p.description,
            "image_data": p.image_data,
            "created_at": p.created_at.isoformat()
        })
        
    # 2. Aid Requests (Prioritized by Urgency: High > Medium > Low)
    from sqlalchemy import case
    aid_requests = db.query(AidRequest).order_by(
        case(
            (AidRequest.urgency == 'High', 1),
            (AidRequest.urgency == 'Medium', 2),
            (AidRequest.urgency == 'Low', 3),
            else_=4
        ),
        AidRequest.timestamp.desc()
    ).all()
    aid_data = []
    for a in aid_requests:
         aid_data.append({
             "id": a.id,
             "user_name": a.user.name if a.user else "Unknown",
             "user_email": a.user.email if a.user else "Unknown",
             "description": a.description,
             "needs": a.needs,
             "urgency": a.urgency,
             "status": a.status,
             "contact": a.contact,
             "location": a.location,
             "timestamp": a.timestamp.isoformat()
         })
         
    return {
        "prioritized_posts": posts_data,
        "aid_requests": aid_data
    }

@router.post("/authority/aid-request")
def log_aid_request(req: AidRequestCreate, db: Session = Depends(get_db)):
    # AI Override/Verification of priority
    ai_urgency = calculate_aid_priority(req.needs, req.description)
    
    new_req = AidRequest(
        user_id=req.user_id,
        description=req.description,
        needs=req.needs,
        urgency=ai_urgency, # Use AI determined urgency
        contact=req.contact,
        location=req.location
    )
    db.add(new_req)
    db.commit()
    return {"message": "Aid request logged", "ai_urgency": ai_urgency}
    
@router.get("/authority/heatmap")
def get_heatmap():
    return generate_heatmap_data()
