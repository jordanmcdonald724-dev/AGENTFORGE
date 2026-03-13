// Builds Screen - View all builds and deployments
import React, { useEffect, useState } from 'react';
import { 
  View, Text, FlatList, TouchableOpacity, StyleSheet, 
  RefreshControl, ActivityIndicator
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { 
  Rocket, CheckCircle, XCircle, Clock, Play, 
  RefreshCw, ChevronRight, Zap
} from 'lucide-react-native';
import { buildsApi } from '../services/api';

const BuildsScreen = ({ navigation }) => {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchBuilds();
  }, []);

  const fetchBuilds = async () => {
    try {
      const res = await buildsApi.list();
      setBuilds(res.data || []);
    } catch (e) {
      console.error('Failed to fetch builds');
    }
    setLoading(false);
  };

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchBuilds();
    setRefreshing(false);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
      case 'success':
        return <CheckCircle size={20} color="#22c55e" />;
      case 'failed':
      case 'error':
        return <XCircle size={20} color="#ef4444" />;
      case 'running':
      case 'in_progress':
        return <RefreshCw size={20} color="#f59e0b" />;
      default:
        return <Clock size={20} color="#6b7280" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
      case 'success':
        return '#22c55e';
      case 'failed':
      case 'error':
        return '#ef4444';
      case 'running':
      case 'in_progress':
        return '#f59e0b';
      default:
        return '#6b7280';
    }
  };

  const renderBuild = ({ item }) => (
    <TouchableOpacity
      style={styles.buildCard}
      onPress={() => navigation.navigate('BuildDetail', { buildId: item.id })}
      activeOpacity={0.7}
    >
      <View style={styles.buildHeader}>
        {getStatusIcon(item.status)}
        <View style={styles.buildInfo}>
          <Text style={styles.buildName}>
            {item.name || `Build #${item.id?.slice(-6)}`}
          </Text>
          <Text style={styles.buildProject}>{item.project_name || 'Unknown Project'}</Text>
        </View>
        <ChevronRight size={20} color="#666" />
      </View>
      
      <View style={styles.buildMeta}>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) + '20' }]}>
          <Text style={[styles.statusText, { color: getStatusColor(item.status) }]}>
            {item.status?.toUpperCase()}
          </Text>
        </View>
        <Text style={styles.buildTime}>
          {item.created_at 
            ? new Date(item.created_at).toLocaleDateString() 
            : 'Unknown date'}
        </Text>
      </View>
      
      {item.phases && (
        <View style={styles.progressContainer}>
          <View style={styles.progressBar}>
            <View 
              style={[
                styles.progressFill, 
                { 
                  width: `${(item.completed_phases / item.total_phases) * 100}%`,
                  backgroundColor: getStatusColor(item.status)
                }
              ]} 
            />
          </View>
          <Text style={styles.progressText}>
            {item.completed_phases || 0}/{item.total_phases || 0} phases
          </Text>
        </View>
      )}
    </TouchableOpacity>
  );

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#8b5cf6" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0a0a0c']}
        style={styles.header}
      >
        <View style={styles.headerTop}>
          <Text style={styles.title}>Builds</Text>
          <TouchableOpacity
            style={styles.newBuildButton}
            onPress={() => navigation.navigate('NewBuild')}
          >
            <Play size={16} color="#fff" />
            <Text style={styles.newBuildText}>New</Text>
          </TouchableOpacity>
        </View>
        
        {/* Stats */}
        <View style={styles.statsContainer}>
          <View style={styles.statCard}>
            <Zap size={20} color="#22c55e" />
            <Text style={styles.statNumber}>
              {builds.filter(b => b.status === 'completed' || b.status === 'success').length}
            </Text>
            <Text style={styles.statLabel}>Successful</Text>
          </View>
          <View style={styles.statCard}>
            <RefreshCw size={20} color="#f59e0b" />
            <Text style={styles.statNumber}>
              {builds.filter(b => b.status === 'running' || b.status === 'in_progress').length}
            </Text>
            <Text style={styles.statLabel}>Running</Text>
          </View>
          <View style={styles.statCard}>
            <XCircle size={20} color="#ef4444" />
            <Text style={styles.statNumber}>
              {builds.filter(b => b.status === 'failed' || b.status === 'error').length}
            </Text>
            <Text style={styles.statLabel}>Failed</Text>
          </View>
        </View>
      </LinearGradient>

      <FlatList
        data={builds}
        renderItem={renderBuild}
        keyExtractor={(item) => item.id || Math.random().toString()}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#fff" />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Rocket size={48} color="#444" />
            <Text style={styles.emptyText}>No builds yet</Text>
            <Text style={styles.emptySubtext}>Start a build to see it here</Text>
          </View>
        }
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0c',
  },
  loadingContainer: {
    flex: 1,
    backgroundColor: '#0a0a0c',
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    padding: 24,
    paddingTop: 60,
  },
  headerTop: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: '800',
    color: '#fff',
  },
  newBuildButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#8b5cf6',
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 12,
  },
  newBuildText: {
    color: '#fff',
    fontWeight: '600',
    marginLeft: 6,
  },
  statsContainer: {
    flexDirection: 'row',
    marginTop: 20,
    gap: 12,
  },
  statCard: {
    flex: 1,
    backgroundColor: '#111',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#222',
  },
  statNumber: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '700',
    marginTop: 8,
  },
  statLabel: {
    color: '#666',
    fontSize: 11,
    marginTop: 4,
  },
  listContent: {
    padding: 20,
  },
  buildCard: {
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222',
  },
  buildHeader: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  buildInfo: {
    flex: 1,
    marginLeft: 12,
  },
  buildName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  buildProject: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
  },
  buildMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  statusBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 6,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '600',
  },
  buildTime: {
    color: '#666',
    fontSize: 12,
    marginLeft: 12,
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 12,
  },
  progressBar: {
    flex: 1,
    height: 4,
    backgroundColor: '#222',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    borderRadius: 2,
  },
  progressText: {
    color: '#666',
    fontSize: 10,
    marginLeft: 12,
  },
  emptyState: {
    alignItems: 'center',
    padding: 60,
  },
  emptyText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: '600',
    marginTop: 16,
  },
  emptySubtext: {
    color: '#666',
    fontSize: 14,
    marginTop: 8,
  },
});

export default BuildsScreen;
