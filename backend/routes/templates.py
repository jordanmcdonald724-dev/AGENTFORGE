"""
Project Templates System
========================
Pre-built, production-ready project templates for instant start
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from core.database import db
from models.base import Project
import uuid

router = APIRouter(prefix="/templates", tags=["templates"])


# Template Library
PROJECT_TEMPLATES = {
    "saas_dashboard": {
        "id": "saas_dashboard",
        "name": "SaaS Dashboard",
        "description": "Complete SaaS starter with auth, billing, analytics, and admin panel",
        "category": "web",
        "type": "web_app",
        "icon": "💼",
        "features": [
            "User authentication & authorization",
            "Stripe billing integration",
            "Admin dashboard with analytics",
            "User management",
            "API with rate limiting",
            "Email notifications",
            "Dark/light theme"
        ],
        "tech_stack": ["React", "FastAPI", "MongoDB", "Stripe", "TailwindCSS"],
        "files": {
            "frontend/src/App.jsx": """import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Analytics from './pages/Analytics';
import Billing from './pages/Billing';
import Settings from './pages/Settings';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/" element={<Dashboard />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}""",
            "backend/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, billing, analytics, users

app = FastAPI(title="SaaS API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(billing.router, prefix="/api/billing")
app.include_router(analytics.router, prefix="/api/analytics")
app.include_router(users.router, prefix="/api/users")

@app.get("/")
def root():
    return {"message": "SaaS API"}
"""
        }
    },
    "ecommerce_store": {
        "id": "ecommerce_store",
        "name": "E-commerce Store",
        "description": "Full-featured online store with products, cart, checkout, and orders",
        "category": "web",
        "type": "web_app",
        "icon": "🛒",
        "features": [
            "Product catalog with categories",
            "Shopping cart with persistence",
            "Checkout with Stripe",
            "Order management",
            "Inventory tracking",
            "Admin panel for products",
            "Customer accounts"
        ],
        "tech_stack": ["React", "Node.js", "MongoDB", "Stripe", "TailwindCSS"],
        "files": {
            "frontend/src/App.jsx": """import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CartProvider } from './context/CartContext';
import Home from './pages/Home';
import Products from './pages/Products';
import ProductDetail from './pages/ProductDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';

export default function App() {
  return (
    <CartProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/products" element={<Products />} />
          <Route path="/product/:id" element={<ProductDetail />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/orders" element={<Orders />} />
        </Routes>
      </BrowserRouter>
    </CartProvider>
  );
}"""
        }
    },
    "rpg_starter": {
        "id": "rpg_starter",
        "name": "RPG Game Starter",
        "description": "Complete RPG foundation with combat, inventory, quests, and save system",
        "category": "game",
        "type": "unreal",
        "icon": "🎮",
        "features": [
            "Character controller with combat",
            "Inventory system with equipment",
            "Quest system with objectives",
            "Dialog system",
            "Save/load system",
            "Enemy AI with behavior trees",
            "Level progression and stats"
        ],
        "tech_stack": ["Unreal Engine 5", "Blueprints", "C++"],
        "files": {
            "Source/Player/PlayerCharacter.h": """// Complete player character with combat and inventory
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "PlayerCharacter.generated.h"

UCLASS()
class APlayerCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    APlayerCharacter();

    // Combat
    UFUNCTION(BlueprintCallable)
    void Attack();
    
    // Inventory
    UFUNCTION(BlueprintCallable)
    void AddItem(class UItem* Item);
    
    // Stats
    UPROPERTY(BlueprintReadWrite)
    float Health;
    
    UPROPERTY(BlueprintReadWrite)
    float MaxHealth;
    
    UPROPERTY(BlueprintReadWrite)
    int32 Level;
};"""
        }
    },
    "portfolio_site": {
        "id": "portfolio_site",
        "name": "Portfolio Website",
        "description": "Beautiful portfolio with projects showcase, about, and contact sections",
        "category": "web",
        "type": "webpage",
        "icon": "🎨",
        "features": [
            "Hero section with animations",
            "Projects showcase with filters",
            "About section with timeline",
            "Contact form with validation",
            "Responsive design",
            "Dark/light theme toggle",
            "Smooth scroll animations"
        ],
        "tech_stack": ["React", "TailwindCSS", "Framer Motion"],
        "files": {
            "src/App.jsx": """import { useState } from 'react';
import Hero from './components/Hero';
import Projects from './components/Projects';
import About from './components/About';
import Contact from './components/Contact';
import Navbar from './components/Navbar';
import Footer from './components/Footer';

export default function App() {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={darkMode ? 'dark' : ''}>
      <div className="min-h-screen bg-white dark:bg-gray-900">
        <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
        <Hero />
        <Projects />
        <About />
        <Contact />
        <Footer />
      </div>
    </div>
  );
}"""
        }
    }
}


@router.get("")
async def get_templates():
    """Get all available project templates"""
    return list(PROJECT_TEMPLATES.values())


@router.get("/{template_id}")
async def get_template(template_id: str):
    """Get specific template details"""
    if template_id not in PROJECT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    return PROJECT_TEMPLATES[template_id]


@router.post("/{template_id}/create")
async def create_from_template(template_id: str, project_name: str = None):
    """Create a new project from template"""
    if template_id not in PROJECT_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    
    template = PROJECT_TEMPLATES[template_id]
    
    # Create project
    project = Project(
        name=project_name or template["name"],
        description=template["description"],
        type=template["type"]
    )
    
    project_doc = project.model_dump()
    project_doc['created_at'] = project_doc['created_at'].isoformat()
    project_doc['updated_at'] = project_doc['updated_at'].isoformat()
    project_doc['template_id'] = template_id
    
    await db.projects.insert_one(project_doc)
    
    # Create files from template
    files_created = 0
    for filepath, content in template.get("files", {}).items():
        file_doc = {
            "id": str(uuid.uuid4()),
            "project_id": project_doc["id"],
            "filepath": filepath,
            "content": content,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.files.insert_one(file_doc)
        files_created += 1
    
    return {
        "success": True,
        "project": project_doc,
        "files_created": files_created,
        "message": f"Created '{project_name or template['name']}' from {template['name']} template"
    }
