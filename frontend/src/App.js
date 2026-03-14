import { useState, useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import { toast } from "sonner";
import { ThemeProvider } from "@/context/ThemeContext";
import LandingPage from "@/pages/LandingPage";
import Dashboard from "@/pages/Dashboard";
import ProjectWorkspace from "@/pages/ProjectWorkspace";
import GodModePage from "@/pages/GodModePage";
import ResearchLab from "@/pages/ResearchLab";
import SettingsPage from "@/pages/SettingsPage";
import LiveLogs from "@/pages/LiveLogs";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function App() {
  return (
    <ThemeProvider>
      <div className="app-container">
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/studio" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/project/:projectId" element={<ProjectWorkspace />} />
            <Route path="/god-mode" element={<GodModePage />} />
            <Route path="/project/:projectId/god-mode" element={<GodModePage />} />
            <Route path="/research" element={<ResearchLab />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/logs" element={<LiveLogs />} />
          </Routes>
        </BrowserRouter>
        <Toaster position="bottom-right" theme="dark" />
      </div>
    </ThemeProvider>
  );
}

export default App;
