"""
Voice Control Routes - Speech-to-text and voice command processing
Uses OpenAI Whisper for transcription via Emergent LLM Key
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime, timezone
import os
import re
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/voice", tags=["voice"])

# Voice command patterns
VOICE_COMMANDS = {
    "create_project": {
        "patterns": [
            r"create (?:a )?(?:new )?project(?: called| named)? (.+)",
            r"new project(?: called| named)? (.+)",
            r"start (?:a )?(?:new )?project (.+)"
        ],
        "action": "create_project",
        "description": "Create a new project"
    },
    "run_build": {
        "patterns": [
            r"run (?:a )?build",
            r"start (?:a )?build",
            r"build (?:the )?project",
            r"execute build"
        ],
        "action": "run_build",
        "description": "Run a build for the current project"
    },
    "deploy": {
        "patterns": [
            r"deploy(?: to)? (vercel|railway|itch)",
            r"push to (vercel|railway|itch)",
            r"ship(?: to)? (vercel|railway|itch)"
        ],
        "action": "deploy",
        "description": "Deploy to a platform"
    },
    "create_file": {
        "patterns": [
            r"create (?:a )?(?:new )?file(?: called| named)? (.+)",
            r"new file (.+)",
            r"add (?:a )?file (.+)"
        ],
        "action": "create_file",
        "description": "Create a new file"
    },
    "delete_file": {
        "patterns": [
            r"delete (?:the )?file (.+)",
            r"remove (?:the )?file (.+)"
        ],
        "action": "delete_file",
        "description": "Delete a file"
    },
    "run_tests": {
        "patterns": [
            r"run (?:the )?tests",
            r"execute tests",
            r"test (?:the )?project"
        ],
        "action": "run_tests",
        "description": "Run project tests"
    },
    "show_status": {
        "patterns": [
            r"(?:show|get|what(?:'s| is)) (?:the )?(?:project )?status",
            r"status(?: update)?",
            r"how(?:'s| is) (?:the )?project"
        ],
        "action": "show_status",
        "description": "Show project status"
    },
    "list_files": {
        "patterns": [
            r"(?:list|show|get) (?:all )?(?:the )?files",
            r"what files (?:do we have|are there)"
        ],
        "action": "list_files",
        "description": "List project files"
    },
    "open_file": {
        "patterns": [
            r"open (?:the )?file (.+)",
            r"show (?:me )?(?:the )?file (.+)",
            r"edit (?:the )?file (.+)"
        ],
        "action": "open_file",
        "description": "Open a file for editing"
    },
    "generate_image": {
        "patterns": [
            r"generate (?:an? )?image (?:of )?(.+)",
            r"create (?:an? )?image (?:of )?(.+)",
            r"make (?:an? )?(?:picture|image) (?:of )?(.+)"
        ],
        "action": "generate_image",
        "description": "Generate an AI image"
    },
    "ask_agent": {
        "patterns": [
            r"ask (?:the )?(commander|atlas|forge|sentinel|probe|prism)(?: to)? (.+)",
            r"tell (?:the )?(commander|atlas|forge|sentinel|probe|prism)(?: to)? (.+)",
            r"(commander|atlas|forge|sentinel|probe|prism)[,:]? (.+)"
        ],
        "action": "ask_agent",
        "description": "Ask a specific agent to do something"
    },
    "help": {
        "patterns": [
            r"(?:what can you do|help|commands|what commands)",
            r"show (?:me )?(?:the )?commands",
            r"voice commands"
        ],
        "action": "help",
        "description": "Show available voice commands"
    }
}


def parse_voice_command(text: str) -> dict:
    """Parse transcribed text into a structured command"""
    text_lower = text.lower().strip()
    
    for cmd_name, cmd_info in VOICE_COMMANDS.items():
        for pattern in cmd_info["patterns"]:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                return {
                    "command": cmd_info["action"],
                    "description": cmd_info["description"],
                    "parameters": list(match.groups()) if match.groups() else [],
                    "original_text": text,
                    "confidence": 1.0
                }
    
    # No command matched - treat as general chat/question
    return {
        "command": "chat",
        "description": "General conversation or question",
        "parameters": [text],
        "original_text": text,
        "confidence": 0.5
    }


@router.get("/commands")
async def get_voice_commands():
    """Get list of available voice commands"""
    commands = []
    for cmd_name, cmd_info in VOICE_COMMANDS.items():
        commands.append({
            "name": cmd_name,
            "action": cmd_info["action"],
            "description": cmd_info["description"],
            "example_phrases": cmd_info["patterns"][:2]  # Show first 2 patterns
        })
    return {
        "commands": commands,
        "total": len(commands),
        "tip": "Speak naturally - the system understands variations of these commands"
    }


@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = "en"
):
    """
    Transcribe audio file to text using OpenAI Whisper
    Supported formats: mp3, mp4, mpeg, mpga, m4a, wav, webm
    Max file size: 25 MB
    """
    # Validate file format
    allowed_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed: {', '.join(allowed_formats)}"
        )
    
    # Check file size (25 MB limit)
    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="File too large. Maximum size is 25 MB."
        )
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="Speech-to-text API key not configured"
        )
    
    try:
        from emergentintegrations.llm.openai import OpenAISpeechToText
        import tempfile
        
        # Save to temp file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        stt = OpenAISpeechToText(api_key=api_key)
        
        with open(tmp_path, "rb") as audio_file:
            response = await stt.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="json",
                language=language
            )
        
        # Clean up temp file
        os.unlink(tmp_path)
        
        transcribed_text = response.text
        
        return {
            "success": True,
            "text": transcribed_text,
            "language": language,
            "duration_seconds": getattr(response, 'duration', None),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(e)}"
        )


@router.post("/command")
async def process_voice_command(
    file: UploadFile = File(...),
    project_id: str = None,
    language: str = "en"
):
    """
    Full voice command pipeline:
    1. Transcribe audio to text
    2. Parse command from text
    3. Return structured command for execution
    """
    # First transcribe
    allowed_formats = ["mp3", "mp4", "mpeg", "mpga", "m4a", "wav", "webm"]
    file_ext = file.filename.split(".")[-1].lower() if file.filename else ""
    
    if file_ext not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format. Allowed: {', '.join(allowed_formats)}"
        )
    
    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 25 MB.")
    
    api_key = os.getenv("EMERGENT_LLM_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="API key not configured")
    
    try:
        from emergentintegrations.llm.openai import OpenAISpeechToText
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_ext}") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        
        stt = OpenAISpeechToText(api_key=api_key)
        
        with open(tmp_path, "rb") as audio_file:
            response = await stt.transcribe(
                file=audio_file,
                model="whisper-1",
                response_format="json",
                language=language,
                prompt="Voice command for software development. Commands like: create project, run build, deploy, create file, delete file, run tests, show status."
            )
        
        os.unlink(tmp_path)
        transcribed_text = response.text
        
        # Parse the command
        parsed = parse_voice_command(transcribed_text)
        
        return {
            "success": True,
            "transcription": transcribed_text,
            "command": parsed,
            "project_id": project_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "execution_hint": _get_execution_hint(parsed, project_id)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice command failed: {str(e)}")


def _get_execution_hint(parsed: dict, project_id: str) -> dict:
    """Generate execution hints for the frontend"""
    action = parsed["command"]
    params = parsed["parameters"]
    
    hints = {
        "create_project": {
            "endpoint": "/api/projects",
            "method": "POST",
            "body": {"name": params[0] if params else "New Project"}
        },
        "run_build": {
            "endpoint": f"/api/celery/jobs/submit?project_id={project_id}&job_type=build",
            "method": "POST"
        },
        "deploy": {
            "endpoint": f"/api/deploy/instant?project_id={project_id}&platform={params[0] if params else 'vercel'}",
            "method": "POST"
        },
        "create_file": {
            "endpoint": f"/api/files?project_id={project_id}",
            "method": "POST",
            "body": {"name": params[0] if params else "new_file.js"}
        },
        "run_tests": {
            "endpoint": f"/api/celery/jobs/submit?project_id={project_id}&job_type=test",
            "method": "POST"
        },
        "show_status": {
            "endpoint": f"/api/projects/{project_id}",
            "method": "GET"
        },
        "list_files": {
            "endpoint": f"/api/files?project_id={project_id}",
            "method": "GET"
        },
        "generate_image": {
            "endpoint": f"/api/images/generate?project_id={project_id}",
            "method": "POST",
            "body": {"prompt": params[0] if params else ""}
        },
        "help": {
            "endpoint": "/api/voice/commands",
            "method": "GET"
        },
        "chat": {
            "endpoint": f"/api/chat?project_id={project_id}",
            "method": "POST",
            "body": {"message": params[0] if params else ""}
        }
    }
    
    return hints.get(action, {"message": "Execute via frontend UI"})


@router.post("/parse")
async def parse_text_command(text: str):
    """Parse text into a voice command (for testing without audio)"""
    parsed = parse_voice_command(text)
    return {
        "input_text": text,
        "parsed_command": parsed,
        "execution_hint": _get_execution_hint(parsed, "test-project")
    }
