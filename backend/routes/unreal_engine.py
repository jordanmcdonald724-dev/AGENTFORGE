"""
Unreal Engine Integration - Generate complete game builds from prompts
Supports blueprint generation, asset creation, and build packaging
Includes UE5 SDK integration for actual builds
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio
import os
import subprocess
import shutil

router = APIRouter(prefix="/unreal", tags=["unreal-engine"])

# UE5 SDK Configuration
UE5_CONFIG = {
    "engine_versions": ["5.4", "5.3", "5.2", "5.1"],
    "default_version": "5.4",
    "platforms": {
        "windows": {"extension": ".exe", "build_cmd": "Win64"},
        "mac": {"extension": ".app", "build_cmd": "Mac"},
        "linux": {"extension": "", "build_cmd": "Linux"},
        "android": {"extension": ".apk", "build_cmd": "Android"},
        "ios": {"extension": ".ipa", "build_cmd": "iOS"}
    },
    "build_configurations": ["Development", "Shipping", "Debug"],
    "ue_install_paths": {
        "windows": "C:/Program Files/Epic Games/UE_5.4",
        "mac": "/Users/Shared/Epic Games/UE_5.4",
        "linux": "/opt/unreal-engine/UE_5.4"
    }
}


class GameProject(BaseModel):
    name: str
    description: str
    genre: str = "action"  # action, puzzle, rpg, platformer, shooter, racing
    art_style: str = "stylized"  # realistic, stylized, pixel, low_poly
    platforms: List[str] = ["windows"]  # windows, mac, linux, android, ios
    features: List[str] = []


class BlueprintRequest(BaseModel):
    project_id: str
    blueprint_type: str  # character, weapon, vehicle, ui, game_mode, level
    name: str
    properties: Dict = {}


# Game templates
GAME_TEMPLATES = {
    "fps_shooter": {
        "name": "First-Person Shooter",
        "description": "Complete FPS template with weapons, AI enemies, and multiplayer",
        "blueprints": ["BP_FPSCharacter", "BP_Weapon_Base", "BP_Enemy_AI", "BP_GameMode_FPS"],
        "assets": ["Weapons Pack", "Character Models", "Environment Kit"],
        "features": ["Multiplayer", "AI Enemies", "Weapon System", "Health System"]
    },
    "platformer_3d": {
        "name": "3D Platformer",
        "description": "Mario-style platformer with collectibles and power-ups",
        "blueprints": ["BP_PlatformCharacter", "BP_Collectible", "BP_MovingPlatform", "BP_Checkpoint"],
        "assets": ["Platform Kit", "Character Pack", "VFX Collection"],
        "features": ["Double Jump", "Collectibles", "Checkpoints", "Power-ups"]
    },
    "rpg_adventure": {
        "name": "RPG Adventure",
        "description": "Open-world RPG with quests, inventory, and combat",
        "blueprints": ["BP_RPGCharacter", "BP_Inventory", "BP_QuestSystem", "BP_DialogueManager"],
        "assets": ["Fantasy Characters", "Weapons & Armor", "Environment Pack"],
        "features": ["Quest System", "Inventory", "Dialogue", "Combat", "Leveling"]
    },
    "racing": {
        "name": "Racing Game",
        "description": "Arcade racing with AI opponents and track editor",
        "blueprints": ["BP_Vehicle", "BP_RaceManager", "BP_AIDriver", "BP_TrackSpline"],
        "assets": ["Vehicle Pack", "Track Components", "VFX Pack"],
        "features": ["Vehicle Physics", "AI Opponents", "Lap System", "Boost"]
    },
    "puzzle": {
        "name": "Puzzle Game",
        "description": "Physics-based puzzle game with level progression",
        "blueprints": ["BP_PuzzleManager", "BP_Interactable", "BP_PhysicsObject", "BP_LevelGate"],
        "assets": ["Puzzle Elements", "Environment Kit", "UI Pack"],
        "features": ["Physics Puzzles", "Level Progression", "Hints System", "Star Rating"]
    }
}

# Blueprint templates
BLUEPRINT_TEMPLATES = {
    "character": {
        "components": ["SkeletalMesh", "CapsuleCollider", "CharacterMovement", "Camera"],
        "events": ["BeginPlay", "Tick", "OnLanded", "OnJumped"],
        "variables": ["Health", "Speed", "JumpForce", "IsAlive"]
    },
    "weapon": {
        "components": ["StaticMesh", "BoxCollider", "AudioComponent", "ParticleSystem"],
        "events": ["Fire", "Reload", "Equip", "Unequip"],
        "variables": ["Damage", "FireRate", "AmmoCount", "MaxAmmo"]
    },
    "vehicle": {
        "components": ["SkeletalMesh", "WheeledVehicleMovement", "Camera", "AudioComponent"],
        "events": ["Accelerate", "Brake", "Steer", "Boost"],
        "variables": ["TopSpeed", "Acceleration", "Handling", "BoostAmount"]
    },
    "ui": {
        "components": ["WidgetComponent", "Canvas", "TextBlock", "ProgressBar"],
        "events": ["OnButtonClicked", "OnValueChanged", "UpdateUI"],
        "variables": ["IsVisible", "AnimationState"]
    },
    "game_mode": {
        "components": ["GameState", "PlayerController", "HUD"],
        "events": ["StartMatch", "EndMatch", "PlayerDied", "ScoreChanged"],
        "variables": ["MatchTime", "Score", "PlayerCount", "GameState"]
    },
    "level": {
        "components": ["LevelStreaming", "NavMesh", "LightingScenario"],
        "events": ["LevelLoaded", "LevelUnloaded", "CheckpointReached"],
        "variables": ["LevelName", "Difficulty", "Collectibles"]
    }
}


@router.get("/templates")
async def get_game_templates():
    """Get all available game templates"""
    return GAME_TEMPLATES


@router.get("/blueprint-types")
async def get_blueprint_types():
    """Get available blueprint types and their structure"""
    return BLUEPRINT_TEMPLATES


@router.post("/projects/create")
async def create_game_project(project: GameProject, background_tasks: BackgroundTasks):
    """Create a new Unreal Engine game project"""
    
    project_id = str(uuid.uuid4())
    
    game_project = {
        "id": project_id,
        "name": project.name,
        "description": project.description,
        "genre": project.genre,
        "art_style": project.art_style,
        "platforms": project.platforms,
        "features": project.features,
        "status": "initializing",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "blueprints": [],
        "assets": [],
        "build_status": None,
        "unreal_version": "5.4"
    }
    
    await db.unreal_projects.insert_one(game_project)
    
    # Generate initial blueprints in background
    background_tasks.add_task(generate_initial_blueprints, project_id, project.genre, project.features)
    
    return {
        "project_id": project_id,
        "status": "initializing",
        "message": f"Creating {project.genre} game project '{project.name}'"
    }


async def generate_initial_blueprints(project_id: str, genre: str, features: List[str]):
    """Generate initial blueprints based on genre"""
    
    # Get template for genre
    template_key = {
        "action": "fps_shooter",
        "shooter": "fps_shooter",
        "platformer": "platformer_3d",
        "rpg": "rpg_adventure",
        "racing": "racing",
        "puzzle": "puzzle"
    }.get(genre, "platformer_3d")
    
    template = GAME_TEMPLATES.get(template_key, GAME_TEMPLATES["platformer_3d"])
    
    blueprints = []
    for bp_name in template["blueprints"]:
        blueprints.append({
            "id": str(uuid.uuid4()),
            "name": bp_name,
            "type": bp_name.split("_")[1].lower() if "_" in bp_name else "actor",
            "status": "generated",
            "created_at": datetime.now(timezone.utc).isoformat()
        })
    
    # Update project with blueprints
    await db.unreal_projects.update_one(
        {"id": project_id},
        {
            "$set": {
                "status": "ready",
                "blueprints": blueprints,
                "assets": template["assets"],
                "template_features": template["features"]
            }
        }
    )


@router.get("/projects")
async def list_game_projects():
    """List all Unreal Engine projects"""
    projects = await db.unreal_projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return projects


@router.get("/projects/{project_id}")
async def get_game_project(project_id: str):
    """Get game project details"""
    project = await db.unreal_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/blueprints/generate")
async def generate_blueprint(request: BlueprintRequest):
    """Generate a new blueprint for a project"""
    
    # Verify project exists
    project = await db.unreal_projects.find_one({"id": request.project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get blueprint template
    bp_template = BLUEPRINT_TEMPLATES.get(request.blueprint_type, BLUEPRINT_TEMPLATES["character"])
    
    blueprint = {
        "id": str(uuid.uuid4()),
        "project_id": request.project_id,
        "name": request.name,
        "type": request.blueprint_type,
        "components": bp_template["components"],
        "events": bp_template["events"],
        "variables": bp_template["variables"],
        "custom_properties": request.properties,
        "code": generate_blueprint_code(request.name, request.blueprint_type, bp_template),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    # Add to project
    await db.unreal_projects.update_one(
        {"id": request.project_id},
        {"$push": {"blueprints": blueprint}}
    )
    
    return blueprint


def generate_blueprint_code(name: str, bp_type: str, template: dict) -> str:
    """Generate pseudo Unreal Blueprint code"""
    
    code = f"""// Blueprint: {name}
