from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/database-viewer", response_class=HTMLResponse)
async def database_viewer(db: Session = Depends(get_db)):
    """Dashboard për të parë databazën në shfletues"""
    
    # Get statistics
    total_users = db.query(models.User).count()
    total_classes = db.query(models.Course).filter(models.Course.parent_class_id.is_(None)).count()
    total_courses = db.query(models.Course).filter(models.Course.parent_class_id.isnot(None)).count()
    total_exercises = db.query(models.Exercise).count()
    total_progress = db.query(models.CourseProgress).count()
    completed_progress = db.query(models.CourseProgress).filter(models.CourseProgress.is_completed == True).count()
    total_attempts = db.query(models.Attempt).count()
    correct_attempts = db.query(models.Attempt).filter(models.Attempt.is_correct == True).count()
    
    # Get users
    users = db.query(models.User).order_by(models.User.created_at.desc()).limit(20).all()
    
    # Get classes with course counts
    classes = db.query(models.Course).filter(models.Course.parent_class_id.is_(None)).order_by(models.Course.order_index).all()
    class_data = []
    for cls in classes:
        course_count = db.query(models.Course).filter(models.Course.parent_class_id == cls.id).count()
        exercise_count = db.query(models.Exercise).join(models.Course).filter(models.Course.parent_class_id == cls.id).count()
        class_data.append({
            'id': cls.id,
            'name': cls.name,
            'order': cls.order_index,
            'courses': course_count,
            'exercises': exercise_count
        })
    
    # Get recent progress
    recent_progress = db.query(models.CourseProgress).order_by(models.CourseProgress.updated_at.desc()).limit(10).all()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="sq">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Viewer - Shqipto</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                min-height: 100vh;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                padding: 30px;
            }}
            h1 {{
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }}
            .subtitle {{
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 25px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }}
            .stat-card h3 {{
                font-size: 0.9em;
                opacity: 0.9;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .stat-card .number {{
                font-size: 2.5em;
                font-weight: bold;
            }}
            .section {{
                margin-bottom: 40px;
            }}
            .section h2 {{
                color: #333;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            th {{
                background: #667eea;
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
            }}
            td {{
                padding: 12px 15px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background: #f5f5f5;
            }}
            .badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 0.85em;
                font-weight: 600;
            }}
            .badge-success {{
                background: #10b981;
                color: white;
            }}
            .badge-warning {{
                background: #f59e0b;
                color: white;
            }}
            .badge-info {{
                background: #3b82f6;
                color: white;
            }}
            .refresh-btn {{
                background: #667eea;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 1em;
                margin-bottom: 20px;
                transition: all 0.3s;
            }}
            .refresh-btn:hover {{
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Database Viewer</h1>
            <p class="subtitle">Shqipto - Albanian Language Learning Platform</p>
            
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh</button>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Përdorues</h3>
                    <div class="number">{total_users}</div>
                </div>
                <div class="stat-card">
                    <h3>Klasa</h3>
                    <div class="number">{total_classes}</div>
                </div>
                <div class="stat-card">
                    <h3>Nivele</h3>
                    <div class="number">{total_courses}</div>
                </div>
                <div class="stat-card">
                    <h3>Ushtrime</h3>
                    <div class="number">{total_exercises}</div>
                </div>
                <div class="stat-card">
                    <h3>Progrese</h3>
                    <div class="number">{total_progress}</div>
                </div>
                <div class="stat-card">
                    <h3>Përfunduar</h3>
                    <div class="number">{completed_progress}</div>
                </div>
                <div class="stat-card">
                    <h3>Përpjekje</h3>
                    <div class="number">{total_attempts}</div>
                </div>
                <div class="stat-card">
                    <h3>Saktësi</h3>
                    <div class="number">{round((correct_attempts/total_attempts*100) if total_attempts > 0 else 0, 1)}%</div>
                </div>
            </div>
            
            <div class="section">
                <h2>📚 Klasat dhe Nivelet</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Klasa</th>
                            <th>Renditja</th>
                            <th>Nivele</th>
                            <th>Ushtrime</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for cls in class_data:
        html_content += f"""
                        <tr>
                            <td>{cls['id']}</td>
                            <td><strong>{cls['name']}</strong></td>
                            <td>{cls['order']}</td>
                            <td><span class="badge badge-info">{cls['courses']}</span></td>
                            <td><span class="badge badge-success">{cls['exercises']}</span></td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>👥 Përdoruesit (20 të fundit)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Username</th>
                            <th>Email</th>
                            <th>Moshë</th>
                            <th>Data Regjistrimit</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for user in users:
        created_at = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else "N/A"
        html_content += f"""
                        <tr>
                            <td>{user.id}</td>
                            <td><strong>{user.username}</strong></td>
                            <td>{user.email}</td>
                            <td>{user.age or 'N/A'}</td>
                            <td>{created_at}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div class="section">
                <h2>📈 Progresi i Fundit (10 të fundit)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Course ID</th>
                            <th>Ushtrime</th>
                            <th>Përfunduar</th>
                            <th>Saktësi</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
    """
    
    for prog in recent_progress:
        course = db.query(models.Course).filter(models.Course.id == prog.course_id).first()
        course_name = course.name if course else f"Course {prog.course_id}"
        status_badge = '<span class="badge badge-success">Përfunduar</span>' if prog.is_completed else '<span class="badge badge-warning">Në Progres</span>'
        accuracy = round(prog.accuracy_percentage, 1) if prog.accuracy_percentage else 0
        html_content += f"""
                        <tr>
                            <td>{prog.user_id}</td>
                            <td>{course_name}</td>
                            <td>{prog.completed_exercises or 0}/{prog.total_exercises or 0}</td>
                            <td>{prog.completed_exercises or 0}</td>
                            <td>{accuracy}%</td>
                            <td>{status_badge}</td>
                        </tr>
        """
    
    html_content += """
                    </tbody>
                </table>
            </div>
            
            <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid #eee; text-align: center; color: #666;">
                <p>Database Viewer - Shqipto Platform</p>
                <p style="margin-top: 10px;">
                    <a href="/api/docs" style="color: #667eea; text-decoration: none;">📖 API Documentation</a> | 
                    <a href="/health" style="color: #667eea; text-decoration: none;">❤️ Health Check</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

