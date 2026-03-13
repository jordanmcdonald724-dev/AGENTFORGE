"""
Mobile App Builder - Autonomous mobile app generation for iOS/Android
Generates React Native, Flutter, or native code from prompts
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime, timezone
from core.database import db
import uuid
import asyncio

router = APIRouter(prefix="/mobile-builder", tags=["mobile-builder"])


class MobileAppRequest(BaseModel):
    name: str
    description: str
    framework: str = "react_native"  # react_native, flutter, native_ios, native_android
    platforms: List[str] = ["ios", "android"]
    features: List[str] = []
    style: str = "modern"  # modern, minimal, playful, corporate


class ScreenRequest(BaseModel):
    app_id: str
    screen_type: str  # home, list, detail, form, profile, settings, auth
    name: str
    properties: Dict = {}


# Mobile frameworks
FRAMEWORKS = {
    "react_native": {
        "name": "React Native",
        "language": "JavaScript/TypeScript",
        "platforms": ["ios", "android"],
        "features": ["Hot Reload", "Native Performance", "Large Ecosystem"],
        "setup_command": "npx react-native init"
    },
    "flutter": {
        "name": "Flutter",
        "language": "Dart",
        "platforms": ["ios", "android", "web", "desktop"],
        "features": ["Hot Reload", "Widget System", "Material/Cupertino"],
        "setup_command": "flutter create"
    },
    "native_ios": {
        "name": "iOS Native (SwiftUI)",
        "language": "Swift",
        "platforms": ["ios"],
        "features": ["Best Performance", "Latest iOS APIs", "SwiftUI"],
        "setup_command": "xcode project"
    },
    "native_android": {
        "name": "Android Native (Compose)",
        "language": "Kotlin",
        "platforms": ["android"],
        "features": ["Best Performance", "Latest Android APIs", "Jetpack Compose"],
        "setup_command": "android studio project"
    }
}

# Screen templates
SCREEN_TEMPLATES = {
    "home": {
        "components": ["Header", "HeroSection", "FeatureGrid", "BottomNav"],
        "navigation": ["detail", "profile", "settings"]
    },
    "list": {
        "components": ["SearchBar", "FilterTabs", "ListView", "ListItem", "FloatingButton"],
        "navigation": ["detail", "form"]
    },
    "detail": {
        "components": ["ImageCarousel", "TitleSection", "ContentBody", "ActionButtons"],
        "navigation": ["back", "share", "edit"]
    },
    "form": {
        "components": ["FormHeader", "InputFields", "Validation", "SubmitButton"],
        "navigation": ["back", "success"]
    },
    "profile": {
        "components": ["Avatar", "UserInfo", "StatsRow", "MenuList"],
        "navigation": ["settings", "edit", "logout"]
    },
    "settings": {
        "components": ["SettingsGroup", "ToggleItem", "LinkItem", "VersionInfo"],
        "navigation": ["back"]
    },
    "auth": {
        "components": ["Logo", "LoginForm", "SocialButtons", "ForgotPassword"],
        "navigation": ["home", "register", "forgot"]
    }
}

# App templates
APP_TEMPLATES = {
    "social": {
        "name": "Social Media",
        "screens": ["auth", "home", "profile", "list", "detail", "settings"],
        "features": ["Authentication", "Feed", "Profiles", "Messaging", "Notifications"]
    },
    "ecommerce": {
        "name": "E-Commerce",
        "screens": ["home", "list", "detail", "cart", "checkout", "profile"],
        "features": ["Product Catalog", "Shopping Cart", "Checkout", "Orders", "Wishlist"]
    },
    "fitness": {
        "name": "Fitness Tracker",
        "screens": ["home", "workouts", "progress", "profile", "settings"],
        "features": ["Workout Tracking", "Progress Charts", "Goals", "Reminders"]
    },
    "delivery": {
        "name": "Delivery App",
        "screens": ["home", "map", "orders", "detail", "profile"],
        "features": ["Real-time Tracking", "Order Management", "Maps Integration"]
    },
    "news": {
        "name": "News Reader",
        "screens": ["home", "categories", "detail", "bookmarks", "settings"],
        "features": ["Article Feed", "Categories", "Bookmarks", "Offline Reading"]
    },
    "blank": {
        "name": "Blank Template",
        "screens": ["home"],
        "features": []
    }
}


@router.get("/frameworks")
async def get_frameworks():
    """Get available mobile frameworks"""
    return FRAMEWORKS


@router.get("/templates")
async def get_app_templates():
    """Get available app templates"""
    return APP_TEMPLATES


@router.get("/screen-types")
async def get_screen_types():
    """Get available screen types"""
    return SCREEN_TEMPLATES


@router.post("/apps")
async def create_mobile_app(request: MobileAppRequest, background_tasks: BackgroundTasks):
    """Create a new mobile app project"""
    
    app_id = str(uuid.uuid4())
    framework_info = FRAMEWORKS.get(request.framework, FRAMEWORKS["react_native"])
    
    app = {
        "id": app_id,
        "name": request.name,
        "description": request.description,
        "framework": request.framework,
        "framework_info": framework_info,
        "platforms": request.platforms,
        "features": request.features,
        "style": request.style,
        "status": "generating",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "screens": [],
        "components": [],
        "navigation": {},
        "build_status": None
    }
    
    await db.mobile_apps.insert_one(app)
    
    # Generate app structure in background
    background_tasks.add_task(generate_app_structure, app_id, request)
    
    return {
        "app_id": app_id,
        "framework": framework_info["name"],
        "status": "generating",
        "message": f"Creating {request.name} with {framework_info['name']}"
    }


async def generate_app_structure(app_id: str, request: MobileAppRequest):
    """Generate app structure and screens"""
    
    # Determine screens based on features
    screens = []
    basic_screens = ["home", "profile", "settings"]
    
    if "Authentication" in request.features or "auth" in request.features:
        screens.append(generate_screen_config("auth", request.framework))
    
    for screen_type in basic_screens:
        screens.append(generate_screen_config(screen_type, request.framework))
    
    if "list" in [f.lower() for f in request.features] or len(request.features) > 2:
        screens.append(generate_screen_config("list", request.framework))
        screens.append(generate_screen_config("detail", request.framework))
    
    # Generate navigation config
    navigation = generate_navigation_config(screens, request.framework)
    
    # Generate app config files
    config_files = generate_config_files(request.name, request.framework, request.platforms)
    
    # Update app
    await db.mobile_apps.update_one(
        {"id": app_id},
        {
            "$set": {
                "status": "ready",
                "screens": screens,
                "navigation": navigation,
                "config_files": config_files,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        }
    )


def generate_screen_config(screen_type: str, framework: str) -> dict:
    """Generate screen configuration"""
    template = SCREEN_TEMPLATES.get(screen_type, SCREEN_TEMPLATES["home"])
    
    return {
        "id": str(uuid.uuid4()),
        "type": screen_type,
        "name": f"{screen_type.capitalize()}Screen",
        "components": template["components"],
        "navigation_targets": template["navigation"],
        "code": generate_screen_code(screen_type, framework)
    }


def generate_screen_code(screen_type: str, framework: str) -> str:
    """Generate screen code based on framework"""
    
    if framework == "react_native":
        return generate_react_native_screen(screen_type)
    elif framework == "flutter":
        return generate_flutter_screen(screen_type)
    elif framework == "native_ios":
        return generate_swiftui_screen(screen_type)
    elif framework == "native_android":
        return generate_compose_screen(screen_type)
    
    return generate_react_native_screen(screen_type)


def generate_react_native_screen(screen_type: str) -> str:
    """Generate React Native screen code"""
    
    templates = {
        "home": '''import React from 'react';
import { View, Text, ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const HomeScreen = ({ navigation }) => {
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>Welcome</Text>
        </View>
        {/* Add your home content here */}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  header: { padding: 20 },
  title: { fontSize: 28, fontWeight: 'bold' }
});

export default HomeScreen;''',

        "auth": '''import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

const AuthScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = () => {
    // Add authentication logic
    navigation.replace('Home');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Login</Text>
      <TextInput
        style={styles.input}
        placeholder="Email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>Login</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 20 },
  title: { fontSize: 32, fontWeight: 'bold', marginBottom: 40, textAlign: 'center' },
  input: { borderWidth: 1, borderColor: '#ddd', padding: 15, borderRadius: 8, marginBottom: 15 },
  button: { backgroundColor: '#007AFF', padding: 15, borderRadius: 8, alignItems: 'center' },
  buttonText: { color: '#fff', fontSize: 16, fontWeight: '600' }
});

export default AuthScreen;''',

        "list": '''import React from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';

const ListScreen = ({ navigation }) => {
  const data = []; // Add your data source

  const renderItem = ({ item }) => (
    <TouchableOpacity 
      style={styles.item}
      onPress={() => navigation.navigate('Detail', { id: item.id })}
    >
      <Text style={styles.itemTitle}>{item.title}</Text>
      <Text style={styles.itemSubtitle}>{item.subtitle}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <FlatList
        data={data}
        renderItem={renderItem}
        keyExtractor={item => item.id}
        contentContainerStyle={styles.list}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f5' },
  list: { padding: 15 },
  item: { backgroundColor: '#fff', padding: 20, borderRadius: 12, marginBottom: 10 },
  itemTitle: { fontSize: 16, fontWeight: '600' },
  itemSubtitle: { fontSize: 14, color: '#666', marginTop: 4 }
});

export default ListScreen;'''
    }
    
    return templates.get(screen_type, templates["home"])


def generate_flutter_screen(screen_type: str) -> str:
    """Generate Flutter screen code"""
    return f'''import 'package:flutter/material.dart';

class {screen_type.capitalize()}Screen extends StatefulWidget {{
  const {screen_type.capitalize()}Screen({{Key? key}}) : super(key: key);

  @override
  State<{screen_type.capitalize()}Screen> createState() => _{screen_type.capitalize()}ScreenState();
}}

class _{screen_type.capitalize()}ScreenState extends State<{screen_type.capitalize()}Screen> {{
  @override
  Widget build(BuildContext context) {{
    return Scaffold(
      appBar: AppBar(
        title: const Text('{screen_type.capitalize()}'),
      ),
      body: Center(
        child: Text('{screen_type.capitalize()} Screen'),
      ),
    );
  }}
}}'''


def generate_swiftui_screen(screen_type: str) -> str:
    """Generate SwiftUI screen code"""
    return f'''import SwiftUI

struct {screen_type.capitalize()}View: View {{
    var body: some View {{
        NavigationView {{
            VStack {{
                Text("{screen_type.capitalize()}")
                    .font(.largeTitle)
                    .fontWeight(.bold)
                
                // Add your content here
            }}
            .navigationTitle("{screen_type.capitalize()}")
        }}
    }}
}}

struct {screen_type.capitalize()}View_Previews: PreviewProvider {{
    static var previews: some View {{
        {screen_type.capitalize()}View()
    }}
}}'''


def generate_compose_screen(screen_type: str) -> str:
    """Generate Jetpack Compose screen code"""
    return f'''package com.app.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun {screen_type.capitalize()}Screen(
    onNavigate: (String) -> Unit = {{}}
) {{
    Scaffold(
        topBar = {{
            TopAppBar(
                title = {{ Text("{screen_type.capitalize()}") }}
            )
        }}
    ) {{ padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {{
            Text(
                text = "{screen_type.capitalize()} Screen",
                style = MaterialTheme.typography.headlineMedium
            )
        }}
    }}
}}'''


def generate_navigation_config(screens: list, framework: str) -> dict:
    """Generate navigation configuration"""
    
    screen_names = [s["name"] for s in screens]
    
    return {
        "type": "stack" if framework in ["react_native", "flutter"] else "native",
        "initial_route": "HomeScreen" if "HomeScreen" in screen_names else screen_names[0],
        "screens": screen_names,
        "bottom_tabs": ["HomeScreen", "ListScreen", "ProfileScreen"] if len(screens) >= 3 else None
    }


def generate_config_files(name: str, framework: str, platforms: list) -> list:
    """Generate app configuration files"""
    
    files = []
    
    if framework == "react_native":
        files.append({
            "name": "app.json",
            "content": f'''{{
  "name": "{name}",
  "displayName": "{name}",
  "expo": {{
    "name": "{name}",
    "slug": "{name.lower().replace(" ", "-")}",
    "version": "1.0.0",
    "platforms": {platforms}
  }}
}}'''
        })
    
    elif framework == "flutter":
        files.append({
            "name": "pubspec.yaml",
            "content": f'''name: {name.lower().replace(" ", "_")}
description: A new Flutter project.
version: 1.0.0+1

environment:
  sdk: ">=3.0.0 <4.0.0"

dependencies:
  flutter:
    sdk: flutter
  cupertino_icons: ^1.0.2

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^2.0.0

flutter:
  uses-material-design: true
'''
        })
    
    return files


@router.get("/apps")
async def list_mobile_apps():
    """List all mobile apps"""
    apps = await db.mobile_apps.find({}, {"_id": 0}).sort("created_at", -1).to_list(50)
    return apps


@router.get("/apps/{app_id}")
async def get_mobile_app(app_id: str):
    """Get mobile app details"""
    app = await db.mobile_apps.find_one({"id": app_id}, {"_id": 0})
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app


@router.delete("/apps/{app_id}")
async def delete_mobile_app(app_id: str):
    """Delete a mobile app"""
    result = await db.mobile_apps.delete_one({"id": app_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="App not found")
    return {"message": "App deleted"}


@router.post("/apps/{app_id}/screens")
async def add_screen(app_id: str, request: ScreenRequest):
    """Add a new screen to an app"""
    
    app = await db.mobile_apps.find_one({"id": app_id}, {"_id": 0})
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    screen = generate_screen_config(request.screen_type, app["framework"])
    screen["name"] = request.name
    screen["custom_properties"] = request.properties
    
    await db.mobile_apps.update_one(
        {"id": app_id},
        {"$push": {"screens": screen}}
    )
    
    return screen


@router.post("/apps/{app_id}/build")
async def build_mobile_app(app_id: str, platform: str = "ios", background_tasks: BackgroundTasks = None):
    """Start a mobile app build"""
    
    app = await db.mobile_apps.find_one({"id": app_id}, {"_id": 0})
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    build_id = str(uuid.uuid4())
    
    build = {
        "id": build_id,
        "app_id": app_id,
        "platform": platform,
        "status": "building",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "stages": [
            {"name": "Installing dependencies", "status": "pending"},
            {"name": "Compiling assets", "status": "pending"},
            {"name": "Building native code", "status": "pending"},
            {"name": "Signing app", "status": "pending"},
            {"name": "Creating package", "status": "pending"}
        ]
    }
    
    await db.mobile_builds.insert_one(build)
    
    if background_tasks:
        background_tasks.add_task(simulate_mobile_build, build_id)
    
    return {"build_id": build_id, "status": "building", "platform": platform}


async def simulate_mobile_build(build_id: str):
    """Simulate mobile build process"""
    stages = ["Installing dependencies", "Compiling assets", "Building native code", "Signing app", "Creating package"]
    
    for i, stage in enumerate(stages):
        await db.mobile_builds.update_one(
            {"id": build_id},
            {"$set": {f"stages.{i}.status": "running"}}
        )
        await asyncio.sleep(2)
        await db.mobile_builds.update_one(
            {"id": build_id},
            {"$set": {f"stages.{i}.status": "completed"}}
        )
    
    await db.mobile_builds.update_one(
        {"id": build_id},
        {
            "$set": {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "download_url": f"/downloads/app_{build_id}.zip"
            }
        }
    )


@router.get("/builds/{build_id}")
async def get_mobile_build(build_id: str):
    """Get mobile build status"""
    build = await db.mobile_builds.find_one({"id": build_id}, {"_id": 0})
    if not build:
        raise HTTPException(status_code=404, detail="Build not found")
    return build


@router.get("/apps/{app_id}/builds")
async def list_app_builds(app_id: str):
    """List all builds for an app"""
    builds = await db.mobile_builds.find({"app_id": app_id}, {"_id": 0}).sort("started_at", -1).to_list(20)
    return builds