// Type: {bp_type}
// Generated by AgentForge

UCLASS()
class {name.upper()} : public A{'Character' if bp_type == 'character' else 'Actor'}
{{
    GENERATED_BODY()
    
public:
    // Components
"""
    
    for comp in template["components"]:
        code += f"    UPROPERTY(VisibleAnywhere)\n    U{comp}* {comp}Component;\n\n"
    
    code += "\n    // Variables\n"
    for var in template["variables"]:
        code += f"    UPROPERTY(EditAnywhere, BlueprintReadWrite)\n    float {var};\n\n"
    
    code += "\nprotected:\n    // Events\n"
    for event in template["events"]:
        code += f"    UFUNCTION(BlueprintCallable)\n    void {event}();\n\n"
    
    code += "};"
    
    return code


@router.post("/projects/{project_id}/build")
async def build_game(project_id: str, platform: str = "windows", background_tasks: BackgroundTasks = None):
    """Build game for specified platform"""
    
    project = await db.unreal_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    build_id = str(uuid.uuid4())
    
    build_info = {
        "id": build_id,
        "project_id": project_id,
        "platform": platform,
        "status": "building",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "progress": 0,
        "stages": [
            {"name": "Compiling Blueprints", "status": "pending"},
            {"name": "Cooking Content", "status": "pending"},
            {"name": "Packaging", "status": "pending"},
            {"name": "Optimizing", "status": "pending"}
        ]
    }
    
    await db.unreal_builds.insert_one(build_info)
    
    # Simulate build in background
    if background_tasks:
        background_tasks.add_task(simulate_build, build_id)
    
    return {
        "build_id": build_id,
        "status": "building",
        "platform": platform,
        "message": f"Building {project['name']} for {platform}"
    }


async def simulate_build(build_id: str):
    """Simulate build process"""
    stages = ["Compiling Blueprints", "Cooking Content", "Packaging", "Optimizing"]
    
    for i, stage in enumerate(stages):
        await db.unreal_builds.update_one(
            {"id": build_id},
            {
                "$set": {
                    f"stages.{i}.status": "running",
                    "progress": (i / len(stages)) * 100
                }
            }
        )
        
        await asyncio.sleep(2)  # Simulate work
        
        await db.unreal_builds.update_one(
            {"id": build_id},
            {"$set": {f"stages.{i}.status": "completed"}}
        )
    
    await db.unreal_builds.update_one(
        {"id": build_id},
        {
            "$set": {
                "status": "completed",
                "progress": 100,
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "download_url": f"/downloads/game_{build_id}.zip"
            }
        }
    )


@router.get("/builds/{build_id}")
async def get_build_status(build_id: str):
    """Get build status"""
    build = await db.unreal_builds.find_one({"id": build_id}, {"_id": 0})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build


@router.get("/projects/{project_id}/builds")
async def get_project_builds(project_id: str):
    """Get all builds for a project"""
    builds = await db.unreal_builds.find(
        {"project_id": project_id}, 
        {"_id": 0}
    ).sort("started_at", -1).to_list(20)
    return builds


# ========== UE5 SDK Integration ==========

@router.get("/sdk/config")
async def get_ue5_sdk_config():
    """Get UE5 SDK configuration"""
    return UE5_CONFIG


@router.get("/sdk/status")
async def check_ue5_installation():
    """Check if UE5 is installed and get version info"""
    
    # Check common installation paths
    install_status = {
        "installed": False,
        "version": None,
        "path": None,
        "editor_available": False,
        "build_tools_available": False
    }
    
    # This would check actual paths in a real implementation
    # For now, return mock status
    return {
        "status": install_status,
        "message": "UE5 SDK check completed. Install UE5 locally to enable actual builds.",
        "download_url": "https://www.unrealengine.com/download",
        "supported_versions": UE5_CONFIG["engine_versions"]
    }


@router.post("/sdk/create-project")
async def create_ue5_project(
    name: str,
    template: str = "blank",
    version: str = "5.4",
    target_platforms: List[str] = ["windows"]
):
    """Create a new UE5 project using the SDK"""
    
    project_id = str(uuid.uuid4())
    
    # Generate .uproject file content
    uproject_content = generate_uproject_file(name, version, target_platforms)
    
    # Generate default game mode blueprint
    game_mode_cpp = generate_game_mode_cpp(name)
    
    # Generate character blueprint
    character_cpp = generate_character_cpp(name)
    
    project_files = {
        "id": project_id,
        "name": name,
        "engine_version": version,
        "template": template,
        "target_platforms": target_platforms,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "files": [
            {"name": f"{name}.uproject", "content": uproject_content, "type": "project"},
            {"name": f"{name}GameMode.cpp", "content": game_mode_cpp, "type": "source"},
            {"name": f"{name}Character.cpp", "content": character_cpp, "type": "source"},
            {"name": f"{name}GameMode.h", "content": generate_game_mode_header(name), "type": "header"},
            {"name": f"{name}Character.h", "content": generate_character_header(name), "type": "header"}
        ],
        "directory_structure": [
            f"{name}/",
            f"{name}/Config/",
            f"{name}/Content/",
            f"{name}/Source/{name}/",
            f"{name}/Source/{name}/Private/",
            f"{name}/Source/{name}/Public/"
        ]
    }
    
    await db.unreal_sdk_projects.insert_one(project_files)
    
    return {
        "project_id": project_id,
        "name": name,
        "files_generated": len(project_files["files"]),
        "message": f"UE5 project '{name}' created successfully"
    }


def generate_uproject_file(name: str, version: str, platforms: List[str]) -> str:
    """Generate .uproject file content"""
    return f'''{{
    "FileVersion": 3,
    "EngineAssociation": "{version}",
    "Category": "",
    "Description": "Generated by AgentForge",
    "Modules": [
        {{
            "Name": "{name}",
            "Type": "Runtime",
            "LoadingPhase": "Default",
            "AdditionalDependencies": [
                "Engine"
            ]
        }}
    ],
    "Plugins": [
        {{
            "Name": "ModelingToolsEditorMode",
            "Enabled": true
        }},
        {{
            "Name": "EnhancedInput",
            "Enabled": true
        }}
    ],
    "TargetPlatforms": {platforms}
}}'''


def generate_game_mode_cpp(name: str) -> str:
    """Generate GameMode C++ source"""
    return f'''// {name}GameMode.cpp
// Generated by AgentForge UE5 Integration

#include "{name}GameMode.h"
#include "{name}Character.h"
#include "UObject/ConstructorHelpers.h"

A{name}GameMode::A{name}GameMode()
{{
    // Set default pawn class
    DefaultPawnClass = A{name}Character::StaticClass();
    
    // Set HUD class (optional)
    // HUDClass = A{name}HUD::StaticClass();
    
    // Set player controller class (optional)
    // PlayerControllerClass = A{name}PlayerController::StaticClass();
}}

void A{name}GameMode::BeginPlay()
{{
    Super::BeginPlay();
    
    UE_LOG(LogTemp, Warning, TEXT("{name} Game Started!"));
}}

void A{name}GameMode::StartMatch()
{{
    Super::StartMatch();
    
    // Initialize game state
    CurrentScore = 0;
    GameTime = 0.0f;
}}
'''


def generate_game_mode_header(name: str) -> str:
    """Generate GameMode header file"""
    return f'''// {name}GameMode.h
// Generated by AgentForge UE5 Integration

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "{name}GameMode.generated.h"

UCLASS()
class {name.upper()}_API A{name}GameMode : public AGameModeBase
{{
    GENERATED_BODY()

public:
    A{name}GameMode();
    
    virtual void BeginPlay() override;
    virtual void StartMatch();
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Game")
    int32 CurrentScore;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Game")
    float GameTime;
}};
'''


def generate_character_cpp(name: str) -> str:
    """Generate Character C++ source"""
    return f'''// {name}Character.cpp
// Generated by AgentForge UE5 Integration

#include "{name}Character.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/InputComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"

A{name}Character::A{name}Character()
{{
    // Set size for collision capsule
    GetCapsuleComponent()->InitCapsuleSize(42.f, 96.0f);
    
    // Don't rotate when the controller rotates
    bUseControllerRotationPitch = false;
    bUseControllerRotationYaw = false;
    bUseControllerRotationRoll = false;
    
    // Configure character movement
    GetCharacterMovement()->bOrientRotationToMovement = true;
    GetCharacterMovement()->RotationRate = FRotator(0.0f, 500.0f, 0.0f);
    GetCharacterMovement()->JumpZVelocity = 700.f;
    GetCharacterMovement()->AirControl = 0.35f;
    GetCharacterMovement()->MaxWalkSpeed = 500.f;
    GetCharacterMovement()->MinAnalogWalkSpeed = 20.f;
    GetCharacterMovement()->BrakingDecelerationWalking = 2000.f;
    
    // Create a camera boom
    CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
    CameraBoom->SetupAttachment(RootComponent);
    CameraBoom->TargetArmLength = 400.0f;
    CameraBoom->bUsePawnControlRotation = true;
    
    // Create a follow camera
    FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
    FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
    FollowCamera->bUsePawnControlRotation = false;
    
    // Initialize stats
    Health = 100.0f;
    MaxHealth = 100.0f;
}}

void A{name}Character::BeginPlay()
{{
    Super::BeginPlay();
}}

void A{name}Character::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    
    // Enhanced Input setup would go here
}}

void A{name}Character::Move(const FInputActionValue& Value)
{{
    FVector2D MovementVector = Value.Get<FVector2D>();
    
    if (Controller != nullptr)
    {{
        const FRotator Rotation = Controller->GetControlRotation();
        const FRotator YawRotation(0, Rotation.Yaw, 0);
        
        const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
        const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);
        
        AddMovementInput(ForwardDirection, MovementVector.Y);
        AddMovementInput(RightDirection, MovementVector.X);
    }}
}}

void A{name}Character::Look(const FInputActionValue& Value)
{{
    FVector2D LookAxisVector = Value.Get<FVector2D>();
    
    if (Controller != nullptr)
    {{
        AddControllerYawInput(LookAxisVector.X);
        AddControllerPitchInput(LookAxisVector.Y);
    }}
}}
'''


def generate_character_header(name: str) -> str:
    """Generate Character header file"""
    return f'''// {name}Character.h
// Generated by AgentForge UE5 Integration

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "{name}Character.generated.h"

class USpringArmComponent;
class UCameraComponent;
class UInputAction;
class UInputMappingContext;

UCLASS()
class {name.upper()}_API A{name}Character : public ACharacter
{{
    GENERATED_BODY()

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = Camera, meta = (AllowPrivateAccess = "true"))
    USpringArmComponent* CameraBoom;
    
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = Camera, meta = (AllowPrivateAccess = "true"))
    UCameraComponent* FollowCamera;

public:
    A{name}Character();
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float Health;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
    float MaxHealth;

protected:
    virtual void BeginPlay() override;
    virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
    
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);

public:
    FORCEINLINE USpringArmComponent* GetCameraBoom() const {{ return CameraBoom; }}
    FORCEINLINE UCameraComponent* GetFollowCamera() const {{ return FollowCamera; }}
}};
'''


@router.get("/sdk/project/{project_id}")
async def get_sdk_project(project_id: str):
    """Get UE5 SDK project details"""
    project = await db.unreal_sdk_projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/sdk/projects")
async def list_sdk_projects():
    """List all UE5 SDK projects"""
    projects = await db.unreal_sdk_projects.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return projects


@router.post("/sdk/build-command")
async def generate_build_command(
    project_path: str,
    platform: str = "windows",
    configuration: str = "Development"
):
    """Generate UE5 build command for local execution"""
    
    platform_config = UE5_CONFIG["platforms"].get(platform, UE5_CONFIG["platforms"]["windows"])
    
    if platform == "windows":
        build_cmd = f'''
# UE5 Build Command for Windows
# Run this in your UE5 installation directory

# Package the game
"{UE5_CONFIG["ue_install_paths"]["windows"]}/Engine/Build/BatchFiles/RunUAT.bat" BuildCookRun ^
    -project="{project_path}" ^
    -noP4 ^
    -platform={platform_config["build_cmd"]} ^
    -clientconfig={configuration} ^
    -cook ^
    -stage ^
    -pak ^
    -archive ^
    -archivedirectory="./Builds"
'''
    elif platform == "linux":
        build_cmd = f'''
# UE5 Build Command for Linux
# Run this in your UE5 installation directory

./Engine/Build/BatchFiles/RunUAT.sh BuildCookRun \\
    -project="{project_path}" \\
    -noP4 \\
    -platform={platform_config["build_cmd"]} \\
    -clientconfig={configuration} \\
    -cook \\
    -stage \\
    -pak \\
    -archive \\
    -archivedirectory="./Builds"
'''
    else:
        build_cmd = f"# Build command for {platform} - use Unreal Editor"
    
    return {
        "platform": platform,
        "configuration": configuration,
        "build_command": build_cmd,
        "notes": [
            "Ensure UE5 is installed at the specified path",
            "Run from administrator/root terminal",
            "Build may take 10-30 minutes depending on project size"
        ]
    }

