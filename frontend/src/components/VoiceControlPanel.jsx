import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Mic, MicOff, Volume2, Send, Loader2, Play, HelpCircle } from 'lucide-react';
import { API } from '@/App';

const VoiceControlPanel = ({ projectId, onCommandExecute }) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcription, setTranscription] = useState('');
  const [lastCommand, setLastCommand] = useState(null);
  const [commands, setCommands] = useState([]);
  const [history, setHistory] = useState([]);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  useEffect(() => {
    fetchCommands();
  }, []);

  const fetchCommands = async () => {
    try {
      const res = await axios.get(`${API}/voice/commands`);
      setCommands(res.data.commands || []);
    } catch (e) {
      console.error('Failed to fetch voice commands');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      chunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await processAudio(blob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      toast.info('Recording... Release to send');
    } catch (error) {
      toast.error('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const processAudio = async (blob) => {
    setIsProcessing(true);
    const formData = new FormData();
    formData.append('file', blob, 'recording.webm');

    try {
      const res = await axios.post(
        `${API}/voice/command?project_id=${projectId || 'default'}`,
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setTranscription(res.data.transcription);
      setLastCommand(res.data.command);
      
      setHistory(prev => [{
        id: Date.now(),
        text: res.data.transcription,
        command: res.data.command,
        time: new Date().toLocaleTimeString()
      }, ...prev].slice(0, 5));

      toast.success(`Command: ${res.data.command?.command || 'chat'}`);
    } catch (error) {
      toast.error('Voice processing failed');
    }
    setIsProcessing(false);
  };

  const executeCommand = () => {
    if (lastCommand && onCommandExecute) {
      onCommandExecute(lastCommand);
    }
  };

  return (
    <div className="h-full flex flex-col bg-[#0a0a0c]" data-testid="voice-control-panel">
      <div className="p-4 border-b border-zinc-800">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Mic className="w-5 h-5 text-cyan-400" />
          Voice Control
        </h3>
        <p className="text-xs text-zinc-500 mt-1">Hold to speak, release to process</p>
      </div>

      <div className="flex-1 overflow-auto p-4 space-y-4">
        {/* Record Button */}
        <div className="flex flex-col items-center py-6">
          <button
            className={`w-24 h-24 rounded-full flex items-center justify-center transition-all ${
              isRecording 
                ? 'bg-red-500 scale-110 shadow-lg shadow-red-500/50' 
                : isProcessing
                  ? 'bg-zinc-700'
                  : 'bg-gradient-to-br from-cyan-500 to-violet-600 hover:scale-105'
            }`}
            onMouseDown={startRecording}
            onMouseUp={stopRecording}
            onTouchStart={startRecording}
            onTouchEnd={stopRecording}
            disabled={isProcessing}
          >
            {isProcessing ? (
              <Loader2 className="w-10 h-10 text-white animate-spin" />
            ) : isRecording ? (
              <MicOff className="w-10 h-10 text-white" />
            ) : (
              <Mic className="w-10 h-10 text-white" />
            )}
          </button>
          <span className="text-xs text-zinc-500 mt-3">
            {isProcessing ? 'Processing...' : isRecording ? 'Recording...' : 'Hold to speak'}
          </span>
        </div>

        {/* Transcription Result */}
        {transcription && (
          <div className="bg-zinc-900 rounded-xl p-4 border border-zinc-800">
            <p className="text-sm text-zinc-400 mb-2">You said:</p>
            <p className="text-white italic">"{transcription}"</p>
            
            {lastCommand && (
              <div className="mt-4 pt-4 border-t border-zinc-800">
                <div className="flex items-center justify-between">
                  <Badge className="bg-cyan-500/20 text-cyan-400">
                    {lastCommand.command}
                  </Badge>
                  <Button 
                    size="sm" 
                    onClick={executeCommand}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Play className="w-3 h-3 mr-1" />
                    Execute
                  </Button>
                </div>
                <p className="text-xs text-zinc-500 mt-2">{lastCommand.description}</p>
              </div>
            )}
          </div>
        )}

        {/* Command History */}
        {history.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-zinc-400 mb-2">Recent</h4>
            <div className="space-y-2">
              {history.map(item => (
                <div key={item.id} className="bg-zinc-900/50 rounded-lg p-3 text-xs">
                  <p className="text-zinc-300">"{item.text}"</p>
                  <div className="flex justify-between mt-1">
                    <span className="text-cyan-400">{item.command?.command}</span>
                    <span className="text-zinc-600">{item.time}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Available Commands */}
        <div>
          <h4 className="text-sm font-medium text-zinc-400 mb-2 flex items-center gap-1">
            <HelpCircle className="w-3 h-3" />
            Available Commands
          </h4>
          <div className="grid grid-cols-2 gap-2">
            {commands.slice(0, 6).map(cmd => (
              <div key={cmd.name} className="bg-zinc-900/50 rounded-lg p-2 text-xs">
                <span className="text-white font-medium">{cmd.description}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceControlPanel;
