// Settings Screen
import React, { useState } from 'react';
import { 
  View, Text, ScrollView, TouchableOpacity, StyleSheet, 
  Switch, Alert, Linking
} from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { 
  User, Bell, Moon, Shield, Server, ExternalLink,
  ChevronRight, LogOut, Trash2, Info, Code, Github
} from 'lucide-react-native';

const SettingsScreen = ({ navigation }) => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(true);
  const [autoSave, setAutoSave] = useState(true);

  const handleLogout = () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Logout', style: 'destructive', onPress: () => {
          // Handle logout
        }}
      ]
    );
  };

  const handleDeleteAccount = () => {
    Alert.alert(
      'Delete Account',
      'This action cannot be undone. Are you sure?',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => {
          // Handle delete
        }}
      ]
    );
  };

  const SettingRow = ({ icon: Icon, iconColor, title, subtitle, onPress, rightElement }) => (
    <TouchableOpacity 
      style={styles.settingRow}
      onPress={onPress}
      activeOpacity={onPress ? 0.7 : 1}
    >
      <View style={[styles.iconContainer, { backgroundColor: iconColor + '20' }]}>
        <Icon size={20} color={iconColor} />
      </View>
      <View style={styles.settingInfo}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      {rightElement || (onPress && <ChevronRight size={20} color="#666" />)}
    </TouchableOpacity>
  );

  const SettingSwitch = ({ icon: Icon, iconColor, title, subtitle, value, onValueChange }) => (
    <View style={styles.settingRow}>
      <View style={[styles.iconContainer, { backgroundColor: iconColor + '20' }]}>
        <Icon size={20} color={iconColor} />
      </View>
      <View style={styles.settingInfo}>
        <Text style={styles.settingTitle}>{title}</Text>
        {subtitle && <Text style={styles.settingSubtitle}>{subtitle}</Text>}
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#333', true: '#8b5cf6' }}
        thumbColor="#fff"
      />
    </View>
  );

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#1a1a2e', '#0a0a0c']}
        style={styles.header}
      >
        <Text style={styles.title}>Settings</Text>
        <Text style={styles.subtitle}>Customize your experience</Text>
      </LinearGradient>

      <ScrollView 
        style={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {/* Account Section */}
        <Text style={styles.sectionTitle}>Account</Text>
        <View style={styles.section}>
          <SettingRow
            icon={User}
            iconColor="#8b5cf6"
            title="Profile"
            subtitle="Manage your account details"
            onPress={() => navigation.navigate('Profile')}
          />
          <SettingRow
            icon={Shield}
            iconColor="#22c55e"
            title="Security"
            subtitle="Password, 2FA"
            onPress={() => navigation.navigate('Security')}
          />
        </View>

        {/* Preferences Section */}
        <Text style={styles.sectionTitle}>Preferences</Text>
        <View style={styles.section}>
          <SettingSwitch
            icon={Bell}
            iconColor="#f59e0b"
            title="Notifications"
            subtitle="Build alerts, updates"
            value={notifications}
            onValueChange={setNotifications}
          />
          <SettingSwitch
            icon={Moon}
            iconColor="#6366f1"
            title="Dark Mode"
            subtitle="Always on for now"
            value={darkMode}
            onValueChange={setDarkMode}
          />
          <SettingSwitch
            icon={Code}
            iconColor="#06b6d4"
            title="Auto-save"
            subtitle="Save changes automatically"
            value={autoSave}
            onValueChange={setAutoSave}
          />
        </View>

        {/* Server Section */}
        <Text style={styles.sectionTitle}>Server</Text>
        <View style={styles.section}>
          <SettingRow
            icon={Server}
            iconColor="#06b6d4"
            title="API Endpoint"
            subtitle="Configure server connection"
            onPress={() => navigation.navigate('ServerConfig')}
          />
          <SettingRow
            icon={Github}
            iconColor="#fff"
            title="GitHub Integration"
            subtitle="Connect your repositories"
            onPress={() => navigation.navigate('GitHubSetup')}
          />
        </View>

        {/* About Section */}
        <Text style={styles.sectionTitle}>About</Text>
        <View style={styles.section}>
          <SettingRow
            icon={Info}
            iconColor="#8b5cf6"
            title="About AgentForge"
            subtitle="Version 5.0.0"
            onPress={() => {}}
          />
          <SettingRow
            icon={ExternalLink}
            iconColor="#22c55e"
            title="Documentation"
            onPress={() => Linking.openURL('https://docs.agentforge.ai')}
          />
        </View>

        {/* Danger Zone */}
        <Text style={[styles.sectionTitle, { color: '#ef4444' }]}>Danger Zone</Text>
        <View style={styles.section}>
          <SettingRow
            icon={LogOut}
            iconColor="#f59e0b"
            title="Logout"
            onPress={handleLogout}
          />
          <SettingRow
            icon={Trash2}
            iconColor="#ef4444"
            title="Delete Account"
            subtitle="Permanently delete your data"
            onPress={handleDeleteAccount}
          />
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
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#666',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 12,
    marginTop: 24,
  },
  section: {
    backgroundColor: '#111',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#222',
    overflow: 'hidden',
  },
  settingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  iconContainer: {
    width: 40,
    height: 40,
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingInfo: {
    flex: 1,
    marginLeft: 14,
  },
  settingTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '500',
  },
  settingSubtitle: {
    color: '#666',
    fontSize: 12,
    marginTop: 2,
  },
});

export default SettingsScreen;
