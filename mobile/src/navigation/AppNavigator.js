// Main Navigation
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Home, Folder, Mic, Users, Settings } from 'lucide-react-native';

// Screens
import HomeScreen from '../screens/HomeScreen';
import ProjectsScreen from '../screens/ProjectsScreen';
import ProjectDetailScreen from '../screens/ProjectDetailScreen';
import VoiceScreen from '../screens/VoiceScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const TabNavigator = () => (
  <Tab.Navigator
    screenOptions={{
      headerShown: false,
      tabBarStyle: {
        backgroundColor: '#111',
        borderTopColor: '#222',
        paddingTop: 8,
        paddingBottom: 8,
        height: 70,
      },
      tabBarActiveTintColor: '#8b5cf6',
      tabBarInactiveTintColor: '#666',
      tabBarLabelStyle: {
        fontSize: 11,
        fontWeight: '600',
        marginTop: 4,
      },
    }}
  >
    <Tab.Screen
      name="HomeTab"
      component={HomeScreen}
      options={{
        tabBarLabel: 'Home',
        tabBarIcon: ({ color, size }) => <Home size={size} color={color} />,
      }}
    />
    <Tab.Screen
      name="ProjectsTab"
      component={ProjectsScreen}
      options={{
        tabBarLabel: 'Projects',
        tabBarIcon: ({ color, size }) => <Folder size={size} color={color} />,
      }}
    />
    <Tab.Screen
      name="VoiceTab"
      component={VoiceScreen}
      options={{
        tabBarLabel: 'Voice',
        tabBarIcon: ({ color, size }) => <Mic size={size} color={color} />,
      }}
    />
  </Tab.Navigator>
);

const AppNavigator = () => (
  <NavigationContainer>
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        contentStyle: { backgroundColor: '#0a0a0c' },
      }}
    >
      <Stack.Screen name="Main" component={TabNavigator} />
      <Stack.Screen name="Projects" component={ProjectsScreen} />
      <Stack.Screen name="ProjectDetail" component={ProjectDetailScreen} />
      <Stack.Screen name="Voice" component={VoiceScreen} />
    </Stack.Navigator>
  </NavigationContainer>
);

export default AppNavigator;
