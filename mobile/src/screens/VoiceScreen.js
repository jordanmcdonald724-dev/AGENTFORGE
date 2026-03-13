// Voice Control Screen - Record and process voice commands
import React, { useState, useEffect, useRef } from 'react';
import { 
  View, Text, TouchableOpacity, StyleSheet, Animated, 
  ScrollView, Alert
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Audio } from 'expo-av';
import * as Haptics from 'expo-haptics';
import { Mic, MicOff, Volume2, Send, X, Check } from 'lucide-react-native';
import { voiceApi } from '../services/api';
import { useVoiceStore, useProjectStore } from '../services/store';

const VoiceScreen = ({ navigation }) => {
  const { currentProject } = useProjectStore();
  const { 
    isRecording, setRecording, 
    isProcessing, setProcessing,
    lastCommand, setLastCommand,
    lastTranscription, setLastTranscription
  } = useVoiceStore();
  
  const [recording, setRecordingObj] = useState(null);
  const [commands, setCommands] = useState([]);
  const [commandHistory, setCommandHistory] = useState([]);
  const pulseAnim = useRef(new Animated.Value(1)).current;
  
  useEffect(() => {
    loadCommands();
    setupAudio();
    
    return () => {
      if (recording) {
        recording.stopAndUnloadAsync();
      }
    };
  }, []);

  useEffect(() => {
    if (isRecording) {
      // Pulse animation while recording
      Animated.loop(
        Animated.sequence([
          Animated.timing(pulseAnim, {
            toValue: 1.2,
            duration: 500,
            useNativeDriver: true,
          }),
          Animated.timing(pulseAnim, {
            toValue: 1,
            duration: 500,
            useNativeDriver: true,
          }),
        ])
      ).start();
    } else {
      pulseAnim.setValue(1);
    }
  }, [isRecording]);

  const setupAudio = async () => {
    try {
      await Audio.requestPermissionsAsync();
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });
    } catch (error) {
      console.error('Failed to setup audio:', error);
    }
  };

  const loadCommands = async () => {
    try {
      const res = await voiceApi.getCommands();
      setCommands(res.data.commands || []);
    } catch (error) {
      console.error('Failed to load commands:', error);
    }
  };

  const startRecording = async () => {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
      
      const { recording: newRecording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      
      setRecordingObj(newRecording);
      setRecording(true);
    } catch (error) {
      console.error('Failed to start recording:', error);
      Alert.alert('Error', 'Failed to start recording. Please check microphone permissions.');
    }
  };

  const stopRecording = async () => {
    try {
      await Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      setRecording(false);
      setProcessing(true);

      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      
      // Process the voice command
      const res = await voiceApi.processCommand(uri, currentProject?.id || 'default');
      
      setLastTranscription(res.data.transcription);
      setLastCommand(res.data.command);
      
      // Add to history
      setCommandHistory(prev => [{
        id: Date.now(),
        text: res.data.transcription,
        command: res.data.command,
        timestamp: new Date().toISOString(),
      }, ...prev].slice(0, 10));
      
      setProcessing(false);
      setRecordingObj(null);
      
    } catch (error) {
      console.error('Failed to process recording:', error);
      setProcessing(false);
      Alert.alert('Error', 'Failed to process voice command. Please try again.');
    }
  };

  const executeCommand = async (command) => {
    if (!command || command.command === 'chat') {
      Alert.alert('Chat', 'This would send your message to the AI agent.');
      return;
    }
    
    const hint = command.execution_hint || lastCommand?.execution_hint;
    if (hint?.endpoint) {
      Alert.alert(
        'Execute Command',
        `Would call: ${hint.method} ${hint.endpoint}`,
        [
          { text: 'Cancel', style: 'cancel' },
          { text: 'Execute', onPress: () => console.log('Executing...') }
        ]
      );
    }
  };

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0a0a0c']}
        style={styles.header}
      >
        <Text style={styles.title}>Voice Control</Text>
        <Text style={styles.subtitle}>
          {currentProject ? `Project: ${currentProject.name}` : 'No project selected'}
        </Text>
      </LinearGradient>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Recording Button */}
        <View style={styles.recordSection}>
          <Animated.View style={{ transform: [{ scale: pulseAnim }] }}>
            <TouchableOpacity
              style={[
                styles.recordButton,
                isRecording && styles.recordButtonActive,
                isProcessing && styles.recordButtonProcessing
              ]}
              onPressIn={startRecording}
              onPressOut={stopRecording}
              disabled={isProcessing}
            >
              <LinearGradient
                colors={isRecording ? ['#ef4444', '#dc2626'] : ['#8b5cf6', '#7c3aed']}
                style={styles.recordButtonGradient}
              >
                {isProcessing ? (
                  <Volume2 size={48} color="#fff" />
                ) : isRecording ? (
                  <MicOff size={48} color="#fff" />
                ) : (
                  <Mic size={48} color="#fff" />
                )}
              </LinearGradient>
            </TouchableOpacity>
          </Animated.View>
          
          <Text style={styles.recordHint}>
            {isProcessing 
              ? 'Processing...' 
              : isRecording 
                ? 'Release to send' 
                : 'Hold to speak'}
          </Text>
        </View>

        {/* Last Transcription */}
        {lastTranscription && (
          <View style={styles.transcriptionCard}>
            <Text style={styles.transcriptionLabel}>Last transcription:</Text>
            <Text style={styles.transcriptionText}>"{lastTranscription}"</Text>
            
            {lastCommand && (
              <View style={styles.commandResult}>
                <View style={styles.commandBadge}>
                  <Text style={styles.commandName}>{lastCommand.command}</Text>
                </View>
                <Text style={styles.commandDesc}>{lastCommand.description}</Text>
                
                <TouchableOpacity
                  style={styles.executeButton}
                  onPress={() => executeCommand(lastCommand)}
                >
                  <Check size={16} color="#fff" />
                  <Text style={styles.executeText}>Execute</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        )}

        {/* Available Commands */}
        <View style={styles.commandsSection}>
          <Text style={styles.sectionTitle}>Available Commands</Text>
          {commands.map((cmd) => (
            <View key={cmd.name} style={styles.commandCard}>
              <Text style={styles.commandTitle}>{cmd.description}</Text>
              <Text style={styles.commandExample}>
                Try: "{cmd.example_phrases?.[0]?.replace(/[()\\|?]/g, '')}"
              </Text>
            </View>
          ))}
        </View>

        {/* Command History */}
        {commandHistory.length > 0 && (
          <View style={styles.historySection}>
            <Text style={styles.sectionTitle}>Recent Commands</Text>
            {commandHistory.map((item) => (
              <View key={item.id} style={styles.historyItem}>
                <Text style={styles.historyText}>"{item.text}"</Text>
                <View style={styles.historyMeta}>
                  <Text style={styles.historyCommand}>{item.command?.command}</Text>
                  <Text style={styles.historyTime}>
                    {new Date(item.timestamp).toLocaleTimeString()}
                  </Text>
                </View>
              </View>
            ))}
          </View>
        )}

        <View style={{ height: 100 }} />
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0c',
  },
  header: {
    padding: 24,
    paddingTop: 60,
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#fff',
  },
  subtitle: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  recordSection: {
    alignItems: 'center',
    marginVertical: 40,
  },
  recordButton: {
    width: 140,
    height: 140,
    borderRadius: 70,
    overflow: 'hidden',
  },
  recordButtonActive: {
    shadowColor: '#ef4444',
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.5,
    shadowRadius: 20,
    elevation: 10,
  },
  recordButtonProcessing: {
    opacity: 0.7,
  },
  recordButtonGradient: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  recordHint: {
    color: '#888',
    fontSize: 14,
    marginTop: 16,
  },
  transcriptionCard: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    borderWidth: 1,
    borderColor: '#222',
  },
  transcriptionLabel: {
    color: '#666',
    fontSize: 12,
    marginBottom: 8,
  },
  transcriptionText: {
    color: '#fff',
    fontSize: 18,
    fontStyle: 'italic',
  },
  commandResult: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#222',
  },
  commandBadge: {
    backgroundColor: '#8b5cf620',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  commandName: {
    color: '#8b5cf6',
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  commandDesc: {
    color: '#aaa',
    fontSize: 14,
    marginTop: 8,
  },
  executeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#22c55e',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 8,
    alignSelf: 'flex-start',
    marginTop: 12,
  },
  executeText: {
    color: '#fff',
    fontWeight: '600',
    marginLeft: 8,
  },
  commandsSection: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 16,
  },
  commandCard: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222',
  },
  commandTitle: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  commandExample: {
    color: '#666',
    fontSize: 12,
    marginTop: 4,
    fontStyle: 'italic',
  },
  historySection: {
    marginBottom: 24,
  },
  historyItem: {
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#222',
  },
  historyText: {
    color: '#aaa',
    fontSize: 14,
    fontStyle: 'italic',
  },
  historyMeta: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 8,
  },
  historyCommand: {
    color: '#8b5cf6',
    fontSize: 12,
  },
  historyTime: {
    color: '#666',
    fontSize: 12,
  },
});

export default VoiceScreen;
