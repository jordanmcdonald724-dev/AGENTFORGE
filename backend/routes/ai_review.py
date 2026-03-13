"""
AI Code Review - Intelligent code analysis using Knowledge Graph patterns
Provides actionable suggestions for code improvement
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio
import re

router = APIRouter(prefix="/ai-review", tags=["ai-review"])


class ReviewRequest(BaseModel):
    project_id: str
    files: List[str] = []  # Specific files to review, empty = all
    review_type: str = "full"  # full, security, performance, style, architecture
    severity_threshold: str = "low"  # low, medium, high, critical


class FileReviewRequest(BaseModel):
    content: str
    filename: str
    language: str = "auto"


# Review patterns from Knowledge Graph
REVIEW_PATTERNS = {
    "react": {
        "hooks_misuse": {
            "pattern": r"useState\([^)]+\)\s*;\s*useState",
            "message": "Consider combining related state into a single useState with an object",
            "severity": "medium",
            "category": "performance"
        },
        "missing_key": {
            "pattern": r"\.map\([^)]+\)\s*=>\s*<(?!.*key=)",
            "message": "Missing 'key' prop in list rendering",
            "severity": "high",
            "category": "correctness"
        },
        "inline_function": {
            "pattern": r"onClick=\{\(\)\s*=>",
            "message": "Consider using useCallback for inline event handlers to prevent unnecessary re-renders",
            "severity": "low",
            "category": "performance"
        },
        "console_log": {
            "pattern": r"console\.(log|warn|error)",
            "message": "Remove console statements in production code",
            "severity": "low",
            "category": "cleanup"
        }
    },
    "python": {
        "bare_except": {
            "pattern": r"except\s*:",
            "message": "Avoid bare 'except:' - specify the exception type",
            "severity": "high",
            "category": "security"
        },
        "sql_injection": {
            "pattern": r"execute\([^)]*%s|execute\([^)]*\+",
            "message": "Potential SQL injection - use parameterized queries",
            "severity": "critical",
            "category": "security"
        },
        "hardcoded_secret": {
            "pattern": r"(password|secret|api_key|token)\s*=\s*['\"][^'\"]+['\"]",
            "message": "Hardcoded secret detected - use environment variables",
            "severity": "critical",
            "category": "security"
        },
        "no_type_hints": {
            "pattern": r"def\s+\w+\([^)]*\)\s*:",
            "message": "Consider adding type hints for better code documentation",
            "severity": "low",
            "category": "style"
        }
    },
    "javascript": {
        "var_usage": {
            "pattern": r"\bvar\s+",
            "message": "Use 'const' or 'let' instead of 'var'",
            "severity": "medium",
            "category": "style"
        },
        "eval_usage": {
            "pattern": r"\beval\s*\(",
            "message": "Avoid using eval() - security risk",
            "severity": "critical",
            "category": "security"
        },
        "callback_hell": {
            "pattern": r"function\s*\([^)]*\)\s*{\s*function\s*\([^)]*\)\s*{",
            "message": "Consider using async/await to avoid callback nesting",
            "severity": "medium",
            "category": "readability"
        },
        "no_error_handling": {
            "pattern": r"\.catch\(\s*\(\s*\)\s*=>\s*{\s*}\s*\)",
            "message": "Empty catch block - handle errors properly",
            "severity": "high",
            "category": "correctness"
        }
    },
    "general": {
        "todo_comment": {
            "pattern": r"(TODO|FIXME|HACK|XXX)",
            "message": "Found TODO/FIXME comment - consider addressing",
            "severity": "low",
            "category": "cleanup"
        },
        "large_function": {
            "pattern": None,  # Special handling
            "message": "Function exceeds 50 lines - consider breaking it up",
            "severity": "medium",
            "category": "architecture"
        },
        "magic_number": {
            "pattern": r"(?<!['\"])\b\d{4,}\b(?!['\"])",
            "message": "Magic number detected - consider using a named constant",
            "severity": "low",
            "category": "readability"
        }
    }
}

# Architecture patterns
ARCHITECTURE_PATTERNS = {
    "separation_of_concerns": {
        "description": "UI components should not contain business logic",
        "check": "business_logic_in_component"
    },
    "single_responsibility": {
        "description": "Each module should have one clear purpose",
        "check": "multiple_responsibilities"
    },
    "dependency_injection": {
        "description": "Dependencies should be injected, not hardcoded",
        "check": "hardcoded_dependencies"
    }
}


@router.post("/review")
async def review_project(request: ReviewRequest, background_tasks: BackgroundTasks):
    """Start a code review for a project"""
    
    # Verify project exists
    project = await db.projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    review_id = str(uuid.uuid4())
    
    review = {
        "id": review_id,
        "project_id": request.project_id,
        "review_type": request.review_type,
        "severity_threshold": request.severity_threshold,
        "status": "analyzing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files_reviewed": 0,
        "issues_found": [],
        "summary": None
    }
    
    await db.code_reviews.insert_one(review)
    
    # Run review in background
    background_tasks.add_task(execute_review, review_id, request)
    
    return {
        "review_id": review_id,
        "status": "analyzing",
        "message": "Code review started"
    }


async def execute_review(review_id: str, request: ReviewRequest):
    """Execute the code review"""
    
    # Get project files
    query = {"project_id": request.project_id}
    if request.files:
        query["filepath"] = {"$in": request.files}
    
    files = await db.files.find(query, {"_id": 0}).to_list(500)
    
    all_issues = []
    
    for file in files:
        content = file.get("content", "")
        filepath = file.get("filepath", file.get("filename", "unknown"))
        
        if not content:
            continue
        
        # Detect language
        language = detect_language(filepath)
        
        # Run pattern matching
        issues = analyze_file(content, filepath, language, request.review_type)
        
        # Filter by severity
        severity_order = ["low", "medium", "high", "critical"]
        threshold_idx = severity_order.index(request.severity_threshold)
        
        filtered_issues = [
            issue for issue in issues 
            if severity_order.index(issue["severity"]) >= threshold_idx
        ]
        
        all_issues.extend(filtered_issues)
    
    # Generate summary
    summary = generate_review_summary(all_issues, len(files))
    
    # Update review
    await db.code_reviews.update_one(
        {"id": review_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "files_reviewed": len(files),
                "issues_found": all_issues,
                "summary": summary
            }
        }
    )


def detect_language(filepath: str) -> str:
    """Detect programming language from file extension"""
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "react",
        ".ts": "javascript",
        ".tsx": "react",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".rb": "ruby",
        ".php": "php"
    }
    
    for ext, lang in ext_map.items():
        if filepath.endswith(ext):
            return lang
    
    return "general"


def analyze_file(content: str, filepath: str, language: str, review_type: str) -> List[dict]:
    """Analyze a file for issues"""
    issues = []
    lines = content.split('\n')
    
    # Get patterns for this language + general patterns
    patterns = {}
    if language in REVIEW_PATTERNS:
        patterns.update(REVIEW_PATTERNS[language])
    patterns.update(REVIEW_PATTERNS["general"])
    
    # Filter by review type
    type_categories = {
        "full": None,  # All categories
        "security": ["security"],
        "performance": ["performance"],
        "style": ["style", "readability"],
        "architecture": ["architecture"]
    }
    
    allowed_categories = type_categories.get(review_type)
    
    for pattern_name, pattern_info in patterns.items():
        if allowed_categories and pattern_info.get("category") not in allowed_categories:
            continue
        
        if pattern_info.get("pattern"):
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern_info["pattern"], line, re.IGNORECASE):
                    issues.append({
                        "id": str(uuid.uuid4()),
                        "file": filepath,
                        "line": line_num,
                        "code": line.strip()[:100],
                        "pattern": pattern_name,
                        "message": pattern_info["message"],
                        "severity": pattern_info["severity"],
                        "category": pattern_info["category"]
                    })
    
    # Check for large functions
    if review_type in ["full", "architecture"]:
        function_starts = []
        in_function = False
        start_line = 0
        
        for i, line in enumerate(lines, 1):
            if re.match(r'\s*(def |function |async function |\w+\s*=\s*\([^)]*\)\s*=>)', line):
                if in_function and (i - start_line) > 50:
                    issues.append({
                        "id": str(uuid.uuid4()),
                        "file": filepath,
                        "line": start_line,
                        "code": lines[start_line-1].strip()[:100],
                        "pattern": "large_function",
                        "message": f"Function is {i - start_line} lines - consider breaking it up",
                        "severity": "medium",
                        "category": "architecture"
                    })
                in_function = True
                start_line = i
    
    return issues


def generate_review_summary(issues: List[dict], files_count: int) -> dict:
    """Generate a summary of the review"""
    
    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    category_counts = {}
    
    for issue in issues:
        severity_counts[issue["severity"]] = severity_counts.get(issue["severity"], 0) + 1
        category_counts[issue["category"]] = category_counts.get(issue["category"], 0) + 1
    
    # Calculate health score (0-100)
    weighted_issues = (
        severity_counts["critical"] * 25 +
        severity_counts["high"] * 10 +
        severity_counts["medium"] * 3 +
        severity_counts["low"] * 1
    )
    
    health_score = max(0, 100 - min(weighted_issues, 100))
    
    # Determine grade
    if health_score >= 90:
        grade = "A"
    elif health_score >= 75:
        grade = "B"
    elif health_score >= 60:
        grade = "C"
    elif health_score >= 40:
        grade = "D"
    else:
        grade = "F"
    
    return {
        "total_issues": len(issues),
        "files_reviewed": files_count,
        "severity_breakdown": severity_counts,
        "category_breakdown": category_counts,
        "health_score": health_score,
        "grade": grade,
        "top_issues": sorted(issues, key=lambda x: ["critical", "high", "medium", "low"].index(x["severity"]))[:5]
    }


@router.get("/review/{review_id}")
async def get_review(review_id: str):
    """Get code review results"""
    review = await db.code_reviews.find_one({"id": review_id}, {"_id": 0})
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/reviews/{project_id}")
async def list_project_reviews(project_id: str):
    """List all reviews for a project"""
    reviews = await db.code_reviews.find(
        {"project_id": project_id},
        {"_id": 0, "issues_found": 0}  # Exclude full issues list
    ).sort("created_at", -1).to_list(20)
    
    return reviews


@router.post("/review-file")
async def review_single_file(request: FileReviewRequest):
    """Review a single file (quick analysis)"""
    
    language = request.language
    if language == "auto":
        language = detect_language(request.filename)
    
    issues = analyze_file(request.content, request.filename, language, "full")
    summary = generate_review_summary(issues, 1)
    
    return {
        "filename": request.filename,
        "language": language,
        "issues": issues,
        "summary": summary
    }


@router.get("/patterns")
async def get_review_patterns():
    """Get all review patterns used by the AI"""
    patterns_summary = {}
    
    for lang, patterns in REVIEW_PATTERNS.items():
        patterns_summary[lang] = [
            {
                "name": name,
                "message": info["message"],
                "severity": info["severity"],
                "category": info["category"]
            }
            for name, info in patterns.items()
        ]
    
    return patterns_summary


@router.post("/learn-pattern")
async def learn_pattern(
    language: str,
    pattern_name: str,
    pattern_regex: str,
    message: str,
    severity: str = "medium",
    category: str = "custom"
):
    """Add a custom review pattern (learning from user feedback)"""
    
    custom_pattern = {
        "id": str(uuid.uuid4()),
        "language": language,
        "pattern_name": pattern_name,
        "pattern_regex": pattern_regex,
        "message": message,
        "severity": severity,
        "category": category,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "usage_count": 0
    }
    
    await db.custom_review_patterns.insert_one(custom_pattern)
    
    return {"status": "learned", "pattern": custom_pattern}
