// Project Detail Screen
import React, { useEffect, useState } from 'react';
import { 
  View, Text, ScrollView, TouchableOpacity, StyleSheet, 
  Alert, RefreshControl
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { 
  ArrowLeft, Rocket, Play, FileCode, CheckSquare, 
  MessageSquare, Settings, Trash2, Users
} from 'lucide-react-native';
import { useProjectStore, useFileStore, useTaskStore, useBuildStore } from '../services/store';
import { deployApi } from '../services/api';

const ProjectDetailScreen = ({ route, navigation }) => {
  const { projectId } = route.params;
  const { currentProject, selectProject, clearCurrentProject } = useProjectStore();
  const { files, fetchFiles } = useFileStore();
  const { tasks, fetchTasks } = useTaskStore();
  const { triggerBuild, currentBuild } = useBuildStore();
  const [refreshing, setRefreshing] = useState(false);
  const [deploying, setDeploying] = useState(false);

  useEffect(() => {
    loadProject();
    return () => clearCurrentProject();
  }, [projectId]);

  const loadProject = async () => {
    await Promise.all([
      selectProject(projectId),
      fetchFiles(projectId),
      fetchTasks(projectId)
    ]);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadProject();
    setRefreshing(false);
  };

  const handleBuild = async () => {
    try {
      const result = await triggerBuild(projectId, 'build');
      Alert.alert('Build Started', `Build job ${result.id} has been queued.`);
    } catch (error) {
      Alert.alert('Error', 'Failed to start build');
    }
  };

  const handleDeploy = async (platform) => {
    setDeploying(true);
    try {
      const res = await deployApi.deploy(projectId, platform);
      Alert.alert('Deployment', `Deploying to ${platform}...\n${res.data.url || 'Check status in deployments.'}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to deploy');
    }
    setDeploying(false);
  };

  const ActionButton = ({ icon: Icon, label, color, onPress, disabled }) => (
    <TouchableOpacity
      style={[styles.actionButton, disabled && styles.actionButtonDisabled]}
      onPress={onPress}
      disabled={disabled}
      activeOpacity={0.7}
    >
      <View style={[styles.actionIcon, { backgroundColor: color + '20' }]}>
        <Icon size={20} color={color} />
      </View>
      <Text style={styles.actionLabel}>{label}</Text>
    </TouchableOpacity>
  );

  const StatCard = ({ icon: Icon, label, value, color }) => (
    <View style={styles.statCard}>
      <View style={[styles.statIcon, { backgroundColor: color + '20' }]}>
        <Icon size={18} color={color} />
      </View>
      <Text style={styles.statValue}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
    </View>
  );

  if (!currentProject) {
    return (
      <View style={[styles.container, styles.centered]}>
        <Text style={styles.loadingText}>Loading project...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0a0a0c']}
        style={styles.header}
      >
        <TouchableOpacity
          style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <ArrowLeft size={24} color="#fff" />
        </TouchableOpacity>
        
        <View style={styles.headerContent}>
          <Text style={styles.projectName}>{currentProject.name}</Text>
          <Text style={styles.projectId}>ID: {projectId.slice(0, 8)}...</Text>
        </View>
      </LinearGradient>

      <ScrollView
        style={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#fff" />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Stats */}
        <View style={styles.statsRow}>
          <StatCard icon={FileCode} label="Files" value={files.length} color="#8b5cf6" />
          <StatCard icon={CheckSquare} label="Tasks" value={tasks.length} color="#22c55e" />
          <StatCard icon={Users} label="Agents" value="6" color="#06b6d4" />
        </View>

        {/* Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Actions</Text>
          <View style={styles.actionsGrid}>
            <ActionButton 
              icon={Play} 
              label="Build" 
              color="#22c55e"
              onPress={handleBuild}
            />
            <ActionButton 
              icon={Rocket} 
              label="Deploy" 
              color="#f59e0b"
              onPress={() => {
                Alert.alert(
                  'Deploy',
                  'Choose deployment platform',
                  [
                    { text: 'Cancel', style: 'cancel' },
                    { text: 'Vercel', onPress: () => handleDeploy('vercel') },
                    { text: 'Railway', onPress: () => handleDeploy('railway') },
                  ]
                );
              }}
              disabled={deploying}
            />
            <ActionButton 
              icon={MessageSquare} 
              label="Chat" 
              color="#8b5cf6"
              onPress={() => navigation.navigate('AgentChat', { projectId })}
            />
            <ActionButton 
              icon={Settings} 
              label="Settings" 
              color="#666"
              onPress={() => Alert.alert('Settings', 'Project settings coming soon!')}
            />
          </View>
        </View>

        {/* Files Preview */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Files</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Files', { projectId })}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          
          {files.slice(0, 5).map((file) => (
            <TouchableOpacity
              key={file.id}
              style={styles.fileItem}
              onPress={() => navigation.navigate('FileEditor', { file })}
            >
              <FileCode size={16} color="#8b5cf6" />
              <Text style={styles.fileName}>{file.name}</Text>
              <Text style={styles.fileSize}>{file.language || 'file'}</Text>
            </TouchableOpacity>
          ))}
          
          {files.length === 0 && (
            <Text style={styles.emptyText}>No files yet</Text>
          )}
        </View>

        {/* Tasks Preview */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Tasks</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Tasks', { projectId })}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          
          {tasks.slice(0, 5).map((task) => (
            <View key={task.id} style={styles.taskItem}>
              <View style={[
                styles.taskStatus,
                { backgroundColor: task.status === 'completed' ? '#22c55e' : '#f59e0b' }
              ]} />
              <Text style={styles.taskTitle}>{task.title}</Text>
            </View>
          ))}
          
          {tasks.length === 0 && (
            <Text style={styles.emptyText}>No tasks yet</Text>
          )}
        </View>

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
  centered: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  loadingText: {
    color: '#666',
    fontSize: 16,
  },
  header: {
    padding: 24,
    paddingTop: 60,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#222',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  headerContent: {
    flex: 1,
  },
  projectName: {
    fontSize: 24,
    fontWeight: '800',
    color: '#fff',
  },
  projectId: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  content: {
    flex: 1,
  },
  statsRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingTop: 20,
    justifyContent: 'space-between',
  },
  statCard: {
    flex: 1,
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 16,
    alignItems: 'center',
    marginHorizontal: 4,
    borderWidth: 1,
    borderColor: '#222',
  },
  statIcon: {
    width: 36,
    height: 36,
    borderRadius: 18,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#fff',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  section: {
    padding: 20,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 16,
  },
  seeAll: {
    color: '#8b5cf6',
    fontSize: 14,
  },
  actionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 20,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222',
  },
  actionButtonDisabled: {
    opacity: 0.5,
  },
  actionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  actionLabel: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  fileItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#222',
  },
  fileName: {
    flex: 1,
    color: '#fff',
    fontSize: 14,
    marginLeft: 12,
  },
  fileSize: {
    color: '#666',
    fontSize: 12,
  },
  taskItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: '#222',
  },
  taskStatus: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 12,
  },
  taskTitle: {
    color: '#fff',
    fontSize: 14,
    flex: 1,
  },
  emptyText: {
    color: '#666',
    fontSize: 14,
    textAlign: 'center',
    padding: 20,
  },
});

export default ProjectDetailScreen;
