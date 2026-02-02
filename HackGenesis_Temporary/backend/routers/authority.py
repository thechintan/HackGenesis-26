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

@router.get("/users/{user_id}/activity")
def get_user_activity(user_id: int, db: Session = Depends(get_db)):
    # 1. User's Posts
    posts = db.query(Post).filter(Post.user_id == user_id).order_by(Post.created_at.desc()).all()
    posts_data = []
    for p in posts:
        posts_data.append({
            "id": p.id,
            "caption": p.caption,
            "status": p.status or "Open",
            "created_at": p.created_at.isoformat(),
            "type": "Community Report"
        })

    # 2. User's Aid Requests
    requests = db.query(AidRequest).filter(AidRequest.user_id == user_id).order_by(AidRequest.timestamp.desc()).all()
    req_data = []
    for r in requests:
        req_data.append({
            "id": r.id,
            "needs": r.needs,
            "status": r.status or "Pending",
            "timestamp": r.timestamp.isoformat(),
            "type": "Aid Request"
        })
        
    return {
        "posts": posts_data,
        "aid_requests": req_data
    }

@router.get("/authority/dashboard-data")
def get_authority_data(view: str = "active", db: Session = Depends(get_db)):
    # view can be 'active' or 'all'
    
    # 1. Posts
    post_query = db.query(Post)
    if view == "active":
        post_query = post_query.filter((Post.status == "Open") | (Post.status == None))
    
    prioritized_posts = post_query.order_by(Post.risk_score.desc()).all()
    
    posts_data = []
    for p in prioritized_posts:
        posts_data.append({
            "id": p.id,
            "risk_score": p.risk_score,
            "location": p.location,
            "caption": p.caption,
            "description": p.description,
            "image_data": p.image_data,
            "status": p.status, # Include status for history view
            "created_at": p.created_at.isoformat()
        })
        
    # 2. Aid Requests
    aid_query = db.query(AidRequest)
    if view == "active":
        aid_query = aid_query.filter(AidRequest.status != "Resolved").filter(AidRequest.status != "Dismissed") # Keep Delegated/In Progress in active? 
        # Actually simplified: Active = Pending, In Progress, Delegated. Resolved/Dismissed = History.
        # Let's be strict: Active does NOT include Resolved or Dismissed.
        aid_query = aid_query.filter(~AidRequest.status.in_(["Resolved", "Dismissed"]))

    aid_requests = aid_query.order_by(
        AidRequest.urgency_score.desc(),
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
             "urgency_score": a.urgency_score, 
             "status": a.status,
             "contact": a.contact,
             "location": a.location,
             "timestamp": a.timestamp.isoformat()
         })
         
    return {
        "prioritized_posts": posts_data,
        "aid_requests": aid_data
    }

class PostStatusUpdate(BaseModel):
    status: str

@router.put("/authority/posts/{post_id}/status")
def update_post_status(post_id: str, update: PostStatusUpdate, db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        return {"error": "Post not found"}
    
    post.status = update.status
    db.commit()
    return {"message": "Status updated", "new_status": post.status}

@router.post("/authority/aid-request")
def log_aid_request(req: AidRequestCreate, db: Session = Depends(get_db)):
    # AI Override/Verification of priority
    ai_label, ai_score = calculate_aid_priority(req.needs, req.description)
    
    new_req = AidRequest(
        user_id=req.user_id,
        description=req.description,
        needs=req.needs,
        urgency=ai_label,      # Use AI determined label
        urgency_score=ai_score, # Use AI determined score
        contact=req.contact,
        location=req.location
    )
    db.add(new_req)
    db.commit()
    return {"message": "Aid request logged", "ai_urgency": ai_label, "ai_score": ai_score}

class AidStatusUpdate(BaseModel):
    status: str

@router.put("/authority/aid-requests/{req_id}/status")
def update_aid_status(req_id: int, update: AidStatusUpdate, db: Session = Depends(get_db)):
    req = db.query(AidRequest).filter(AidRequest.id == req_id).first()
    if not req:
        return {"error": "Request not found"}
    
    req.status = update.status
    db.commit()
    return {"message": "Status updated", "new_status": req.status}
    
@router.get("/authority/heatmap")
def get_heatmap():
    return generate_heatmap_data()
