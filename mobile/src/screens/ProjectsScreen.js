// Projects List Screen
import React, { useEffect, useState } from 'react';
import { 
  View, Text, FlatList, TouchableOpacity, StyleSheet, 
  RefreshControl, TextInput
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { Folder, Plus, Search, Clock, FileCode } from 'lucide-react-native';
import { useProjectStore } from '../services/store';

const ProjectsScreen = ({ navigation }) => {
  const { projects, fetchProjects, loading } = useProjectStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await fetchProjects();
    setRefreshing(false);
  };

  const filteredProjects = projects.filter(p => 
    p.name?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderProject = ({ item }) => (
    <TouchableOpacity
      style={styles.projectCard}
      onPress={() => navigation.navigate('ProjectDetail', { projectId: item.id })}
      activeOpacity={0.7}
    >
      <View style={styles.projectIconContainer}>
        <LinearGradient
          colors={['#8b5cf620', '#8b5cf610']}
          style={styles.projectIcon}
        >
          <Folder size={24} color="#8b5cf6" />
        </LinearGradient>
      </View>
      
      <View style={styles.projectInfo}>
        <Text style={styles.projectName}>{item.name}</Text>
        <View style={styles.projectMeta}>
          <View style={styles.metaItem}>
            <FileCode size={12} color="#666" />
            <Text style={styles.metaText}>{item.files?.length || 0} files</Text>
          </View>
          <View style={styles.metaItem}>
            <Clock size={12} color="#666" />
            <Text style={styles.metaText}>
              {item.updated_at 
                ? new Date(item.updated_at).toLocaleDateString() 
                : 'No date'}
            </Text>
          </View>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0a0a0c']}
        style={styles.header}
      >
        <View style={styles.headerTop}>
          <Text style={styles.title}>Projects</Text>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => navigation.navigate('NewProject')}
          >
            <Plus size={20} color="#fff" />
          </TouchableOpacity>
        </View>
        
        {/* Search */}
        <View style={styles.searchContainer}>
          <Search size={18} color="#666" />
          <TextInput
            style={styles.searchInput}
            placeholder="Search projects..."
            placeholderTextColor="#666"
            value={searchQuery}
            onChangeText={setSearchQuery}
          />
        </View>
      </LinearGradient>

      <FlatList
        data={filteredProjects}
        renderItem={renderProject}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.listContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#fff" />
        }
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <Folder size={48} color="#444" />
            <Text style={styles.emptyText}>
              {searchQuery ? 'No projects match your search' : 'No projects yet'}
            </Text>
            {!searchQuery && (
              <TouchableOpacity
                style={styles.createButton}
                onPress={() => navigation.navigate('NewProject')}
              >
                <Text style={styles.createButtonText}>Create Project</Text>
              </TouchableOpacity>
            )}
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
  addButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#8b5cf6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    borderRadius: 12,
    paddingHorizontal: 16,
    marginTop: 20,
    borderWidth: 1,
    borderColor: '#222',
  },
  searchInput: {
    flex: 1,
    paddingVertical: 14,
    marginLeft: 12,
    color: '#fff',
    fontSize: 16,
  },
  listContent: {
    padding: 20,
  },
  projectCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#111',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#222',
  },
  projectIconContainer: {},
  projectIcon: {
    width: 52,
    height: 52,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  projectInfo: {
    flex: 1,
    marginLeft: 16,
  },
  projectName: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  projectMeta: {
    flexDirection: 'row',
    marginTop: 8,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginRight: 16,
  },
  metaText: {
    color: '#666',
    fontSize: 12,
    marginLeft: 4,
  },
  emptyState: {
    alignItems: 'center',
    padding: 60,
  },
  emptyText: {
    color: '#666',
    fontSize: 16,
    marginTop: 16,
    textAlign: 'center',
  },
  createButton: {
    backgroundColor: '#8b5cf6',
    paddingHorizontal: 24,
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 20,
  },
  createButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default ProjectsScreen;
