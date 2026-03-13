// Home Screen - Dashboard with quick actions
import React, { useEffect, useState } from 'react';
import { 
  View, Text, ScrollView, TouchableOpacity, StyleSheet, 
  RefreshControl, Dimensions 
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { 
  Folder, Users, Mic, Rocket, Activity, Plus, ChevronRight 
} from 'lucide-react-native';
import { useProjectStore, useAgentStore } from '../services/store';
import { healthApi } from '../services/api';

const { width } = Dimensions.get('window');

const HomeScreen = ({ navigation }) => {
  const { projects, fetchProjects, loading } = useProjectStore();
  const { agents, fetchAgents } = useAgentStore();
  const [health, setHealth] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    await Promise.all([
      fetchProjects(),
      fetchAgents(),
      checkHealth()
    ]);
  };

  const checkHealth = async () => {
    try {
      const res = await healthApi.check();
      setHealth(res.data);
    } catch (e) {
      setHealth({ status: 'error' });
    }
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const QuickAction = ({ icon: Icon, label, color, onPress }) => (
    <TouchableOpacity 
      style={styles.quickAction}
      onPress={onPress}
      activeOpacity={0.7}
    >
      <LinearGradient
        colors={[color + '30', color + '10']}
        style={styles.quickActionGradient}
      >
        <Icon size={24} color={color} />
        <Text style={styles.quickActionLabel}>{label}</Text>
      </LinearGradient>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#fff" />
        }
        showsVerticalScrollIndicator={false}
      >
        {/* Header */}
        <LinearGradient
          colors={['#1a1a2e', '#0a0a0c']}
          style={styles.header}
        >
          <Text style={styles.logo}>AgentForge</Text>
          <Text style={styles.tagline}>AI Development Studio</Text>
          
          {/* Status indicator */}
          <View style={styles.statusBadge}>
            <View style={[
              styles.statusDot, 
              { backgroundColor: health?.status === 'healthy' ? '#22c55e' : '#ef4444' }
            ]} />
            <Text style={styles.statusText}>
              {health?.status === 'healthy' ? 'System Online' : 'Connecting...'}
            </Text>
          </View>
        </LinearGradient>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.quickActionsGrid}>
            <QuickAction 
              icon={Plus} 
              label="New Project" 
              color="#8b5cf6"
              onPress={() => navigation.navigate('NewProject')}
            />
            <QuickAction 
              icon={Mic} 
              label="Voice" 
              color="#06b6d4"
              onPress={() => navigation.navigate('Voice')}
            />
            <QuickAction 
              icon={Rocket} 
              label="Deploy" 
              color="#f59e0b"
              onPress={() => navigation.navigate('Projects')}
            />
            <QuickAction 
              icon={Activity} 
              label="Builds" 
              color="#22c55e"
              onPress={() => navigation.navigate('Builds')}
            />
          </View>
        </View>

        {/* Recent Projects */}
        <View style={styles.section}>
          <View style={styles.sectionHeader}>
            <Text style={styles.sectionTitle}>Recent Projects</Text>
            <TouchableOpacity onPress={() => navigation.navigate('Projects')}>
              <Text style={styles.seeAll}>See All</Text>
            </TouchableOpacity>
          </View>
          
          {projects.slice(0, 3).map((project) => (
            <TouchableOpacity
              key={project.id}
              style={styles.projectCard}
              onPress={() => navigation.navigate('ProjectDetail', { projectId: project.id })}
              activeOpacity={0.7}
            >
              <View style={styles.projectIcon}>
                <Folder size={20} color="#8b5cf6" />
              </View>
              <View style={styles.projectInfo}>
                <Text style={styles.projectName}>{project.name}</Text>
                <Text style={styles.projectMeta}>
                  {project.files?.length || 0} files • {project.tasks?.length || 0} tasks
                </Text>
              </View>
              <ChevronRight size={20} color="#666" />
            </TouchableOpacity>
          ))}
          
          {projects.length === 0 && (
            <View style={styles.emptyState}>
              <Folder size={40} color="#444" />
              <Text style={styles.emptyText}>No projects yet</Text>
              <TouchableOpacity 
                style={styles.createButton}
                onPress={() => navigation.navigate('NewProject')}
              >
                <Text style={styles.createButtonText}>Create First Project</Text>
              </TouchableOpacity>
            </View>
          )}
        </View>

        {/* Agents */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>AI Agents</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {agents.map((agent) => (
              <TouchableOpacity
                key={agent.id}
                style={styles.agentCard}
                onPress={() => navigation.navigate('AgentChat', { agent })}
              >
                <View style={[styles.agentAvatar, { backgroundColor: agent.color || '#8b5cf6' }]}>
                  <Text style={styles.agentInitial}>{agent.name?.[0]}</Text>
                </View>
                <Text style={styles.agentName}>{agent.name}</Text>
                <Text style={styles.agentRole}>{agent.role}</Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
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
  header: {
    padding: 24,
    paddingTop: 60,
    paddingBottom: 32,
  },
  logo: {
    fontSize: 32,
    fontWeight: '800',
    color: '#fff',
  },
  tagline: {
    fontSize: 14,
    color: '#888',
    marginTop: 4,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#1a1a2e',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    alignSelf: 'flex-start',
    marginTop: 16,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusText: {
    color: '#aaa',
    fontSize: 12,
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
  quickActionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  quickAction: {
    width: (width - 52) / 2,
    marginBottom: 12,
  },
  quickActionGradient: {
    padding: 20,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#222',
  },
  quickActionLabel: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
    marginTop: 8,
  },
  projectCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222',
  },
  projectIcon: {
    width: 44,
    height: 44,
    borderRadius: 12,
    backgroundColor: '#8b5cf620',
    alignItems: 'center',
    justifyContent: 'center',
  },
  projectInfo: {
    flex: 1,
    marginLeft: 12,
  },
  projectName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  projectMeta: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
  },
  emptyState: {
    alignItems: 'center',
    padding: 40,
  },
  emptyText: {
    color: '#666',
    fontSize: 14,
    marginTop: 12,
  },
  createButton: {
    backgroundColor: '#8b5cf6',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
    marginTop: 16,
  },
  createButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  agentCard: {
    alignItems: 'center',
    marginRight: 16,
    padding: 16,
    backgroundColor: '#111',
    borderRadius: 16,
    width: 100,
    borderWidth: 1,
    borderColor: '#222',
  },
  agentAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: 'center',
    justifyContent: 'center',
  },
  agentInitial: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
  },
  agentName: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
    marginTop: 8,
  },
  agentRole: {
    color: '#666',
    fontSize: 10,
    marginTop: 2,
  },
});

export default HomeScreen;
