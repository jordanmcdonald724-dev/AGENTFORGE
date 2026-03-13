# Routes module
from .health import router as health_router
from .agents import router as agents_router
from .projects import router as projects_router
from .chat import router as chat_router
from .files import router as files_router
from .tasks import router as tasks_router
from .images import router as images_router
from .plans import router as plans_router
from .github import router as github_router
from .builds import router as builds_router
from .collaboration import router as collaboration_router
from .sandbox import router as sandbox_router
from .command_center import router as command_center_router
